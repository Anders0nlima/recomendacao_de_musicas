"""Ponto de entrada do Sistema de Recomendação de Músicas."""

from pathlib import Path
from rich.console import Console

from src.carregador import carregar_catalogo
from src.cli import InterfaceCLI
from src.estruturas.lista_encadeada import ListaHistorico
from src.motor_recomendacao import MotorRecomendacao


def main() -> None:
    console = Console()
    caminho_csv = Path(__file__).resolve().parent / "dados" / "musicas_1000.csv"

    try:
        with console.status("[bold cyan]Carregando catálogo e construindo grafo de similaridade...[/bold cyan]"):
            tabela_hash, grafo, duplicados = carregar_catalogo(caminho_csv)
    except FileNotFoundError as erro:
        console.print(f"[bold red]Erro:[/bold red] {erro}")
        console.print("Execute primeiro: [cyan]python scripts/preparar_dataset.py[/cyan]")
        return

    historico = ListaHistorico()
    motor = MotorRecomendacao(tabela_hash=tabela_hash, historico=historico, grafo=grafo)

    console.print(
        f"[bold green]Catálogo carregado![/bold green] "
        f"{len(tabela_hash)} músicas indexadas na Tabela Hash | "
        f"{grafo.obter_estatisticas()['total_arestas']} conexões no Grafo."
    )
    if duplicados > 0:
        console.print(f"[yellow]{duplicados} registro(s) duplicado(s) ou inválido(s) ignorado(s).[/yellow]")

    try:
        InterfaceCLI(motor).executar()
    except (KeyboardInterrupt, EOFError):
        console.print("\n[bold green]Execução interrompida pelo usuário. Até logo![/bold green]")


if __name__ == "__main__":
    main()
