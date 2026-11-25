"""Testes unitários para a TabelaHash."""

import csv
from pathlib import Path
import pytest

from src.estruturas.tabela_hash import TabelaHash
from src.modelos import Musica


def _criar_musica(id_musica: str, titulo: str = "Faixa Teste") -> Musica:
    return Musica(
        id=id_musica,
        titulo=titulo,
        artista="Artista Teste",
        genero="pop",
        energia=0.8,
        dancabilidade=0.7,
        valencia=0.6,
        popularidade=90,
    )


def test_inserir_e_buscar_sucesso() -> None:
    tabela: TabelaHash[Musica] = TabelaHash(capacidade=17)
    m1 = _criar_musica("id_1", "Musica Um")
    m2 = _criar_musica("id_2", "Musica Dois")

    tabela.inserir(m1.id, m1)
    tabela.inserir(m2.id, m2)

    assert len(tabela) == 2
    assert tabela.buscar("id_1") == m1
    assert tabela.buscar("id_2") == m2


def test_buscar_inexistente_retorna_none() -> None:
    tabela: TabelaHash[Musica] = TabelaHash()
    assert tabela.buscar("nao_existe") is None
    assert tabela.buscar("") is None


def test_inserir_chave_duplicada_lanca_erro() -> None:
    tabela: TabelaHash[Musica] = TabelaHash()
    m1 = _criar_musica("id_dup")
    tabela.inserir(m1.id, m1)

    with pytest.raises(ValueError, match="Chave duplicada"):
        tabela.inserir("id_dup", _criar_musica("id_dup", "Outro Titulo"))


def test_colisoes_encadeamento_separado_e_remocao() -> None:
    # Capacidade pequena (3) força colisões entre 6 chaves
    tabela: TabelaHash[Musica] = TabelaHash(capacidade=3)
    musicas = [_criar_musica(f"track_{i}", f"Titulo {i}") for i in range(6)]
    for m in musicas:
        tabela.inserir(m.id, m)

    stats = tabela.obter_estatisticas()
    assert stats["tamanho"] == 6
    assert stats["colisoes"] >= 3
    assert stats["maior_cadeia"] >= 2

    # Todas devem continuar localizáveis mesmo com colisão
    for m in musicas:
        assert tabela.buscar(m.id) == m

    # Remover elemento do meio/início da cadeia não pode quebrar os demais
    assert tabela.remover("track_0") is True
    assert tabela.remover("track_3") is True
    assert tabela.remover("track_inexistente") is False
    assert tabela.buscar("track_0") is None
    assert tabela.buscar("track_3") is None
    assert tabela.buscar("track_1") == musicas[1]
    assert len(tabela) == 4


def test_carga_real_1000_musicas() -> None:
    csv_path = Path(__file__).resolve().parent.parent / "dados" / "musicas_1000.csv"
    tabela: TabelaHash[Musica] = TabelaHash(capacidade=1301)

    with csv_path.open("r", encoding="utf-8") as f:
        leitor = csv.DictReader(f, delimiter=";")
        for linha in leitor:
            musica = Musica(
                id=linha["id"],
                titulo=linha["titulo"],
                artista=linha["artista"],
                genero=linha["genero"],
                energia=float(linha["energia"]),
                dancabilidade=float(linha["dancabilidade"]),
                valencia=float(linha["valencia"]),
                popularidade=int(linha["popularidade"]),
            )
            tabela.inserir(musica.id, musica)

    stats = tabela.obter_estatisticas()
    assert stats["tamanho"] == 1000
    assert stats["fator_carga"] < 0.8
    assert len(tabela.listar_todos()) == 1000
