"""Testes para o carregador de catálogo CSV e tratamento de IDs duplicados."""

from pathlib import Path
from src.carregador import carregar_catalogo


def test_carregar_catalogo_ignora_id_duplicado(tmp_path: Path) -> None:
    csv_file = tmp_path / "musicas_dup.csv"
    csv_file.write_text(
        "id;titulo;artista;genero;energia;dancabilidade;valencia;popularidade\n"
        "id1;Musica A;Artista 1;pop;0.8;0.7;0.6;90\n"
        "id1;Musica A Duplicada;Artista 1;pop;0.8;0.7;0.6;85\n"
        "id2;Musica B;Artista 2;pop;0.75;0.65;0.55;88\n",
        encoding="utf-8",
    )

    tabela, grafo, duplicados = carregar_catalogo(csv_file, capacidade_hash=17, k_vizinhos=5)
    assert len(tabela) == 2
    assert duplicados == 1
    assert tabela.buscar("id1").titulo == "Musica A"  # type: ignore[union-attr]
    assert grafo.obter_estatisticas()["total_vertices"] == 2
