"""Testes unitários para o GrafoMusicas (Grafo Ponderado com Lista de Adjacência)."""

import csv
from pathlib import Path
import pytest

from src.estruturas.grafo import GrafoMusicas, calcular_afinidade
from src.modelos import Musica


def _criar_musica(
    id_musica: str,
    artista: str = "Artista A",
    genero: str = "pop",
    energia: float = 0.8,
    dancabilidade: float = 0.7,
    valencia: float = 0.6,
) -> Musica:
    return Musica(
        id=id_musica,
        titulo=f"Musica {id_musica}",
        artista=artista,
        genero=genero,
        energia=energia,
        dancabilidade=dancabilidade,
        valencia=valencia,
        popularidade=85,
    )


def test_calculo_afinidade_maxima_e_parcial() -> None:
    m1 = _criar_musica("1", artista="Dua Lipa", genero="pop", energia=0.8, dancabilidade=0.7, valencia=0.6)
    m2 = _criar_musica("2", artista="Dua Lipa", genero="pop", energia=0.8, dancabilidade=0.7, valencia=0.6)
    m3 = _criar_musica("3", artista="Slipknot", genero="metal", energia=0.95, dancabilidade=0.3, valencia=0.1)

    peso_identico, detalhes_identico = calcular_afinidade(m1, m2)
    peso_distante, detalhes_distante = calcular_afinidade(m1, m3)

    assert peso_identico == 100.0
    assert detalhes_identico["mesmo_artista"] is True
    assert detalhes_identico["mesmo_genero"] is True
    assert peso_distante < 50.0
    assert detalhes_distante["mesmo_artista"] is False
    assert detalhes_distante["mesmo_genero"] is False


def test_construir_conexoes_limita_top_k_e_ordena() -> None:
    base = _criar_musica("base", artista="Artista Base", genero="pop")
    parecida = _criar_musica("parecida", artista="Artista Base", genero="pop", energia=0.79)
    media = _criar_musica("media", artista="Outro", genero="pop", energia=0.75)
    diferente = _criar_musica("diferente", artista="Outro Metal", genero="metal", energia=0.1, dancabilidade=0.1, valencia=0.1)

    grafo = GrafoMusicas()
    grafo.construir_conexoes([base, parecida, media, diferente], k=2)

    vizinhos = grafo.obter_vizinhos("base")
    assert len(vizinhos) == 2
    assert [v.destino_id for v in vizinhos] == ["parecida", "media"]
    assert vizinhos[0].peso >= vizinhos[1].peso


def test_vertice_isolado_e_vertice_inexistente() -> None:
    grafo = GrafoMusicas()
    grafo.adicionar_vertice("isolada")

    assert grafo.contem_vertice("isolada") is True
    assert grafo.obter_vizinhos("isolada") == []
    assert grafo.obter_vizinhos("nao_existe") == []

    stats = grafo.obter_estatisticas()
    assert stats["vertices_isolados"] == 1


def test_k_invalido_lanca_erro() -> None:
    grafo = GrafoMusicas()
    with pytest.raises(ValueError, match="maior que zero"):
        grafo.construir_conexoes([], k=0)


def test_grafo_com_1000_musicas_reais() -> None:
    csv_path = Path(__file__).resolve().parent.parent / "dados" / "musicas_1000.csv"
    musicas: list[Musica] = []
    with csv_path.open("r", encoding="utf-8") as f:
        for linha in csv.DictReader(f, delimiter=";"):
            musicas.append(
                Musica(
                    id=linha["id"],
                    titulo=linha["titulo"],
                    artista=linha["artista"],
                    genero=linha["genero"],
                    energia=float(linha["energia"]),
                    dancabilidade=float(linha["dancabilidade"]),
                    valencia=float(linha["valencia"]),
                    popularidade=int(linha["popularidade"]),
                )
            )

    grafo = GrafoMusicas()
    grafo.construir_conexoes(musicas, k=10)
    stats = grafo.obter_estatisticas()

    assert stats["total_vertices"] == 1000
    assert stats["total_arestas"] == 10000
    assert stats["grau_medio"] == 10.0
    assert stats["vertices_isolados"] == 0
