from datetime import datetime
from typing import List
from rich.console import Console
from rich.table import Table
from .providers.base import AssetPrice

def print_price_table(prices: List[AssetPrice]):
    """
    Renders a beautiful terminal table using the 'rich' library.
    Gracefully handles and displays errors if an asset failed to fetch.
    """
    console = Console()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
    
    table = Table(title=f"Live Market Data — fetched at {timestamp}")
    table.add_column("Asset", style="cyan bold")
    table.add_column("Price", justify="right", style="green")
    table.add_column("Currency", style="yellow")
    table.add_column("Source", style="dim")
    table.add_column("Status", style="bold")
    
    for asset in prices:
        if asset.error:
            # Render failed fetches clearly without breaking the table
            table.add_row(
                asset.name, 
                "---", 
                "---", 
                asset.source, 
                f"[red]Error: {asset.error}[/red]"
            )
        else:
            # Format price with commas for readability
            formatted_price = f"{asset.price:,.2f}"
            table.add_row(
                asset.name, 
                formatted_price, 
                asset.currency, 
                asset.source, 
                "[green]Live[/green]"
            )
            
    console.print(table)
