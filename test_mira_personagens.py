import os
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from mira_personagens import (
    buscar_evidencias,
    carregar_base,
    preview_habilitado,
    responder_personagem,
)


class TestMiraPersonagens(unittest.TestCase):
    def test_bases_e_limites_de_release_sao_lidos(self):
        esperanca = carregar_base("esperanca")
        clara = carregar_base("clara")
        self.assertEqual(len(esperanca["perguntas"]), 60)
        self.assertEqual(len(clara["perguntas"]), 25)
        self.assertEqual(len(clara["lacunas"]), 15)
        self.assertFalse(clara["perfil"]["aprovado_para_conversa"])

    def test_previas_ativas_por_padrao_e_podem_ser_desativadas(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertTrue(preview_habilitado("esperanca"))
            self.assertTrue(preview_habilitado("clara"))
        with patch.dict(os.environ, {"MIRA_PREVIEW_ENABLED": "0"}, clear=True):
            self.assertFalse(preview_habilitado("esperanca"))
            self.assertFalse(preview_habilitado("clara"))
        with patch.dict(os.environ, {
            "MIRA_PREVIEW_ENABLED": "1",
            "MIRA_CLARA_PREVIEW_ENABLED": "0",
        }, clear=True):
            self.assertTrue(preview_habilitado("esperanca"))
            self.assertFalse(preview_habilitado("clara"))

    def test_pergunta_livre_recupera_fatos_e_fontes_da_carta(self):
        resultado = buscar_evidencias("esperanca", "por que escreveu aquela carta")
        ids = {item["id"] for item in resultado["perguntas"]}
        self.assertIn("EGQA001", ids)
        self.assertTrue(resultado["fontes"])
        self.assertTrue(all(item["status_verificacao"] == "verificada" for item in resultado["fontes"]))

    def test_mensagem_com_varias_perguntas_nao_vira_uma_resposta_fixa(self):
        resultado = buscar_evidencias("esperanca", "Quando a carta foi escrita? O que ela pediu?")
        self.assertIsNone(resultado["resposta_exata"])
        ids = {item["id"] for item in resultado["perguntas"]}
        self.assertIn("EGQA002", ids)
        self.assertIn("EGQA007", ids)

        resultado_clara = buscar_evidencias(
            "clara", "As homenagens de 2017 e 2023 provam que Clara venceu as batalhas?"
        )
        ids_clara = {item["id"] for item in resultado_clara["perguntas"]}
        self.assertIn("CCQ017", ids_clara)
        self.assertIn("CCQ018", ids_clara)

    def test_lacuna_sobre_sentimentos_de_clara_e_recuperada(self):
        resultado = buscar_evidencias("clara", "ela sentiu medo durante a batalha?")
        ids = {item.get("lacuna_id") or item.get("id") for item in resultado["lacunas"]}
        self.assertIn("CCL011", ids)

    def test_pergunta_sem_evidencia_nao_chama_o_modelo(self):
        chamar = unittest.mock.Mock(side_effect=AssertionError("modelo nao deveria ser chamado"))
        resultado = responder_personagem("clara", "qual a previsao do tempo?", chamar_modelo=chamar)
        self.assertIn("evidencia suficiente", resultado["resposta"])
        chamar.assert_not_called()

    def test_sobreposicao_fraca_de_tema_nao_vira_resposta_inventada(self):
        chamar = unittest.mock.Mock(side_effect=AssertionError("modelo nao deveria ser chamado"))
        resultado = responder_personagem(
            "esperanca_garcia",
            "Que linguas uma crianca afro-brasileira aprende?",
            chamar_modelo=chamar,
        )
        self.assertEqual(resultado["status"], "limitacao_documental")
        self.assertFalse(resultado["fontes"])
        chamar.assert_not_called()

    def test_geracao_livre_anexa_apenas_fontes_cadastradas(self):
        chamar = unittest.mock.Mock(return_value="A base descreve o relato e seus limites.")
        resultado = responder_personagem(
            "clara",
            "o que se sabe sobre a participacao de Clara em Guararapes?",
            chamar_modelo=chamar,
        )
        self.assertIn("Fontes historicas:", resultado["resposta"])
        self.assertTrue(resultado["fontes"])
        permitidas = carregar_base("clara")["referencias_permitidas"]
        self.assertTrue(all(fonte["id"] in permitidas for fonte in resultado["fontes"]))

    def test_14_cenarios_de_clara_recuperam_apoio_indicado_pelo_revisor(self):
        arquivo = Path("documents/mira/clara_camarao/testes/cenarios_comportamento_etapa7.json")
        casos = json.loads(arquivo.read_text(encoding="utf-8"))["casos"]
        self.assertEqual(len(casos), 14)
        for caso in casos:
            with self.subTest(cenario=caso["id"]):
                resultado = buscar_evidencias("clara", caso["entrada_para_futuro_teste"])
                recuperados = {item["id"] for item in resultado["perguntas"]}
                esperados = set(caso["apoios_selecionados_pelo_revisor"])
                self.assertTrue(recuperados & esperados)

    def test_teste_de_esperanca_separa_cumprimento_de_consulta_historica(self):
        arquivo = Path("documents/mira/esperanca_garcia/esperanca_garcia/testes_validacao.json")
        casos = json.loads(arquivo.read_text(encoding="utf-8"))
        for caso in casos:
            with self.subTest(cenario=caso["id"]):
                resultado = buscar_evidencias("esperanca", caso["pergunta"])
                if caso["id"] == "T09":
                    self.assertEqual(caso["pergunta"], "Olá!")
                    continue  # A saudacao e tratada antes da busca historica.
                self.assertGreaterEqual(resultado["score"], 0.14)
        for pergunta in ("Qual era a cor dos seus olhos?", "Você usava WhatsApp?"):
            resultado = buscar_evidencias("esperanca", pergunta)
            self.assertFalse(resultado["fontes"])


if __name__ == "__main__":
    unittest.main()
