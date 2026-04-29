import copy
from typing import Dict, Any
from .risk_calculator import compute_risk_metrics

def compute_multi_scenario(portfolio_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes risk metrics for multiple scenarios (worst-case and moderate).
    
    Worst-case: Full expected crash magnitude.
    Moderate: 50% of the expected crash magnitude.
    """
    if not portfolio_dict:
        return {}

    # Worst case is simply the standard compute_risk_metrics call
    worst_case_metrics = compute_risk_metrics(portfolio_dict)
    
    # Moderate case: reduce all crash percentages by half
    moderate_portfolio = copy.deepcopy(portfolio_dict)
    for asset in moderate_portfolio.get("assets", []):
        asset["expected_crash_pct"] = asset["expected_crash_pct"] / 2.0
        
    moderate_metrics = compute_risk_metrics(moderate_portfolio)
    
    return {
        "worst_case": worst_case_metrics,
        "moderate_case": moderate_metrics
    }
