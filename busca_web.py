from urllib.parse import urlparse
import re
import unicodedata

from ddgs import DDGS
from escopo_assunto import eh_conteudo_improprio


FONTES_PRIORITARIAS = (
    "gov.br",
    "ibge.gov.br",
    "iphan.gov.br",
    "edu.br",
    "edu",
    "scielo.br",
    "unesco.org",
    "uol.com.br",
    "globo.com",
    "folha.uol.com.br",
    "bbc.com",
    "apublica.org",
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
    return len(termos & documento)


def pesquisar_web(consulta, quantidade=5):
    consulta = str(consulta or "").strip()
    if not consulta:
        raise ValueError("Informe o tema que deve ser pesquisado na web.")

    quantidade = max(1, min(5, int(quantidade)))
    parametros = {
        "region": "br-pt",
        # DDGS aceita "on", "moderate" ou "off"; "on" e a opcao mais restritiva.
        "safesearch": "on",
        "max_results": quantidade,
    }
    try:
        resultados = DDGS(timeout=7).text(
            consulta[:300],
            backend="auto",
            **parametros,
        )
    except Exception:
        resultados = []

    # O backend automatico pode nao encontrar resultados em redes que bloqueiam
    # alguns provedores. O fallback Startpage/Google evita retornar vazio cedo.
    if not resultados:
        try:
            resultados = DDGS(timeout=5).text(
                consulta[:300],
                backend="google",
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
                f"{consulta[:240]} site:gov.br OR site:edu.br OR "
                "site:unesco.org OR site:scielo.br"
            )
            candidatos = DDGS(timeout=4).text(
                consulta_prioritaria,
                backend="google",
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
