"""Carregamento do catálogo de músicas a partir do arquivo CSV."""

import csv
from pathlib import Path

from src.estruturas.grafo import GrafoMusicas
from src.estruturas.tabela_hash import TabelaHash
from src.modelos import Musica


def carregar_catalogo(
    caminho_csv: Path,
    capacidade_hash: int = 1301,
    k_vizinhos: int = 10,
) -> tuple[TabelaHash[Musica], GrafoMusicas, int]:
    """Lê o CSV, popula a Tabela Hash (ignorando IDs duplicados) e constrói o Grafo."""
    if not caminho_csv.exists():
        raise FileNotFoundError(f"Arquivo de catálogo não encontrado: {caminho_csv}")

    tabela: TabelaHash[Musica] = TabelaHash(capacidade=capacidade_hash)
    duplicados_ignorados = 0

    with caminho_csv.open("r", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo, delimiter=";")
        for linha in leitor:
            try:
                musica = Musica(
                    id=linha["id"].strip(),
                    titulo=linha["titulo"].strip(),
                    artista=linha["artista"].strip(),
                    genero=linha["genero"].strip(),
                    energia=float(linha["energia"]),
                    dancabilidade=float(linha["dancabilidade"]),
                    valencia=float(linha["valencia"]),
                    popularidade=int(linha["popularidade"]),
                )
                tabela.inserir(musica.id, musica)
            except (ValueError, KeyError):
                # Trata ID duplicado na Tabela Hash ou linha malformada sem interromper a carga
                duplicados_ignorados += 1

    grafo = GrafoMusicas()
    grafo.construir_conexoes(tabela.listar_todos(), k=k_vizinhos)
    return tabela, grafo, duplicados_ignorados
