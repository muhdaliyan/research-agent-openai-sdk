import asyncio
from rich.console import Console
from rich.prompt import Prompt
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text
from rich.panel import Panel

# Local imports
from agent import research_agent
from banner import show_banner
from agents import Runner, TResponseInputItem

console = Console()

async def main():
    # Initial Banner
    show_banner()
    
    conversation_history: list[TResponseInputItem] = []
    
    try:
        while True:
            # User Input with style
            user_input = Prompt.ask("[bold green]Chat You[/bold green]")
            
            if not user_input.strip():
                continue
            
            conversation_history.append({
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": user_input
                    }
                ]
            })
            
            # Show reasoning status
            console.print("[dim italic blue]Agent is reasoning...[/dim italic blue]", end="\r")
            
            result = Runner.run_streamed(
                research_agent,
                input=conversation_history
            )
            
            is_first_chunk = True
            
            async for event in result.stream_events():
                # Clear reasoning status on first output (chunk or tool call)
                if is_first_chunk and (event.type == "raw_response_event" or event.name == "tool_called"):
                    # Print whitespace to clear the reasoning message
                    console.print(" " * 50, end="\r")
                    console.print("[bold blue]AI:[/bold blue] ", end="", flush=True)
                    is_first_chunk = False

                # Handle streaming text deltas
                if event.type == "raw_response_event":
                    content = None
                    if hasattr(event.data, "choices") and event.data.choices:
                        delta = getattr(event.data.choices[0], "delta", None)
                        content = getattr(delta, "content", None)
                    elif hasattr(event.data, "delta"):
                        content = getattr(event.data.delta, "content", None)
                    elif hasattr(event.data, "text"):
                        content = event.data.text
                    
                    if content:
                        console.print(content, end="", flush=True)
                
                # Handle tool calls
                elif event.type == "run_item_stream_event":
                    if event.name == "tool_called":
                        raw = getattr(event.item, "raw_item", None)
                        tool_name = (
                            getattr(event.item, "tool_name", None) or 
                            getattr(event.item, "name", None) or
                            getattr(getattr(raw, "function", None), "name", None) or
                            "Unknown Tool"
                        )
                        console.print(f"\n[bold yellow]⚡ {tool_name}...[/bold yellow]", flush=True)
                    elif event.name == "tool_output":
                        console.print(f"[dim green]✅ Tool results received.[/dim green]\n[bold blue]AI:[/bold blue] ", end="", flush=True)
            
            console.print() # Final newline after response
            
            # Update history (result.new_items is updated during streaming)
            conversation_history.extend([item.to_input_item() for item in result.new_items])
            
    except KeyboardInterrupt:
        console.print("\n[bold red]Exiting chat... Bye![/bold red]")

if __name__ == "__main__":
    asyncio.run(main())
