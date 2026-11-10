
import json
import re
import sys
import threading
import os
import time
from datetime import datetime
from collections import OrderedDict

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
from busca_web import pesquisar_web
from rag_local import listar_documentos
from escopo_assunto import (
    contem_tentativa_de_injecao,
    eh_conteudo_improprio,
    eh_cumprimento,
    eh_reacao_curta,
    pertence_ao_assunto,
    normalizar,
)
from fila_whatsapp import FilaMensagens
from midia_whatsapp import buscar_imagem, buscar_imagens, ImagemNaoEncontrada
from faq_esbam import responder_faq_esbam


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


def adquirir_lock_instancia():
    """Impede que duas copias conectem a mesma sessao do WhatsApp."""
    pasta_logs = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(pasta_logs, exist_ok=True)
    arquivo_lock = open(os.path.join(pasta_logs, "bot_agentes.lock"), "a+b")
    arquivo_lock.seek(0, os.SEEK_END)
    if arquivo_lock.tell() == 0:
        arquivo_lock.write(b"0")
        arquivo_lock.flush()
    arquivo_lock.seek(0)
    try:
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(arquivo_lock.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(arquivo_lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except (OSError, BlockingIOError):
        arquivo_lock.close()
        print(
            "Outra instancia do bot ja esta conectada a esta sessao do WhatsApp; "
            "esta copia sera encerrada.",
            flush=True,
        )
        raise SystemExit(0)
    return arquivo_lock


_LOCK_INSTANCIA = adquirir_lock_instancia()

cliente = NewClient(SESSAO_WHATSAPP)

# Estado da conexao
conectado_evento = threading.Event()
INICIO_PROCESSO_TIMESTAMP = time.time()
inicio_conexao_timestamp = INICIO_PROCESSO_TIMESTAMP

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
avisos_fora_tema = {}
mensagens_em_rajada = {}
JANELA_AGRUPAMENTO_MENSAGENS = max(
    0.3, float(os.getenv("WHATSAPP_MESSAGE_BURST_WINDOW_SECONDS", "1.8"))
)
INTERVALO_AVISO_FORA_TEMA = max(
    30, int(os.getenv("WHATSAPP_OFF_TOPIC_NOTICE_SECONDS", "180"))
)
INTERVALO_FIGURINHA = max(2, int(os.getenv("WHATSAPP_STICKER_INTERVAL", "5")))

# O Neonize pode reentregar mensagens pendentes ao conectar ou reconectar.
# Processamos apenas mensagens recentes e guardamos IDs recentes para evitar
# respostas duplicadas se o mesmo evento for emitido mais de uma vez.
IDADE_MAXIMA_MENSAGEM_SEGUNDOS = max(
    30, int(os.getenv("WHATSAPP_MAX_MESSAGE_AGE_SECONDS", "120"))
)
MAXIMO_IDS_RECENTES = 10000
ids_mensagens_recentes = OrderedDict()


# ==========================================
# GERENCIAMENTO DE CONVERSAS
# ==========================================

def obter_conversa(identificador):

    if identificador not in conversas:

        conversas[identificador] = {
            "historico": [],
            "plano": None,
            "resultados": None,
            "ultima_pergunta": None
        }

    return conversas[identificador]


# ==========================================
# GERAR MENU
# ==========================================

def gerar_menu():
    return (
        "Oi! Sou o assistente do projeto sobre histórias e culturas afro-brasileiras e indígenas.\n\n"
        "Você pode perguntar, por exemplo:\n"
        "• O que são povos afro-brasileiros?\n"
        "• Qual é a função do berimbau na capoeira?\n"
        "• Quem foi Tereza de Benguela?\n"
        "• Como os povos indígenas preservam suas línguas?\n\n"
        "Voce tambem pode perguntar: O que e a ESBAM? Qual o telefone ou o Instagram?\n\n"
        "/menu — mostrar este menu\n"
        "/web pergunta — pesquisar na internet\n"
        "/fontes — buscar referências da última resposta\n\n"
        "Pode escrever normalmente; não precisa usar comandos."
    )


def gerar_ajuda():
    return (
        gerar_menu()
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
# PESQUISAR FONTES E RESPONDER
# ==========================================

def processar_pergunta(pergunta, identificador, forcar_web=False):
    # A fila ja serializa cada conversa. O lock protege apenas a memoria curta,
    # sem segurar os outros usuarios enquanto o Ollama ou a web respondem.
    with bloqueio:
        conversa = obter_conversa(identificador)
        historico = list(conversa["historico"])

    print("\n[FONTES] Consultando documentos e pesquisa...", flush=True)
    pesquisa = pesquisar_com_ia(
        pergunta,
        historico,
        forcar_web=forcar_web,
    )
    print("\n[FONTES] Consulta concluida.", flush=True)
    print("Fontes:", pesquisa["categoria"], flush=True)
    print("Consultas realizadas:", pesquisa["consultas"], flush=True)

    print("\n[RESPOSTA] Preparando resposta...", flush=True)
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
        conversa["ultima_pergunta"] = pergunta

    print("\n[RESPOSTA] Texto preparado:", resposta, flush=True)
    return resposta


# ==========================================
# EVENTO: CONEXAO WHATSAPP
# ==========================================

@cliente.event(ConnectedEv)
def conectado(client, evento):

    global inicio_conexao_timestamp
    inicio_conexao_timestamp = time.time()
    conectado_evento.set()

    print(
        "\n✅ WhatsApp conectado!",
        flush=True
    )

    print(
        "🤖 Assistente com fontes locais e pesquisa na web disponivel.",
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
    if eh_conteudo_improprio(texto):
        return (
            "Posso ajudar com conteúdos educativos e respeitosos sobre histórias e "
            "culturas afro-brasileiras e indígenas. Não produzo material sexual "
            "explícito, sexualização de menores, ataques a grupos ou instruções de "
            "violência. Posso explicar um tema histórico de forma adequada e sem "
            "detalhes gráficos."
        )
    pergunta_fontes = bool(re.search(
        r"\b(fontes?|referencias?|links?|de onde (?:veio|tirou)|qual a fonte|tem fonte|tem fontes)\b",
        normalizar(texto),
    ))

    if comando in ("/menu", "/ajuda", "/fontes", "/sobre", "/plano") or pergunta_fontes:
        if comando == "/menu":
            return gerar_menu()
        if comando == "/ajuda":
            return gerar_ajuda()
        if comando == "/fontes" or pergunta_fontes:
            return pesquisar_fontes_ultima_resposta(identificador)
        if comando == "/sobre":
            return gerar_sobre()
        if comando == "/plano":
            with bloqueio:
                plano = obter_conversa(identificador)["plano"]
            if not plano:
                return "Nenhuma pesquisa foi realizada nesta conversa."
            return "ULTIMA PESQUISA DA IA\n\n" + json.dumps(
                plano, ensure_ascii=False, indent=2
            )[:3500]

    resposta_esbam = responder_faq_esbam(texto)
    if resposta_esbam:
        return resposta_esbam

    forcar_web = comando == "/web" or comando.startswith("/web ")
    pergunta = texto[4:].strip() if forcar_web else texto.strip()
    if forcar_web and not pergunta:
        return "Envie a pergunta depois de /web. Exemplo: /web historia do Quilombo dos Palmares"

    if eh_cumprimento(pergunta):
        return (
            "Oi! 😊 Posso explicar histórias e culturas afro-brasileiras e indígenas. "
            "Por exemplo: “O que são povos afro-brasileiros?”, “Qual é a função "
            "do berimbau na capoeira?” ou “Quem foi Tereza de Benguela?”. "
            "Digite /menu para ver mais exemplos."
        )
    conversa_curta = normalizar(pergunta).strip(" .!?\t\n")
    if re.fullmatch(
        r"(?:bugou|travou|ta ai|esta ai|ainda ta ai|esta funcionando|"
        r"ta funcionando|funciona|teste|testando|oxi|oxe|ixi)",
        conversa_curta,
    ):
        return (
            "Estou aqui 😊 Pode mandar sua pergunta sobre histórias e culturas "
            "afro-brasileiras ou indígenas; se eu demorar, talvez esteja buscando "
            "informações."
        )
    if eh_reacao_curta(pergunta):
        return None

    with bloqueio:
        historico = list(obter_conversa(identificador)["historico"])

    if contem_tentativa_de_injecao(pergunta):
        return "Nao posso seguir instrucoes para ignorar as regras ou revelar prompts internos. Posso ajudar com duvidas sobre cultura e historia afro-brasileira e indigena."

    pergunta_normalizada = normalizar(pergunta)
    mistura_povos = (
        ("povos originarios" in pergunta_normalizada or "povos indigen" in pergunta_normalizada)
        and re.search(r"afro[- ]brasileir", pergunta_normalizada)
    )
    if mistura_povos:
        resposta = (
            "Essa expressao mistura categorias diferentes. Povos originarios sao povos "
            "indigenas: o Censo 2022 identificou 391 etnias, povos ou grupos; entre os "
            "mais numerosos estao Tikuna, Kokama, Makuxi e Guarani Kaiowa. "
            "Comunidades quilombolas e de matriz africana aparecem como segmentos "
            "tradicionais distintos dos povos indigenas. Ha pessoas com identidades "
            "afro-indigenas, mas os termos nao formam uma unica categoria. Voce queria "
            "saber sobre povos indigenas ou comunidades afro-brasileiras?\n\n"
            "Fontes: IBGE https://www.ibge.gov.br/brasil-indigena/ "
            "| MDA https://www.gov.br/mda/pt-br/acesso-a-informacao/acoes-e-programas/"
            "programas-projetos-acoes-obras-e-atividades/selos-quilombolas/"
            "selo-povos-e-comunidades-tradicionais-do-brasil"
        )
        with bloqueio:
            conversa = obter_conversa(identificador)
            conversa["historico"] = (
                historico
                + [
                    {"role": "user", "content": pergunta},
                    {"role": "assistant", "content": resposta},
                ]
            )[-12:]
            conversa["ultima_pergunta"] = pergunta
        return resposta

    solicitacao_midia = extrair_solicitacao_midia(texto)
    if solicitacao_midia:
        tipo, assunto = solicitacao_midia
        assunto_normalizado = normalizar(assunto).strip(" .,!?")
        if assunto_normalizado in {"cultura", "historia", "povo", "povos", "tradicao", "tradicoes"}:
            assunto = next(
                (
                    assunto_para_midia(mensagem.get("content", ""))
                    for mensagem in reversed(historico)
                    if mensagem.get("role") == "user"
                    and assunto_para_midia(mensagem.get("content", ""))
                ),
                "",
            )
        if not assunto:
            return "Qual povo ou manifestacao cultural voce quer ver? Por exemplo: capoeira, Quilombo dos Palmares ou arte Kusiwa do povo Wajapi."
        if not pertence_ao_assunto(assunto, historico):
            return "Posso buscar imagens relacionadas ao tema do projeto. Diga qual povo, periodo ou manifestacao cultural voce quer ver."
        try:
            if tipo == "imagens":
                return {"tipo_midia": "imagens", "itens": buscar_imagens(assunto, quantidade=2)}
            dados, titulo, atribuicao = buscar_imagem(assunto)
            return {"tipo_midia": tipo, "dados": dados, "titulo": titulo, "atribuicao": atribuicao}
        except ImagemNaoEncontrada as erro:
            return str(erro)
        except Exception as erro:
            print("Erro na busca de imagem:", repr(erro), flush=True)
            return "Nao consegui buscar uma imagem agora. Tente novamente em alguns instantes."

    if not pertence_ao_assunto(pergunta, historico):
        agora = time.monotonic()
        with bloqueio:
            ultimo_aviso = avisos_fora_tema.get(identificador, 0)
            if agora - ultimo_aviso < INTERVALO_AVISO_FORA_TEMA:
                return None
            avisos_fora_tema[identificador] = agora
        return (
            "Posso ajudar com histórias e culturas afro-brasileiras e indígenas. "
            "Tente, por exemplo: “Quais povos indígenas vivem no Brasil?” ou "
            "“Quem são personalidades negras importantes?”. Digite /menu para ver exemplos."
        )

    resposta = processar_pergunta(pergunta, identificador, forcar_web=forcar_web)
    assunto_visual = assunto_para_midia(pergunta)
    if assunto_visual and eh_pedido_explicativo(pergunta):
        try:
            dados, titulo, atribuicao = buscar_imagem(assunto_visual)
            return {
                "tipo_midia": "imagem_com_texto",
                "texto": resposta,
                "dados": dados,
                "titulo": titulo,
                "atribuicao": atribuicao,
            }
        except Exception as erro:
            print("Imagem ilustrativa indisponivel:", repr(erro), flush=True)
    return resposta


def gerar_fontes(evidencias):
    """Formata links da web usados ou pesquisados para a conversa."""
    fontes = []
    vistas = set()
    for evidencia in evidencias:
        if evidencia.get("ferramenta") != "web_busca":
            continue
        resultado = evidencia.get("resultado") or {}
        for item in resultado.get("resultados") or []:
            titulo = str(item.get("titulo") or "Fonte da web").strip()
            url = str(item.get("url") or "").strip()
            chave = url or titulo
            if chave and chave not in vistas:
                vistas.add(chave)
                fontes.append(f"{len(fontes) + 1}. {titulo}" + (f": {url}" if url else ""))
            if len(fontes) >= 5:
                break
    if not fontes:
        return "Não encontrei referências online para esta resposta. Posso tentar outra busca se você me disser qual afirmação quer conferir."
    return "Claro, procurei referências públicas relacionadas ao que conversamos:\n\n" + "\n".join(fontes)


def pesquisar_fontes_ultima_resposta(identificador):
    with bloqueio:
        conversa = obter_conversa(identificador)
        pergunta = conversa.get("ultima_pergunta")
    if not pergunta:
        return "Ainda não tenho uma pergunta anterior para buscar fontes. Qual assunto você quer pesquisar?"
    consulta = f"{pergunta} fontes confiáveis"
    try:
        resultados = pesquisar_web(consulta, quantidade=5)
    except Exception as erro:
        print("Falha ao buscar fontes solicitadas:", repr(erro), flush=True)
        resultados = []
    evidencias = [{
        "ferramenta": "web_busca",
        "consulta": consulta,
        "resultado": {"resultados": resultados},
    }]
    with bloqueio:
        obter_conversa(identificador)["resultados"] = evidencias
    return gerar_fontes(evidencias)


def processar_item_fila(item):
    client, evento, texto, identificador = item
    try:
        resposta = responder_mensagem(texto, identificador)
    except Exception as erro:
        print("Erro no processamento da fila:", repr(erro), flush=True)
        resposta = "Nao consegui responder agora. Sua mensagem continua dentro do tema; tente novamente em alguns instantes."
    registrar_interacao_whatsapp(texto, resposta)
    if resposta is None:
        print("Resposta suprimida para evitar repeticao de aviso ou reacao curta.", flush=True)
        return
    if isinstance(resposta, dict) and resposta.get("tipo_midia") == "imagem_com_texto":
        enviar_resposta(client, evento, resposta["texto"])
        enviar_midia(client, evento, resposta)
    elif isinstance(resposta, dict) and resposta.get("tipo_midia") in ("imagem", "imagens", "figurinha"):
        enviar_midia(client, evento, resposta)
    else:
        enviou_texto = enviar_resposta(client, evento, resposta)
        if enviou_texto and deve_enviar_figurinha(identificador, texto, resposta):
            assunto = assunto_para_midia(texto) or texto
            try:
                dados, titulo, atribuicao = buscar_imagem(assunto)
                enviar_midia(client, evento, {
                    "tipo_midia": "figurinha",
                    "dados": dados,
                    "titulo": titulo,
                    "atribuicao": atribuicao,
                }, avisar_erro=False)
            except Exception as erro:
                print("Figurinha automatica indisponivel:", repr(erro), flush=True)
                registrar_envio_midia(
                    {"tipo_midia": "figurinha", "titulo": assunto},
                    "falhou",
                    repr(erro),
                )


def registrar_interacao_whatsapp(entrada, saida):
    """Guarda texto de entrada/saida sem telefone, nome ou ID do contato."""
    if isinstance(saida, str) or saida is None:
        saida_registrada = saida
    elif isinstance(saida, dict):
        saida_registrada = f"[{saida.get('tipo_midia', 'midia')}]"
    else:
        saida_registrada = f"[{type(saida).__name__}]"
    registro = {
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "entrada": str(entrada or ""),
        "saida": saida_registrada,
    }
    try:
        caminho = os.path.join(os.path.dirname(__file__), "logs", "interacoes_whatsapp.jsonl")
        with open(caminho, "a", encoding="utf-8") as arquivo:
            arquivo.write(json.dumps(registro, ensure_ascii=False) + "\n")
    except Exception as erro:
        print("Falha ao salvar entrada/saida WhatsApp:", repr(erro), flush=True)


def registrar_envio_midia(midia, estado, erro=None):
    """Registra resultado de envio sem nome, telefone ou ID do contato."""
    registro = {
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "evento": "envio_midia",
        "tipo": str(midia.get("tipo_midia") or "midia"),
        "titulo": str(midia.get("titulo") or "")[:180],
        "estado": estado,
    }
    if erro:
        registro["erro"] = str(erro)[:500]
    try:
        caminho = os.path.join(os.path.dirname(__file__), "logs", "interacoes_whatsapp.jsonl")
        with open(caminho, "a", encoding="utf-8") as arquivo:
            arquivo.write(json.dumps(registro, ensure_ascii=False) + "\n")
    except Exception as erro_log:
        print("Falha ao registrar envio de midia:", repr(erro_log), flush=True)


def extrair_solicitacao_midia(texto):
    """Detecta comandos explicitos e pedidos naturais de foto/figurinha."""
    limpo = texto.strip()
    pedido = re.match(
        r"^(?:(?:oi|ola)[,! ]*)?(?:(?:por favor)\s+)?(?:(?:me\s+)?(?:manda(?:r)?|envia(?:r)?|mostra(?:r)?|exibe(?:r)?)|"
        r"quero(?:\s+ver)?|queria(?:\s+ver)?|pode(?:ria)?(?:\s+me)?\s+(?:mandar|enviar|mostrar|exibir)|"
        r"tem\s+como\s+(?:me\s+)?(?:mandar|enviar|mostrar|exibir)|consegue\s+(?:me\s+)?(?:mandar|enviar|mostrar|exibir))"
        r"\b.*?\b(fotos?|fotografias?|image(?:m|ns)|figurinhas?|stickers?)\b(.*)$",
        limpo,
        flags=re.IGNORECASE,
    )
    if not pedido:
        return None
    substantivo = pedido.group(1).casefold()
    tipo = "figurinha" if substantivo.startswith(("figurinha", "sticker")) else ("imagens" if substantivo.endswith("s") else "imagem")
    assunto = re.sub(r"^(?:(?:de|do|da|dos|das|sobre|com|a|o|as|os)\s+)+", "", pedido.group(2).strip(), flags=re.IGNORECASE).strip(" .,!?")
    return tipo, assunto


def enviar_midia(client, evento, midia, avisar_erro=True):
    if not conectado_evento.is_set():
        conectado_evento.wait(timeout=30)
    if not conectado_evento.is_set():
        erro = "WhatsApp desconectado"
        print("Midia nao enviada:", erro, flush=True)
        registrar_envio_midia(midia, "falhou", erro)
        return False
    try:
        chat = evento.Info.MessageSource.Chat
        if midia["tipo_midia"] in ("imagem", "imagem_com_texto"):
            client.send_image(
                chat,
                midia["dados"],
                caption=midia["atribuicao"],
            )
        elif midia["tipo_midia"] == "imagens":
            for dados, titulo, atribuicao in midia["itens"]:
                client.send_image(chat, dados, caption=atribuicao)
                print(f"Imagem enviada: {titulo}", flush=True)
        else:
            client.send_sticker(chat, midia["dados"])
            client.send_message(chat, midia["atribuicao"])
        titulo_log = midia.get("titulo") or f"{len(midia.get('itens', []))} imagens"
        print(f"Midia enviada: {midia['tipo_midia']} - {titulo_log}", flush=True)
        registrar_envio_midia(midia, "enviada")
        return True
    except Exception as erro:
        print("Erro ao enviar midia:", repr(erro), flush=True)
        registrar_envio_midia(midia, "falhou", repr(erro))
        if avisar_erro:
            enviar_resposta(
                client,
                evento,
                "Encontrei a imagem, mas o WhatsApp nao conseguiu envia-la. Tente pedir imagens novamente daqui a pouco.",
            )
        return False


def assunto_para_midia(texto):
    normalizado = normalizar(texto)
    temas_visuais = (
        ("samba de roda", "samba de roda"),
        ("tereza de benguela", "Tereza de Benguela quilombo"),
        ("ganga zumba", "Ganga Zumba Palmares"),
        ("ganga-zumba", "Ganga Zumba Palmares"),
        ("marabaixo", "Marabaixo Amapa"),
        ("capoeira", "capoeira afro brasileira"),
        ("quilombo", "quilombo brasileiro"),
        ("palmares", "Quilombo dos Palmares"),
        ("zumbi", "Zumbi dos Palmares"),
        ("dandara", "Dandara dos Palmares"),
        ("carolina maria de jesus", "Carolina Maria de Jesus Brazil"),
        ("maria firmina", "Maria Firmina dos Reis"),
        ("antonieta de barros", "Antonieta de Barros"),
        ("esperanca garcia", "Esperanca Garcia"),
        ("abdias do nascimento", "Abdias do Nascimento"),
        ("jongo", "jongo afro brasileiro"),
        ("sateré-mawé", "Sateré Mawé povo Amazonas"),
        ("sateré mawé", "Sateré Mawé povo Amazonas"),
        ("tikuna", "povo Tikuna Amazonas Brasil"),
        ("kokama", "povo Kokama Amazonas Brasil"),
        ("yanomami", "povo Yanomami Brasil"),
        ("munduruku", "povo Munduruku Brasil"),
        ("tukano", "povo Tukano Brasil"),
        ("guarani", "povo Guarani Brasil"),
        ("kaingang", "povo Kaingang Brasil"),
        ("pataxó", "povo Pataxó Brasil"),
        ("pataxo", "povo Pataxó Brasil"),
        ("wajãpi", "Arte Kusiwa povo Wajãpi"),
        ("wajapi", "Arte Kusiwa povo Wajãpi"),
        ("kusiwa", "Arte Kusiwa povo Wajãpi"),
        ("ritxoko", "Ritxoko cerâmica Karajá"),
        ("yaokwa", "Yaokwa povo Enawene Nawe"),
        ("cerâmica marajoara", "cerâmica marajoara Museu Brasil"),
        ("ceramica marajoara", "cerâmica marajoara Museu Brasil"),
        ("congado", "Congado Minas Gerais Brasil"),
        ("congada", "Congada Brasil"),
        ("acarajé", "baiana de acarajé Bahia"),
        ("acaraje", "baiana de acarajé Bahia"),
        ("baiana de acarajé", "baiana de acarajé Bahia"),
        ("baiana de acaraje", "baiana de acarajé Bahia"),
        ("maracatu", "Maracatu Pernambuco Brasil"),
        ("mulheres negras", "mulheres negras Brasil cultura"),
    )
    for termo, busca in temas_visuais:
        if normalizar(termo) in normalizado:
            return busca
    return None


def eh_pedido_explicativo(texto):
    normalizado = normalizar(texto)
    return bool(re.search(
        r"\b(me explica|me fale|me fala|explique|explica|o que e|oq e|"
        r"quem foi|quem e|quem sao|qual foi|qual a historia|qual a importancia|"
        r"por que .* (?:importante|lembrad[oa]s?)|fale sobre|fala sobre|"
        r"me fale sobre|conte sobre|como e|como surgiu|qual a funcao)\b",
        normalizado,
    ))


def deve_enviar_figurinha(identificador, texto, resposta, intervalo=None):
    intervalo = INTERVALO_FIGURINHA if intervalo is None else max(2, int(intervalo))
    if not pertence_ao_assunto(texto) or eh_cumprimento(texto) or not assunto_para_midia(texto):
        return False
    if not isinstance(resposta, str) or resposta.startswith(("Sou um assistente apenas", "Nao encontrei evidencia", "Nao consegui responder")):
        return False
    with bloqueio:
        conversa = obter_conversa(identificador)
        total = conversa.get("respostas_desde_figurinha", 0) + 1
        if total >= intervalo:
            conversa["respostas_desde_figurinha"] = 0
            return True
        conversa["respostas_desde_figurinha"] = total
    return False


@cliente.event(MessageEv)
def mensagem(client, evento):
    try:
        origem = evento.Info.MessageSource
        if origem.IsFromMe:
            return
        if origem.Chat.Server not in SERVIDORES_CHAT_INDIVIDUAL:
            return

        agora = time.time()
        timestamp = int(evento.Info.Timestamp)
        idade = agora - timestamp
        corte_conexao = max(INICIO_PROCESSO_TIMESTAMP, inicio_conexao_timestamp)
        if timestamp < corte_conexao - 1:
            print(
                f"Mensagem anterior a esta conexao ignorada "
                f"(horario={timestamp}, corte={corte_conexao:.0f}, id={evento.Info.ID}).",
                flush=True,
            )
            return
        if timestamp <= 0 or idade > IDADE_MAXIMA_MENSAGEM_SEGUNDOS:
            print(
                f"Mensagem antiga ignorada (idade={idade:.0f}s, "
                f"limite={IDADE_MAXIMA_MENSAGEM_SEGUNDOS}s, id={evento.Info.ID}).",
                flush=True,
            )
            return
        chave_mensagem = (str(origem.Chat), str(evento.Info.ID))
        with bloqueio:
            if chave_mensagem in ids_mensagens_recentes:
                print(f"Evento duplicado ignorado (id={evento.Info.ID}).", flush=True)
                return
            ids_mensagens_recentes[chave_mensagem] = agora
            while len(ids_mensagens_recentes) > MAXIMO_IDS_RECENTES:
                ids_mensagens_recentes.popitem(last=False)

        texto = (extract_text(evento.Message) or "").strip()
        if not texto:
            return

        identificador = f"{origem.Chat.User}@{origem.Chat.Server}"
        agendar_item_apos_rajada(client, evento, texto, identificador)

    except Exception as erro:
        print("Erro ao receber mensagem do WhatsApp:", repr(erro), flush=True)


def agendar_item_apos_rajada(client, evento, texto, identificador):
    """Espera a rajada terminar e processa uma mensagem por conversa."""
    with bloqueio:
        estado = mensagens_em_rajada.get(identificador)
        if estado is None:
            estado = {"itens": [], "timer": None}
            mensagens_em_rajada[identificador] = estado
        estado["itens"].append((client, evento, texto, identificador))
        if estado["timer"] is not None:
            estado["timer"].cancel()
        timer = threading.Timer(
            JANELA_AGRUPAMENTO_MENSAGENS,
            despachar_rajada,
            args=(identificador,),
        )
        timer.daemon = True
        estado["timer"] = timer
        timer.start()


def despachar_rajada(identificador):
    with bloqueio:
        estado = mensagens_em_rajada.pop(identificador, None)
    if not estado or not estado["itens"]:
        return
    itens = estado["itens"]
    cumprimentos = []
    partes = []
    vistas = set()
    ultimo_item_util = None
    for item in itens:
        _, _, texto, _ = item
        texto = str(texto or "").strip()
        if not texto or eh_reacao_curta(texto):
            continue
        if eh_cumprimento(texto):
            cumprimentos.append(texto)
            continue
        # Um ponto de interrogacao enviado sozinho complementa a pergunta
        # anterior; nao deve virar uma segunda pergunta nem ser descartado.
        if re.fullmatch(r"[?!.,;:]+", texto):
            if partes:
                partes[-1] = partes[-1].rstrip() + texto[0]
            continue
        chave = normalizar(texto).strip(" ?!.,;:\n")
        if not chave or chave in vistas:
            continue
        vistas.add(chave)
        partes.append(texto)
        ultimo_item_util = item

    if partes:
        texto_consolidado = "\n".join(partes)[:3000]
    elif cumprimentos:
        texto_consolidado = cumprimentos[-1]
    else:
        print("Rajada composta apenas por reacoes/pontuacao; sem resposta.", flush=True)
        return

    # Responde citando a ultima mensagem, mas envia todas as partes da rajada
    # para o classificador, a busca local/web e o modelo.
    escolhido = ultimo_item_util or itens[-1]
    if len(itens) > 1:
        print(
            f"Rajada agrupada: {len(itens)} mensagens em uma consulta; processando uma resposta.",
            flush=True,
        )
    client, evento, _, _ = escolhido
    texto = texto_consolidado
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


# ==========================================
# INICIAR APLICACAO
# ==========================================

if __name__ == "__main__":

    print("====================================")
    print("    WHATSAPP - CULTURA AFRO-INDIGENA")
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
