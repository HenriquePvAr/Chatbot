$ErrorActionPreference = "Stop"
$repo = (Resolve-Path -LiteralPath $PSScriptRoot).Path
Set-Location -LiteralPath $repo

function Find-CommandPath([string]$Name) {
    $found = Get-Command $Name -ErrorAction SilentlyContinue
    if ($found) { return $found.Source }
    return $null
}

function Refresh-UserPath {
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $machinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $env:Path = @($userPath, $machinePath, $env:Path) -join ";"
}

function Install-Python {
    $winget = Find-CommandPath "winget.exe"
    if ($winget) {
        Write-Host "Instalando Python 3.12 x64 pelo WinGet..."
        & $winget install --id Python.Python.3.12 --exact --scope user --silent --accept-package-agreements --accept-source-agreements
        if ($LASTEXITCODE -ne 0) { Write-Warning "WinGet nao concluiu a instalacao do Python; tentando o instalador oficial." }
    }
    Refresh-UserPath
    $python = Find-CommandPath "python.exe"
    if (-not $python) { $python = Find-CommandPath "py.exe" }
    if (-not $python) {
        Write-Host "Baixando o instalador oficial do Python 3.12 x64..."
        $page = Invoke-WebRequest -Uri "https://www.python.org/downloads/windows/" -UseBasicParsing
        $match = [regex]::Match($page.Content, 'https://www\.python\.org/ftp/python/3\.12\.[0-9]+/python-3\.12\.[0-9]+-amd64\.exe')
        if (-not $match.Success) { throw "Nao encontrei o instalador oficial do Python 3.12 x64 em python.org." }
        $installer = Join-Path $env:TEMP "python-3.12-amd64-setup.exe"
        Invoke-WebRequest -Uri $match.Value -OutFile $installer -UseBasicParsing
        $proc = Start-Process -FilePath $installer -ArgumentList @("/quiet", "InstallAllUsers=0", "PrependPath=1", "Include_launcher=1", "Include_test=0") -Wait -PassThru
        if ($proc.ExitCode -ne 0) { throw "Instalador do Python terminou com codigo $($proc.ExitCode)." }
        Refresh-UserPath
        $python = Find-CommandPath "python.exe"
        if (-not $python) { $python = Find-CommandPath "py.exe" }
    }
    if (-not $python) { throw "Python foi instalado, mas nao foi localizado. Feche e reabra o PowerShell e execute o script novamente." }
    return $python
}

function Get-PythonInfo([string]$Executable) {
    $output = & $Executable -c "import json,struct,sys; print(json.dumps({'exe':sys.executable,'version':list(sys.version_info[:2]),'bits':struct.calcsize('P')*8}))" 2>$null
    if ($LASTEXITCODE -ne 0) { return $null }
    try { return ($output | ConvertFrom-Json) } catch { return $null }
}

$venvPython = Join-Path $repo ".venv\Scripts\python.exe"
$python = $null
if (Test-Path -LiteralPath $venvPython) {
    $info = Get-PythonInfo $venvPython
    if ($info -and $info.version[0] -ge 3 -and ($info.version[0] -gt 3 -or $info.version[1] -ge 10) -and $info.bits -eq 64) {
        $python = $venvPython
        Write-Host "Reutilizando o ambiente virtual existente ($($info.version -join '.'))."
    } else {
        Write-Warning "O ambiente .venv existente esta quebrado ou usa Python incompatível; vou preserva-lo e criar .venv_novo."
    }
}

if (-not $python) {
    $systemPython = Find-CommandPath "python.exe"
    $launcher = Find-CommandPath "py.exe"
    if ($systemPython) {
        $candidate = $systemPython
    } elseif ($launcher) {
        $candidate = $launcher
    } else {
        $candidate = Install-Python
    }
    $info = Get-PythonInfo $candidate
    if (-not $info -and (Split-Path $candidate -Leaf) -ieq "py.exe") {
        $candidate = (& $candidate -3 -c "import sys; print(sys.executable)").Trim()
        $info = Get-PythonInfo $candidate
    }
    if (-not $info -or $info.bits -ne 64 -or $info.version[0] -lt 3 -or ($info.version[0] -eq 3 -and $info.version[1] -lt 10)) {
        Write-Host "Python ausente ou incompativel; instalando Python 3.12 x64..."
        $candidate = Install-Python
        $info = Get-PythonInfo $candidate
        if (-not $info -and (Split-Path $candidate -Leaf) -ieq "py.exe") {
            $candidate = (& $candidate -3.12 -c "import sys; print(sys.executable)").Trim()
            $info = Get-PythonInfo $candidate
        }
    }
    if (-not $info -or $info.bits -ne 64 -or $info.version[0] -lt 3 -or ($info.version[0] -eq 3 -and $info.version[1] -lt 10)) {
        throw "Nao foi possivel instalar ou localizar Python 3.10+ de 64 bits."
    }

    $venvPath = Join-Path $repo ".venv"
    if (Test-Path -LiteralPath $venvPath) {
        $resolvedVenv = (Resolve-Path -LiteralPath $venvPath).Path
        if (-not $resolvedVenv.StartsWith(($repo.TrimEnd('\') + '\'), [StringComparison]::OrdinalIgnoreCase)) { throw "Caminho .venv fora da pasta do projeto; abortando por seguranca." }
        $backupPath = Join-Path $repo (".venv_invalido_" + (Get-Date -Format "yyyyMMdd_HHmmss"))
        Move-Item -LiteralPath $resolvedVenv -Destination $backupPath
        Write-Host "Ambiente anterior preservado em $(Split-Path $backupPath -Leaf)."
    }
    Write-Host "Criando ambiente virtual Python..."
    & $candidate -m venv $venvPath
    if ($LASTEXITCODE -ne 0) { throw "Falha ao criar o ambiente virtual Python." }
    $python = $venvPython
}

$info = Get-PythonInfo $python
if (-not $info) { throw "Nao foi possivel iniciar o Python em $python." }
Write-Host "Python $($info.version -join '.') ($($info.bits) bits) pronto."

$ollama = Find-CommandPath "ollama.exe"
if (-not $ollama) {
    $winget = Find-CommandPath "winget.exe"
    if ($winget) {
        Write-Host "Instalando Ollama pelo WinGet..."
        & $winget install --id Ollama.Ollama --exact --scope user --silent --accept-package-agreements --accept-source-agreements
        Refresh-UserPath
        $ollama = Find-CommandPath "ollama.exe"
    }
    if (-not $ollama) {
        Write-Host "Instalando Ollama pelo instalador oficial..."
        Invoke-Expression (Invoke-WebRequest -Uri "https://ollama.com/install.ps1" -UseBasicParsing).Content
        Refresh-UserPath
        $ollama = Find-CommandPath "ollama.exe"
    }
}
if (-not $ollama) { throw "Ollama nao foi localizado apos a instalacao. Feche e reabra o PowerShell e tente novamente." }

$envFile = Join-Path $repo ".env.extensao"
$envExample = Join-Path $repo ".env.extensao.example"
if (-not (Test-Path -LiteralPath $envFile)) {
    Copy-Item -LiteralPath $envExample -Destination $envFile
    Write-Host "Criado .env.extensao a partir do exemplo; configuracoes existentes sao preservadas."
}
$ollamaUrl = "http://localhost:11434"
$model = "qwen2.5:3b"
$embeddingModel = "nomic-embed-text"
foreach ($line in Get-Content -LiteralPath $envFile) {
    if ($line -match '^\s*OLLAMA_URL\s*=\s*(.+?)\s*$') { $ollamaUrl = $Matches[1].Trim('"', "'") }
    if ($line -match '^\s*OLLAMA_MODEL\s*=\s*(.+?)\s*$') { $model = $Matches[1].Trim('"', "'") }
    if ($line -match '^\s*EMBEDDING_MODEL\s*=\s*(.+?)\s*$') { $embeddingModel = $Matches[1].Trim('"', "'") }
}

$ollamaHost = $ollamaUrl -replace '/+$', ''
$env:OLLAMA_HOST = $ollamaHost
$apiReady = $false
for ($attempt = 0; $attempt -lt 10; $attempt++) {
    try { Invoke-RestMethod -Uri "$ollamaHost/api/version" -TimeoutSec 3 | Out-Null; $apiReady = $true; break }
    catch { Start-Sleep -Seconds 2 }
}
if (-not $apiReady -and $ollamaHost -match '^https?://(localhost|127\.0\.0\.1)(:\d+)?$') {
    Write-Host "Iniciando o servico local do Ollama em segundo plano..."
    try { Start-Process -FilePath $ollama -ArgumentList "serve" -WindowStyle Hidden | Out-Null } catch { }
    for ($attempt = 0; $attempt -lt 20; $attempt++) {
        try { Invoke-RestMethod -Uri "$ollamaHost/api/version" -TimeoutSec 3 | Out-Null; $apiReady = $true; break }
        catch { Start-Sleep -Seconds 2 }
    }
}
if (-not $apiReady) { throw "A API do Ollama nao respondeu em $ollamaHost. Confira OLLAMA_URL e tente novamente." }

Write-Host "Verificando dependencias Python..."
& $python -m pip install --disable-pip-version-check -r (Join-Path $repo "requirements.txt")
if ($LASTEXITCODE -ne 0) { throw "Falha ao instalar dependencias Python." }
$neonizeCheck = & $python -c "from neonize.client import NewClient; print('neonize OK')" 2>&1
if ($LASTEXITCODE -ne 0) {
    $diagnosticoNeonize = $neonizeCheck -join "`n"
    if ($diagnosticoNeonize -match '4551|Application Control|Controle de Aplicativo') {
        throw "O Windows bloqueou a DLL nativa do Neonize pela politica de Controle de Aplicativos (WinError 4551). Peca ao administrador de TI para liberar o componente. O script nao contorna essa politica."
    }
    throw "A dependencia Neonize nao conseguiu carregar. Diagnostico: $diagnosticoNeonize"
}
Write-Host "Neonize carregado; a conexao WhatsApp pode iniciar."

$tags = Invoke-RestMethod -Uri "$ollamaHost/api/tags" -TimeoutSec 10
$installedModels = @($tags.models | ForEach-Object { $_.name })
foreach ($requiredModel in @($model, $embeddingModel)) {
    $present = $installedModels | Where-Object { $_ -eq $requiredModel -or $_ -eq ($requiredModel + ":latest") }
    if (-not $present) {
        Write-Host "Baixando modelo ausente: $requiredModel"
        & $ollama pull $requiredModel
        if ($LASTEXITCODE -ne 0) { throw "Falha ao baixar o modelo $requiredModel." }
    } else { Write-Host "Modelo ja instalado: $requiredModel" }
}

$documentsPath = Join-Path $repo "documents"
$manifestPath = Join-Path $repo "dados_rag\setup_manifest.json"
$indexPath = Join-Path $repo "dados_rag\indice.json"
$docHashes = @()
if (Test-Path -LiteralPath $documentsPath) {
    $docHashes = @(Get-ChildItem -LiteralPath $documentsPath -Recurse -File | Where-Object { $_.Extension -in @(".md", ".pdf", ".txt") } | Sort-Object FullName | ForEach-Object {
        [PSCustomObject]@{ name = $_.FullName.Substring($repo.Length).TrimStart('\'); hash = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash }
    })
}
$manifest = @{ model = $embeddingModel; documents = $docHashes }
$manifestJson = $manifest | ConvertTo-Json -Depth 5 -Compress
$sameIndex = $false
if ((Test-Path -LiteralPath $indexPath) -and (Test-Path -LiteralPath $manifestPath)) {
    try { $sameIndex = ((Get-Content -Raw -LiteralPath $manifestPath).Trim() -eq $manifestJson) } catch { $sameIndex = $false }
}
if ($sameIndex) {
    Write-Host "Indice RAG ja atualizado; ignorando reindexacao."
} else {
    Write-Host "Indexando materiais novos ou alterados em documents/..."
    & $python (Join-Path $repo "indexar_pdfs.py")
    if ($LASTEXITCODE -ne 0) { throw "Falha ao indexar os documentos." }
    $manifestJson | Set-Content -LiteralPath $manifestPath -Encoding UTF8
}

Write-Host ""
Write-Host "Ambiente pronto. Inicie com: .\.venv\Scripts\python.exe .\bot_agentes.py"
Write-Host "Para recarregar mudancas Python automaticamente: .\.venv\Scripts\python.exe .\rodar_com_reload.py"
Write-Host "Se o Windows bloquear neonize-windows-amd64.dll (WinError 4551), solicite a liberacao da politica ao administrador de TI; este script nao tenta contorna-la."
