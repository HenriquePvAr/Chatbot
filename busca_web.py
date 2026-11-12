from urllib.parse import urlparse
from collections import OrderedDict
from copy import deepcopy
import re
import threading
import time
import unicodedata

from ddgs import DDGS
from escopo_assunto import eh_conteudo_improprio


FONTES_PRIORITARIAS = (
    "gov.br",
    "ibge.gov.br",
    "iphan.gov.br",
    "planalto.gov.br",
    "camara.leg.br",
    "senado.leg.br",
    "bn.gov.br",
    "museudoindio.gov.br",
    "edu.br",
    "edu",
    "scielo.br",
    "unesco.org",
)

DOMINIOS_BAIXA_CONFIANCA = (
    "facebook.com", "instagram.com", "tiktok.com", "pinterest.com",
    "reddit.com", "quora.com", "x.com", "twitter.com", "youtube.com",
    "wikipedia.org", "wikidata.org", "osegredo.com.br",
    "revistaanamaria.com.br",
)

PALAVRAS_IGNORADAS = {
    "para", "pela", "pelas", "pelo", "pelos", "sobre", "qual", "quais",
    "quem", "como", "quando", "onde", "porque", "por", "que", "uma",
    "umas", "uns", "dos", "das", "de", "do", "da", "no", "na", "nos",
    "nas", "com", "sem", "entre", "cada", "mais", "menos", "muito",
    "muita", "seu", "sua", "seus", "suas", "isso", "essa", "esse",
    "eram", "foi", "sao", "ser", "tem", "tinha", "inclui", "incluem",
    "significa", "significam", "funcao", "objetivo", "objetivos", "falar",
    "explicar", "explica", "importancia", "diferenca", "entre", "brasil",
    "brasileiro", "brasileira", "brasileiros", "brasileiras",
}

_CACHE_TTL_SEGUNDOS = 300
_CACHE_TTL_VAZIO_SEGUNDOS = 20
_CACHE_MAXIMO = 128
_CACHE_LOCK = threading.Lock()
_CACHE_RESULTADOS = OrderedDict()


def _normalizar_texto(valor):
    texto = unicodedata.normalize("NFKD", str(valor or "").casefold())
    return "".join(char for char in texto if not unicodedata.combining(char))


def _termos_relevantes(consulta):
    consulta = re.split(r"\s+site:", str(consulta or ""), maxsplit=1, flags=re.IGNORECASE)[0]
    normalizada = _normalizar_texto(consulta)
    termos = {
        termo for termo in re.findall(r"[a-z]+|\d{4,}", normalizada)
        if termo not in PALAVRAS_IGNORADAS and len(termo) >= 4
        and not (termo.isdigit() and 1800 <= int(termo) <= 2099)
    }
    # Preserva identificadores de leis escritos com pontuacao (10.639/2003).
    for numero in re.findall(r"\b(\d{1,2})\s*\.?\s*(\d{3})\b", normalizada):
        termos.add("".join(numero))
    return termos


def _pontuacao_relevancia(consulta, titulo, trecho):
    termos = _termos_relevantes(consulta)
    if not termos:
        return 1
    texto_documento = _normalizar_texto(f"{titulo} {trecho}")
    documento = set(re.findall(r"[a-z]+|\d{4,}", texto_documento))
    for numero in re.findall(r"\b(\d{1,2})\s*\.?\s*(\d{3})\b", texto_documento):
        documento.add("".join(numero))
    correspondencias = len(termos & documento)
    minimo = 2 if len(termos) >= 3 else 1
    return correspondencias if correspondencias >= minimo else 0


def pesquisar_web(consulta, quantidade=5):
    consulta = str(consulta or "").strip()
    if not consulta:
        raise ValueError("Informe o tema que deve ser pesquisado na web.")

    quantidade = max(1, min(5, int(quantidade)))
    chave = (
        re.sub(r"\s+", " ", _normalizar_texto(consulta)).strip(),
        quantidade,
    )
    agora = time.monotonic()
    with _CACHE_LOCK:
        item = _CACHE_RESULTADOS.get(chave)
        ttl = (
            _CACHE_TTL_SEGUNDOS
            if item and item[1]
            else _CACHE_TTL_VAZIO_SEGUNDOS
        )
        if item and agora - item[0] < ttl:
            _CACHE_RESULTADOS.move_to_end(chave)
            return deepcopy(item[1])
        if item:
            del _CACHE_RESULTADOS[chave]

    resultados = _pesquisar_web_sem_cache(consulta, quantidade)
    with _CACHE_LOCK:
        _CACHE_RESULTADOS[chave] = (time.monotonic(), deepcopy(resultados))
        _CACHE_RESULTADOS.move_to_end(chave)
        while len(_CACHE_RESULTADOS) > _CACHE_MAXIMO:
            _CACHE_RESULTADOS.popitem(last=False)
    return resultados


def _pesquisar_web_sem_cache(consulta, quantidade):
    parametros = {
        "region": "br-pt",
        # DDGS aceita "on", "moderate" ou "off"; "on" e a opcao mais restritiva.
        "safesearch": "on",
        "max_results": quantidade,
    }
    try:
        resultados = DDGS(timeout=5).text(
            consulta[:300],
            backend="auto",
            **parametros,
        )
    except Exception:
        resultados = []

    # O backend automatico pode nao encontrar resultados em redes que bloqueiam
    # alguns provedores. O fallback Startpage evita retornar vazio cedo.
    # "google" nao e mais um backend valido na biblioteca ddgs instalada; usa-lo
    # so desperdica tempo (cai de volta para "auto" silenciosamente).
    if not resultados:
        try:
            resultados = DDGS(timeout=3).text(
                consulta[:300],
                backend="startpage",
                **parametros,
            )
        except Exception:
            resultados = []

    formatados = []
    for item in resultados or []:
        url = str(item.get("href") or item.get("url") or "").strip()
        if urlparse(url).scheme not in {"http", "https"}:
            continue
        dominio = (urlparse(url).hostname or "").lower()
        if any(dominio == item or dominio.endswith("." + item) for item in DOMINIOS_BAIXA_CONFIANCA):
            continue
        titulo = str(item.get("title") or "Sem titulo")
        trecho = str(item.get("body") or "")
        if eh_conteudo_improprio(titulo + " " + trecho):
            continue
        confiavel_prioritario = any(
            dominio == fonte or dominio.endswith("." + fonte)
            for fonte in FONTES_PRIORITARIAS
        )
        relevancia = _pontuacao_relevancia(consulta, titulo, trecho)
        if relevancia <= 0:
            continue
        formatados.append(
            {
                "titulo": titulo[:120],
                "url": url[:1000],
                "trecho": trecho[:900],
                "dominio_prioritario": confiavel_prioritario,
                "relevancia": relevancia,
            }
        )

    formatados.sort(key=lambda item: (-item["relevancia"], not item["dominio_prioritario"]))

    # Se a busca comum so trouxe paginas sem prioridade editorial, tente uma
    # busca curta em dominios oficiais/academicos antes de usar esses trechos.
    if not formatados or not any(item["dominio_prioritario"] for item in formatados):
        try:
            consulta_prioritaria = (
                consulta[:300]
                if re.search(r"\bsite:", consulta, re.IGNORECASE)
                else f"{consulta[:240]} site:gov.br"
            )
            candidatos = DDGS(timeout=3).text(
                consulta_prioritaria,
                backend="startpage",
                **parametros,
            )
        except Exception:
            candidatos = []

        priorizados = []
        for item in candidatos or []:
            url = str(item.get("href") or item.get("url") or "").strip()
            if urlparse(url).scheme not in {"http", "https"}:
                continue
            dominio = (urlparse(url).hostname or "").lower()
            if any(dominio == item or dominio.endswith("." + item) for item in DOMINIOS_BAIXA_CONFIANCA):
                continue
            titulo = str(item.get("title") or "Sem titulo")
            trecho = str(item.get("body") or "")
            if eh_conteudo_improprio(titulo + " " + trecho):
                continue
            relevancia = _pontuacao_relevancia(consulta, titulo, trecho)
            if relevancia <= 0:
                continue
            confiavel_prioritario = any(
                dominio == fonte or dominio.endswith("." + fonte)
                for fonte in FONTES_PRIORITARIAS
            )
            priorizados.append({
                "titulo": titulo[:120],
                "url": url[:1000],
                "trecho": trecho[:900],
                "dominio_prioritario": confiavel_prioritario,
                "relevancia": relevancia,
            })
        priorizados.sort(key=lambda item: (-item["relevancia"], not item["dominio_prioritario"]))
        if any(item["dominio_prioritario"] for item in priorizados):
            formatados = priorizados

    resultados_unicos = []
    vistos = set()
    for item in formatados:
        chave = item["url"].split("#", 1)[0].rstrip("/").casefold()
        if chave in vistos:
            continue
        vistos.add(chave)
        resultados_unicos.append(item)
        if len(resultados_unicos) >= quantidade:
            break
    return resultados_unicos
