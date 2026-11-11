import re
import unicodedata


TERMOS_DO_TEMA = (
    "esbam",
    "uniesbam",
    "escola superior batista do amazonas",
    "centro universitario esbam",
    "faculdade esbam",
    "afro-brasileir",
    "afro brasileir",
    "afro brasileiro",
    "afrobrasileir",
    "afrodescendent",
    "afro-indigen",
    "afroindigen",
    "african",
    "africa",
    "povos africanos",
    "reinos africanos",
    "yoruba",
    "bantu",
    "jeje",
    "ashanti",
    "reino do kongo",
    "cultura afro",
    "cultura negra",
    "cultura afro-brasileira",
    "movimento negro",
    "movimentos negros",
    "movimento indigena",
    "movimentos indigenas",
    "oralidade",
    "historia oral",
    "patrimonio cultural",
    "patrimonio imaterial",
    "grafismos indigenas",
    "arte indigena",
    "artes indigenas",
    "culinaria afro",
    "culinaria indigena",
    "conhecimentos tradicionais",
    "saberes tradicionais",
    "negro",
    "negra",
    "quilomb",
    "mocambo",
    "ganga zumba",
    "ganga-zumba",
    "1678",
    "escrav",
    "abolicao",
    "lei aurea",
    "colonial",
    "seculo xvii",
    "palmares",
    "zumbi",
    "dandara",
    "tereza de benguela",
    "tereza",
    "carolina maria de jesus",
    "carolina de jesus",
    "maria firmina",
    "antonieta de barros",
    "esperanca garcia",
    "luiza mahin",
    "beatriz nascimento",
    "lelia gonzalez",
    "abdias do nascimento",
    "mae menininha",
    "mae stella",
    "dona ivone lara",
    "elza soares",
    "machado de assis",
    "sua importancia",
    "marcaram a historia",
    "capoeira",
    "berimbau",
    "berimbal",
    "birimbau",
    "birimbal",
    "candomble",
    "umbanda",
    "marabaixo",
    "congada",
    "congado",
    "acaraje",
    "baiana de acaraje",
    "samba",
    "jongo",
    "quilombola",
    "terreiro",
    "matriz africana",
    "religiao afro",
    "orixa",
    "orixas",
    "cultura africana",
    "historia da africa",
    "diaspora africana",
    "trafico transatlantico",
    "racismo estrutural",
    "lei 10639",
    "lei 11645",
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
    "amazon",
    "povos da floresta",
    "aldeia indigena",
    "indio",
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
    "kaingang",
    "terena",
    "pataxo",
    "xavante",
    "enawene nawe",
    "ritxoko",
    "tava guarani",
    "povos isolados",
    "povos de recente contato",
    "lingua indigena",
    "linguas indigenas",
    "educacao indigena",
    "educacao escolar indigena",
    "demarcacao",
    "demarcacao de terras",
    "terra indigena",
    "terras indigenas",
    "direitos indigenas",
    "revolta dos males",
    "revolta dos malês",
    "males",
    "marco temporal",
    "racismo ambiental",
    "justica ambiental",
    "retomada territorial",
    "territorios quilombolas",
    "conflitos fundiarios",
    "capoeira angola",
    "capoeira regional",
    "constituicao de 1988",
    "19 de abril",
    "20 de novembro",
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

PADROES_CONTEUDO_IMPROPRIO = tuple(
    re.compile(padrao)
    for padrao in (
        r"\b(porn\w*|hentai|erotic\w*|erotica|erotico|nudes?|nudez explicita|"
        r"conteudo sexual explicito|sexo explicito|posicoes sexuais|fetiche\w*|"
        r"masturb\w*|putaria)\b",
        r"\b(?:conteudo|material|imagem|video) (?:18|adulto|adulta|adultos|adultas)\b",
        r"\b(como (?:fazer|ter) sexo|descreva (?:uma cena|o ato) sexual|"
        r"conto sexual|conto erotico|fanfic erotica)\b",
        r"\b(?:crian\w*|menor(?:es)?|adolescen\w*|bebes?)\b.{0,50}\b"
        r"(?:sexual|sexo|nude|porn|erotic)\w*\b",
        r"\b(?:sexual|sexo|nude|porn|erotic)\w*\b.{0,50}\b"
        r"(?:crian\w*|menor(?:es)?|adolescen\w*|bebes?)\b",
        r"\b(ofender|humilhar|xingar|insultar|ameacar)\w*.{0,60}\b"
        r"(negro|negra|indigena|quilombola|povo|etnia|raca)\w*\b",
        r"\b(como (?:fabricar|fazer) (?:uma )?(?:bomba|arma)|"
        r"como matar|instrucoes para torturar)\b",
    )
)


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", str(texto or "").casefold())
    return "".join(c for c in texto if not unicodedata.combining(c))


def contem_tentativa_de_injecao(texto):
    normalizado = normalizar(texto)
    return any(padrao.search(normalizado) for padrao in PADROES_INJECAO)


def eh_conteudo_improprio(texto):
    """Bloqueia pedidos explícitos impróprios sem bloquear história educativa."""
    normalizado = re.sub(r"[^a-z0-9]+", " ", normalizar(texto)).strip()
    return any(padrao.search(normalizado) for padrao in PADROES_CONTEUDO_IMPROPRIO)


def eh_cumprimento(texto):
    normalizado = re.sub(r"[^a-z0-9]+", " ", normalizar(texto)).strip()
    return bool(
        re.fullmatch(
            r"(?:oi+e?|ola+|bom dia|boa tarde|boa noite|e ai|eae|tudo bem|tudo bom|como vai|hello|hi|hey)"
            r"(?: (?:tudo bem|tudo bom|como vai))?",
            normalizado,
        )
    )


def eh_reacao_curta(texto):
    normalizado = re.sub(r"[^a-z0-9]+", " ", normalizar(texto)).strip()
    return bool(
        re.fullmatch(
            r"(?:(?:a+i+a+i+|a+i+|k{2,}|h+a+h+a+|r+s+|h+m+|eita|nossa)"
            r"(?:\s+(?:a+i+a+i+|a+i+|k{2,}|h+a+h+a+|r+s+|h+m+|eita|nossa))*)",
            normalizado,
        )
    )


def eh_retomada_curta(texto):
    normalizado = re.sub(r"[^a-z0-9]+", " ", normalizar(texto)).strip()
    palavras = normalizado.split()
    if len(palavras) <= 8:
        if re.match(
            r"^(?:nao entendi|nao compreendi|pode explicar melhor|explica melhor|"
            r"explique melhor|me explica melhor|explica de novo|pode repetir|"
            r"repete|mais detalhes|me da um exemplo|me de um exemplo|"
            r"pode dar um exemplo|um exemplo|por exemplo)\b",
            normalizado,
        ):
            return True
        pergunta_com_referente = bool(
            re.match(r"^(?:e )?(?:o que|oq|quem|quando|onde|como|por que|porque|qual|quais)\b", normalizado)
            and re.search(r"\b(ele|ela|eles|elas|isso|esse|essa|esses|essas|dele|dela|deles|delas)\b", normalizado)
        )
        if pergunta_com_referente:
            return True
    if len(palavras) > 8:
        pedido_texto = (
            len(palavras) <= 35
            and re.search(r"\b(povos?|tema|assunto|cultura|historia)\b", normalizado)
            and re.search(r"\b(falar|fale|explica|explique|texto|formato|trechos?)\b", normalizado)
        )
        continuacao = bool(
            re.match(
                r"^(?:e|mas e) (?:por que|porque|como|qual|quais|quando|onde|"
                r"eles|elas|ele|ela|isso|esse|essa)\b",
                normalizado,
            )
        )
        return bool(pedido_texto or continuacao)
    return bool(
        re.match(
            r"^(?:e (?:o|a|os|as|ele|ela|eles|elas|isso|esse|essa|esses|essas|"
            r"depois|como|qual|quais|quando|onde)\b|"
            r"mas e\b|entao\b|nesse caso\b|"
            r"e sobre (?:isso|esse assunto|essa cultura|esse tema|(?:a|as) linguas?|"
            r"essa historia|esses? direitos|essa origem)\b|"
            r"e quanto a (?:isso|esse assunto|essa cultura|esse tema|data|epoca|"
            r"origem|historia|linguas?|direitos|territorio|funcao|importancia)\b|"
            r"por que\b|porque\b|e por que\b|e porque\b|e pq\b|como assim\b|"
            r"qual deles\b|quais deles\b|ele\b|ela\b|eles\b|elas\b|"
            r"isso\b|essa\b|esse\b|me explica melhor\b|continua\b|continue\b)",
            normalizado,
        )
    )


def eh_pedido_texto_sobre_povos(texto):
    normalizado = re.sub(r"[^a-z0-9]+", " ", normalizar(texto)).strip()
    return bool(
        re.search(r"\bpovos?\b", normalizado)
        and re.search(r"\b(texto|formato|trechos?|publicacoes)\b", normalizado)
        and re.search(r"\b(falar|fale|explica|explique|poderia|pode|trechos?|publicacoes)\b", normalizado)
    )


def eh_pergunta_ampla_sobre_povos(texto):
    """Reconhece perguntas cujo referente ja e o assunto central do bot."""
    normalizado = re.sub(r"[^a-z0-9]+", " ", normalizar(texto)).strip()
    tem_referente = bool(
        re.search(r"\b(povos?|personalidades|figuras|culturas?|historia)\b", normalizado)
    )
    pergunta = bool(
        re.search(
            r"\b(o que|oq|quem|quais?|qual|como|porque|por que|pq|"
            r"fizeram|contribuiram|marcaram?|representam?)\b",
            normalizado,
        )
        or len(normalizado.split()) <= 3
    )
    menciona_historia_ou_contribuicao = bool(
        re.search(
            r"\b(historia|historias|marcaram?|importancia|contribu|papel|"
            r"fizeram|influencia|legado|personalidades|figuras|linguas?|"
            r"culturas?|preserv\w*|tradicoes|costumes|territor\w*|direitos|"
            r"identidades|origens?|vivem|vida|signific\w*|definicao|"
            r"sao|e)\b",
            normalizado,
        )
    )
    return tem_referente and pergunta and (
        menciona_historia_ou_contribuicao or len(normalizado.split()) <= 2
    )


def eh_confusao_povos_afro_originarios(texto):
    """Reconhece o uso de 'povos originarios afro-brasileiros' como categoria unica."""
    normalizado = re.sub(r"[^a-z0-9]+", " ", normalizar(texto)).strip()
    return bool(
        re.search(r"\bpovos? originarios? afro ?brasileir\w*\b", normalizado)
        or re.search(r"\bpovos? afro ?brasileir\w* originarios?\b", normalizado)
    )


def pertence_ao_assunto(texto, historico=None):
    normalizado = normalizar(texto)
    if any(normalizar(termo) in normalizado for termo in TERMOS_DO_TEMA):
        return True
    if eh_pedido_texto_sobre_povos(texto):
        return True
    if eh_pergunta_ampla_sobre_povos(texto):
        return True

    # So usa o contexto anterior para retomadas claras; reacoes como "kkk"
    # nao devem virar buscas sobre o assunto da conversa.
    if not eh_retomada_curta(texto):
        return False

    for mensagem in reversed(historico or []):
        if mensagem.get("role") == "user":
            return any(
                normalizar(termo) in normalizar(mensagem.get("content", ""))
                for termo in TERMOS_DO_TEMA
            )
    return False
