from rich.console import Console
from src.search import search

console = Console()

def run_repl():
    console.print("[bold green]📚 Wikipedia Vector Search REPL[/bold green]")
    console.print("Type your query or 'exit' to quit.\n")
    while True:
        query = input(">").strip()
        if query.lower() in {"exit", "quit"}:
            console.print("Goodbye! 👋")
            break

        try:
            results = search(query)
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            continue

        if not results:
            console.print("[yellow]No results found.[/yellow]\n")
            continue

        top_three = results[:3]

        for i, (question, answer, statement, original, dist, embed) in enumerate(top_three, 1):
            console.print(f"[i]{i}.[/i] [bold cyan]Q:[/bold cyan] {question}")
            console.print(f"[bold green]A:[/bold green] {answer}")
            console.print(f"[magenta]Statement:[/magenta] {statement}")
            console.print(f"[dim]Original: {original}[/dim]")
            console.print(f"[blue]Distance: {dist:.4f}\n[/blue]")

if __name__ == "__main__":
    run_repl()
