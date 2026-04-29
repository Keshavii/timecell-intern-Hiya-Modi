import sys
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel

def draw_allocation_chart(portfolio_dict: dict):
    """
    Renders a pure-Python terminal bar chart showing portfolio allocation.
    Uses the `rich` library for terminal formatting.
    """
    console = Console()
    assets = portfolio_dict.get("assets", [])
    
    if not assets:
        console.print("[yellow]No assets to visualize.[/yellow]")
        return
        
    # Set up the table without external borders
    table = Table(title="Portfolio Allocation Breakdown", show_header=False, box=None)
    table.add_column("Asset", style="cyan bold", justify="right")
    table.add_column("Bar")
    table.add_column("Pct", style="green bold", justify="left")
    
    max_bar_len = 40  # Max block characters for the progress bar
    
    # Handle case where total allocation is not exactly 100%
    total_pct = sum(a.get("allocation_pct", 0) for a in assets)
    if total_pct <= 0:
        total_pct = 1.0  # Prevent division by zero if all allocations are zero
        
    for asset in assets:
        name = asset.get("name", "Unknown")
        pct = asset.get("allocation_pct", 0)
        expected_crash = asset.get("expected_crash_pct", 0)
        
        # Calculate scaled bar length
        # Using pure percentage for the bar if total <= 100, else normalized
        scale_pct = pct if total_pct <= 100 else (pct / total_pct) * 100
        bar_len = int((scale_pct / 100.0) * max_bar_len)
        bar = "█" * bar_len
        
        # Dynamically color the bar based on the asset's risk and size
        if expected_crash <= -50:
            color = "red"  # High crash risk
        elif pct > 40:
            color = "yellow"  # Concentration warning
        elif expected_crash >= -10:
            color = "green"  # Low risk (e.g., cash, bonds)
        else:
            color = "blue"  # Moderate risk
            
        styled_bar = Text(bar, style=color)
        table.add_row(name, styled_bar, f"{pct}%")
        
    # Wrap in a neat panel
    console.print(Panel(table, border_style="dim", expand=False))

if __name__ == "__main__":
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
    draw_allocation_chart(sample_portfolio)
