import yfinance as yf
import logging
from .base import DataProvider, AssetPrice

logger = logging.getLogger(__name__)

class YFinanceProvider(DataProvider):
    """
    Provider for fetching stock, index, and commodity prices via Yahoo Finance.
    Free, no API key required.
    """
    def fetch_price(self, asset_symbol: str) -> AssetPrice:
        try:
            ticker = yf.Ticker(asset_symbol)
            
            # We use 'fast_info' instead of 'info' because it is significantly 
            # faster and less prone to rate-limiting or blocking.
            price = ticker.fast_info['last_price']
            
            if price is None:
                raise ValueError(f"No price data available for {asset_symbol} (may be delisted or invalid).")
            
            # Map ticker symbols to clean names and appropriate currencies
            currency = "USD"
            name = asset_symbol
            
            if asset_symbol == "^NSEI":
                currency = "INR"
                name = "NIFTY 50"
            elif asset_symbol.endswith(".NS"):
                currency = "INR"
                name = asset_symbol.replace(".NS", "")
            elif asset_symbol == "GC=F":
                currency = "USD"
                name = "GOLD (Futures)"
                
            return AssetPrice(
                name=name, 
                price=float(price), 
                currency=currency, 
                source="yfinance"
            )
            
        except Exception as e:
            logger.error(f"yfinance failed to fetch {asset_symbol}: {e}")
            raise
