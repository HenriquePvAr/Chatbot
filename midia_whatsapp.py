"""Busca imagens reutilizaveis no Wikimedia Commons para enviar no WhatsApp."""

from html import unescape
import re
import unicodedata
from urllib.parse import quote

import requests
from escopo_assunto import eh_conteudo_improprio


API_COMMONS = "https://commons.wikimedia.org/w/api.php"
TIMEOUT = (5, 20)
TAMANHO_MAXIMO = 10 * 1024 * 1024


class ImagemNaoEncontrada(Exception):
    pass


def buscar_imagem(assunto):
    """Retorna bytes, titulo e atribuicao de uma imagem do Commons."""
    opcoes = buscar_opcoes_imagem(assunto, quantidade=5)
    erros = []
    for opcao in opcoes:
        try:
            return baixar_imagem(opcao), opcao["titulo"], opcao["atribuicao"]
        except (ImagemNaoEncontrada, requests.RequestException) as erro:
            erros.append(erro)
    raise ImagemNaoEncontrada("O Wikimedia Commons encontrou arquivos, mas nao entregou nenhum deles agora.") from (erros[-1] if erros else None)


def buscar_imagens(assunto, quantidade=2):
    """Retorna um pequeno conjunto de imagens para pedidos no plural."""
    opcoes = buscar_opcoes_imagem(assunto, quantidade=max(5, quantidade * 2))
    imagens = []
    for opcao in opcoes:
        try:
            imagens.append((baixar_imagem(opcao), opcao["titulo"], opcao["atribuicao"]))
        except (ImagemNaoEncontrada, requests.RequestException):
            continue
        if len(imagens) >= quantidade:
            break
    if not imagens:
        raise ImagemNaoEncontrada("Nao encontrei imagens compativeis para esse assunto.")
    return imagens


def buscar_opcoes_imagem(assunto, quantidade=5):
    """Retorna opcoes de imagens sem baixar os arquivos ainda."""
    assunto = re.sub(r"\s+", " ", str(assunto or "")).strip()
    if not assunto:
        raise ImagemNaoEncontrada("Informe o assunto da imagem.")
    if eh_conteudo_improprio(assunto):
        raise ImagemNaoEncontrada("Esse pedido de imagem não é apropriado para este assistente.")

    assunto_normalizado = _texto_normalizado(assunto)
    if re.search(r"\b(indigen\w*|originari\w*)\b", assunto_normalizado):
        povos_com_imagens_especificas = (
            "tikuna", "kokama", "sateré mawé", "yanomami", "munduruku",
            "tukano", "guarani", "kaingang", "pataxo", "wajapi", "kusiwa",
            "ritxoko", "yaokwa", "ceramica marajoara", "cestaria indigena",
            "arte indigena", "grafismo indigena", "pintura corporal indigena",
            "ceramica indigena",
        )
        if not any(_texto_normalizado(povo) in assunto_normalizado for povo in povos_com_imagens_especificas):
            raise ImagemNaoEncontrada(
                "Esse tema reúne muitos povos e culturas. Para escolher uma imagem "
                "representativa, diga um povo ou manifestação específica, como "
                "Tikuna, Yanomami, arte Kusiwa Wajãpi ou cerâmica Ritxoko Karajá."
            )
    if "afro" in assunto_normalizado:
        manifestacoes_especificas = (
            "capoeira", "quilombo", "zumbi", "ganga zumba", "tereza de benguela",
            "jongo", "marabaixo", "samba de roda", "congado", "congada",
            "acaraje", "maracatu",
        )
        if not any(_texto_normalizado(tema) in assunto_normalizado for tema in manifestacoes_especificas):
            raise ImagemNaoEncontrada(
                "A cultura afro-brasileira é diversa. Diga qual manifestação ou "
                "personalidade quer ver, por exemplo: capoeira, jongo, Marabaixo, "
                "samba de roda, Tereza de Benguela ou Quilombo dos Palmares."
            )

    resposta = requests.get(
        API_COMMONS,
        params={
            "action": "query",
            "generator": "search",
            "gsrsearch": f"filetype:bitmap {assunto}",
            "gsrnamespace": 6,
            "gsrlimit": 12,
            "prop": "imageinfo",
            "iiprop": "url|mime|extmetadata",
            "iiurlwidth": 1000,
            "format": "json",
            "formatversion": 2,
        },
        headers={"User-Agent": "AssistenteCulturaAfroIndigena/1.0 (educational WhatsApp bot)"},
        timeout=TIMEOUT,
    )
    resposta.raise_for_status()
    paginas = resposta.json().get("query", {}).get("pages", [])

    opcoes = []
    assunto_normalizado = _texto_normalizado(assunto)
    povos_especificos = (
        "tikuna", "kokama", "satere mawe", "baniwa", "tukano", "yanomami",
        "munduruku", "guarani", "wajapi", "huni kui", "karaja",
    )
    for pagina in paginas:
        info = (pagina.get("imageinfo") or [{}])[0]
        mime = info.get("thumbmime") or info.get("mime", "")
        if mime not in ("image/jpeg", "image/png", "image/webp"):
            continue
        url = info.get("thumburl") or info.get("url")
        if not url:
            continue

        metadados = info.get("extmetadata", {})
        titulo = pagina.get("title", "Imagem do Wikimedia Commons")
        titulo_limpo = titulo.removeprefix("File:").removeprefix("Ficheiro:")
        descricao = _texto_metadata(metadados.get("ImageDescription", {}).get("value", ""))
        busca_texto = _texto_normalizado(titulo_limpo + " " + descricao)
        if eh_conteudo_improprio(titulo_limpo + " " + descricao):
            continue
        if re.search(r"\b(submarinos?|submarines?|navio|ship|battleship)\b", _texto_normalizado(titulo_limpo)):
            continue
        if re.search(r"\b(razor|knife|sword|weapon|armed)\b", _texto_normalizado(titulo_limpo)):
            continue
        if "map" not in assunto_normalizado and re.search(r"\b(map|maps|atlas|carte)\b", _texto_normalizado(titulo_limpo)):
            continue
        if re.search(r"\b(?:1[78][0-9]{2})\b", _texto_normalizado(titulo_limpo)) and re.search(r"\b(indio|indios|savage|tribe)\b", _texto_normalizado(titulo_limpo)):
            continue
        povo_pedido = next((povo for povo in povos_especificos if povo in assunto_normalizado), None)
        if povo_pedido and povo_pedido not in busca_texto:
            continue
        artista = _texto_metadata(metadados.get("Artist", {}).get("value", ""))
        licenca = _texto_metadata(metadados.get("LicenseShortName", {}).get("value", ""))
        link = "https://commons.wikimedia.org/wiki/" + quote(titulo.replace(" ", "_"), safe="():_")
        atribuicao = f"Imagem: {titulo_limpo}"
        if artista:
            atribuicao += f" — {artista}"
        if licenca:
            atribuicao += f" ({licenca})"
        atribuicao += f"\nFonte: {link}"
        opcoes.append({"url": url, "titulo": titulo_limpo, "atribuicao": atribuicao})
        if len(opcoes) >= max(1, min(5, int(quantidade))):
            break

    if not opcoes:
        raise ImagemNaoEncontrada("Nao encontrei uma imagem adequada no Wikimedia Commons para esse assunto.")
    return opcoes


def baixar_imagem(opcao):
    arquivo = requests.get(
        opcao["url"],
        headers={"User-Agent": "AssistenteCulturaAfroIndigena/1.0"},
        timeout=TIMEOUT,
    )
    arquivo.raise_for_status()
    tipo = arquivo.headers.get("Content-Type", "").split(";", 1)[0].lower()
    if tipo not in ("image/jpeg", "image/png", "image/webp"):
        raise ImagemNaoEncontrada("O arquivo encontrado nao e um formato de imagem compativel.")
    if len(arquivo.content) > TAMANHO_MAXIMO:
        raise ImagemNaoEncontrada("A imagem encontrada e grande demais para enviar pelo WhatsApp.")
    return arquivo.content


def _texto_metadata(valor):
    valor = unescape(re.sub(r"<[^>]*>", " ", str(valor or "")))
    valor = valor.replace("\ufffd", "")
    partes = [re.sub(r"\s+", " ", parte).strip() for parte in valor.split(";")]
    unicas = list(dict.fromkeys(parte for parte in partes if parte))
    return "; ".join(unicas)[:180]


def _texto_normalizado(valor):
    sem_acentos = "".join(
        caractere
        for caractere in unicodedata.normalize("NFKD", str(valor or "").casefold())
        if not unicodedata.combining(caractere)
    )
    return re.sub(r"[^a-z0-9]+", " ", sem_acentos).strip()
