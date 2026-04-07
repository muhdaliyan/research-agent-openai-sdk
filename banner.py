import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout

console = Console()

def clear_console():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner():
    """Display a stylish banner for the Research Agent."""
    clear_console()
    
    from rich.table import Table
    
    table = Table.grid(expand=True)
    table.add_column("Main", justify="left", ratio=1, min_width=35)
    table.add_column("Features", justify="right", style="dim")
    
    title = Text("RESEARCH AGENT AI", style="bold cyan", justify="left")
    subtitle = Text("Using OpenAI Agents SDK & Ollama", style="dim italic white", justify="left")
    left_banner = Text.assemble(title, "\n", subtitle)
    
    right_features = Text.assemble(
        Text("Features:\n", style="bold yellow"),
        Text("+ Tool Calling\n", style="green"),
        Text("+ AI Reasoning", style="green")
    )
    
    table.add_row(left_banner, right_features)
    
    panel = Panel(
        table,
        border_style="bright_blue",
        padding=(1, 2),
        title="[bold white]V1.0[/bold white]",
        title_align="right",
        subtitle="[bold red]Press Ctrl+C to exit[/bold red]",
        subtitle_align="center"
    )
    
    console.print(panel)
    console.print("\n")

if __name__ == "__main__":
    show_banner()
