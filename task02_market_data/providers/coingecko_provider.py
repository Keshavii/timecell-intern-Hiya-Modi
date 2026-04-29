import requests
import logging
from .base import DataProvider, AssetPrice

logger = logging.getLogger(__name__)

class CoinGeckoProvider(DataProvider):
    """
    Provider for fetching cryptocurrency prices via CoinGecko's free API tier.
    No authentication required.
    """
    def fetch_price(self, asset_symbol: str) -> AssetPrice:
        try:
            # asset_symbol expects CoinGecko IDs like 'bitcoin' or 'ethereum'
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={asset_symbol}&vs_currencies=usd"
            
            # Enforce a strict timeout so one stuck request doesn't hang the whole script
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if asset_symbol not in data:
                raise ValueError(f"Asset '{asset_symbol}' not found in CoinGecko response.")
                
            price = data[asset_symbol]["usd"]
            
            # Format display names
            name = asset_symbol.upper()
            if asset_symbol == "bitcoin": 
                name = "BTC"
            elif asset_symbol == "ethereum": 
                name = "ETH"
            
            return AssetPrice(
                name=name, 
                price=float(price), 
                currency="USD", 
                source="CoinGecko"
            )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching {asset_symbol} from CoinGecko: {e}")
            raise
        except Exception as e:
            logger.error(f"CoinGecko API failed for {asset_symbol}: {e}")
            raise
