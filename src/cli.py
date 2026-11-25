"""Interface de linha de comando (CLI) estilizada com Rich."""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from src.modelos import Musica
from src.motor_recomendacao import MotorRecomendacao, Recomendacao


class InterfaceCLI:
    """Menu interativo no terminal para demonstrar o sistema de recomendação."""

    def __init__(self, motor: MotorRecomendacao) -> None:
        self.motor = motor
        self.console = Console()

    def executar(self) -> None:
        """Loop principal do menu interativo."""
        while True:
            self._exibir_menu()
            opcao = Prompt.ask(
                "[bold cyan]Escolha uma opção[/bold cyan]",
                choices=["0", "1", "2", "3", "4", "5"],
                show_choices=False,
            )

            if opcao == "1":
                self._fluxo_buscar_e_tocar()
            elif opcao == "2":
                self._fluxo_ver_historico()
            elif opcao == "3":
                self._fluxo_recomendar_por_historico()
            elif opcao == "4":
                self._fluxo_inspecionar_estruturas()
            elif opcao == "5":
                self._fluxo_limpar_historico()
            elif opcao == "0":
                self.console.print("\n[bold green]Encerrando o sistema. Até logo![/bold green]")
                break

    def _exibir_menu(self) -> None:
        texto_menu = (
            "[bold]1.[/bold] Buscar e reproduzir música\n"
            "[bold]2.[/bold] Ver histórico de reprodução (Lista Encadeada)\n"
            "[bold]3.[/bold] Recomendar com base no meu histórico\n"
            "[bold]4.[/bold] Painel técnico das estruturas de dados\n"
            "[bold]5.[/bold] Limpar histórico\n"
            "[bold]0.[/bold] Sair"
        )
        self.console.print()
        self.console.print(
            Panel(
                texto_menu,
                title="[bold magenta]Sistema de Recomendação de Músicas[/bold magenta]",
                border_style="bright_blue",
            )
        )

    def _fluxo_buscar_e_tocar(self) -> None:
        termo = Prompt.ask("[cyan]Digite o nome da música ou artista[/cyan]").strip()
        if not termo:
            self.console.print("[yellow]Digite um termo válido para buscar.[/yellow]")
            return

        resultados = self.motor.buscar_por_texto(termo, limite=10)
        if not resultados:
            self.console.print(f"[red]Nenhuma música encontrada para '{termo}'.[/red]")
            sugestoes = self.motor.sugerir_parecidas(termo, limite=5)
            if sugestoes:
                self.console.print("[yellow]Você quis dizer alguma destas?[/yellow]")
                resultados = sugestoes
            else:
                return

        self._exibir_tabela_musicas(resultados, titulo="Resultados da Busca")
        escolha = Prompt.ask(
            "[cyan]Digite o número da música para reproduzir (ou 0 para cancelar)[/cyan]",
            default="0",
        ).strip()

        if not escolha.isdigit():
            self.console.print("[red]Entrada inválida. Informe apenas números.[/red]")
            return

        indice = int(escolha)
        if indice == 0:
            return
        if indice < 1 or indice > len(resultados):
            self.console.print("[red]Número fora da lista exibida.[/red]")
            return

        selecionada = resultados[indice - 1]
        self.motor.reproduzir_musica(selecionada.id)

        self.console.print(
            Panel(
                f"[bold green]Reproduzindo agora:[/bold green] {selecionada.titulo} — [italic]{selecionada.artista}[/italic]\n"
                f"Gênero: [cyan]{selecionada.genero}[/cyan] | "
                f"Energia: {selecionada.energia:.2f} | "
                f"Dançabilidade: {selecionada.dancabilidade:.2f} | "
                f"Valência: {selecionada.valencia:.2f}",
                border_style="green",
            )
        )

        recomendacoes = self.motor.recomendar_por_musica(selecionada.id, limite=5)
        if not recomendacoes:
            self.console.print(
                "[yellow]Esta música não possui vizinhos disponíveis no grafo (ou todos já foram ouvidos).[/yellow]"
            )
            return

        self._exibir_recomendacoes(
            recomendacoes,
            titulo=f"Próximas recomendadas a partir de '{selecionada.titulo}'",
        )

    def _fluxo_ver_historico(self) -> None:
        if self.motor.historico.esta_vazia():
            self.console.print("[yellow]Seu histórico de reprodução ainda está vazio.[/yellow]")
            return

        nos = self.motor.historico.listar_historico(mais_recente_primeiro=True)
        tabela = Table(title="Histórico de Reprodução (Mais Recentes Primeiro)", border_style="cyan")
        tabela.add_column("Ordem", justify="right", style="bold")
        tabela.add_column("Hora", style="dim")
        tabela.add_column("Título", style="bold white")
        tabela.add_column("Artista", style="green")
        tabela.add_column("Gênero", style="magenta")

        for no in nos:
            tabela.add_row(
                str(no.ordem),
                no.timestamp,
                no.musica.titulo,
                no.musica.artista,
                no.musica.genero,
            )

        self.console.print(tabela)

    def _fluxo_recomendar_por_historico(self) -> None:
        try:
            recomendacoes = self.motor.recomendar_por_historico(limite=5)
        except ValueError as erro:
            self.console.print(f"[yellow]{erro}[/yellow]")
            return

        if not recomendacoes:
            self.console.print(
                "[yellow]Não há novas recomendações disponíveis no momento (todas as vizinhas já estão no histórico).[/yellow]"
            )
            return

        self._exibir_recomendacoes(
            recomendacoes,
            titulo="Recomendações Personalizadas Baseadas no seu Histórico",
        )

    def _fluxo_inspecionar_estruturas(self) -> None:
        stats_hash = self.motor.tabela_hash.obter_estatisticas()
        stats_grafo = self.motor.grafo.obter_estatisticas()

        tabela = Table(title="Diagnóstico das Estruturas de Dados em Memória", border_style="yellow")
        tabela.add_column("Estrutura", style="bold cyan")
        tabela.add_column("Métricas", style="white")

        tabela.add_row(
            "Tabela Hash\n(Encadeamento Separado)",
            f"Capacidade: {stats_hash['capacidade']} buckets | "
            f"Elementos: {stats_hash['tamanho']} | "
            f"Fator de carga: {stats_hash['fator_carga']}\n"
            f"Colisões: {stats_hash['colisoes']} | "
            f"Buckets ocupados: {stats_hash['buckets_ocupados']} | "
            f"Maior cadeia: {stats_hash['maior_cadeia']}",
        )
        tabela.add_row(
            "Lista Duplamente Encadeada\n(Histórico)",
            f"Reproduções registradas: {len(self.motor.historico)} | "
            f"Vazia: {'Sim' if self.motor.historico.esta_vazia() else 'Não'}",
        )
        tabela.add_row(
            "Grafo Ponderado\n(Lista de Adjacência)",
            f"Vértices: {stats_grafo['total_vertices']} | "
            f"Arestas: {stats_grafo['total_arestas']} | "
            f"Grau médio: {stats_grafo['grau_medio']} | "
            f"Vértices isolados: {stats_grafo['vertices_isolados']}",
        )

        self.console.print(tabela)

    def _fluxo_limpar_historico(self) -> None:
        if self.motor.historico.esta_vazia():
            self.console.print("[yellow]O histórico já está vazio.[/yellow]")
            return
        self.motor.historico.limpar()
        self.console.print("[green]Histórico de reprodução limpo com sucesso.[/green]")

    def _exibir_tabela_musicas(self, musicas: list[Musica], titulo: str) -> None:
        tabela = Table(title=titulo, border_style="blue")
        tabela.add_column("#", justify="right", style="bold cyan")
        tabela.add_column("Título", style="bold white")
        tabela.add_column("Artista", style="green")
        tabela.add_column("Gênero", style="magenta")
        tabela.add_column("Pop.", justify="right")

        for idx, m in enumerate(musicas, start=1):
            tabela.add_row(str(idx), m.titulo, m.artista, m.genero, str(m.popularidade))

        self.console.print(tabela)

    def _exibir_recomendacoes(self, recomendacoes: list[Recomendacao], titulo: str) -> None:
        tabela = Table(title=titulo, border_style="green", show_lines=True)
        tabela.add_column("#", justify="right", style="bold cyan")
        tabela.add_column("Música", style="bold white")
        tabela.add_column("Afinidade", justify="center", style="bold yellow")
        tabela.add_column("Por que recomendamos?", style="white")

        for idx, rec in enumerate(recomendacoes, start=1):
            info_musica = (
                f"{rec.musica.titulo}\n"
                f"[green]{rec.musica.artista}[/green] · [magenta]{rec.musica.genero}[/magenta]"
            )
            razoes = "\n".join(f"• {r}" for r in rec.justificativas)
            bases = ", ".join(rec.musicas_base)
            explicacao = f"{razoes}\n[dim]Baseado em: {bases}[/dim]"
            tabela.add_row(
                str(idx),
                info_musica,
                f"{rec.afinidade_percentual:.1f}%",
                explicacao,
            )

        self.console.print(tabela)
