"""
Rebalancer Module — Suggests an improved portfolio allocation based on risk analysis.

This is pure Python logic (no LLM dependency), making it fully testable.
The rebalancer applies conservative wealth management heuristics used by
real family offices to reduce ruin probability.
"""

# Maximum acceptable allocation to any single high-volatility asset
MAX_VOLATILE_ALLOCATION = 15.0

# Assets considered high-volatility (expected crash > 50%)
HIGH_VOLATILITY_THRESHOLD = -50

# Conservative rebalancing target: assets to suggest when reducing risk
SAFE_HAVEN_SUGGESTION = {"name": "FIXED_INCOME", "allocation_pct": 0, "expected_crash_pct": -5}


def suggest_rebalance(portfolio: dict) -> dict:
    """
    Analyzes a portfolio and suggests a rebalanced version that reduces
    concentration risk in high-volatility assets.
    
    Strategy:
    1. Cap any high-volatility asset at MAX_VOLATILE_ALLOCATION (15%)
    2. Redistribute freed allocation to a new Fixed Income bucket
    3. Return the rebalanced portfolio for re-simulation
    
    Returns:
        dict: A new portfolio dict with the same structure but adjusted allocations,
              plus a 'changes' list describing what was modified.
    """
    assets = portfolio.get("assets", [])
    changes = []
    rebalanced_assets = []
    freed_allocation = 0.0
    
    for asset in assets:
        name = asset["name"]
        alloc = asset["allocation_pct"]
        crash = asset.get("expected_crash_pct", 0)
        
        # Check if this asset is high-volatility AND over-concentrated
        if crash <= HIGH_VOLATILITY_THRESHOLD and alloc > MAX_VOLATILE_ALLOCATION:
            old_alloc = alloc
            new_alloc = MAX_VOLATILE_ALLOCATION
            freed = old_alloc - new_alloc
            freed_allocation += freed
            
            changes.append({
                "asset": name,
                "action": "REDUCE",
                "from_pct": old_alloc,
                "to_pct": new_alloc,
                "reason": f"{name} has {crash}% crash risk — capping at {MAX_VOLATILE_ALLOCATION}%"
            })
            
            rebalanced_assets.append({
                **asset,
                "allocation_pct": new_alloc
            })
        else:
            rebalanced_assets.append({**asset})
    
    # If we freed up allocation, add it to Fixed Income
    if freed_allocation > 0:
        # Check if Fixed Income already exists
        fi_exists = False
        for asset in rebalanced_assets:
            if asset["name"] == "FIXED_INCOME":
                asset["allocation_pct"] += freed_allocation
                fi_exists = True
                break
        
        if not fi_exists:
            rebalanced_assets.append({
                "name": "FIXED_INCOME",
                "allocation_pct": freed_allocation,
                "expected_crash_pct": -5
            })
            changes.append({
                "asset": "FIXED_INCOME",
                "action": "ADD",
                "from_pct": 0,
                "to_pct": freed_allocation,
                "reason": f"Redirected {freed_allocation}% from volatile assets into stable fixed income"
            })
    
    rebalanced_portfolio = {
        **portfolio,
        "assets": rebalanced_assets
    }
    
    return {
        "original_portfolio": portfolio,
        "rebalanced_portfolio": rebalanced_portfolio,
        "changes": changes,
        "total_freed_pct": freed_allocation
    }
