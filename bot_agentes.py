
import json
import re
import sys
import threading
import os
import time
from datetime import datetime
from collections import OrderedDict

# Evita que mensagens com emoji derrubem callbacks em terminais Windows cp1252.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(errors="replace")
    except (OSError, ValueError):
        pass

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
    _consultas_contexto,
    _secao_de_referencias,
    _separar_perguntas,
    chamar_ia,
    pesquisar_com_ia,
    resposta_direta_zumbi,
    responder_com_ia,
    registrar_trace,
)
from mira_personagens import (
    preview_habilitado,
    responder_personagem,
    slug_personagem,
)
from busca_web import pesquisar_web
from rag_local import listar_documentos
from escopo_assunto import (
    contem_tentativa_de_injecao,
    eh_conteudo_improprio,
    eh_cumprimento,
    eh_confusao_povos_afro_originarios,
    eh_reacao_curta,
    eh_retomada_curta,
    pertence_ao_assunto,
    normalizar,
    tipo_mensagem_social,
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

# A seleção MIRA deve sobreviver ao reinício do processo (por exemplo, pelo
# recarregador de código); o arquivo fica em logs/, já excluído do Git.
ARQUIVO_ESTADOS_MIRA = os.path.join(os.path.dirname(__file__), "logs", "mira_modos.json")


aliases_mira = {}


def _carregar_estados_mira():
    global aliases_mira
    try:
        with open(ARQUIVO_ESTADOS_MIRA, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        if not isinstance(dados, dict):
            return {}
        aliases = dados.get("aliases")
        if isinstance(aliases, dict):
            aliases_mira = {
                str(alias): str(canonico)
                for alias, canonico in aliases.items()
                if isinstance(alias, str) and isinstance(canonico, str)
            }
        modos = dados.get("modes")
        if isinstance(modos, dict):
            dados = modos
        return {
            str(chave): personagem
            for chave, personagem in dados.items()
            if isinstance(personagem, str)
            and personagem in {"esperanca_garcia", "clara_camarao"}
        }
    except (OSError, json.JSONDecodeError):
        return {}


estados_mira = _carregar_estados_mira()
aliases_conversa_mira = {}


def _persistir_estados_mira():
    temporario = ARQUIVO_ESTADOS_MIRA + ".tmp"
    try:
        os.makedirs(os.path.dirname(ARQUIVO_ESTADOS_MIRA), exist_ok=True)
        with open(temporario, "w", encoding="utf-8") as arquivo:
            json.dump(
                {"modes": estados_mira, "aliases": aliases_mira},
                arquivo,
                ensure_ascii=False,
                indent=2,
            )
        os.replace(temporario, ARQUIVO_ESTADOS_MIRA)
    except OSError as erro:
        print("Nao foi possivel salvar a selecao MIRA localmente:", repr(erro), flush=True)


def _definir_personagem_mira(identificador, personagem):
    with bloqueio:
        conversa = obter_conversa(identificador)
        conversa["mira_personagem"] = personagem
        aliases = set(aliases_conversa_mira.get(identificador, {identificador}))
        aliases.update(
            alias for alias, canonico in aliases_mira.items()
            if canonico == identificador
        )
        for alias in aliases:
            if personagem:
                estados_mira[alias] = personagem
            else:
                estados_mira.pop(alias, None)
        _persistir_estados_mira()


def _jid_conversa(jid):
    usuario = str(getattr(jid, "User", "") or "").strip()
    servidor = str(getattr(jid, "Server", "") or "").strip()
    if usuario and servidor in SERVIDORES_CHAT_INDIVIDUAL:
        return f"{usuario}@{servidor}"
    return ""


def _identificador_conversa_whatsapp(origem):
    chat = origem.Chat
    candidatos = list(dict.fromkeys(
        chave for chave in (
            _jid_conversa(chat),
            _jid_conversa(getattr(origem, "Sender", None)),
            _jid_conversa(getattr(origem, "SenderAlt", None)),
        ) if chave
    ))
    if not candidatos:
        return f"{chat.User}@{chat.Server}"

    with bloqueio:
        canonicos_conhecidos = [aliases_mira.get(chave, chave) for chave in candidatos]
        ativo = next((chave for chave in canonicos_conhecidos if chave in estados_mira), None)
        if ativo is None:
            ativo = next((
                canonico for chave, canonico in zip(candidatos, canonicos_conhecidos)
                if chave in conversas and conversas[chave].get("mira_personagem")
            ), None)
        if ativo is None:
            ativo = next((
                chave for chave in candidatos
                if chave in conversas and conversas[chave].get("mira_personagem")
            ), None)
        # Prefira a identidade de telefone quando o WhatsApp também fornece
        # a identidade LID; se só houver LID, mantenha o identificador do chat.
        canonico = ativo or next((
            chave for chave in candidatos
            if chave.rsplit("@", 1)[-1] in {"s.whatsapp.net", "c.us"}
        ), candidatos[0])
        aliases_conversa_mira.setdefault(canonico, set()).update(candidatos)
        for alias in candidatos:
            aliases_mira[alias] = canonico
        personagem = estados_mira.get(canonico) or next(
            (estados_mira[alias] for alias in canonicos_conhecidos if alias in estados_mira),
            None,
        )
        if personagem:
            estados_mira[canonico] = personagem
            _persistir_estados_mira()
        return canonico

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
    0.3, float(os.getenv("WHATSAPP_MESSAGE_BURST_WINDOW_SECONDS", "3.5"))
)
INTERVALO_AVISO_FORA_TEMA = max(
    30, int(os.getenv("WHATSAPP_OFF_TOPIC_NOTICE_SECONDS", "180"))
)
INTERVALO_FIGURINHA = max(2, int(os.getenv("WHATSAPP_STICKER_INTERVAL", "5")))
INTERVALO_IMAGEM = max(2, int(os.getenv("WHATSAPP_IMAGE_INTERVAL", "5")))

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
            "ultima_pergunta": None,
            "mira_personagem": estados_mira.get(identificador),
            "mira_historicos": {},
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
        "/menu: mostrar este menu\n"
        "/web sua pergunta: pesquisar na internet (ex.: /web preservação das línguas indígenas)\n"
        "/fontes: buscar referências da última resposta\n\n"
        "MIRA: Vozes que atravessam gerações é outro projeto com duas personagens educativas:\n"
        "• /mira esperanca\n"
        "  Selecionar Esperança Garcia\n"
        "• /mira clara\n"
        "  Selecionar Clara Camarão\n"
        "• /mira sair: voltar ao assistente geral\n"
        "Envie somente /mira esperanca ou /mira clara, sem acrescentar o nome.\n"
        "Digite /mira para ver as orientações. A prévia precisa estar habilitada nesta instalação.\n\n"
        "Pode escrever normalmente; não precisa usar comandos."
    )


def gerar_ajuda():
    return (
        gerar_menu()
    )


def gerar_menu_mira():
    return (
        "MIRA: Vozes que atravessam gerações\n\n"
        "MIRA é o nome do projeto; suas duas personagens são Esperança Garcia e Clara Camarão.\n"
        "As personagens são representações educativas virtuais, não as mulheres "
        "históricas nem testemunhas de suas memórias.\n\n"
        "Envie somente um destes comandos, sem nome ou texto depois dele:\n"
        "/mira esperanca\n"
        "  Conversar sobre Esperança Garcia\n"
        "/mira clara\n"
        "  Conversar sobre Clara Camarão\n"
        "/mira sair: voltar ao assistente geral\n\n"
        "As perguntas podem ser livres. As respostas usam a base histórica da personagem "
        "selecionada e reconhecem quando falta evidência. A prévia precisa estar habilitada "
        "nesta instalação."
    )


def _comando_mira(texto, identificador):
    comando = texto.strip()
    if not re.match(r"(?i)^/mira(?:\s|$)", comando):
        return None
    argumento = re.sub(r"(?i)^/mira\s*", "", comando, count=1).strip()
    # Compatibilidade com a forma antiga do menu, que podia ser copiada como
    # comando completo: "/mira esperanca: Esperança Garcia".
    argumento = re.split(r"[\s:]+", argumento, maxsplit=1)[0].strip()
    if not argumento:
        return gerar_menu_mira()
    if normalizar(argumento) in {"sair", "off", "voltar", "desativar"}:
        _definir_personagem_mira(identificador, None)
        return "Pronto. Voltamos ao assistente geral do projeto."
    personagem = slug_personagem(argumento)
    if not personagem:
        # Tolerar descrições copiadas sem separador e o alias com acento.
        primeiro_termo = normalizar(argumento).split(maxsplit=1)[0] if argumento else ""
        personagem = slug_personagem(primeiro_termo)
    if not personagem:
        return "Escolha /mira esperanca, /mira clara ou /mira sair."
    if not preview_habilitado(personagem):
        _definir_personagem_mira(identificador, None)
        if personagem == "clara_camarao":
            return (
                "A base textual de Clara Camarão foi integrada, mas a própria entrega "
                "marca a personagem como não aprovada para conversa pública. A prévia "
                "permanece desativada até a avaliação e liberação do projeto."
            )
        return (
            "A prévia MIRA está desativada nesta instalação. Ela só pode ser ativada "
            "depois da avaliação das respostas da base."
        )
    _definir_personagem_mira(identificador, personagem)
    nome = "Esperança Garcia" if personagem == "esperanca_garcia" else "Clara Camarão"
    return (
        f"Prévia MIRA ativada: {nome}. Sou uma representação virtual educativa, "
        "não a personagem histórica. Pode perguntar livremente sobre sua trajetória; "
        "vou me limitar às evidências e lacunas da base. Digite /mira sair para voltar."
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

def processar_pergunta(pergunta, identificador, forcar_web=False, personagem_mira=None):
    inicio = time.perf_counter()
    # A fila ja serializa cada conversa. O lock protege apenas a memoria curta,
    # sem segurar os outros usuarios enquanto o Ollama ou a web respondem.
    with bloqueio:
        conversa = obter_conversa(identificador)
        if personagem_mira:
            historicos_mira = conversa.setdefault("mira_historicos", {})
            historico = list(historicos_mira.get(personagem_mira, []))
        else:
            historico = list(conversa["historico"])

    if personagem_mira:
        print(f"\n[MIRA] Consultando base de {personagem_mira}...", flush=True)
        resultado_mira = responder_personagem(
            personagem_mira,
            pergunta,
            historico,
            chamar_modelo=chamar_ia,
        )
        pesquisa_mira = {
            "categoria": "mira_local",
            "consultas": 1,
            "evidencias": [{
                "ferramenta": "mira_base",
                "consulta": pergunta,
                "resultado": {
                    "fontes": resultado_mira.get("fontes", []),
                    "status_verificacao": resultado_mira.get("status"),
                    "score_recuperacao": (resultado_mira.get("evidencias") or {}).get("score"),
                },
            }],
        }
        resposta = resultado_mira["resposta"]
        with bloqueio:
            conversa = obter_conversa(identificador)
            historicos_mira = conversa.setdefault("mira_historicos", {})
            historicos_mira[personagem_mira] = (
                historico
                + [
                    {"role": "user", "content": pergunta},
                    {"role": "assistant", "content": resposta},
                ]
            )[-12:]
            conversa["plano"] = pesquisa_mira
            conversa["resultados"] = pesquisa_mira["evidencias"]
            conversa["ultima_pergunta"] = pergunta
        print(f"[MIRA] Resposta preparada em {time.perf_counter() - inicio:.2f}s", flush=True)
        return resposta

    print("\n[FONTES] Consultando documentos e pesquisa...", flush=True)
    pesquisa = pesquisar_com_ia(
        pergunta,
        historico,
        forcar_web=forcar_web,
    )
    # pesquisar_com_ia ja tentou a busca web. Se ela voltou vazia, repetir uma
    # segunda busca quase igual so acrescentava varios segundos de espera.
    tentou_busca_web = any(
        evidencia.get("ferramenta") == "web_busca"
        for evidencia in pesquisa.get("evidencias", [])
    )
    tem_resultados_web = any(
        (evidencia.get("resultado") or {}).get("resultados")
        for evidencia in pesquisa.get("evidencias", [])
        if evidencia.get("ferramenta") == "web_busca"
    )
    resposta_local_verificada = bool(
        pesquisa.get("resposta_direta")
        or pesquisa.get("resposta_template_povos")
        or pesquisa.get("resposta_local_suficiente")
    )
    if not tentou_busca_web and not tem_resultados_web and not resposta_local_verificada:
        consulta_fontes = montar_consulta_fontes(pergunta)
        consultas_adicionais = 1
        try:
            resultados_fontes = pesquisar_web(consulta_fontes, quantidade=5)
        except Exception as erro:
            print("Falha ao buscar fontes complementares:", repr(erro), flush=True)
            resultados_fontes = []
        pesquisa.setdefault("evidencias", []).append({
            "ferramenta": "web_busca",
            "consulta": consulta_fontes,
            "resultado": {"resultados": resultados_fontes},
        })
        if resultados_fontes:
            pesquisa["categoria"] = (
                "mista"
                if pesquisa.get("categoria") == "rag"
                else pesquisa.get("categoria", "web")
            )
        pesquisa["consultas"] = int(pesquisa.get("consultas", 0)) + consultas_adicionais
    fim_pesquisa = time.perf_counter()
    print("\n[FONTES] Consulta concluida.", flush=True)
    print("Fontes:", pesquisa["categoria"], flush=True)
    print("Consultas realizadas:", pesquisa["consultas"], flush=True)
    print(f"[TEMPO] Pesquisa: {fim_pesquisa - inicio:.2f}s", flush=True)

    print("\n[RESPOSTA] Preparando resposta...", flush=True)
    resposta_bruta = responder_com_ia(pergunta, pesquisa, historico)
    fim_resposta = time.perf_counter()
    resposta = anexar_fontes_no_final(
        resposta_bruta,
        pesquisa.get("evidencias", []),
        pergunta=pergunta,
        usar_fontes_web=not pesquisa.get("resposta_local_contextual"),
    )
    if resposta != resposta_bruta:
        registrar_trace(
            pergunta,
            pesquisa,
            resposta,
            resposta_bruta=resposta_bruta,
            tipo="resposta_final_com_fontes",
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
        conversa["plano"] = pesquisa
        conversa["resultados"] = pesquisa["evidencias"]
        conversa["ultima_pergunta"] = pergunta

    print("\n[RESPOSTA] Texto preparado:", resposta, flush=True)
    print(
        f"[TEMPO] Geracao: {fim_resposta - fim_pesquisa:.2f}s; "
        f"total: {fim_resposta - inicio:.2f}s",
        flush=True,
    )
    return resposta


def montar_consulta_fontes(pergunta):
    """Dá preferência à instituição mais ligada ao assunto perguntado."""
    pergunta_normalizada = normalizar(pergunta)
    lei = re.search(r"\blei\s*(\d{1,2})\s*\.?\s*(\d{3})(?:\s*/\s*(\d{4}))?\b", pergunta_normalizada)
    if lei:
        numero = "".join(lei.group(1, 2))
        ano = lei.group(3) or ""
        identificador = f"Lei {numero}/{ano}" if ano else f"Lei {numero}"
        return f"{pergunta} {identificador} texto integral site:planalto.gov.br"
    if re.search(r"\b(lingua|linguas|idioma|idiomas)\b", pergunta_normalizada) and re.search(
        r"\b(indigena|indigenas|originario|originarios)\b", pergunta_normalizada
    ):
        return f"{pergunta} Censo 2022 IBGE linguas indigenas site:ibge.gov.br"
    if (
        re.search(r"\bcapoeira\b", pergunta_normalizada)
        and re.search(r"\b(angola|regional|diferenca|estilos?)\b", pergunta_normalizada)
    ):
        return (
            f"{pergunta} capoeira Angola Regional diferenças IPHAN "
            "site:iphan.gov.br OR site:gov.br"
        )
    if re.search(r"\b(berimbau|berimbal)\b", pergunta_normalizada):
        return (
            f"{pergunta} berimbau capoeira IPHAN "
            "site:iphan.gov.br OR site:unesco.org OR site:edu.br"
        )
    if re.search(r"\bcapoeira\b", pergunta_normalizada):
        return f"{pergunta} capoeira IPHAN site:iphan.gov.br OR site:gov.br"
    if re.search(r"\b(esbam|uniesbam)\b", pergunta_normalizada):
        return f"{pergunta} site:esbam.edu.br"
    return f"{pergunta} fonte oficial site:gov.br"


def anexar_fontes_no_final(resposta, evidencias, pergunta=None, usar_fontes_web=True):
    """Anexa fontes web reais e preserva respostas sustentadas apenas por RAG."""
    if not isinstance(resposta, str) or not resposta.strip():
        return resposta
    # Remove rodapes produzidos livremente pelo modelo e gera a lista a partir
    # dos resultados reais da busca, evitando URLs inventadas.
    resposta = re.sub(
        r"\n\s*(?:Fontes|Refer\w*):[\s\S]*$",
        "",
        resposta,
        flags=re.IGNORECASE,
    ).rstrip()
    if not usar_fontes_web:
        return resposta

    grupos = {}
    vistos_por_grupo = {}
    partes = _separar_perguntas(pergunta) if pergunta else []
    for evidencia in evidencias or []:
        if evidencia.get("ferramenta") != "web_busca":
            continue
        resultado = evidencia.get("resultado") or {}
        consulta = normalizar(evidencia.get("consulta", ""))
        grupo = None
        if len(partes) > 1:
            for parte in partes:
                normalizada = normalizar(parte)
                termos = [
                    termo for termo in re.findall(r"[a-z0-9]+", normalizada)
                    if len(termo) > 3 and termo not in {"sobre", "para", "como", "qual", "quais", "porque"}
                ]
                if normalizada and normalizada in consulta or (
                    termos and sum(termo in consulta for termo in termos) >= min(2, len(termos))
                ):
                    grupo = parte
                    break
        chave_grupo = grupo or ""
        grupos.setdefault(chave_grupo, []).extend(resultado.get("resultados") or [])
    fontes_formatadas = []
    for grupo, itens in grupos.items():
        itens.sort(key=lambda item: not item.get("dominio_prioritario", False))
        fontes_grupo = []
        vistos = vistos_por_grupo.setdefault(grupo, set())
        for item in itens:
            url = str(item.get("url") or "").strip()
            titulo = str(item.get("titulo") or "Fonte consultada").strip()
            if not url or url in vistos:
                continue
            vistos.add(url)
            fontes_grupo.append(f"{len(fontes_grupo) + 1}. {titulo}: {url}")
            if len(fontes_grupo) >= 3:
                break
        if fontes_grupo:
            if len(partes) > 1 and grupo:
                fontes_formatadas.append(f"{grupo}:")
            fontes_formatadas.extend(fontes_grupo)
    if fontes_formatadas:
        return resposta.rstrip() + "\n\nFontes:\n" + "\n".join(fontes_formatadas)
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
    resposta_comando_mira = _comando_mira(texto, identificador)
    if resposta_comando_mira is not None:
        return resposta_comando_mira
    texto_normalizado = normalizar(texto)
    pergunta_fontes = bool(re.search(
        r"\b(fontes?|referencias?|links?|artigos?|leituras?|materiais?|"
        r"onde (?:posso |consigo |da para )?(?:ler|encontrar|buscar|pesquisar)|"
        r"(?:ler|saber|pesquisar) mais|"
        r"(?:me indica|indique|recomenda|recomende) (?:uma? )?(?:leitura|artigo|fonte|material)|"
        r"de onde (?:veio|tirou)|qual a fonte|tem fonte|tem fontes)\b",
        texto_normalizado,
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
    if not resposta_esbam and eh_retomada_curta(texto):
        with bloqueio:
            historico_esbam = list(obter_conversa(identificador)["historico"])
        pergunta_anterior_esbam = next(
            (
                str(mensagem.get("content") or "")
                for mensagem in reversed(historico_esbam)
                if mensagem.get("role") == "user"
            ),
            "",
        )
        if pergunta_anterior_esbam:
            resposta_esbam = responder_faq_esbam(pergunta_anterior_esbam + " " + texto)
    if resposta_esbam:
        if not re.search(r"\n\s*Fontes:", resposta_esbam, re.IGNORECASE):
            resposta_esbam = resposta_esbam.rstrip() + (
                "\n\nFontes:\n1. Site oficial da ESBAM: https://esbam.edu.br/"
            )
        with bloqueio:
            conversa_esbam = obter_conversa(identificador)
            conversa_esbam["historico"] = (
                list(conversa_esbam["historico"])
                + [
                    {"role": "user", "content": texto},
                    {"role": "assistant", "content": resposta_esbam},
                ]
            )[-12:]
        return resposta_esbam

    forcar_web = comando == "/web" or comando.startswith("/web ")
    pergunta = texto[4:].strip() if forcar_web else texto.strip()
    if forcar_web and not pergunta:
        return "Envie a pergunta depois de /web. Exemplo: /web historia do Quilombo dos Palmares"

    with bloqueio:
        personagem_mira = obter_conversa(identificador).get("mira_personagem")
    if personagem_mira:
        if not preview_habilitado(personagem_mira):
            with bloqueio:
                obter_conversa(identificador)["mira_personagem"] = None
            return "A prévia MIRA foi desativada. Você voltou ao assistente geral do projeto."
        if forcar_web:
            return "No modo MIRA uso as fontes cadastradas na base da personagem. Digite /mira sair para usar a pesquisa geral."
        nome = "Esperança Garcia" if personagem_mira == "esperanca_garcia" else "Clara Camarão"
        if eh_cumprimento(pergunta):
            return (
                f"Olá! Sou uma representação virtual educativa de {nome}, personagem do projeto MIRA: "
                "Vozes que atravessam gerações. Também há a prévia de "
                f"{'Clara Camarão' if personagem_mira == 'esperanca_garcia' else 'Esperança Garcia'}. "
                "Pode perguntar livremente sobre a trajetória registrada nas fontes. "
                "Use /mira esperanca ou /mira clara para trocar; /mira sair volta ao assistente geral."
            )
        tipo_social_mira = tipo_mensagem_social(pergunta)
        if tipo_social_mira == "agradecimento":
            return "Por nada! Se quiser, pode perguntar mais sobre os registros e as fontes da base."
        if tipo_social_mira == "confirmacao":
            return "Certo. Pode continuar perguntando sobre a trajetoria de " + nome + "."
        if eh_reacao_curta(pergunta):
            return None
        status_curto = normalizar(pergunta).strip(" .!?\t\n")
        if re.fullmatch(r"(?:deu ruim|deu erro|bugou|travou|falhou|lascou|deu problema)", status_curto):
            return "Parece que uma resposta falhou. Estou aqui; pode reenviar a pergunta que eu tento de novo."
        return processar_pergunta(
            pergunta,
            identificador,
            personagem_mira=personagem_mira,
        )

    # Um nome isolado em uma conversa costuma ser um pedido implícito para
    # apresentar a pessoa. Corrige apenas variantes conhecidas de Marielle e
    # responde com uma síntese local, sem depender do classificador genérico.
    consulta_marielle = normalizar(pergunta).strip(" .!?\t\n")
    if re.fullmatch(
        r"(?:(?:quem foi|quem e|fale sobre|me fale sobre|me fala sobre|conte sobre) )?"
        r"marielle franco(?: marielle francisco da silva)?",
        consulta_marielle,
    ):
        resposta = (
            "Marielle Franco (Marielle Francisco da Silva, 1979–2018) foi uma "
            "socióloga, ativista de direitos humanos e vereadora do Rio de Janeiro, "
            "eleita em 2016. Seu trabalho político deu destaque a direitos das "
            "mulheres negras, de moradores de comunidades e da população LGBT. "
            "Ela foi assassinada em 14 de março de 2018 junto com o motorista "
            "Anderson Gomes. Marielle é lembrada por sua atuação política e pela "
            "luta contra desigualdades e violência política.\n\n"
            "Fontes:\n"
            "1. Câmara dos Deputados, resumo biográfico de Marielle Franco: "
            "https://www2.camara.leg.br/atividade-legislativa/comissoes/"
            "comissoes-permanentes/cmulher/outros-documentos/diploma-mulher-cidada-"
            "carlota-pereira-de-queiros/edicao-2018-diploma-mulher-cidada-carlota-"
            "pereira-de-queiros/resumo-marielle-franco\n"
            "2. Instituto Marielle Franco, Quem é Marielle Franco?: "
            "https://www.institutomariellefranco.org/quem-e-marielle"
        )
        with bloqueio:
            conversa = obter_conversa(identificador)
            conversa["historico"] = (
                list(conversa["historico"])
                + [
                    {"role": "user", "content": pergunta},
                    {"role": "assistant", "content": resposta},
                ]
            )[-12:]
            conversa["ultima_pergunta"] = pergunta
        return anexar_imagem_se_fizer_sentido(pergunta, resposta)

    # A pergunta "qual o maior museu indigena" nao define se "maior" e por
    # area, visitantes ou tamanho do acervo. Responder com o museu federal de
    # referencia e explicitar esse limite evita transformar uma metrica em
    # ranking absoluto. A Funai atualizou o nome oficial em 2025.
    consulta_museu_indigena = normalizar(pergunta).strip(" .!?\t\n")
    if re.search(r"\bmuseu\w*\b", consulta_museu_indigena) and re.search(
        r"\b(indigena|indigenas|povos originarios|indio|indios)\b",
        consulta_museu_indigena,
    ) and re.search(r"\b(maior|grande|acervo|pecas|colecao)\b", consulta_museu_indigena):
        fonte_titulo = "Funai, Museu Nacional dos Povos Indígenas"
        fonte_url = (
            "https://www.gov.br/funai/pt-br/assuntos/noticias/2025/"
            "governo-federal-oficializa-mudanca-de-nome-do-museu-nacional-dos-povos-indigenas"
        )
        resposta = (
            "Se você quer dizer o principal museu federal dedicado aos povos indígenas, "
            "é o Museu Nacional dos Povos Indígenas, da Funai, no Rio de Janeiro. "
            "A instituição informa que seu acervo etnográfico reúne mais de 20 mil objetos "
            "de cerca de 150 povos. Mas “o maior” pode significar área, número de peças "
            "ou visitação; sem definir o critério, não dá para afirmar um ranking absoluto.\n\n"
            f"Fonte: {fonte_titulo}: {fonte_url}"
        )
        evidencia = {
            "ferramenta": "web_busca",
            "consulta": pergunta,
            "resultado": {"resultados": [{
                "titulo": fonte_titulo,
                "url": fonte_url,
                "trecho": "Nome oficial e acervo etnográfico com mais de 20 mil objetos de cerca de 150 povos.",
            }]},
        }
        with bloqueio:
            conversa = obter_conversa(identificador)
            conversa["historico"] = (
                list(conversa["historico"])
                + [
                    {"role": "user", "content": pergunta},
                    {"role": "assistant", "content": resposta},
                ]
            )[-12:]
            conversa["plano"] = {"categoria": "web", "consultas": 1, "evidencias": [evidencia]}
            conversa["resultados"] = [evidencia]
            conversa["ultima_pergunta"] = pergunta
        return anexar_imagem_se_fizer_sentido(pergunta, resposta)

    resposta_zumbi = resposta_direta_zumbi(pergunta)
    if resposta_zumbi:
        resposta = (
            resposta_zumbi
            + "\n\nFontes:\n"
            + "1. UFF, Impress?es Rebeldes, Palmares: "
            + "https://www.historia.uff.br/impressoesrebeldes/revolta/palmares/\n"
            + "2. UFF, Impress?es Rebeldes, Zumbi: "
            + "https://www.historia.uff.br/impressoesrebeldes/pessoa/zumbi/\n"
            + "3. Minist?rio dos Direitos Humanos e da Cidadania, Quilombo dos Palmares: "
            + "https://www.gov.br/mdh/pt-br/navegue-por-temas/memoria-e-verdade-da-escravidao/"
            + "acao/lugares-de-memoria/quilombo-dos-palmares"
        )
        with bloqueio:
            conversa = obter_conversa(identificador)
            conversa["historico"] = (
                list(conversa["historico"])
                + [
                    {"role": "user", "content": pergunta},
                    {"role": "assistant", "content": resposta},
                ]
            )[-12:]
            conversa["ultima_pergunta"] = pergunta
        return anexar_imagem_se_fizer_sentido(pergunta, resposta)

    if eh_cumprimento(pergunta):
        return (
            "Oi! 😊 Posso explicar histórias e culturas afro-brasileiras e indígenas. "
            "Por exemplo: “O que são povos afro-brasileiros?”, “Qual é a função "
            "do berimbau na capoeira?” ou “Quem foi Tereza de Benguela?”. "
            "Também há as personagens educativas do projeto MIRA: Esperança Garcia e Clara Camarão. "
            "Use /mira esperanca ou /mira clara para chamá-las; /mira sair volta para cá. "
            "Digite /menu para ver exemplos e orientações."
        )
    tipo_social = tipo_mensagem_social(pergunta)
    if tipo_social == "agradecimento":
        return "Por nada! Se quiser, posso continuar explicando ou indicar fontes sobre o assunto."
    if tipo_social == "confirmacao":
        if normalizar(pergunta) == "entendi":
            return "Que bom 🙂 Se algum ponto ficou confuso, posso explicar de outro jeito."
        return "Beleza 🙂 Pode mandar a próxima dúvida quando quiser."
    conversa_curta = normalizar(pergunta).strip(" .!?\t\n")
    if re.fullmatch(r"(?:deu ruim|deu erro|bugou|travou|falhou|lascou|deu problema)", conversa_curta):
        return "Parece que uma resposta falhou. Estou aqui; pode reenviar a pergunta que eu tento de novo."
    if re.fullmatch(r"(?:testa perguntas?|testar perguntas?|vamos testar|quero testar)", conversa_curta):
        return (
            "Claro! Pode testar com: Quem foi Marielle Franco? O que Zumbi fez em Palmares? "
            "Como os povos indigenas preservam suas linguas? Tambem pode perguntar com suas "
            "proprias palavras; se uma resposta ficar confusa, peca para eu explicar melhor."
        )
    if re.fullmatch(
        r"(?:bugou|travou|ta ai|esta ai|ainda ta ai|esta funcionando|"
        r"ta funcionando|funciona|teste|testando|oxi|oxe|ixi|opa)",
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
        len(_separar_perguntas(pergunta)) == 1
        and eh_confusao_povos_afro_originarios(pergunta)
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
            "Fontes:\n"
            "1. IBGE, O Brasil Indigena: https://www.ibge.gov.br/brasil-indigena/\n"
            "2. MDA, Povos e comunidades tradicionais: "
            "https://www.gov.br/mda/pt-br/acesso-a-informacao/acoes-e-programas/"
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
        return anexar_imagem_se_fizer_sentido(pergunta, resposta)

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
    return anexar_imagem_se_fizer_sentido(pergunta, resposta)


def anexar_imagem_se_fizer_sentido(pergunta, resposta):
    """Anexa imagem ilustrativa a uma resposta de texto quando a pergunta pede
    explicacao e cita um assunto visual, mesmo quando a resposta veio de um
    atalho (ex.: Zumbi, Marielle, museu indigena) em vez do fluxo de IA."""
    pedido_explicativo = eh_pedido_explicativo(pergunta)
    assunto_visual = assunto_para_midia(pergunta)
    assuntos_resposta = []
    if not assunto_visual and pedido_explicativo and isinstance(resposta, str):
        assuntos_resposta = assuntos_visuais_no_texto(resposta, maximo=2)
        if assuntos_resposta:
            assunto_visual = assuntos_resposta[0]
    if assunto_visual and pedido_explicativo:
        try:
            if len(assuntos_resposta) >= 2 and eh_pedido_de_lista(pergunta):
                itens = []
                for termo_busca in assuntos_resposta[:2]:
                    try:
                        itens.append(buscar_imagem(termo_busca))
                    except Exception:
                        continue
                if len(itens) >= 2:
                    return {
                        "tipo_midia": "imagens_com_texto",
                        "texto": resposta,
                        "itens": itens,
                    }
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
        if evidencia.get("ferramenta") == "mira_base":
            resultado = evidencia.get("resultado") or {}
            for item in resultado.get("fontes") or []:
                titulo = str(item.get("titulo") or "Fonte MIRA").strip()
                url = str(item.get("url") or "").strip()
                localizador = str(item.get("localizador") or "").strip()
                if not url or url in vistas:
                    continue
                vistas.add(url)
                detalhe = f" ({localizador})" if localizador else ""
                fontes.append(f"{len(fontes) + 1}. {titulo}: {url}{detalhe}")
                if len(fontes) >= 5:
                    break
            continue
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
        historico = list(conversa.get("historico") or [])
        evidencias_anteriores = list(conversa.get("resultados") or [])
    if not pergunta:
        return "Ainda nao tenho uma pergunta anterior para buscar fontes. Qual assunto voce quer pesquisar?"

    fontes_anteriores = gerar_fontes(evidencias_anteriores)
    if any(evidencia.get("ferramenta") == "mira_base" for evidencia in evidencias_anteriores):
        if fontes_anteriores:
            return "Fontes registradas na base MIRA para a resposta anterior:\n\n" + fontes_anteriores
        return "A base MIRA não registrou fontes específicas para a resposta anterior."
    ja_tem_fontes_web = any(
        evidencia.get("ferramenta") == "web_busca"
        and (evidencia.get("resultado") or {}).get("resultados")
        for evidencia in evidencias_anteriores
    )
    if ja_tem_fontes_web:
        return fontes_anteriores

    historico_anterior = historico[:-2] if len(historico) >= 2 else []
    pergunta_contextual = "; ".join(_consultas_contexto(pergunta, historico_anterior))
    consulta = montar_consulta_fontes(
        f"{pergunta_contextual} artigos academicos para leitura complementar"
    )
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
    # A mensagem pode envelhecer enquanto aguarda na fila. Revalide antes de
    # processar para evitar responder atrasado a mensagens antigas.
    agora = time.time()
    timestamp = normalizar_timestamp_whatsapp(evento.Info.Timestamp)
    corte_conexao = max(INICIO_PROCESSO_TIMESTAMP, inicio_conexao_timestamp)
    if (
        timestamp <= 0
        # O WhatsApp fornece Timestamp em segundos inteiros. Aceite o mesmo
        # segundo do corte para nao rejeitar mensagem nova por arredondamento.
        or timestamp < int(corte_conexao)
        or timestamp > agora + 30
        or agora - timestamp > IDADE_MAXIMA_MENSAGEM_SEGUNDOS
    ):
        print(
            f"Mensagem descartada antes da resposta (idade={agora - timestamp:.0f}s; "
            "fora da janela da conexao ou antiga).",
            flush=True,
        )
        return
    try:
        resposta = responder_mensagem(texto, identificador)
    except Exception as erro:
        print("Erro no processamento da fila:", repr(erro), flush=True)
        resposta = "Nao consegui responder agora. Sua mensagem continua dentro do tema; tente novamente em alguns instantes."
    registrar_interacao_whatsapp(texto, resposta)
    if resposta is None:
        print("Resposta suprimida para evitar repeticao de aviso ou reacao curta.", flush=True)
        return
    if isinstance(resposta, dict) and resposta.get("tipo_midia") in ("imagem_com_texto", "imagens_com_texto"):
        enviar_resposta(client, evento, resposta["texto"])
        enviar_midia(client, evento, resposta)
    elif isinstance(resposta, dict) and resposta.get("tipo_midia") in ("imagem", "imagens", "figurinha"):
        enviar_midia(client, evento, resposta)
    else:
        enviou_texto = enviar_resposta(client, evento, resposta)
        enviou_figurinha = False
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
                enviou_figurinha = True
            except Exception as erro:
                print("Figurinha automatica indisponivel:", repr(erro), flush=True)
                registrar_envio_midia(
                    {"tipo_midia": "figurinha", "titulo": assunto},
                    "falhou",
                    repr(erro),
                )
        if enviou_texto and not enviou_figurinha:
            enviar_imagem, assunto_imagem = deve_enviar_imagem_periodica(identificador, texto, resposta)
            if enviar_imagem:
                try:
                    dados, titulo, atribuicao = buscar_imagem(assunto_imagem)
                    enviar_midia(client, evento, {
                        "tipo_midia": "imagem",
                        "dados": dados,
                        "titulo": titulo,
                        "atribuicao": atribuicao,
                    }, avisar_erro=False)
                except Exception as erro:
                    print("Imagem periodica indisponivel:", repr(erro), flush=True)
                    registrar_envio_midia(
                        {"tipo_midia": "imagem", "titulo": assunto_imagem},
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
        r"tem\s+como\s+(?:me\s+)?(?:mandar|enviar|mostrar|exibir)|consegue\s+(?:me\s+)?(?:mandar|enviar|mostrar|exibir)|"
        r"(?:voce\s+)?(?:tem|possui)(?:\s+(?:uma|alguma))?)"
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
        elif midia["tipo_midia"] in ("imagens", "imagens_com_texto"):
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


TEMAS_VISUAIS = (
        ("berimbau", "berimbau musical instrument capoeira"),
        ("atabaque", "atabaque cultura afro brasileira Brasil"),
        ("maculele", "maculele capoeira Brasil"),
        ("afoxe", "afoxe Bahia Brasil"),
        ("tambor de crioula", "tambor de crioula Maranhao"),
        ("samba reggae", "samba reggae Bahia Olodum"),
        ("coco de roda", "coco de roda Nordeste Brasil"),
        ("bumba meu boi", "bumba meu boi Maranhao"),
        ("boi bumba", "bumba meu boi Maranhao"),
        ("mestre bimba", "Mestre Bimba capoeira"),
        ("mestre pastinha", "Mestre Pastinha capoeira"),
        ("mae menininha", "Mae Menininha do Gantois"),
        ("ailton krenak", "Ailton Krenak"),
        ("raoni", "Raoni Metuktire povo Kayapo"),
        ("sonia guajajara", "Sonia Guajajara"),
        ("sepe tiaraju", "Sepe Tiaraju"),
        ("cestaria indigena", "cestaria indigena Brasil"),
        ("arte indigena", "arte indigena brasileira grafismo"),
        ("grafismo indigena", "grafismo indigena brasileiro"),
        ("pintura corporal indigena", "pintura corporal indigena Brasil"),
        ("ceramica indigena", "ceramica indigena brasileira"),
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
        ("satere mawe", "Satere Mawe povo Amazonas"),
        ("tikuna", "povo Tikuna Amazonas Brasil"),
        ("kokama", "povo Kokama Amazonas Brasil"),
        ("yanomami", "povo Yanomami Brasil"),
        ("munduruku", "povo Munduruku Brasil"),
        ("tukano", "povo Tukano Brasil"),
        ("guarani", "povo Guarani Brasil"),
        ("kaingang", "povo Kaingang Brasil"),
        ("pataxo", "povo Pataxo Brasil"),
        ("wajapi", "Arte Kusiwa povo Wajapi"),
        ("ritxoko", "Ritxoko ceramica Karaja"),
        ("yaokwa", "Yaokwa povo Enawene Nawe"),
        ("ceramica marajoara", "ceramica marajoara Museu Brasil"),
        ("congado", "Congado Minas Gerais Brasil"),
        ("congada", "Congada Brasil"),
        ("acaraje", "baiana de acaraje Bahia"),
        ("mulheres negras", "mulheres negras Brasil cultura"),
        ("maracatu", "Maracatu Pernambuco Brasil"),
    )


def assunto_para_midia(texto):
    normalizado = normalizar(texto)
    for termo, busca in TEMAS_VISUAIS:
        if normalizar(termo) in normalizado:
            return busca
    return None


def assuntos_visuais_no_texto(texto, maximo=2):
    """Retorna ate `maximo` buscas visuais distintas citadas no texto."""
    normalizado = normalizar(texto)
    encontrados = []
    for termo, busca in TEMAS_VISUAIS:
        if normalizar(termo) in normalizado and busca not in encontrados:
            encontrados.append(busca)
            if len(encontrados) >= maximo:
                break
    return encontrados


def eh_pedido_de_lista(texto):
    normalizado = normalizar(texto)
    return bool(re.search(
        r"\b(me diga algum[ao]s|cite|liste|quais pessoas|quem ajudou|quem lutou|"
        r"quem contribuiu)\b",
        normalizado,
    ))


def eh_pedido_explicativo(texto):
    normalizado = normalizar(texto)
    return bool(re.search(
        r"\b(me explica|me fale|me fala|explique|explica|o que e|oq e|"
        r"quem foi|quem foram|quem e|quem sao|quais sao|quais foram|qual foi|"
        r"qual (?:a )?(?:historia|importancia|funcao|objetivo)|"
        r"por que .* (?:importante|lembrad[oa]s?)|fale sobre|fala sobre|"
        r"me fale sobre|conte sobre|como e|como surgiu|qual a funcao|"
        r"me diga algum[ao]s|cite|liste|quais pessoas|quem ajudou|quem lutou|"
        r"quem contribuiu)\b",
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


def assunto_principal_dinamico(identificador):
    """Descobre o assunto da troca atual pela secao/arquivo do melhor trecho
    do RAG usado na ultima resposta, sem depender de lista fixa de termos."""
    with bloqueio:
        evidencias = list(obter_conversa(identificador).get("resultados") or [])
    trechos = [
        trecho
        for evidencia in evidencias
        if evidencia.get("ferramenta") == "rag_busca"
        for trecho in (evidencia.get("resultado") or {}).get("trechos") or []
        if not _secao_de_referencias(trecho.get("secao"))
    ]
    melhor = max(trechos, key=lambda trecho: float(trecho.get("relevancia", 0)), default=None)
    if not melhor:
        return None
    secao = str(melhor.get("secao") or "").strip(" #-:.")
    if secao:
        return secao
    arquivo = str(melhor.get("arquivo") or "").strip()
    if arquivo:
        return os.path.splitext(arquivo)[0].replace("_", " ")
    return None


def deve_enviar_imagem_periodica(identificador, texto, resposta, intervalo=None):
    """A cada N respostas que fazem sentido, sugere o assunto para uma
    imagem ilustrativa, independente da solicitacao explicita de midia."""
    intervalo = INTERVALO_IMAGEM if intervalo is None else max(2, int(intervalo))
    if not pertence_ao_assunto(texto) or eh_cumprimento(texto):
        return False, None
    if not isinstance(resposta, str) or resposta.startswith(("Sou um assistente apenas", "Nao encontrei evidencia", "Nao consegui responder")):
        return False, None
    with bloqueio:
        conversa = obter_conversa(identificador)
        total = conversa.get("respostas_desde_imagem", 0) + 1
        if total >= intervalo:
            conversa["respostas_desde_imagem"] = 0
            atingiu_intervalo = True
        else:
            conversa["respostas_desde_imagem"] = total
            atingiu_intervalo = False
    if not atingiu_intervalo:
        return False, None
    assunto = assunto_principal_dinamico(identificador)
    return (bool(assunto), assunto)


def registrar_diagnostico_timestamp(timestamp, agora, corte, motivo, servidor=None, de_mim=None):
    """Registra apenas metadados de horario para diagnosticar descartes."""
    try:
        caminho = os.path.join(os.path.dirname(__file__), "logs", "diagnostico_horarios.jsonl")
        registro = {
            "agora_epoch": round(agora, 3),
            "mensagem_epoch": timestamp,
            "idade_segundos": round(agora - timestamp, 3),
            "corte_epoch": round(corte, 3),
            "motivo": motivo,
            "servidor": servidor,
            "de_mim": de_mim,
        }
        with open(caminho, "a", encoding="utf-8") as arquivo:
            arquivo.write(json.dumps(registro, ensure_ascii=True) + "\n")
    except OSError:
        pass


def normalizar_timestamp_whatsapp(valor):
    """Converte timestamp para segundos Unix, aceitando entradas em ms."""
    timestamp = int(valor or 0)
    if timestamp > 10_000_000_000:
        timestamp //= 1000
    return timestamp


@cliente.event(MessageEv)
def mensagem(client, evento):
    try:
        origem = evento.Info.MessageSource
        agora = time.time()
        timestamp = normalizar_timestamp_whatsapp(evento.Info.Timestamp)
        corte_conexao = max(INICIO_PROCESSO_TIMESTAMP, inicio_conexao_timestamp)
        registrar_diagnostico_timestamp(
            timestamp, agora, corte_conexao, "evento_recebido",
            servidor=str(origem.Chat.Server), de_mim=bool(origem.IsFromMe),
        )
        if origem.IsFromMe:
            return
        if origem.Chat.Server not in SERVIDORES_CHAT_INDIVIDUAL:
            registrar_diagnostico_timestamp(
                timestamp, agora, corte_conexao, "servidor_nao_aceito",
                servidor=str(origem.Chat.Server), de_mim=False,
            )
            return

        idade = agora - timestamp
        registrar_diagnostico_timestamp(timestamp, agora, corte_conexao, "recebida")
        # Timestamp do evento tem precisao de segundos; o corte tem decimais.
        if timestamp <= 0 or timestamp < int(corte_conexao):
            registrar_diagnostico_timestamp(timestamp, agora, corte_conexao, "anterior_conexao")
            print(
                f"Mensagem anterior a esta conexao ignorada "
                f"(horario={timestamp}, corte={corte_conexao:.0f}, id={evento.Info.ID}).",
                flush=True,
            )
            return
        if timestamp > agora + 30:
            registrar_diagnostico_timestamp(timestamp, agora, corte_conexao, "futuro")
            print(
                f"Mensagem com horario futuro ignorada (horario={timestamp}, agora={agora:.0f}).",
                flush=True,
            )
            return
        if idade > IDADE_MAXIMA_MENSAGEM_SEGUNDOS:
            registrar_diagnostico_timestamp(timestamp, agora, corte_conexao, "antiga")
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

        identificador = _identificador_conversa_whatsapp(origem)
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
    status_conversa = []
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
        normalizado_curto = normalizar(texto).strip(" .!?\t\n")
        if re.fullmatch(
            r"(?:deu ruim|deu erro|bugou|travou|falhou|lascou|deu problema|"
            r"ixi|eita|oxi|oxe)",
            normalizado_curto,
        ):
            status_conversa.append((texto, item))
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
    elif status_conversa:
        texto_consolidado = status_conversa[-1][0]
        ultimo_item_util = status_conversa[-1][1]
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
