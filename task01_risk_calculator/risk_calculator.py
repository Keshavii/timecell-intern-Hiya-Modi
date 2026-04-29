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

if __name__ == "__main__":
    # Example usage
    sample_portfolio = {
        "total_value_inr": 10_000_000, # 1 Crore INR
        "monthly_expenses_inr": 80_000,
        "assets": [
            {"name": "BTC", "allocation_pct": 30, "expected_crash_pct": -80},
            {"name": "NIFTY50","allocation_pct": 40, "expected_crash_pct": -40},
            {"name": "GOLD", "allocation_pct": 20, "expected_crash_pct": -15},
            {"name": "CASH", "allocation_pct": 10, "expected_crash_pct": 0},
        ]
    }
    from rich import print
    metrics = compute_risk_metrics(sample_portfolio)
    print("[bold green]Risk Metrics Computed:[/bold green]")
    print(metrics)
