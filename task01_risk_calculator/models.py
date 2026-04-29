from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class Asset:
    """Represents a single financial asset in a portfolio."""
    name: str
    allocation_pct: float
    expected_crash_pct: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Asset":
        """Creates an Asset instance from a dictionary."""
        return cls(
            name=str(data.get("name", "Unknown")),
            allocation_pct=float(data.get("allocation_pct", 0.0)),
            expected_crash_pct=float(data.get("expected_crash_pct", 0.0))
        )

@dataclass
class Portfolio:
    """Represents a financial portfolio with its configuration and assets."""
    total_value_inr: float
    monthly_expenses_inr: float
    assets: List[Asset]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Portfolio":
        """Creates a Portfolio instance from a dictionary."""
        return cls(
            total_value_inr=float(data.get("total_value_inr", 0.0)),
            monthly_expenses_inr=float(data.get("monthly_expenses_inr", 0.0)),
            assets=[Asset.from_dict(a) for a in data.get("assets", [])]
        )
