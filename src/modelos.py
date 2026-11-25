"""Modelos de domínio da aplicação."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Musica:
    """Representa uma faixa musical carregada do catálogo."""

    id: str
    titulo: str
    artista: str
    genero: str
    energia: float
    dancabilidade: float
    valencia: float
    popularidade: int
