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
            user_input = Prompt.ask("\n[bold green]You[/bold green]")
            
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
            
            # Increased turn limit for deeper research
            result = Runner.run_streamed(
                research_agent,
                input=conversation_history,
                max_turns=20
            )
            
            is_first_chunk = True
            current_mode = "reasoning"
            is_reasoning_label_printed = False
            is_content_label_printed = False
            
            async for event in result.stream_events():
                if is_first_chunk:
                    console.print(" " * 50, end="\r")
                    is_first_chunk = False

                if event.type == "raw_response_event":
                    data_type = getattr(event.data, "type", None)
                    reason = None
                    content = None
                    
                    if data_type == "response.reasoning_text.delta":
                        reason = getattr(event.data, "delta", None)
                    elif data_type == "response.output_text.delta":
                        content = getattr(event.data, "delta", None)
                    elif hasattr(event.data, "choices") and event.data.choices:
                        delta = event.data.choices[0].delta
                        reason = getattr(delta, "reasoning_content", getattr(delta, "thought", None))
                        content = getattr(delta, "content", getattr(event.data, "text", None))
                    
                    # 1. Text found in reasoning field
                    if reason:
                        if not is_reasoning_label_printed:
                            console.print("\n[bold grey50]AI Reasoning:[/bold grey50] ", end="")
                            is_reasoning_label_printed = True
                        print(f"\033[3;90m{reason}\033[0m", end="", flush=True)
                    
                    # 2. Text found in content field
                    if content:
                        if not is_content_label_printed:
                            if is_reasoning_label_printed: print("\n")
                            console.print("[bold blue]AI:[/bold blue] ", end="")
                            is_content_label_printed = True
                        print(content, end="", flush=True)

                elif event.type == "run_item_stream_event":
                    item_type = getattr(event.item, "type", None)
                    
                    if getattr(event, "name", None) == "tool_called":
                        raw = getattr(event.item, "raw_item", None)
                        tool_name = (getattr(event.item, "tool_name", None) or 
                                     getattr(event.item, "name", None) or 
                                     "Tool")
                        console.print(f"\n[bold yellow]⚡ {tool_name}...[/bold yellow]")
                    elif getattr(event, "name", None) == "tool_output":
                        console.print(f"[dim green]✅ Tool results received.[/dim green]")
            
            print()
            
            # Update history (result.new_items is updated during streaming)
            conversation_history.extend([item.to_input_item() for item in result.new_items])
            
    except KeyboardInterrupt:
        console.print("\n[bold red]Exiting chat... Bye![/bold red]")

if __name__ == "__main__":
    asyncio.run(main())
