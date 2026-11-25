"""Implementação própria de Tabela Hash com encadeamento separado."""

from typing import Generic, TypeVar

T = TypeVar("T")


class _NoHash(Generic[T]):
    """Nó de lista encadeada armazenado dentro de cada bucket da Tabela Hash."""

    def __init__(self, chave: str, valor: T, proximo: "_NoHash[T] | None" = None) -> None:
        self.chave = chave
        self.valor = valor
        self.proximo = proximo


class TabelaHash(Generic[T]):
    """Tabela Hash indexada por chave textual com tratamento de colisões por encadeamento separado."""

    def __init__(self, capacidade: int = 1301) -> None:
        if capacidade <= 0:
            raise ValueError("A capacidade da Tabela Hash deve ser maior que zero.")
        self._capacidade = capacidade
        self._buckets: list[_NoHash[T] | None] = [None] * capacidade
        self._tamanho = 0
        self._colisoes = 0

    def _hash(self, chave: str) -> int:
        """Função de espalhamento polinomial sobre os caracteres da chave."""
        if not chave:
            raise ValueError("A chave não pode ser vazia.")
        h = 0
        for caractere in chave:
            h = (h * 31 + ord(caractere)) % self._capacidade
        return h

    def inserir(self, chave: str, valor: T) -> None:
        """Insere um par (chave, valor). Lança ValueError se a chave já existir."""
        indice = self._hash(chave)
        atual = self._buckets[indice]

        if atual is not None:
            # Verifica duplicidade na cadeia do bucket antes de contabilizar colisão
            cursor: _NoHash[T] | None = atual
            while cursor is not None:
                if cursor.chave == chave:
                    raise ValueError(f"Chave duplicada na Tabela Hash: '{chave}'.")
                cursor = cursor.proximo
            self._colisoes += 1

        # Insere no início da cadeia do bucket em O(1)
        novo_no = _NoHash(chave=chave, valor=valor, proximo=atual)
        self._buckets[indice] = novo_no
        self._tamanho += 1

    def buscar(self, chave: str) -> T | None:
        """Retorna o valor associado à chave ou None se não existir."""
        if not chave:
            return None
        indice = self._hash(chave)
        atual = self._buckets[indice]
        while atual is not None:
            if atual.chave == chave:
                return atual.valor
            atual = atual.proximo
        return None

    def remover(self, chave: str) -> bool:
        """Remove a entrada pela chave. Retorna True se removida, False caso contrário."""
        if not chave:
            return False
        indice = self._hash(chave)
        atual = self._buckets[indice]
        anterior: _NoHash[T] | None = None

        while atual is not None:
            if atual.chave == chave:
                if anterior is None:
                    self._buckets[indice] = atual.proximo
                else:
                    anterior.proximo = atual.proximo
                self._tamanho -= 1
                return True
            anterior = atual
            atual = atual.proximo

        return False

    def listar_todos(self) -> list[T]:
        """Retorna todos os valores armazenados na Tabela Hash."""
        itens: list[T] = []
        for cabeca in self._buckets:
            atual = cabeca
            while atual is not None:
                itens.append(atual.valor)
                atual = atual.proximo
        return itens

    def obter_estatisticas(self) -> dict[str, int | float]:
        """Retorna métricas estruturais úteis para diagnóstico e apresentação."""
        buckets_ocupados = 0
        maior_cadeia = 0
        for cabeca in self._buckets:
            if cabeca is not None:
                buckets_ocupados += 1
                comprimento = 0
                atual: _NoHash[T] | None = cabeca
                while atual is not None:
                    comprimento += 1
                    atual = atual.proximo
                if comprimento > maior_cadeia:
                    maior_cadeia = comprimento

        return {
            "capacidade": self._capacidade,
            "tamanho": self._tamanho,
            "fator_carga": round(self._tamanho / self._capacidade, 4),
            "colisoes": self._colisoes,
            "buckets_ocupados": buckets_ocupados,
            "maior_cadeia": maior_cadeia,
        }

    def __len__(self) -> int:
        return self._tamanho
