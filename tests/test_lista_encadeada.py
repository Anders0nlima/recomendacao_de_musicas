"""Testes unitários para a ListaHistorico (Lista Duplamente Encadeada)."""

import pytest

from src.estruturas.lista_encadeada import ListaHistorico
from src.modelos import Musica


def _criar_musica(id_musica: str, titulo: str) -> Musica:
    return Musica(
        id=id_musica,
        titulo=titulo,
        artista="Artista Teste",
        genero="rock",
        energia=0.85,
        dancabilidade=0.60,
        valencia=0.55,
        popularidade=80,
    )


def test_lista_vazia_inicial() -> None:
    historico = ListaHistorico()
    assert historico.esta_vazia() is True
    assert len(historico) == 0
    assert historico.ultimas_musicas(3) == []
    assert historico.listar_historico() == []
    assert historico.contem_musica("m1") is False


def test_registrar_reproducao_e_ordem_cronologica() -> None:
    historico = ListaHistorico()
    m1 = _criar_musica("m1", "Primeira")
    m2 = _criar_musica("m2", "Segunda")
    m3 = _criar_musica("m3", "Terceira")

    no1 = historico.registrar_reproducao(m1)
    no2 = historico.registrar_reproducao(m2)
    no3 = historico.registrar_reproducao(m3)

    assert historico.esta_vazia() is False
    assert len(historico) == 3
    assert (no1.ordem, no2.ordem, no3.ordem) == (1, 2, 3)

    cronologico = historico.listar_historico(mais_recente_primeiro=False)
    assert [n.musica.id for n in cronologico] == ["m1", "m2", "m3"]

    inverso = historico.listar_historico(mais_recente_primeiro=True)
    assert [n.musica.id for n in inverso] == ["m3", "m2", "m1"]


def test_ultimas_musicas_com_e_sem_duplicatas() -> None:
    historico = ListaHistorico()
    m1 = _criar_musica("m1", "Faixa 1")
    m2 = _criar_musica("m2", "Faixa 2")
    m3 = _criar_musica("m3", "Faixa 3")

    historico.registrar_reproducao(m1)
    historico.registrar_reproducao(m2)
    historico.registrar_reproducao(m1)  # repetida mais recente
    historico.registrar_reproducao(m3)

    ultimas_unicas = historico.ultimas_musicas(quantidade=3, unicas=True)
    assert [m.id for m in ultimas_unicas] == ["m3", "m1", "m2"]

    ultimas_brutas = historico.ultimas_musicas(quantidade=3, unicas=False)
    assert [m.id for m in ultimas_brutas] == ["m3", "m1", "m2"]

    ultimas_2 = historico.ultimas_musicas(quantidade=2, unicas=True)
    assert [m.id for m in ultimas_2] == ["m3", "m1"]


def test_contem_musica_e_limpar() -> None:
    historico = ListaHistorico()
    m1 = _criar_musica("m1", "Faixa 1")
    historico.registrar_reproducao(m1)

    assert historico.contem_musica("m1") is True
    assert historico.contem_musica("m99") is False

    historico.limpar()
    assert historico.esta_vazia() is True
    assert len(historico) == 0
    assert historico.contem_musica("m1") is False


def test_ultimas_musicas_quantidade_invalida() -> None:
    historico = ListaHistorico()
    with pytest.raises(ValueError, match="maior que zero"):
        historico.ultimas_musicas(0)
