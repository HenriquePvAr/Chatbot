$ErrorActionPreference = "Stop"
$repo = $PSScriptRoot
Set-Location -LiteralPath $repo

$pythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue
if (-not $pythonCommand) {
    throw "Python 3.10+ nao foi encontrado. Instale-o e marque 'Add Python to PATH'."
}

$pythonVersionText = & $pythonCommand.Source --version 2>&1
if ($pythonVersionText -notmatch 'Python\s+(\d+)\.(\d+)') {
    throw "Nao consegui identificar a versao do Python: $pythonVersionText"
}
$pythonMajor = [int]$Matches[1]
$pythonMinor = [int]$Matches[2]
if (($pythonMajor -lt 3) -or (($pythonMajor -eq 3) -and ($pythonMinor -lt 10))) {
    throw "Python 3.10+ e necessario. Versao encontrada: $pythonVersionText"
}

$ollamaCommand = Get-Command ollama.exe -ErrorAction SilentlyContinue
if (-not $ollamaCommand) {
    throw "Ollama nao foi encontrado. Instale-o em https://ollama.com/download/windows, abra-o e execute este script novamente."
}

$envFile = Join-Path $repo ".env.extensao"
$envExample = Join-Path $repo ".env.extensao.example"
if (-not (Test-Path -LiteralPath $envFile)) {
    Copy-Item -LiteralPath $envExample -Destination $envFile
    Write-Host "Criado .env.extensao a partir do exemplo."
}

$ollamaUrl = "http://localhost:11434"
$model = "qwen2.5:3b"
$embeddingModel = "nomic-embed-text"
foreach ($line in Get-Content -LiteralPath $envFile) {
    if ($line -match '^\s*OLLAMA_URL\s*=\s*(.+?)\s*$') { $ollamaUrl = $Matches[1] }
    if ($line -match '^\s*OLLAMA_MODEL\s*=\s*(.+?)\s*$') { $model = $Matches[1] }
    if ($line -match '^\s*EMBEDDING_MODEL\s*=\s*(.+?)\s*$') { $embeddingModel = $Matches[1] }
}

$ollamaHost = $ollamaUrl -replace '/+$', ''
$env:OLLAMA_HOST = $ollamaHost
$apiReady = $false
for ($attempt = 0; $attempt -lt 15; $attempt++) {
    try {
        Invoke-RestMethod -Uri "$ollamaHost/api/version" -TimeoutSec 3 | Out-Null
        $apiReady = $true
        break
    }
    catch {
        Start-Sleep -Seconds 2
    }
}
if (-not $apiReady) {
    throw "A API do Ollama nao respondeu em $ollamaHost. Abra o Ollama, aguarde iniciar e tente novamente."
}

$venvPython = Join-Path $repo ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $venvPython)) {
    & $pythonCommand.Source -m venv (Join-Path $repo ".venv")
    if ($LASTEXITCODE -ne 0) { throw "Falha ao criar o ambiente virtual." }
}

& $venvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "Falha ao atualizar o pip." }
& $venvPython -m pip install -r (Join-Path $repo "requirements.txt")
if ($LASTEXITCODE -ne 0) { throw "Falha ao instalar as dependencias Python." }

Write-Host "Baixando modelo de conversa: $model"
& $ollamaCommand.Source pull $model
if ($LASTEXITCODE -ne 0) { throw "Falha ao baixar o modelo $model." }

Write-Host "Baixando modelo de embeddings: $embeddingModel"
& $ollamaCommand.Source pull $embeddingModel
if ($LASTEXITCODE -ne 0) { throw "Falha ao baixar o modelo $embeddingModel." }

Write-Host "Indexando os materiais em documents/..."
& $venvPython (Join-Path $repo "indexar_pdfs.py")
if ($LASTEXITCODE -ne 0) { throw "Falha ao indexar os documentos." }

Write-Host ""
Write-Host "Ambiente pronto. Inicie com: .\.venv\Scripts\python.exe .\bot_agentes.py"
