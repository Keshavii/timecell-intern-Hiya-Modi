import time
import logging
from typing import List
from .providers.base import AssetPrice
from .providers.yfinance_provider import YFinanceProvider
from .providers.coingecko_provider import CoinGeckoProvider
from .formatter import print_price_table

# Configure standard Python logging for background warnings/errors
logging.basicConfig(level=logging.WARNING, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fetch_all_prices() -> List[AssetPrice]:
    """
    Orchestrates data fetching across multiple providers.
    Implements robust error handling and exponential backoff retries.
    NEVER crashes the whole process if a single API fails.
    """
    # Configuration: What to fetch and from where
    assets_to_fetch = [
        {"symbol": "bitcoin", "provider": CoinGeckoProvider()},
        {"symbol": "ethereum", "provider": CoinGeckoProvider()},
        {"symbol": "^NSEI", "provider": YFinanceProvider()},       # NIFTY 50 (Indian Index)
        {"symbol": "RELIANCE.NS", "provider": YFinanceProvider()}, # Reliance (Indian Equity)
        {"symbol": "GC=F", "provider": YFinanceProvider()},        # Gold Futures
    ]
    
    results = []
    
    for item in assets_to_fetch:
        symbol = item["symbol"]
        provider = item["provider"]
        max_retries = 2
        
        asset_price = None
        
        # Exponential backoff retry loop
        for attempt in range(max_retries + 1):
            try:
                asset_price = provider.fetch_price(symbol)
                break  # Success! Break out of the retry loop
                
            except Exception as e:
                if attempt < max_retries:
                    sleep_time = 2 ** attempt  # 1s, 2s...
                    logger.warning(f"Fetch failed for {symbol}. Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                else:
                    logger.error(f"All retries failed for {symbol}.")
                    # Graceful degradation: create an error record instead of crashing
                    asset_price = AssetPrice(
                        name=symbol.upper(),
                        price=0.0,
                        currency="N/A",
                        source=provider.__class__.__name__,
                        error="API Unavailable"
                    )
        
        if asset_price:
            results.append(asset_price)
            
    return results

if __name__ == "__main__":
    from rich.console import Console
    console = Console()
    console.print("\n[dim]Fetching live market data from multiple APIs...[/dim]\n")
    
    prices = fetch_all_prices()
    print_price_table(prices)
