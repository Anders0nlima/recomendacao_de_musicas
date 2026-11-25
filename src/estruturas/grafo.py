"""Implementação própria de Grafo Ponderado com Lista de Adjacência."""

from dataclasses import dataclass, field
import math
from src.modelos import Musica


@dataclass(frozen=True)
class Aresta:
    """Aresta direcionada e ponderada ligando uma música de origem a um destino."""

    destino_id: str
    peso: float
    detalhes: dict[str, float | bool | str] = field(default_factory=dict)


def _extrair_artistas(artista_str: str) -> set[str]:
    """Separa múltiplos artistas (ex.: 'Sam Smith;Kim Petras') em conjunto normalizado."""
    return {parte.strip().lower() for parte in artista_str.split(";") if parte.strip()}


def calcular_afinidade(a: Musica, b: Musica) -> tuple[float, dict[str, float | bool | str]]:
    """Calcula o peso de afinidade (0 a 100) entre duas músicas e retorna detalhes explicativos."""
    diff_energia = abs(a.energia - b.energia)
    diff_dancabilidade = abs(a.dancabilidade - b.dancabilidade)
    diff_valencia = abs(a.valencia - b.valencia)

    distancia = math.sqrt(diff_energia**2 + diff_dancabilidade**2 + diff_valencia**2)
    sim_audio = 1.0 / (1.0 + distancia)

    mesmo_genero = a.genero.strip().lower() == b.genero.strip().lower()
    mesmo_artista = bool(_extrair_artistas(a.artista) & _extrair_artistas(b.artista))

    peso = 60.0 * sim_audio
    if mesmo_genero:
        peso += 25.0
    if mesmo_artista:
        peso += 15.0

    peso = round(min(100.0, peso), 2)
    detalhes: dict[str, float | bool | str] = {
        "sim_audio": round(sim_audio, 4),
        "mesmo_genero": mesmo_genero,
        "mesmo_artista": mesmo_artista,
        "diff_energia": round(diff_energia, 4),
        "diff_dancabilidade": round(diff_dancabilidade, 4),
        "diff_valencia": round(diff_valencia, 4),
    }
    return peso, detalhes


class GrafoMusicas:
    """Grafo ponderado representado por Lista de Adjacência para similaridade musical."""

    def __init__(self) -> None:
        self._adjacencias: dict[str, list[Aresta]] = {}

    def adicionar_vertice(self, id_musica: str) -> None:
        """Adiciona um vértice ao grafo caso ainda não exista."""
        if not id_musica:
            raise ValueError("O ID da música não pode ser vazio.")
        if id_musica not in self._adjacencias:
            self._adjacencias[id_musica] = []

    def adicionar_aresta(
        self,
        id_origem: str,
        id_destino: str,
        peso: float,
        detalhes: dict[str, float | bool | str] | None = None,
    ) -> None:
        """Adiciona uma aresta ponderada de id_origem para id_destino."""
        if id_origem == id_destino:
            return
        self.adicionar_vertice(id_origem)
        self.adicionar_vertice(id_destino)
        aresta = Aresta(destino_id=id_destino, peso=peso, detalhes=detalhes or {})
        self._adjacencias[id_origem].append(aresta)

    def construir_conexoes(self, musicas: list[Musica], k: int = 10) -> None:
        """Conecta cada música às suas K músicas mais semelhantes."""
        if k <= 0:
            raise ValueError("O valor de K deve ser maior que zero.")

        self._adjacencias.clear()
        for musica in musicas:
            self.adicionar_vertice(musica.id)

        n = len(musicas)
        candidatos: list[list[Aresta]] = [[] for _ in range(n)]

        # Calcula cada par (i, j) apenas uma vez aproveitando a simetria da afinidade
        for i in range(n):
            m_i = musicas[i]
            for j in range(i + 1, n):
                m_j = musicas[j]
                peso, detalhes = calcular_afinidade(m_i, m_j)
                candidatos[i].append(Aresta(destino_id=m_j.id, peso=peso, detalhes=detalhes))
                candidatos[j].append(Aresta(destino_id=m_i.id, peso=peso, detalhes=detalhes))

        for i, m_i in enumerate(musicas):
            arestas_ordenadas = sorted(candidatos[i], key=lambda a: a.peso, reverse=True)
            self._adjacencias[m_i.id] = arestas_ordenadas[:k]

    def obter_vizinhos(self, id_musica: str) -> list[Aresta]:
        """Retorna as arestas de saída ordenadas por maior peso (ou [] se isolado/inexistente)."""
        arestas = self._adjacencias.get(id_musica, [])
        return sorted(arestas, key=lambda a: a.peso, reverse=True)

    def contem_vertice(self, id_musica: str) -> bool:
        """Verifica se o vértice existe no grafo."""
        return id_musica in self._adjacencias

    def obter_estatisticas(self) -> dict[str, int | float]:
        """Retorna métricas estruturais do grafo para diagnóstico e apresentação."""
        total_vertices = len(self._adjacencias)
        total_arestas = sum(len(vizinhos) for vizinhos in self._adjacencias.values())
        vertices_isolados = sum(1 for vizinhos in self._adjacencias.values() if len(vizinhos) == 0)
        grau_medio = round(total_arestas / total_vertices, 2) if total_vertices > 0 else 0.0

        return {
            "total_vertices": total_vertices,
            "total_arestas": total_arestas,
            "grau_medio": grau_medio,
            "vertices_isolados": vertices_isolados,
        }
