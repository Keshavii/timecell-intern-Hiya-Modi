import pytest
from task04_open_problem.stress_tester import run_monte_carlo

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

def test_monte_carlo_runs_successfully(sample_portfolio):
    """Test that the simulator runs and returns the expected metric dictionary."""
    # Use fewer simulations for fast CI/unit tests
    results = run_monte_carlo(sample_portfolio, years=10, num_simulations=100)
    
    assert "ruin_probability_pct" in results
    assert "median_end_value_inr" in results
    assert results["simulations_run"] == 100
    assert results["years_projected"] == 10

def test_guaranteed_ruin():
    """Test a scenario mathematically guaranteed to fail quickly."""
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
    # 100 million INR, spending 10k a month, high yield -> guaranteed survival
    p = {
        "total_value_inr": 100_000_000,
        "monthly_expenses_inr": 10_000,
        "assets": [{"name": "NIFTY50", "allocation_pct": 100}]
    }
    results = run_monte_carlo(p, years=5, num_simulations=100)
    assert results["ruin_probability_pct"] == 0.0
