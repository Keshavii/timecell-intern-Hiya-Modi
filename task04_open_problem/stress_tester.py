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
    
    median_end_value = float(np.median(current_values))
    
    return {
        "ruin_probability_pct": float(ruin_probability),
        "median_end_value_inr": median_end_value,
        "simulations_run": num_simulations,
        "years_projected": years
    }
    
def display_results(results: dict, portfolio: dict):
    console = Console()
    
    # Format the table
    table = Table(title="Monte Carlo Ruin Probability (30-Year Projection)")
    table.add_column("Metric", style="cyan")
    table.add_column("Result", justify="right", style="green")
    
    prob = results["ruin_probability_pct"]
    color = "green" if prob < 5 else "yellow" if prob < 15 else "red"
    
    table.add_row("Simulations Run", f"{results['simulations_run']:,}")
    table.add_row("Probability of Ruin", f"[{color}]{prob:.2f}%[/{color}]")
    table.add_row("Median End Value", f"₹{results['median_end_value_inr']:,.2f}")
    
    console.print("\n")
    console.print(Panel(table, expand=False, border_style="blue"))
    
    if prob > 10:
        console.print("\n[bold red]Wealth Advisor Warning:[/bold red] Your probability of ruin is uncomfortably high. Consider lowering your withdrawal rate or reallocating to less volatile assets.")
    else:
        console.print("\n[bold green]Wealth Advisor Insight:[/bold green] Your portfolio shows strong long-term resilience based on stochastic modeling.")

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
    console = Console()
    console.print("[dim]Initializing vector matrix... running 10,000 market paths...[/dim]")
    res = run_monte_carlo(sample_portfolio)
    display_results(res, sample_portfolio)
