
import os
import json
import math
import re
import unicodedata
from pathlib import Path

import requests
from dotenv import load_dotenv
from pypdf import PdfReader


# ==========================================
# CONFIGURACOES
# ==========================================

load_dotenv(".env.extensao")

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434"
).rstrip("/")

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "nomic-embed-text"
)

PASTA_DOCUMENTOS = Path("documents")
PASTA_INDICE = Path("dados_rag")
ARQUIVO_INDICE = PASTA_INDICE / "indice.json"

PALAVRAS_VAZIAS_BUSCA = {
    "o", "a", "os", "as", "um", "uma", "uns", "umas", "de", "do", "da",
    "dos", "das", "em", "no", "na", "nos", "nas", "por", "para", "com",
    "e", "ou", "que", "quem", "qual", "quais", "quando", "onde", "como",
    "porque", "sobre", "foi", "sao", "era", "me", "diga", "explique", "fale",
    "conte", "significa", "significado", "diz", "faz", "fez", "determina",
}


def _tokens_busca(texto):
    sem_acentos = "".join(
        caractere
        for caractere in unicodedata.normalize("NFKD", str(texto or "").casefold())
        if not unicodedata.combining(caractere)
    )
    return {
        token for token in re.findall(r"[a-z0-9]+", sem_acentos)
        if token not in PALAVRAS_VAZIAS_BUSCA
    }


# ==========================================
# GERAR EMBEDDINGS
# ==========================================

def gerar_embeddings(textos):

    resposta = requests.post(
        f"{OLLAMA_URL}/api/embed",
        json={
            "model": EMBEDDING_MODEL,
            "input": textos
        },
        timeout=180
    )

    resposta.raise_for_status()

    vetores = resposta.json()["embeddings"]

    if len(vetores) != len(textos):
        raise RuntimeError(
            "Quantidade de embeddings inesperada."
        )

    return vetores


# ==========================================
# DIVIDIR O TEXTO EM TRECHOS
# ==========================================

def dividir_texto(texto, tamanho=900, sobreposicao=120):

    if tamanho <= 0 or not 0 <= sobreposicao < tamanho:
        raise ValueError("Parametros de divisao invalidos.")

    texto = re.sub(r"\s+", " ", texto).strip()

    trechos = []
    inicio = 0

    while inicio < len(texto):

        fim = min(inicio + tamanho, len(texto))

        # Evitar cortar palavras no meio
        if fim < len(texto):
            ultimo_espaco = texto.rfind(
                " ", inicio + tamanho // 2, fim
            )
            if ultimo_espaco > inicio:
                fim = ultimo_espaco

        trecho = texto[inicio:fim].strip()

        if trecho:
            trechos.append(trecho)

        if fim >= len(texto):
            break

        inicio = fim - sobreposicao

    return trechos


# ==========================================
# INDEXAR DOCUMENTOS PDF
# ==========================================

def indexar_documentos():

    PASTA_DOCUMENTOS.mkdir(exist_ok=True)
    PASTA_INDICE.mkdir(exist_ok=True)

    registros = []

    arquivos = sorted(
        [*PASTA_DOCUMENTOS.glob("*.pdf"), *PASTA_DOCUMENTOS.glob("*.md")]
    )

    if not arquivos:
        raise RuntimeError(
            "Nenhum PDF ou arquivo Markdown encontrado em documents/."
        )

    for arquivo in arquivos:

        print(f"Lendo: {arquivo.name}", flush=True)

        if arquivo.suffix.lower() == ".pdf":
            leitor = PdfReader(str(arquivo))
            paginas = [
                (numero, None, pagina.extract_text() or "")
                for numero, pagina in enumerate(leitor.pages, start=1)
            ]
        else:
            texto_markdown = arquivo.read_text(encoding="utf-8")
            marcadores = list(
                re.finditer(
                    r"(?m)^<!-- (pagina|secao): (.*?) -->\s*$",
                    texto_markdown,
                )
            )
            if not marcadores:
                paginas = [(None, None, texto_markdown)]
            else:
                paginas = []
                for indice, marcador in enumerate(marcadores):
                    fim = (
                        marcadores[indice + 1].start()
                        if indice + 1 < len(marcadores)
                        else len(texto_markdown)
                    )
                    valor = marcador.group(2).strip()
                    pagina = int(valor) if marcador.group(1) == "pagina" else None
                    secao = valor if marcador.group(1) == "secao" else None
                    paginas.append(
                        (pagina, secao, texto_markdown[marcador.end():fim])
                    )

        for numero_pagina, secao, texto in paginas:

            trechos = dividir_texto(texto)

            for trecho in trechos:

                registros.append({
                    "arquivo": arquivo.name,
                    "pagina": numero_pagina,
                    "secao": secao,
                    "texto": trecho
                })

    if not registros:
        raise RuntimeError(
            "Nenhum texto extraido dos documentos. "
            "PDFs digitalizados precisam de OCR antes da indexacao."
        )

    print(
        f"Gerando embeddings de {len(registros)} trechos..."
    )

    # Processar em pequenos lotes
    for inicio in range(0, len(registros), 12):

        lote = registros[inicio:inicio + 12]

        vetores = gerar_embeddings(
            [item["texto"] for item in lote]
        )

        for item, vetor in zip(lote, vetores):
            item["embedding"] = vetor

        print(
            f"Processados: {min(inicio + 12, len(registros))}"
            f"/{len(registros)}",
            flush=True
        )

    indice = {
        "modelo": EMBEDDING_MODEL,
        "registros": registros
    }

    ARQUIVO_INDICE.write_text(
        json.dumps(indice, ensure_ascii=False),
        encoding="utf-8"
    )

    return len(registros)


# ==========================================
# SIMILARIDADE DE COSSENO
# ==========================================

def similaridade(vetor_a, vetor_b):

    if len(vetor_a) != len(vetor_b):
        raise ValueError("Vetores incompatíveis.")

    produto = sum(
        a * b for a, b in zip(vetor_a, vetor_b)
    )

    norma_a = math.sqrt(
        sum(a * a for a in vetor_a)
    )

    norma_b = math.sqrt(
        sum(b * b for b in vetor_b)
    )

    if norma_a == 0 or norma_b == 0:
        return 0.0

    return produto / (norma_a * norma_b)


# ==========================================
# CONSULTAR A BASE RAG
# ==========================================

def buscar_documentos(pergunta, quantidade=3):

    return buscar_documentos_multiplos([pergunta], quantidade=quantidade)[0]


def buscar_documentos_multiplos(perguntas, quantidade=3):
    """Busca varias perguntas em um unico lote de embeddings."""
    perguntas = [str(pergunta or "").strip() for pergunta in perguntas]
    perguntas = [pergunta for pergunta in perguntas if pergunta]
    if not perguntas:
        return []

    if not ARQUIVO_INDICE.exists():
        raise RuntimeError(
            "Base RAG nao encontrada. "
            "Execute indexar_pdfs.py primeiro."
        )

    indice = json.loads(
        ARQUIVO_INDICE.read_text(encoding="utf-8")
    )

    if indice["modelo"] != EMBEDDING_MODEL:
        raise RuntimeError(
            "Modelo de embeddings diferente. "
            "Reindexe os documentos."
        )

    vetores_perguntas = gerar_embeddings(perguntas)
    resultados_por_pergunta = []
    for pergunta, vetor_pergunta in zip(perguntas, vetores_perguntas):
        tokens_pergunta = _tokens_busca(pergunta)
        resultados = []
        for registro in indice["registros"]:
            pontuacao = similaridade(vetor_pergunta, registro["embedding"])
            tokens_trecho = _tokens_busca(registro["texto"])
            cobertura_lexical = (
                len(tokens_pergunta & tokens_trecho) / len(tokens_pergunta)
                if tokens_pergunta
                else 0.0
            )
            resultados.append({
                "arquivo": registro["arquivo"],
                "pagina": registro["pagina"],
                "secao": registro.get("secao"),
                "texto": registro["texto"],
                "similaridade": pontuacao,
                "cobertura_lexical": cobertura_lexical,
                "relevancia": pontuacao + 0.35 * cobertura_lexical,
            })
        resultados.sort(key=lambda item: item["relevancia"], reverse=True)
        resultados_por_pergunta.append(resultados[:quantidade])
    return resultados_por_pergunta



def listar_documentos():

    if not ARQUIVO_INDICE.exists():
        return []

    indice = json.loads(
        ARQUIVO_INDICE.read_text(encoding="utf-8")
    )

    documentos = {}

    for registro in indice.get("registros", []):

        nome = registro["arquivo"]

        if nome not in documentos:
            documentos[nome] = {
                "paginas": set(),
                "secoes": set(),
                "trechos": 0,
            }

        pagina = registro.get("pagina")
        secao = registro.get("secao")
        if pagina is not None:
            documentos[nome]["paginas"].add(pagina)
        if secao:
            documentos[nome]["secoes"].add(secao)
        documentos[nome]["trechos"] += 1

    resultado = []
    for nome, dados in sorted(documentos.items()):
        item = {"arquivo": nome, "trechos_indexados": dados["trechos"]}
        if dados["paginas"]:
            item["paginas_indexadas"] = len(dados["paginas"])
        if dados["secoes"]:
            item["secoes_indexadas"] = sorted(dados["secoes"])
        resultado.append(item)
    return resultado
