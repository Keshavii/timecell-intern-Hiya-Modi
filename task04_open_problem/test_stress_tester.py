import pytest
import numpy as np
from task04_open_problem.stress_tester import run_monte_carlo
from task04_open_problem.rebalancer import suggest_rebalance
from task04_open_problem.cio_memo import format_simulation_for_cio

@pytest.fixture
def sample_portfolio():
    return {
        "total_value_inr": 10_000_000,
        "monthly_expenses_inr": 80_000,
        "assets": [
            {"name": "BTC", "allocation_pct": 30, "expected_crash_pct": -80},
            {"name": "NIFTY50", "allocation_pct": 40, "expected_crash_pct": -40},
            {"name": "GOLD", "allocation_pct": 20, "expected_crash_pct": -15},
            {"name": "CASH", "allocation_pct": 10, "expected_crash_pct": 0},
        ]
    }

# ═══════════════════════════════════════════════════════════
# Monte Carlo Engine Tests
# ═══════════════════════════════════════════════════════════

def test_monte_carlo_runs_successfully(sample_portfolio):
    """Test that the simulator runs and returns the expected metric dictionary."""
    np.random.seed(42)  # Deterministic results for CI
    # Use fewer simulations for fast CI/unit tests
    results = run_monte_carlo(sample_portfolio, years=10, num_simulations=100)
    
    assert "ruin_probability_pct" in results
    assert "median_end_value_inr" in results
    assert "percentiles" in results
    assert results["simulations_run"] == 100
    assert results["years_projected"] == 10
    
    # Verify percentile ordering: p5 <= p25 <= p50 <= p75 <= p95
    pct = results["percentiles"]
    assert pct["p5"] <= pct["p25"] <= pct["p50"] <= pct["p75"] <= pct["p95"]

def test_guaranteed_ruin():
    """Test a scenario mathematically guaranteed to fail quickly."""
    np.random.seed(42)
    # 1 million INR, spending 500k a month -> guaranteed ruin in ~2 months
    p = {
        "total_value_inr": 1_000_000,
        "monthly_expenses_inr": 500_000,
        "assets": [{"name": "CASH", "allocation_pct": 100}]
    }
    results = run_monte_carlo(p, years=5, num_simulations=100)
    assert results["ruin_probability_pct"] == 100.0
    
def test_guaranteed_survival():
    """Test a scenario mathematically guaranteed to survive."""
    np.random.seed(42)
    # 100 million INR, spending 10k a month, high yield -> guaranteed survival
    p = {
        "total_value_inr": 100_000_000,
        "monthly_expenses_inr": 10_000,
        "assets": [{"name": "NIFTY50", "allocation_pct": 100}]
    }
    results = run_monte_carlo(p, years=5, num_simulations=100)
    assert results["ruin_probability_pct"] == 0.0

def test_invalid_portfolio():
    """Test that invalid portfolio raises ValueError."""
    np.random.seed(42)
    with pytest.raises(ValueError, match="Invalid portfolio"):
        run_monte_carlo({"total_value_inr": 0, "assets": []})

# ═══════════════════════════════════════════════════════════
# Rebalancer Tests
# ═══════════════════════════════════════════════════════════

def test_rebalancer_caps_volatile_assets(sample_portfolio):
    """Test that BTC (30%, crash -80%) gets capped to 15%."""
    result = suggest_rebalance(sample_portfolio)
    
    assert len(result["changes"]) >= 1
    assert result["total_freed_pct"] == 15.0  # 30% -> 15% = freed 15%
    
    # BTC should be reduced to 15%
    rebalanced = result["rebalanced_portfolio"]
    btc = next(a for a in rebalanced["assets"] if a["name"] == "BTC")
    assert btc["allocation_pct"] == 15.0
    
    # Fixed Income should be added with 15%
    fi = next(a for a in rebalanced["assets"] if a["name"] == "FIXED_INCOME")
    assert fi["allocation_pct"] == 15.0

def test_rebalancer_no_changes_needed():
    """Test that a conservative portfolio triggers no rebalancing."""
    conservative = {
        "total_value_inr": 10_000_000,
        "monthly_expenses_inr": 50_000,
        "assets": [
            {"name": "NIFTY50", "allocation_pct": 50, "expected_crash_pct": -40},
            {"name": "GOLD", "allocation_pct": 30, "expected_crash_pct": -15},
            {"name": "CASH", "allocation_pct": 20, "expected_crash_pct": 0},
        ]
    }
    result = suggest_rebalance(conservative)
    assert len(result["changes"]) == 0
    assert result["total_freed_pct"] == 0.0

def test_rebalancer_preserves_portfolio_total(sample_portfolio):
    """Test that total allocation percentages are preserved after rebalancing."""
    result = suggest_rebalance(sample_portfolio)
    rebalanced = result["rebalanced_portfolio"]
    
    total = sum(a["allocation_pct"] for a in rebalanced["assets"])
    assert total == pytest.approx(100.0)

def test_rebalanced_portfolio_reduces_ruin(sample_portfolio):
    """Integration test: rebalanced portfolio should have lower ruin probability."""
    np.random.seed(42)
    
    original_results = run_monte_carlo(sample_portfolio, years=15, num_simulations=500)
    
    rebalance_data = suggest_rebalance(sample_portfolio)
    rebalanced = rebalance_data["rebalanced_portfolio"]
    
    np.random.seed(42)  # Same seed for fair comparison
    rebalanced_results = run_monte_carlo(rebalanced, years=15, num_simulations=500)
    
    # Rebalanced portfolio should have lower or equal ruin probability
    assert rebalanced_results["ruin_probability_pct"] <= original_results["ruin_probability_pct"]

# ═══════════════════════════════════════════════════════════
# CIO Memo Formatting Tests
# ═══════════════════════════════════════════════════════════

def test_cio_format_includes_key_data(sample_portfolio):
    """Test that the CIO prompt formatter includes all critical data."""
    results = {
        "ruin_probability_pct": 12.5,
        "median_end_value_inr": 45_000_000,
        "percentiles": {"p5": 0, "p25": 10_000_000, "p50": 45_000_000, "p75": 130_000_000, "p95": 500_000_000},
        "simulations_run": 10000,
        "years_projected": 30
    }
    
    formatted = format_simulation_for_cio(sample_portfolio, results)
    
    assert "10,000,000" in formatted  # Total value
    assert "80,000" in formatted      # Monthly expenses
    assert "12.50%" in formatted      # Ruin probability
    assert "BTC" in formatted         # Asset name
    assert "30 years" in formatted    # Projection horizon
