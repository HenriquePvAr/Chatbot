
import json
import threading
import os
import time

from dotenv import load_dotenv

# ==========================================
# CONFIGURACOES DA EXTENSAO
# ==========================================

load_dotenv(".env.extensao", override=True)

from neonize.client import NewClient
from neonize.events import (
    ConnectedEv,
    DisconnectedEv,
    MessageEv
)
from neonize import extract_text

from agentes_autonomos import (
    pesquisar_com_ia,
    responder_com_ia
)
from rag_local import listar_documentos
from escopo_assunto import contem_tentativa_de_injecao, pertence_ao_assunto
from fila_whatsapp import FilaMensagens


# ==========================================
# CONFIGURACOES GERAIS
# ==========================================

SESSAO_WHATSAPP = "sessao_whatsapp.db"
SERVIDORES_CHAT_INDIVIDUAL = {
    "s.whatsapp.net",
    "lid",
    "hosted",
    "hosted.lid",
    "c.us",
}

cliente = NewClient(SESSAO_WHATSAPP)

# Estado da conexao
conectado_evento = threading.Event()

# Controle de acesso as conversas
bloqueio = threading.RLock()

# Historico e resultados por conversa
conversas = {}

fila_mensagens = FilaMensagens(
    trabalhadores=max(1, int(os.getenv("WHATSAPP_QUEUE_WORKERS", "2"))),
    rajada_por_usuario=max(1, int(os.getenv("WHATSAPP_USER_BURST", "3"))),
    pausa_segundos=max(0.0, float(os.getenv("WHATSAPP_USER_PAUSE_SECONDS", "5"))),
    maximo_por_usuario=max(1, int(os.getenv("WHATSAPP_MAX_PENDING_PER_USER", "30"))),
    maximo_total=max(1, int(os.getenv("WHATSAPP_MAX_PENDING_TOTAL", "2000"))),
)
avisos_fila_cheia = {}


# ==========================================
# GERENCIAMENTO DE CONVERSAS
# ==========================================

def obter_conversa(identificador):

    if identificador not in conversas:

        conversas[identificador] = {
            "historico": [],
            "plano": None,
            "resultados": None
        }

    return conversas[identificador]


# ==========================================
# GERAR MENU
# ==========================================

def gerar_menu():
    return (
        "ASSISTENTE CULTURA AFRO-INDIGENA 2026.2\n\n"
        "Envie sua pergunta sobre o tema do projeto. Consulto os documentos e posso pesquisar na web.\n\n"
        "/web pergunta - Forcar pesquisa na web\n"
        "/documentos - Ver materiais indexados\n"
        "/ajuda - Exemplos de perguntas\n"
        "/limpar - Reiniciar a conversa"
    )


def gerar_ajuda():
    return (
        "POSSO AJUDAR COM\n\n"
        "- Historia e culturas afro-brasileiras e indigenas\n"
        "- Identidade, memoria, territorio e resistencia\n"
        "- Contribuicoes culturais e respeito intercultural\n"
        "- Resumos, atividades, apresentacoes e ideias para o projeto\n\n"
        "Para pedir pesquisa na internet, envie /web seguido da pergunta.\n\n"
        "Pergunte livremente. Vou indicar quando uma informacao vier dos documentos do projeto ou de conhecimento geral.\n\n"
        "/documentos - Ver materiais disponiveis\n"
        "/limpar - Limpar o historico"
    )


def gerar_sobre():
    return (
        "ASSISTENTE CULTURA AFRO-INDIGENA\n\n"
        "Assistente escolar sobre cultura afro-indigena, integrado ao WhatsApp e ao Ollama. "
        "Usa a base local e pode pesquisar na web, citando fontes e links."
    )


def gerar_lista_documentos():
    documentos = listar_documentos()
    if not documentos:
        return "Ainda nao ha documentos indexados. Recrie a base RAG antes de consultar os materiais."
    linhas = ["MATERIAIS NA BASE DE CONHECIMENTO:"]
    for documento in documentos:
        detalhe = f"{documento['trechos_indexados']} trechos"
        if documento.get("paginas_indexadas"):
            detalhe += f", {documento['paginas_indexadas']} paginas"
        if documento.get("secoes_indexadas"):
            detalhe += f", secoes: {', '.join(documento['secoes_indexadas'])}"
        linhas.append(f"- {documento['arquivo']} ({detalhe})")
    return "\n".join(linhas)


# ==========================================
# PROCESSAR PERGUNTA COM DOIS AGENTES
# ==========================================

def processar_pergunta(pergunta, identificador, forcar_web=False):
    # A fila ja serializa cada conversa. O lock protege apenas a memoria curta,
    # sem segurar os outros usuarios enquanto o Ollama ou a web respondem.
    with bloqueio:
        conversa = obter_conversa(identificador)
        historico = list(conversa["historico"])

    print("\n[IA 1] Iniciando planejamento...", flush=True)
    pesquisa = pesquisar_com_ia(
        pergunta,
        historico,
        forcar_web=forcar_web,
    )
    print("\n[IA 1] Pesquisa concluida.", flush=True)
    print("Categoria:", pesquisa["categoria"], flush=True)
    print("Consultas realizadas:", pesquisa["consultas"], flush=True)

    print("\n[IA 2] Gerando resposta...", flush=True)
    resposta = responder_com_ia(pergunta, pesquisa, historico)

    with bloqueio:
        conversa = obter_conversa(identificador)
        conversa["historico"] = (
            historico
            + [
                {"role": "user", "content": pergunta},
                {"role": "assistant", "content": resposta},
            ]
        )[-12:]
        conversa["plano"] = pesquisa
        conversa["resultados"] = pesquisa["evidencias"]

    print("\n[IA 2] Resposta final:", resposta, flush=True)
    return resposta


# ==========================================
# EVENTO: CONEXAO WHATSAPP
# ==========================================

@cliente.event(ConnectedEv)
def conectado(client, evento):

    conectado_evento.set()

    print(
        "\n✅ WhatsApp conectado!",
        flush=True
    )

    print(
        "🤖 Dois agentes de IA disponíveis.",
        flush=True
    )

    print(
        "📨 Aguardando perguntas...\n",
        flush=True
    )


# ==========================================
# EVENTO: DESCONEXAO WHATSAPP
# ==========================================

@cliente.event(DisconnectedEv)
def desconectado(client, evento):

    conectado_evento.clear()

    print(
        "\n⚠️ WhatsApp desconectado!",
        flush=True
    )

    print(
        "Aguardando reconexão...",
        flush=True
    )


# ==========================================
# ENVIAR RESPOSTA PELO WHATSAPP
# ==========================================

def enviar_resposta(client, evento, texto):

    # Verificar conexao
    if not conectado_evento.is_set():

        print(
            "WhatsApp desconectado. "
            "Aguardando reconexão...",
            flush=True
        )

        conectado_evento.wait(
            timeout=30
        )

    if not conectado_evento.is_set():

        print(
            "Resposta não enviada: "
            "WhatsApp indisponível.",
            flush=True
        )

        return False

    try:

        print(
            "\n📤 Enviando resposta...",
            flush=True
        )

        client.reply_message(
            texto,
            evento
        )

        print(
            "✅ Resposta enviada!",
            flush=True
        )

        return True

    except Exception as erro:

        print(
            "❌ Erro ao enviar resposta:",
            repr(erro),
            flush=True
        )

        if "client is nil" in str(erro).lower():

            conectado_evento.clear()

            print(
                "Cliente WhatsApp indisponível. "
                "Aguardando reconexão.",
                flush=True
            )

        return False


# ==========================================
# EVENTO: NOVA MENSAGEM
# ==========================================

def responder_mensagem(texto, identificador):
    comando = texto.strip().lower()

    if comando in ("/menu", "/ajuda", "/sobre", "/documentos", "/plano", "/limpar"):
        if comando == "/menu":
            return gerar_menu()
        if comando == "/ajuda":
            return gerar_ajuda()
        if comando == "/sobre":
            return gerar_sobre()
        if comando == "/documentos":
            return gerar_lista_documentos()
        if comando == "/plano":
            with bloqueio:
                plano = obter_conversa(identificador)["plano"]
            if not plano:
                return "Nenhuma pesquisa foi realizada nesta conversa."
            return "ULTIMA PESQUISA DA IA\n\n" + json.dumps(
                plano, ensure_ascii=False, indent=2
            )[:3500]
        with bloqueio:
            conversas.pop(identificador, None)
        return "Conversa reiniciada. O historico e as pesquisas anteriores foram apagados."

    forcar_web = comando == "/web" or comando.startswith("/web ")
    pergunta = texto[4:].strip() if forcar_web else texto.strip()
    if forcar_web and not pergunta:
        return "Envie a pergunta depois de /web. Exemplo: /web historia do Quilombo dos Palmares"

    with bloqueio:
        historico = list(obter_conversa(identificador)["historico"])

    if contem_tentativa_de_injecao(pergunta):
        return "Nao posso seguir instrucoes para ignorar as regras ou revelar prompts internos. Posso ajudar com duvidas sobre cultura e historia afro-brasileira e indigena."

    if not pertence_ao_assunto(pergunta, historico):
        return "Sou um assistente apenas sobre historia, culturas e povos afro-brasileiros e indigenas. Envie uma pergunta dentro desse tema."

    return processar_pergunta(pergunta, identificador, forcar_web=forcar_web)


def processar_item_fila(item):
    client, evento, texto, identificador = item
    try:
        resposta = responder_mensagem(texto, identificador)
    except Exception as erro:
        print("Erro no processamento da fila:", repr(erro), flush=True)
        resposta = "Nao consegui responder agora. Sua mensagem continua dentro do tema; tente novamente em alguns instantes."
    enviar_resposta(client, evento, resposta)


@cliente.event(MessageEv)
def mensagem(client, evento):
    try:
        origem = evento.Info.MessageSource
        if origem.IsFromMe:
            return
        if origem.Chat.Server not in SERVIDORES_CHAT_INDIVIDUAL:
            return

        texto = (extract_text(evento.Message) or "").strip()
        if not texto:
            return

        identificador = f"{origem.Chat.User}@{origem.Chat.Server}"
        item = (client, evento, texto, identificador)
        if not fila_mensagens.enviar(identificador, item):
            agora = time.monotonic()
            with bloqueio:
                ultimo_aviso = avisos_fila_cheia.get(identificador, 0)
                pode_avisar = agora - ultimo_aviso >= 60
                if pode_avisar:
                    avisos_fila_cheia[identificador] = agora
            if pode_avisar:
                enviar_resposta(
                    client,
                    evento,
                    "Recebi muitas mensagens de uma vez. A fila esta cheia; aguarde um pouco e envie novamente.",
                )
            print("Fila cheia para", identificador, flush=True)
    except Exception as erro:
        print("Erro ao receber mensagem do WhatsApp:", repr(erro), flush=True)


# ==========================================
# INICIAR APLICACAO
# ==========================================

if __name__ == "__main__":

    print("====================================")
    print("    WHATSAPP - DOIS AGENTES DE IA")
    print("====================================")

    print(
        "Iniciando chatbot...",
        flush=True
    )

    fila_mensagens.iniciar(processar_item_fila)
    try:
        cliente.connect()
    finally:
        fila_mensagens.parar(aguardar=False)
