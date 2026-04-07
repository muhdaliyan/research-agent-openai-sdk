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
    
    title = Text("RESEARCH AGENT AI", style="bold cyan", justify="center")
    subtitle = Text("Using OpenAI Agents SDK & Ollama", style="dim italic white", justify="center")
    
    banner_text = Text.assemble(title, "\n", subtitle)
    
    panel = Panel(
        banner_text,
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
