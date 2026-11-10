"""Executa o bot e reinicia quando arquivos Python forem salvos."""

import os
from pathlib import Path
import signal
import subprocess
import sys
import time


PASTA = Path(__file__).resolve().parent
INTERVALO = 0.8
IGNORAR = {".git", ".venv", "__pycache__", "dados_rag"}


def arquivos_python():
    for caminho in PASTA.rglob("*.py"):
        if not any(parte in IGNORAR for parte in caminho.relative_to(PASTA).parts):
            yield caminho


def fotografia_arquivos():
    estado = {}
    caminhos = list(arquivos_python())
    arquivo_configuracao = PASTA / ".env.extensao"
    if arquivo_configuracao.exists():
        caminhos.append(arquivo_configuracao)
    for caminho in caminhos:
        try:
            stat = caminho.stat()
            estado[str(caminho.relative_to(PASTA))] = (stat.st_mtime_ns, stat.st_size)
        except FileNotFoundError:
            continue
    return estado


def validar_sintaxe():
    erros = []
    for caminho in arquivos_python():
        try:
            compile(caminho.read_bytes(), str(caminho), "exec")
        except (OSError, SyntaxError, UnicodeError) as erro:
            erros.append((caminho.name, erro))
    return erros


def iniciar_bot():
    opcoes = {"cwd": PASTA}
    if os.name == "nt":
        opcoes["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        opcoes["start_new_session"] = True
    return subprocess.Popen([sys.executable, "-u", "bot_agentes.py"], **opcoes)


def parar_bot(processo):
    if processo is None or processo.poll() is not None:
        return
    try:
        if os.name == "nt":
            processo.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            processo.send_signal(signal.SIGINT)
        processo.wait(timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        processo.terminate()
        try:
            processo.wait(timeout=5)
        except subprocess.TimeoutExpired:
            processo.kill()
            processo.wait()


def main():
    erros = validar_sintaxe()
    if erros:
        for nome, erro in erros:
            print(f"Sintaxe invalida em {nome}: {erro}", flush=True)
        return 1

    estado = fotografia_arquivos()
    processo = iniciar_bot()
    print("Modo de recarga ativo. Salve um arquivo .py ou .env.extensao para reiniciar o bot.", flush=True)
    try:
        while True:
            time.sleep(INTERVALO)
            novo_estado = fotografia_arquivos()
            if novo_estado == estado:
                if processo is not None and processo.poll() is not None:
                    print(f"Bot encerrou com codigo {processo.returncode}; aguardando alteracao no codigo.", flush=True)
                    processo = None
                continue

            # Aguarda o editor terminar gravações em vários arquivos.
            time.sleep(INTERVALO)
            novo_estado = fotografia_arquivos()
            alterados = sorted(
                nome for nome in set(estado) | set(novo_estado)
                if estado.get(nome) != novo_estado.get(nome)
            )
            estado = novo_estado
            erros = validar_sintaxe()
            if erros:
                for nome, erro in erros:
                    print(f"Recarga aguardando correcao em {nome}: {erro}", flush=True)
                continue

            print("Alteracao detectada:", ", ".join(alterados), flush=True)
            parar_bot(processo)
            processo = iniciar_bot()
            print("Bot reiniciado. A sessao salva sera reutilizada.", flush=True)
    except KeyboardInterrupt:
        print("Encerrando modo de recarga...", flush=True)
        parar_bot(processo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
