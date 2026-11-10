import re
import unicodedata


TERMOS_DO_TEMA = (
    "afro-brasileir",
    "afro brasileir",
    "afro brasileiro",
    "african",
    "cultura afro",
    "cultura negra",
    "negro",
    "negra",
    "quilomb",
    "escrav",
    "abolicao",
    "palmares",
    "zumbi",
    "dandara",
    "tereza de benguela",
    "capoeira",
    "candomble",
    "umbanda",
    "marabaixo",
    "jongo",
    "samba de roda",
    "consciencia negra",
    "mulheres negras",
    "povos indigen",
    "povo indigen",
    "indigena",
    "indigenas",
    "povos originarios",
    "povo originario",
    "etnia",
    "etnias",
    "lingua indigena",
    "linguas indigenas",
    "territorio indigena",
    "terra indigena",
    "ancestral",
    "ancestralidade",
    "tikuna",
    "kokama",
    "satere",
    "satere-mawe",
    "satere mawe",
    "baniwa",
    "tukano",
    "yanomami",
    "munduruku",
    "guarani",
    "wajapi",
    "yaokwa",
    "kusiwa",
    "huni kui",
    "karaja",
    "rio negro",
    "relacoes etnico-raciais",
    "racismo",
    "preconceito racial",
    "discriminacao racial",
    "lei 10639",
    "lei 11645",
    "lei 10.639",
    "lei 11.645",
    "falas de maria",
    "cultura afro-indigena",
)

PADROES_INJECAO = tuple(
    re.compile(padrao)
    for padrao in (
        r"\bignore\b.{0,50}\b(instrucoes|regras|prompt|sistema)\b",
        r"\bdesconsidere\b.{0,50}\b(instrucoes|regras|prompt|sistema)\b",
        r"\besqueca\b.{0,50}\b(instrucoes|regras|prompt|sistema)\b",
        r"\b(ignore|forget|disregard)\b.{0,60}\b(previous|prior|system|instructions|rules)\b",
        r"\b(revele|mostre|imprima|repita|exiba)\b.{0,50}\b(prompt|instrucoes|mensagem do sistema)\b",
        r"\b(reveal|print|show)\b.{0,50}\b(system prompt|hidden instructions|developer message)\b",
        r"\b(jailbreak|prompt injection|modo sem restricoes|sem filtros)\b",
        r"\b(finja ser|aja como|act as)\b.{0,40}\b(sistema|desenvolvedor|admin|sem restricoes)\b",
    )
)


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", str(texto or "").casefold())
    return "".join(c for c in texto if not unicodedata.combining(c))


def contem_tentativa_de_injecao(texto):
    normalizado = normalizar(texto)
    return any(padrao.search(normalizado) for padrao in PADROES_INJECAO)


def pertence_ao_assunto(texto, historico=None):
    normalizado = normalizar(texto)
    if any(normalizar(termo) in normalizado for termo in TERMOS_DO_TEMA):
        return True

    # Permite retomadas curtas apenas quando a conversa ja esta no tema.
    for mensagem in reversed(historico or []):
        if mensagem.get("role") == "user":
            return any(
                normalizar(termo) in normalizar(mensagem.get("content", ""))
                for termo in TERMOS_DO_TEMA
            )
    return False
