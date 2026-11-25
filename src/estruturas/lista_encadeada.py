"""Implementação própria de Lista Duplamente Encadeada para o histórico de reprodução."""

from datetime import datetime
from src.modelos import Musica


class NoHistorico:
    """Nó da Lista Duplamente Encadeada representando uma reprodução."""

    def __init__(
        self,
        musica: Musica,
        ordem: int,
        timestamp: str,
        anterior: "NoHistorico | None" = None,
        proximo: "NoHistorico | None" = None,
    ) -> None:
        self.musica = musica
        self.ordem = ordem
        self.timestamp = timestamp
        self.anterior = anterior
        self.proximo = proximo


class ListaHistorico:
    """Lista Duplamente Encadeada para armazenar e consultar o histórico de reprodução."""

    def __init__(self) -> None:
        self._inicio: NoHistorico | None = None
        self._fim: NoHistorico | None = None
        self._tamanho = 0
        self._contador_ordem = 0

    def esta_vazia(self) -> bool:
        """Retorna True se o histórico não possuir nenhuma reprodução."""
        return self._tamanho == 0

    def registrar_reproducao(self, musica: Musica) -> NoHistorico:
        """Insere uma música ao final do histórico em tempo O(1)."""
        self._contador_ordem += 1
        agora = datetime.now().strftime("%H:%M:%S")
        novo_no = NoHistorico(
            musica=musica,
            ordem=self._contador_ordem,
            timestamp=agora,
            anterior=self._fim,
            proximo=None,
        )

        if self._fim is None:
            self._inicio = novo_no
            self._fim = novo_no
        else:
            self._fim.proximo = novo_no
            self._fim = novo_no

        self._tamanho += 1
        return novo_no

    def ultimas_musicas(self, quantidade: int = 5, unicas: bool = True) -> list[Musica]:
        """Recupera as últimas N músicas ouvidas percorrendo do fim para o início."""
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")

        resultado: list[Musica] = []
        ids_vistos: set[str] = set()
        atual = self._fim

        while atual is not None and len(resultado) < quantidade:
            if not unicas or atual.musica.id not in ids_vistos:
                resultado.append(atual.musica)
                ids_vistos.add(atual.musica.id)
            atual = atual.anterior

        return resultado

    def listar_historico(self, mais_recente_primeiro: bool = False) -> list[NoHistorico]:
        """Retorna todos os nós do histórico na ordem solicitada."""
        nos: list[NoHistorico] = []
        if mais_recente_primeiro:
            atual = self._fim
            while atual is not None:
                nos.append(atual)
                atual = atual.anterior
        else:
            atual = self._inicio
            while atual is not None:
                nos.append(atual)
                atual = atual.proximo
        return nos

    def contem_musica(self, id_musica: str) -> bool:
        """Verifica se uma música (pelo ID) já foi reproduzida no histórico."""
        atual = self._inicio
        while atual is not None:
            if atual.musica.id == id_musica:
                return True
            atual = atual.proximo
        return False

    def limpar(self) -> None:
        """Remove todas as entradas do histórico."""
        self._inicio = None
        self._fim = None
        self._tamanho = 0
        self._contador_ordem = 0

    def __len__(self) -> int:
        return self._tamanho
