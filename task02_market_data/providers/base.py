from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class AssetPrice:
    """Standardized model for an asset's current market price."""
    name: str
    price: float
    currency: str
    source: str
    error: Optional[str] = None

class DataProvider(ABC):
    """
    Abstract Base Class for all market data providers.
    Enforces a standard contract for fetching prices.
    """
    @abstractmethod
    def fetch_price(self, asset_symbol: str) -> AssetPrice:
        """Fetch current price for the given asset."""
        pass
