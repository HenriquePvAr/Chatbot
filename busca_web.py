from urllib.parse import urlparse

from ddgs import DDGS


FONTES_PRIORITARIAS = (
    "gov.br",
    "ibge.gov.br",
    "iphan.gov.br",
    "edu.br",
    "unesco.org",
)


def pesquisar_web(consulta, quantidade=5):
    consulta = str(consulta or "").strip()
    if not consulta:
        raise ValueError("Informe o tema que deve ser pesquisado na web.")

    quantidade = max(1, min(5, int(quantidade)))
    resultados = DDGS(timeout=12).text(
        consulta[:300],
        region="br-pt",
        safesearch="moderate",
        max_results=quantidade,
        backend="auto",
    )

    formatados = []
    for item in resultados or []:
        url = str(item.get("href") or item.get("url") or "").strip()
        if urlparse(url).scheme not in {"http", "https"}:
            continue
        dominio = (urlparse(url).hostname or "").lower()
        confiavel_prioritario = any(
            dominio == fonte or dominio.endswith("." + fonte)
            for fonte in FONTES_PRIORITARIAS
        )
        formatados.append(
            {
                "titulo": str(item.get("title") or "Sem titulo")[:240],
                "url": url[:1000],
                "trecho": str(item.get("body") or "")[:900],
                "dominio_prioritario": confiavel_prioritario,
            }
        )

    formatados.sort(key=lambda item: not item["dominio_prioritario"])
    return formatados[:quantidade]
