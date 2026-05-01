import os
import sys
import json
import argparse
import logging
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

from .prompts import SYSTEM_PROMPT_FINAL, TONE_MODIFIERS, format_portfolio_for_prompt
from .llm_client import LLMClient
from .output_parser import parse_llm_json
from .critic import critique_explanation

logging.basicConfig(level=logging.WARNING)
console = Console()


def run_explainer(portfolio: dict, tone: str = "experienced", use_critic: bool = False):
    """
    Main orchestrator for Task 03.
    Accepts any portfolio dict — not hardcoded to a single example.
    """
    load_dotenv()

    try:
        client = LLMClient()
    except ValueError as e:
        console.print(f"[bold red]Configuration Error:[/bold red] {e}")
        return

    # ── Cross-Task Integration: Show Task 01 risk metrics alongside LLM output ──
    try:
        from task01_risk_calculator.risk_calculator import compute_risk_metrics, _format_inr
        risk_metrics = compute_risk_metrics(portfolio)

        metrics_table = Table(title="Computed Risk Metrics (Task 01)", show_lines=True)
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Value", justify="right", style="green")

        ruin_color = "green" if risk_metrics["ruin_test"] == "PASS" else "red"
        metrics_table.add_row("Post-Crash Value", _format_inr(risk_metrics["post_crash_value"]))
        metrics_table.add_row("Runway (months)", f"{risk_metrics['runway_months']:.1f}")
        metrics_table.add_row("Ruin Test", f"[{ruin_color}]{risk_metrics['ruin_test']}[/{ruin_color}]")
        metrics_table.add_row("Largest Risk Asset", risk_metrics["largest_risk_asset"] or "—")
        conc = "[red]⚠ YES[/red]" if risk_metrics["concentration_warning"] else "[green]✓ No[/green]"
        metrics_table.add_row("Concentration Warning", conc)

        console.print(Panel(metrics_table, expand=False, border_style="dim"))
        console.print()
    except ImportError:
        pass  # Graceful degradation if Task 01 is not available

    # 1. Prepare Prompts
    system_prompt = SYSTEM_PROMPT_FINAL
    if tone in TONE_MODIFIERS:
        system_prompt += f"\n\n{TONE_MODIFIERS[tone]}"

    user_message = format_portfolio_for_prompt(portfolio)

    # 2. Call LLM
    console.print(f"[dim]Analyzing portfolio using Gemini (Tone: {tone})...[/dim]")
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


# Default portfolio used when no --portfolio flag is provided
DEFAULT_PORTFOLIO = {
    "total_value_inr": 10_000_000,
    "monthly_expenses_inr": 80_000,
    "assets": [
        {"name": "BTC", "allocation_pct": 30, "expected_crash_pct": -80},
        {"name": "NIFTY50", "allocation_pct": 40, "expected_crash_pct": -40},
        {"name": "GOLD", "allocation_pct": 20, "expected_crash_pct": -15},
        {"name": "CASH", "allocation_pct": 10, "expected_crash_pct": 0},
    ]
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="AI-Powered Portfolio Explainer — generates plain-English risk analysis using Gemini."
    )
    parser.add_argument(
        "--portfolio", "-p",
        type=str,
        help="Path to a JSON file containing the portfolio. Uses a default sample if not provided."
    )
    parser.add_argument(
        "--tone", "-t",
        type=str,
        choices=["beginner", "experienced", "expert"],
        default="experienced",
        help="Tone of the explanation (default: experienced)"
    )
    parser.add_argument(
        "--critic", "-c",
        action="store_true",
        help="Enable self-critique: a second LLM call audits the first for accuracy."
    )

    args = parser.parse_args()

    # Load portfolio from file or use default
    if args.portfolio:
        try:
            with open(args.portfolio, "r") as f:
                portfolio = json.load(f)
            console.print(f"[dim]Loaded portfolio from: {args.portfolio}[/dim]")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            console.print(f"[bold red]Error loading portfolio:[/bold red] {e}")
            sys.exit(1)
    else:
        portfolio = DEFAULT_PORTFOLIO
        console.print("[dim]Using default sample portfolio (use --portfolio <file.json> to provide your own)[/dim]")

    console.print()
    run_explainer(portfolio, tone=args.tone, use_critic=args.critic)
