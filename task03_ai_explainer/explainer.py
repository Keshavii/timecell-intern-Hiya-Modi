import os
import json
import logging
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from .prompts import SYSTEM_PROMPT_FINAL, TONE_MODIFIERS, format_portfolio_for_prompt
from .llm_client import ClaudeClient
from .output_parser import parse_llm_json
from .critic import critique_explanation

logging.basicConfig(level=logging.WARNING)
console = Console()

def run_explainer(portfolio: dict, tone: str = "experienced", use_critic: bool = False):
    """
    Main orchestrator for Task 03.
    """
    load_dotenv()
    
    try:
        client = ClaudeClient()
    except ValueError as e:
        console.print(f"[bold red]Configuration Error:[/bold red] {e}")
        return
        
    # 1. Prepare Prompts
    system_prompt = SYSTEM_PROMPT_FINAL
    if tone in TONE_MODIFIERS:
        system_prompt += f"\n\n{TONE_MODIFIERS[tone]}"
        
    user_message = format_portfolio_for_prompt(portfolio)
    
    # 2. Call LLM
    console.print(f"[dim]Analyzing portfolio using Claude (Tone: {tone})...[/dim]")
    raw_response = client.generate_response(system_prompt, user_message)
    
    # 3. Display RAW Output (Required by assignment)
    console.print("\n[bold cyan]1. RAW API RESPONSE[/bold cyan]")
    console.print(Panel(raw_response, border_style="cyan"))
    
    # 4. Parse and Display STRUCTURED Output (Required by assignment)
    parsed_json = parse_llm_json(raw_response)
    
    console.print("\n[bold green]2. EXTRACTED STRUCTURED OUTPUT[/bold green]")
    formatted_json = json.dumps(parsed_json, indent=2)
    console.print(Panel(Syntax(formatted_json, "json", theme="monokai", background_color="default"), border_style="green"))
    
    # 5. Bonus: Self-Critique
    if use_critic:
        console.print("\n[dim]Generating second-pass critique...[/dim]")
        critique = critique_explanation(client, portfolio, parsed_json)
        console.print("\n[bold yellow]3. EXPERT CRITIQUE[/bold yellow]")
        console.print(Panel(critique, border_style="yellow"))

if __name__ == "__main__":
    # Test with standard portfolio
    sample_portfolio = {
        "total_value_inr": 10_000_000,
        "monthly_expenses_inr": 80_000,
        "assets": [
            {"name": "BTC", "allocation_pct": 30, "expected_crash_pct": -80},
            {"name": "NIFTY50","allocation_pct": 40, "expected_crash_pct": -40},
            {"name": "GOLD", "allocation_pct": 20, "expected_crash_pct": -15},
            {"name": "CASH", "allocation_pct": 10, "expected_crash_pct": 0},
        ]
    }
    
    run_explainer(sample_portfolio, tone="experienced", use_critic=True)
