"""Testes de integração para o MotorRecomendacao."""

import pytest

from src.estruturas.grafo import GrafoMusicas
from src.estruturas.lista_encadeada import ListaHistorico
from src.estruturas.tabela_hash import TabelaHash
from src.modelos import Musica
from src.motor_recomendacao import MotorRecomendacao


def _montar_cenario() -> tuple[MotorRecomendacao, list[Musica]]:
    musicas = [
        Musica("1", "Levitating", "Dua Lipa", "pop", 0.82, 0.70, 0.91, 95),
        Musica("2", "Don't Start Now", "Dua Lipa", "pop", 0.79, 0.79, 0.68, 94),
        Musica("3", "Blinding Lights", "The Weeknd", "pop", 0.73, 0.51, 0.33, 96),
        Musica("4", "As It Was", "Harry Styles", "pop", 0.73, 0.52, 0.66, 95),
        Musica("5", "Enter Sandman", "Metallica", "metal", 0.82, 0.58, 0.62, 88),
        Musica("6", "Isolada", "Artista Unico", "mpb", 0.10, 0.10, 0.10, 50),
    ]

    tabela: TabelaHash[Musica] = TabelaHash(capacidade=17)
    for m in musicas:
        tabela.inserir(m.id, m)

    historico = ListaHistorico()
    grafo = GrafoMusicas()
    grafo.construir_conexoes(musicas[:5], k=3)
    grafo.adicionar_vertice("6")  # vértice propositalmente isolado

    motor = MotorRecomendacao(tabela, historico, grafo)
    return motor, musicas


def test_erro_ao_recomendar_com_historico_vazio() -> None:
    motor, _ = _montar_cenario()
    with pytest.raises(ValueError, match="histórico de reprodução está vazio"):
        motor.recomendar_por_historico()


def test_erro_ao_reproduzir_id_inexistente() -> None:
    motor, _ = _montar_cenario()
    with pytest.raises(KeyError, match="não encontrada"):
        motor.reproduzir_musica("id_que_nao_existe")


def test_recomendacao_exclui_musicas_ja_ouvidas_e_explica() -> None:
    motor, _ = _montar_cenario()
    motor.reproduzir_musica("1")  # Levitating
    motor.reproduzir_musica("3")  # Blinding Lights

    recomendacoes = motor.recomendar_por_historico(limite=5)
    ids_recomendados = {r.musica.id for r in recomendacoes}

    assert "1" not in ids_recomendados
    assert "3" not in ids_recomendados
    assert "2" in ids_recomendados  # Don't Start Now (mesma artista e gênero)
    for rec in recomendacoes:
        assert len(rec.justificativas) > 0
        assert len(rec.musicas_base) >= 1
        assert 0.0 <= rec.afinidade_percentual <= 100.0


def test_musica_isolada_retorna_lista_vazia() -> None:
    motor, _ = _montar_cenario()
    assert motor.recomendar_por_musica("6") == []


def test_busca_e_sugestao_aproximada() -> None:
    motor, _ = _montar_cenario()
    encontradas = motor.buscar_por_texto("Levit")
    assert len(encontradas) == 1
    assert encontradas[0].id == "1"

    assert motor.buscar_por_texto("Levitatingg") == []
    sugestoes = motor.sugerir_parecidas("Levitatingg")
    assert any(m.id == "1" for m in sugestoes)
