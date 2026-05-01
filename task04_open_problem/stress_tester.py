import numpy as np
import logging
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

logger = logging.getLogger(__name__)

# Historical baselines for simulation (Annualized Mean Return, Annualized Volatility)
# These are rough historical estimates for demonstration purposes.
ASSET_PROFILES = {
    "BTC": {"mu": 0.40, "vol": 0.70},       # High return, extremely high volatility
    "NIFTY50": {"mu": 0.12, "vol": 0.18},   # Indian Equity baseline
    "GOLD": {"mu": 0.08, "vol": 0.15},      # Safe haven, lower volatility
    "CASH": {"mu": 0.04, "vol": 0.02},      # Liquid yield (e.g., FD or liquid fund)
    "DEFAULT": {"mu": 0.10, "vol": 0.20}    # Fallback for unknown assets
}

def run_monte_carlo(portfolio: dict, years: int = 30, num_simulations: int = 10000) -> dict:
    """
    Runs a stochastic Monte Carlo simulation on the portfolio to determine the 
    probability of ruin (running out of money before the end of the timeframe).
    
    Utilizes numpy vectorization to compute millions of data points in milliseconds.
    """
    total_value = portfolio.get("total_value_inr", 0)
    monthly_expenses = portfolio.get("monthly_expenses_inr", 0)
    assets = portfolio.get("assets", [])
    
    if not assets or total_value <= 0:
        raise ValueError("Invalid portfolio configuration.")
        
    months = years * 12
    
    # Calculate weighted portfolio return (mu) and volatility (vol)
    weighted_mu = 0.0
    weighted_var = 0.0 # Simplified: assuming 0 correlation for elegance in this test
    
    for asset in assets:
        alloc = asset.get("allocation_pct", 0) / 100.0
        name = asset.get("name", "DEFAULT")
        profile = ASSET_PROFILES.get(name, ASSET_PROFILES["DEFAULT"])
        
        weighted_mu += alloc * profile["mu"]
        weighted_var += (alloc * profile["vol"]) ** 2
        
    weighted_vol = np.sqrt(weighted_var)
    
    # Convert annualized metrics to monthly metrics
    monthly_mu = weighted_mu / 12
    monthly_vol = weighted_vol / np.sqrt(12)
    
    # Vectorized Monte Carlo Simulation
    # Generate random monthly returns for all simulations across all months
    # Matrix Shape: (num_simulations, months)
    random_shocks = np.random.normal(monthly_mu, monthly_vol, (num_simulations, months))
    
    # Track portfolio values across simulations
    # Array Shape: (num_simulations,)
    current_values = np.full(num_simulations, float(total_value))
    
    for m in range(months):
        # Apply market returns simultaneously across all 10,000 simulations
        current_values = current_values * (1 + random_shocks[:, m])
        # Deduct expenses
        current_values -= monthly_expenses
        
        # Prevent negative balances (once ruined, stays ruined)
        current_values = np.maximum(current_values, 0)
        
    # Count how many simulations ended up at exactly 0
    ruined_count = np.sum(current_values <= 0)
    ruin_probability = (ruined_count / num_simulations) * 100.0
    
    # Percentile bands for wealth distribution analysis
    percentiles = {
        "p5": float(np.percentile(current_values, 5)),
        "p25": float(np.percentile(current_values, 25)),
        "p50": float(np.median(current_values)),
        "p75": float(np.percentile(current_values, 75)),
        "p95": float(np.percentile(current_values, 95)),
    }
    
    return {
        "ruin_probability_pct": float(ruin_probability),
        "median_end_value_inr": percentiles["p50"],
        "percentiles": percentiles,
        "simulations_run": num_simulations,
        "years_projected": years
    }
    
def _format_inr(value: float) -> str:
    """Formats a number into Indian Rupee display (Crores/Lakhs)."""
    if value <= 0:
        return "₹0"
    if value >= 1_00_00_000:
        return f"₹{value / 1_00_00_000:,.2f} Cr"
    elif value >= 1_00_000:
        return f"₹{value / 1_00_000:,.2f} L"
    else:
        return f"₹{value:,.2f}"


def display_results(results: dict, portfolio: dict):
    console = Console()
    years = results["years_projected"]

    # Main metrics table
    table = Table(title=f"Monte Carlo Ruin Probability ({years}-Year Projection)")
    table.add_column("Metric", style="cyan")
    table.add_column("Result", justify="right", style="green")

    prob = results["ruin_probability_pct"]
    color = "green" if prob < 5 else "yellow" if prob < 15 else "red"

    table.add_row("Simulations Run", f"{results['simulations_run']:,}")
    table.add_row("Probability of Ruin", f"[{color}]{prob:.2f}%[/{color}]")
    table.add_row("Median End Value", _format_inr(results["median_end_value_inr"]))

    console.print("\n")
    console.print(Panel(table, expand=False, border_style="blue"))

    # Percentile bands table (wealth distribution)
    if "percentiles" in results:
        pct = results["percentiles"]
        band_table = Table(title="Wealth Distribution — Percentile Bands")
        band_table.add_column("Percentile", style="cyan")
        band_table.add_column("End Value", justify="right")
        band_table.add_column("Interpretation", style="dim")

        band_table.add_row("5th (Worst case)", f"[red]{_format_inr(pct['p5'])}[/red]", "Only 5% of outcomes are worse")
        band_table.add_row("25th", f"[yellow]{_format_inr(pct['p25'])}[/yellow]", "Pessimistic but plausible")
        band_table.add_row("50th (Median)", f"[green]{_format_inr(pct['p50'])}[/green]", "Most likely outcome")
        band_table.add_row("75th", f"[green]{_format_inr(pct['p75'])}[/green]", "Optimistic but plausible")
        band_table.add_row("95th (Best case)", f"[blue]{_format_inr(pct['p95'])}[/blue]", "Only 5% of outcomes are better")

        console.print(Panel(band_table, expand=False, border_style="dim"))

    console.print()
    if prob < 5:
        console.print(f"[bold green]✓ Wealth Advisor Insight (LOW RISK):[/bold green] Your portfolio shows strong long-term resilience and is highly likely to survive the {years}-year timeframe.")
    elif prob < 10:
        console.print(f"[bold yellow]⚠ Wealth Advisor Insight (MODERATE RISK):[/bold yellow] Your portfolio is generally stable over {years} years, but minor rebalancing could further secure your runway.")
    elif prob <= 20:
        console.print(f"[bold orange3]⚠ Wealth Advisor Warning (ELEVATED RISK):[/bold orange3] Over {years} years, your probability of ruin is uncomfortably high. Consider lowering your withdrawal rate or reallocating to less volatile assets.")
    else:
        console.print(f"[bold red]⛔ Wealth Advisor Alert (CRITICAL RISK):[/bold red] Over {years} years, your portfolio trajectory is financially dangerous. Drastic asset reallocation is required immediately.")

def conduct_cio_interview() -> dict:
    """
    Interactive CIO Interview — asks qualifying questions before running analysis.
    
    This transforms the tool from a generic calculator into a bespoke advisory
    experience, mirroring how a real Private CIO would operate: understand the
    client FIRST, then run the numbers.
    
    Returns:
        dict: Client context with goal, failure_definition, and time_horizon.
              Returns None if the user skips the interview.
    """
    console = Console()
    
    console.print(Panel(
        "[bold]Before we run the numbers, let me understand your family's situation.[/bold]\n"
        "[dim]Answer 3 quick questions so the AI CIO can tailor its advice.\n"
        "Press Enter to skip any question for default values.[/dim]",
        title="[bold cyan]🎙 CIO INTERVIEW[/bold cyan]",
        border_style="cyan",
        expand=False
    ))
    
    # Question 1: The Goal
    console.print("\n[bold cyan]Q1.[/bold cyan] What is this capital meant to achieve?")
    console.print("[dim]   (e.g., Generational wealth, Business succession, Children's education, Retirement)[/dim]")
    goal = input("   → ").strip()
    if not goal:
        goal = "Long-term wealth preservation for the family"
        console.print(f"   [dim]Using default: {goal}[/dim]")
    
    # Question 2: The Nightmare
    console.print("\n[bold cyan]Q2.[/bold cyan] What does financial failure look like for your family?")
    console.print("[dim]   (e.g., Portfolio falling below ₹50 Lakhs, Unable to fund children's education abroad)[/dim]")
    failure = input("   → ").strip()
    if not failure:
        failure = "Portfolio depleting before the end of the time horizon"
        console.print(f"   [dim]Using default: {failure}[/dim]")
    
    # Question 3: The Clock
    console.print("\n[bold cyan]Q3.[/bold cyan] What is your real time horizon in years?")
    console.print("[dim]   (e.g., 10, 15, 20, 30)[/dim]")
    horizon_input = input("   → ").strip()
    try:
        time_horizon = int(horizon_input) if horizon_input else 30
    except ValueError:
        time_horizon = 30
        console.print(f"   [dim]Could not parse — using default: {time_horizon} years[/dim]")
    
    if not horizon_input:
        console.print(f"   [dim]Using default: {time_horizon} years[/dim]")
    
    client_context = {
        "goal": goal,
        "failure_definition": failure,
        "time_horizon_years": time_horizon
    }
    
    console.print(Panel(
        f"[bold]Goal:[/bold] {goal}\n"
        f"[bold]Failure defined as:[/bold] {failure}\n"
        f"[bold]Time horizon:[/bold] {time_horizon} years",
        title="[bold green]✓ Client Profile Captured[/bold green]",
        border_style="green",
        expand=False
    ))
    
    return client_context


if __name__ == "__main__":
    import json
    from dotenv import load_dotenv
    from rich.syntax import Syntax
    from .rebalancer import suggest_rebalance
    
    load_dotenv()
    console = Console()
    
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
    
    # ═══════════════════════════════════════════════════════════════
    # PHASE 0: CIO Interview (Client Profiling)
    # ═══════════════════════════════════════════════════════════════
    console.print("\n[bold cyan]━━━ TIMECELL CIO — INVESTMENT COMMITTEE MEMO PIPELINE ━━━[/bold cyan]\n")
    
    client_context = conduct_cio_interview()
    
    # Use the client's time horizon for the simulation
    sim_years = client_context["time_horizon_years"]
    
    # ═══════════════════════════════════════════════════════════════
    # PHASE 1: Monte Carlo Simulation (Original Portfolio)
    # ═══════════════════════════════════════════════════════════════
    console.print(f"\n[dim]Phase 1: Running Monte Carlo simulation ({sim_years}-year horizon)...[/dim]")
    
    original_results = run_monte_carlo(sample_portfolio, years=sim_years)
    display_results(original_results, sample_portfolio)
    
    # ═══════════════════════════════════════════════════════════════
    # PHASE 2: Rebalancing Engine
    # ═══════════════════════════════════════════════════════════════
    console.print("\n[bold cyan]━━━ PHASE 2: REBALANCING ENGINE ━━━[/bold cyan]\n")
    
    rebalance_data = suggest_rebalance(sample_portfolio)
    changes = rebalance_data["changes"]
    
    if changes:
        change_table = Table(title="Proposed Rebalancing Actions")
        change_table.add_column("Asset", style="cyan")
        change_table.add_column("Action", style="yellow")
        change_table.add_column("From", justify="right")
        change_table.add_column("To", justify="right", style="green")
        change_table.add_column("Reason", style="dim")
        
        for c in changes:
            change_table.add_row(
                c["asset"], c["action"],
                f"{c['from_pct']}%", f"{c['to_pct']}%",
                c["reason"]
            )
        
        console.print(Panel(change_table, expand=False, border_style="yellow"))
        
        # ═══════════════════════════════════════════════════════════
        # PHASE 3: Re-simulate with Rebalanced Portfolio
        # ═══════════════════════════════════════════════════════════
        console.print("\n[bold cyan]━━━ PHASE 3: REBALANCED PORTFOLIO SIMULATION ━━━[/bold cyan]\n")
        console.print("[dim]Re-running 10,000 market paths with rebalanced allocation...[/dim]")
        
        rebalanced_portfolio = rebalance_data["rebalanced_portfolio"]
        rebalanced_results = run_monte_carlo(rebalanced_portfolio, years=sim_years)
        display_results(rebalanced_results, rebalanced_portfolio)
        
        # Show the improvement
        old_ruin = original_results["ruin_probability_pct"]
        new_ruin = rebalanced_results["ruin_probability_pct"]
        improvement = old_ruin - new_ruin
        
        console.print(f"\n[bold]Ruin Probability: [red]{old_ruin:.2f}%[/red] → [green]{new_ruin:.2f}%[/green] ([green]↓ {improvement:.2f} pp[/green])[/bold]")
    else:
        console.print("[green]✓ No rebalancing needed — portfolio is already within risk tolerance.[/green]")
        rebalanced_results = None
    
    # ═══════════════════════════════════════════════════════════════
    # PHASE 4: AI CIO Investment Committee Memo
    # ═══════════════════════════════════════════════════════════════
    try:
        from task03_ai_explainer.llm_client import LLMClient
        from task03_ai_explainer.output_parser import parse_llm_json
        from .cio_memo import generate_cio_memo
        
        client = LLMClient()
        
        console.print("\n[bold cyan]━━━ PHASE 4: AI CIO INVESTMENT COMMITTEE MEMO ━━━[/bold cyan]\n")
        console.print("[dim]Generating institutional-grade memo via Gemini...[/dim]")
        
        raw_memo = generate_cio_memo(
            client, sample_portfolio, original_results,
            rebalance_data if changes else None,
            rebalanced_results,
            client_context=client_context
        )
        
        # Parse and display the structured memo
        try:
            memo = parse_llm_json(raw_memo)
            
            # Risk Rating Header
            rating = memo.get("risk_rating", "UNKNOWN")
            rating_colors = {"LOW": "green", "MODERATE": "yellow", "ELEVATED": "red", "CRITICAL": "bold red"}
            rc = rating_colors.get(rating, "white")
            
            console.print(Panel(
                f"[{rc}]RISK RATING: {rating}[/{rc}]",
                title="[bold]TIMECELL AI — INVESTMENT COMMITTEE MEMO[/bold]",
                border_style="blue",
                expand=False
            ))
            
            # Executive Summary
            console.print(f"\n[bold]Executive Summary[/bold]")
            console.print(f"  {memo.get('executive_summary', 'N/A')}")
            
            # Key Findings
            findings = memo.get("key_findings", [])
            if findings:
                console.print(f"\n[bold]Key Findings[/bold]")
                for i, finding in enumerate(findings, 1):
                    console.print(f"  {i}. {finding}")
            
            # Recommended Actions
            actions = memo.get("recommended_actions", [])
            if actions:
                console.print(f"\n[bold]Recommended Actions[/bold]")
                for i, action in enumerate(actions, 1):
                    console.print(f"  {i}. {action}")
            
            # Client Talking Points
            talking = memo.get("client_talking_points", "")
            if talking:
                console.print(f"\n[bold]Client Talking Points[/bold]")
                console.print(Panel(talking, border_style="dim", expand=False))
            
        except (ValueError, KeyError):
            # Fallback: show raw response if JSON parsing fails
            console.print(Panel(raw_memo, title="CIO Memo (Raw)", border_style="blue"))
    
    except (ImportError, ValueError) as e:
        console.print(f"\n[dim]Skipping AI CIO memo (no API key configured): {e}[/dim]")
        console.print("[dim]Set GOOGLE_API_KEY in .env to enable the AI-powered CIO memo.[/dim]")
    
    console.print()

