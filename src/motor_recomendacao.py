"""Motor de recomendação e explicabilidade integrando Tabela Hash, Lista Encadeada e Grafo."""

from dataclasses import dataclass
from difflib import get_close_matches

from src.estruturas.grafo import Aresta, GrafoMusicas
from src.estruturas.lista_encadeada import ListaHistorico
from src.estruturas.tabela_hash import TabelaHash
from src.modelos import Musica


@dataclass(frozen=True)
class Recomendacao:
    """Resultado de recomendação pronto para exibição com pontuação e justificativa."""

    musica: Musica
    afinidade_percentual: float
    justificativas: list[str]
    musicas_base: list[str]


def _gerar_justificativas(
    referencia: Musica,
    recomendada: Musica,
    detalhes: dict[str, float | bool | str],
) -> list[str]:
    """Constrói explicações legíveis com base nos componentes da afinidade."""
    razoes: list[str] = []

    if detalhes.get("mesmo_artista"):
        razoes.append(f"Mesmo artista ({recomendada.artista})")
    if detalhes.get("mesmo_genero"):
        razoes.append(f"Mesmo gênero musical ({recomendada.genero})")

    diff_e = float(detalhes.get("diff_energia", abs(referencia.energia - recomendada.energia)))
    diff_d = float(detalhes.get("diff_dancabilidade", abs(referencia.dancabilidade - recomendada.dancabilidade)))
    diff_v = float(detalhes.get("diff_valencia", abs(referencia.valencia - recomendada.valencia)))

    if diff_e <= 0.08:
        razoes.append("Nível de energia muito próximo")
    elif diff_e <= 0.15:
        razoes.append("Energia semelhante")

    if diff_d <= 0.08:
        razoes.append("Dançabilidade muito próxima")
    elif diff_d <= 0.15:
        razoes.append("Dançabilidade semelhante")

    if diff_v <= 0.08:
        razoes.append("Clima/valência equivalente")

    if not razoes:
        razoes.append("Sonoridade geral compatível nas métricas de áudio")

    return razoes


class MotorRecomendacao:
    """Coordena busca na Tabela Hash, histórico na Lista Encadeada e vizinhos no Grafo."""

    def __init__(
        self,
        tabela_hash: TabelaHash[Musica],
        historico: ListaHistorico,
        grafo: GrafoMusicas,
    ) -> None:
        self.tabela_hash = tabela_hash
        self.historico = historico
        self.grafo = grafo

    def buscar_por_texto(self, termo: str, limite: int = 10) -> list[Musica]:
        """Busca músicas por trecho do título ou artista."""
        consulta = termo.strip().lower()
        if not consulta:
            return []

        correspondencias: list[tuple[int, Musica]] = []
        for musica in self.tabela_hash.listar_todos():
            titulo_low = musica.titulo.lower()
            artista_low = musica.artista.lower()
            if consulta in titulo_low or consulta in artista_low:
                prioridade = 2 if titulo_low.startswith(consulta) else 1
                correspondencias.append((prioridade, musica))

        correspondencias.sort(key=lambda item: (item[0], item[1].popularidade), reverse=True)
        return [item[1] for item in correspondencias[:limite]]

    def sugerir_parecidas(self, termo: str, limite: int = 5) -> list[Musica]:
        """Sugere músicas com títulos aproximados quando a busca exata não retorna nada."""
        consulta = termo.strip().lower()
        if not consulta:
            return []

        todas = self.tabela_hash.listar_todos()
        mapa_titulos: dict[str, Musica] = {}
        for m in todas:
            chave = m.titulo.lower()
            if chave not in mapa_titulos or m.popularidade > mapa_titulos[chave].popularidade:
                mapa_titulos[chave] = m

        parecidos = get_close_matches(consulta, list(mapa_titulos.keys()), n=limite, cutoff=0.4)
        return [mapa_titulos[t] for t in parecidos]

    def reproduzir_musica(self, id_musica: str) -> Musica:
        """Localiza a música na Tabela Hash e registra no histórico de reprodução."""
        musica = self.tabela_hash.buscar(id_musica)
        if musica is None:
            raise KeyError(f"Música com ID '{id_musica}' não encontrada na Tabela Hash.")
        self.historico.registrar_reproducao(musica)
        return musica

    def recomendar_por_musica(
        self,
        id_musica: str,
        limite: int = 5,
        excluir_historico: bool = True,
    ) -> list[Recomendacao]:
        """Gera recomendações a partir dos vizinhos de uma única música no Grafo."""
        referencia = self.tabela_hash.buscar(id_musica)
        if referencia is None:
            raise KeyError(f"Música com ID '{id_musica}' não encontrada na Tabela Hash.")

        vizinhos = self.grafo.obter_vizinhos(id_musica)
        recomendacoes: list[Recomendacao] = []

        for aresta in vizinhos:
            if aresta.destino_id == id_musica:
                continue
            if excluir_historico and self.historico.contem_musica(aresta.destino_id):
                continue

            candidata = self.tabela_hash.buscar(aresta.destino_id)
            if candidata is None:
                continue

            justificativas = _gerar_justificativas(referencia, candidata, aresta.detalhes)
            recomendacoes.append(
                Recomendacao(
                    musica=candidata,
                    afinidade_percentual=aresta.peso,
                    justificativas=justificativas,
                    musicas_base=[referencia.titulo],
                )
            )
            if len(recomendacoes) >= limite:
                break

        return recomendacoes

    def recomendar_por_historico(
        self,
        limite: int = 5,
        janela_historico: int = 5,
    ) -> list[Recomendacao]:
        """Combina os vizinhos das últimas músicas ouvidas, removendo faixas já reproduzidas."""
        if self.historico.esta_vazia():
            raise ValueError(
                "O histórico de reprodução está vazio. Ouça ao menos uma música antes de pedir recomendações."
            )

        ultimas = self.historico.ultimas_musicas(quantidade=janela_historico, unicas=True)

        # Acumula candidatos por ID: guarda melhor pontuação ponderada, aresta principal e músicas-base
        acumulado: dict[str, dict[str, object]] = {}

        for idx, musica_base in enumerate(ultimas):
            fator_recencia = max(0.4, 1.0 - 0.15 * idx)
            vizinhos = self.grafo.obter_vizinhos(musica_base.id)

            for aresta in vizinhos:
                if self.historico.contem_musica(aresta.destino_id):
                    continue

                score_ponderado = aresta.peso * fator_recencia
                if aresta.destino_id not in acumulado:
                    acumulado[aresta.destino_id] = {
                        "melhor_score": score_ponderado,
                        "melhor_peso_bruto": aresta.peso,
                        "melhor_ref": musica_base,
                        "melhor_aresta": aresta,
                        "bases": [musica_base.titulo],
                    }
                else:
                    registro = acumulado[aresta.destino_id]
                    bases = registro["bases"]
                    assert isinstance(bases, list)
                    if musica_base.titulo not in bases:
                        bases.append(musica_base.titulo)
                    # Bônus leve quando a mesma faixa é recomendada por múltiplas músicas do histórico
                    if score_ponderado > float(registro["melhor_score"]):  # type: ignore[arg-type]
                        registro["melhor_score"] = score_ponderado
                        registro["melhor_peso_bruto"] = aresta.peso
                        registro["melhor_ref"] = musica_base
                        registro["melhor_aresta"] = aresta

        ranking: list[Recomendacao] = []
        for id_candidato, dados in acumulado.items():
            candidata = self.tabela_hash.buscar(id_candidato)
            if candidata is None:
                continue

            bases = dados["bases"]
            ref = dados["melhor_ref"]
            aresta_principal = dados["melhor_aresta"]
            assert isinstance(bases, list)
            assert isinstance(ref, Musica)
            assert isinstance(aresta_principal, Aresta)

            bonus_coocorrencia = min(6.0, (len(bases) - 1) * 3.0)
            afinidade_final = round(
                min(100.0, float(dados["melhor_peso_bruto"]) + bonus_coocorrencia),  # type: ignore[arg-type]
                2,
            )
            justificativas = _gerar_justificativas(ref, candidata, aresta_principal.detalhes)
            if len(bases) > 1:
                justificativas.insert(0, f"Compatível com {len(bases)} músicas do seu histórico")

            ranking.append(
                Recomendacao(
                    musica=candidata,
                    afinidade_percentual=afinidade_final,
                    justificativas=justificativas,
                    musicas_base=bases,
                )
            )

        ranking.sort(key=lambda r: r.afinidade_percentual, reverse=True)
        return ranking[:limite]
