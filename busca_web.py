from urllib.parse import urlparse

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
        resultados = DDGS(timeout=12).text(
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
            resultados = DDGS(timeout=12).text(
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
        formatados.append(
            {
                "titulo": titulo[:240],
                "url": url[:1000],
                "trecho": trecho[:900],
                "dominio_prioritario": confiavel_prioritario,
            }
        )

    formatados.sort(key=lambda item: not item["dominio_prioritario"])
    return formatados[:quantidade]
