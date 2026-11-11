"""Respostas curadas para perguntas institucionais frequentes sobre a ESBAM."""

import re

from escopo_assunto import normalizar


SITE = "https://esbam.edu.br/"
CONTATO = "https://esbam.edu.br/contato/"
FACEBOOK = "https://www.facebook.com/faculdadeesbamoficial/"
INSTAGRAM = "https://www.instagram.com/uniesbamoficial/"


def _com_fontes(resposta, fontes):
    linhas = [f"{i}. {titulo}: {url}" for i, (titulo, url) in enumerate(fontes, 1)]
    return resposta.rstrip() + "\n\nFontes:\n" + "\n".join(linhas)


def responder_faq_esbam(texto):
    pergunta = normalizar(texto)
    menciona_esbam = any(t in pergunta for t in (
        "esbam", "uniesbam", "escola superior batista do amazonas",
        "centro universitario esbam", "faculdade esbam",
    ))
    if not menciona_esbam:
        return None

    quer_redes = re.search(r"\b(instagram|facebook|twitter|youtube|redes? sociais?|\bx\b)\b", pergunta)
    quer_contato = re.search(r"\b(email|e mail|ouvidoria|telefone|numero|contato|endereco|onde fica|unidades?|campus)\b", pergunta)

    if quer_redes:
        resposta_redes = (
            "As redes sociais oficiais que consegui confirmar são: "
            f"Instagram: {INSTAGRAM}\nFacebook: {FACEBOOK}\n"
            "O site oficial também exibe os links atuais de YouTube e X/Twitter."
        )

    if quer_contato:
        resposta_contato = (
            "A ESBAM/UNIESBAM informa estes contatos e unidades em Manaus:\n"
            "• Adrianópolis: Rua Leonor Teles, 153, Conjunto Abílio Nery, CEP 69057-510. "
            "Telefones: (92) 3305-1800, 3305-1801, 3305-1815 e 3305-1823.\n"
            "• Centro: Av. Leonardo Malcher, 1086, CEP 69010-170. "
            "Telefones divulgados: (92) 3023-9071, 3023-0851, 3023-0498 e 3023-1145.\n"
            "• Shopping Via Norte: Av. Arquiteto José Henrique Bento Rodrigues, 3541, "
            "Santa Etelvina, piso G2. Telefone: (92) 3042-0007.\n"
            "E-mail da ouvidoria: ouvidoria@esbam.edu.br\n"
            ""
        )
        if quer_redes:
            return _com_fontes(
                resposta_contato + "\n\n" + resposta_redes,
                [("ESBAM — Contatos", CONTATO), ("Site oficial", SITE)],
            )
        return _com_fontes(resposta_contato, [("ESBAM — Contatos", CONTATO)])

    if quer_redes:
        return _com_fontes(resposta_redes, [("Site oficial", SITE)])

    if re.search(r"\b(o que e|que e|significa|sobre|instituicao|faculdade|universidade|centro universitario)\b", pergunta):
        return (
            "A ESBAM é o Centro Universitário ESBAM, também divulgado como UNIESBAM. "
            "O nome histórico da instituição é Escola Superior Batista do Amazonas. "
            "Ela oferece cursos e serviços acadêmicos em Manaus; para conferir cursos, "
            f"processos seletivos e informações atualizadas, consulte {SITE}"
        )

    if re.search(r"\b(curso|vestibular|matricula|mensalidade|bolsa|inscricao|horario)\b", pergunta):
        return (
            "Essas informações podem mudar conforme o curso e o período. Consulte a página oficial "
            f"da ESBAM para ver os dados atualizados: {SITE}"
        )

    return (
        "Posso ajudar com informações institucionais básicas da ESBAM. Para dados atualizados "
        f"sobre cursos e serviços, consulte o site oficial: {SITE}"
    )
