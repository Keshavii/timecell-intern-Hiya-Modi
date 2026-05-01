from typing import Dict, Any
from .models import Portfolio

def compute_risk_metrics(portfolio_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes key risk metrics for a given portfolio.
    
    Args:
        portfolio_dict: A dictionary representing the portfolio configuration.
        
    Returns:
        A dictionary containing the post-crash value, runway months, ruin test result,
        largest risk asset, and concentration warning.
    """
    if not portfolio_dict:
        return {}
        
    try:
        portfolio = Portfolio.from_dict(portfolio_dict)
    except (KeyError, ValueError, TypeError) as e:
        raise ValueError(f"Invalid portfolio data provided: {e}")

    # Edge case: Empty assets list
    if not portfolio.assets:
        runway = float('inf') if portfolio.monthly_expenses_inr <= 0 else portfolio.total_value_inr / portfolio.monthly_expenses_inr
        return {
            "post_crash_value": portfolio.total_value_inr,
            "runway_months": runway,
            "ruin_test": "PASS" if runway > 12 else "FAIL",
            "largest_risk_asset": None,
            "concentration_warning": False
        }

    post_crash_value = 0.0
    largest_risk_magnitude = -1.0
    largest_risk_asset_name = None
    concentration_warning = False
    
    # Calculate metrics over all assets
    for asset in portfolio.assets:
        if asset.allocation_pct < 0:
            raise ValueError(f"Negative allocation for asset {asset.name} is not allowed.")
        
        # Calculate post-crash value for this asset
        allocation_value = portfolio.total_value_inr * (asset.allocation_pct / 100.0)
        
        # Expected crash pct is given as a negative number (e.g., -80 for -80%)
        # So 1 + (crash_pct/100) calculates the remaining value multiplier.
        remaining_multiplier = 1.0 + (asset.expected_crash_pct / 100.0)
        # Ensure asset value doesn't go below 0 
        post_crash_asset_value = max(0.0, allocation_value * remaining_multiplier)
        post_crash_value += post_crash_asset_value
        
        # Identify the largest risk contributor
        # Risk magnitude is allocation_pct * absolute crash magnitude
        risk_magnitude = asset.allocation_pct * abs(asset.expected_crash_pct)
        if risk_magnitude > largest_risk_magnitude:
            largest_risk_magnitude = risk_magnitude
            largest_risk_asset_name = asset.name
            
        # Check for concentration
        if asset.allocation_pct > 40:
            concentration_warning = True

    # Calculate runway in months
    if portfolio.monthly_expenses_inr <= 0:
        runway_months = float('inf')
    else:
        runway_months = post_crash_value / portfolio.monthly_expenses_inr

    # Determine pass/fail for the ruin test
    ruin_test = "PASS" if runway_months > 12 else "FAIL"

    return {
        "post_crash_value": post_crash_value,
        "runway_months": runway_months,
        "ruin_test": ruin_test,
        "largest_risk_asset": largest_risk_asset_name,
        "concentration_warning": concentration_warning
    }

def _format_inr(value: float) -> str:
    """Formats a number into Indian Rupee display (Crores/Lakhs)."""
    if value == float('inf'):
        return "∞"
    if value >= 1_00_00_000:
        return f"₹{value / 1_00_00_000:,.2f} Cr"
    elif value >= 1_00_000:
        return f"₹{value / 1_00_000:,.2f} L"
    else:
        return f"₹{value:,.2f}"


if __name__ == "__main__":
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from .scenarios import compute_multi_scenario
    from .visualizer import draw_allocation_chart

    console = Console()

    sample_portfolio = {
        "total_value_inr": 10_000_000,  # 1 Crore INR
        "monthly_expenses_inr": 80_000,
        "assets": [
            {"name": "BTC", "allocation_pct": 30, "expected_crash_pct": -80},
            {"name": "NIFTY50", "allocation_pct": 40, "expected_crash_pct": -40},
            {"name": "GOLD", "allocation_pct": 20, "expected_crash_pct": -15},
            {"name": "CASH", "allocation_pct": 10, "expected_crash_pct": 0},
        ]
    }

    console.print("\n[bold cyan]━━━ TIMECELL PORTFOLIO RISK ANALYZER ━━━[/bold cyan]\n")

    # ── Section 1: Portfolio Overview ──
    console.print(f"  [dim]Total Value:[/dim]      {_format_inr(sample_portfolio['total_value_inr'])}")
    console.print(f"  [dim]Monthly Expenses:[/dim] {_format_inr(sample_portfolio['monthly_expenses_inr'])}")
    console.print()

    # ── Section 2: Allocation Breakdown (Bonus: CLI Bar Chart) ──
    draw_allocation_chart(sample_portfolio)

    # ── Section 3: Multi-Scenario Risk Analysis ──
    scenarios = compute_multi_scenario(sample_portfolio)
    worst = scenarios["worst_case"]
    moderate = scenarios["moderate_case"]

    table = Table(title="Risk Metrics — Scenario Comparison", show_lines=True)
    table.add_column("Metric", style="cyan bold")
    table.add_column("Worst Case", justify="right", style="red")
    table.add_column("Moderate Case", justify="right", style="yellow")

    # Post-crash value
    table.add_row(
        "Post-Crash Value",
        _format_inr(worst["post_crash_value"]),
        _format_inr(moderate["post_crash_value"])
    )

    # Runway months
    table.add_row(
        "Runway (months)",
        f"{worst['runway_months']:.1f}",
        f"{moderate['runway_months']:.1f}"
    )

    # Ruin test
    worst_ruin_color = "green" if worst["ruin_test"] == "PASS" else "red"
    mod_ruin_color = "green" if moderate["ruin_test"] == "PASS" else "red"
    table.add_row(
        "12-Month Ruin Test",
        f"[{worst_ruin_color}]{worst['ruin_test']}[/{worst_ruin_color}]",
        f"[{mod_ruin_color}]{moderate['ruin_test']}[/{mod_ruin_color}]"
    )

    # Largest risk asset
    table.add_row(
        "Largest Risk Asset",
        worst["largest_risk_asset"] or "—",
        moderate["largest_risk_asset"] or "—"
    )

    # Concentration warning
    worst_conc = "[red]⚠ YES[/red]" if worst["concentration_warning"] else "[green]✓ No[/green]"
    mod_conc = "[red]⚠ YES[/red]" if moderate["concentration_warning"] else "[green]✓ No[/green]"
    table.add_row("Concentration Warning", worst_conc, mod_conc)

    console.print()
    console.print(Panel(table, expand=False, border_style="blue"))
    console.print()
