import pytest
from task01_risk_calculator.risk_calculator import compute_risk_metrics
from task01_risk_calculator.scenarios import compute_multi_scenario

@pytest.fixture
def standard_portfolio():
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

def test_standard_portfolio(standard_portfolio):
    """Test the correctness of the mathematical calculation on the example portfolio."""
    metrics = compute_risk_metrics(standard_portfolio)
    
    # Mathematical breakdown:
    # 3M in BTC -> -80% -> 0.6M
    # 4M in NIFTY -> -40% -> 2.4M
    # 2M in GOLD -> -15% -> 1.7M
    # 1M in CASH -> 0% -> 1.0M
    # Total post-crash = 0.6 + 2.4 + 1.7 + 1.0 = 5.7M
    assert pytest.approx(metrics["post_crash_value"]) == 5_700_000
    
    # Runway: 5.7M / 80k = 71.25 months
    assert pytest.approx(metrics["runway_months"]) == 71.25
    
    # Ruin test: PASS (71.25 > 12)
    assert metrics["ruin_test"] == "PASS"
    
    # Largest risk asset: BTC (30 * |-80| = 2400) > NIFTY (40 * |-40| = 1600)
    assert metrics["largest_risk_asset"] == "BTC"
    
    # Concentration warning: None > 40% (40% is not strictly > 40%)
    assert metrics["concentration_warning"] is False

def test_empty_portfolio():
    """Test graceful handling of an empty portfolio."""
    assert compute_risk_metrics({}) == {}
    
    empty_assets = {
        "total_value_inr": 1_000_000,
        "monthly_expenses_inr": 50_000,
        "assets": []
    }
    metrics = compute_risk_metrics(empty_assets)
    assert metrics["post_crash_value"] == 1_000_000
    assert metrics["runway_months"] == 20.0

def test_100_percent_cash():
    """Test when the portfolio is completely insulated from crash."""
    p = {
        "total_value_inr": 1_000_000,
        "monthly_expenses_inr": 50_000,
        "assets": [{"name": "CASH", "allocation_pct": 100, "expected_crash_pct": 0}]
    }
    metrics = compute_risk_metrics(p)
    assert metrics["post_crash_value"] == 1_000_000
    assert metrics["runway_months"] == 20.0
    assert metrics["ruin_test"] == "PASS"
    assert metrics["concentration_warning"] is True

def test_zero_expenses():
    """Test handling of 0 expenses (should result in infinite runway)."""
    p = {
        "total_value_inr": 1_000_000,
        "monthly_expenses_inr": 0,
        "assets": [{"name": "CASH", "allocation_pct": 100, "expected_crash_pct": 0}]
    }
    metrics = compute_risk_metrics(p)
    assert metrics["runway_months"] == float('inf')
    assert metrics["ruin_test"] == "PASS"

def test_negative_allocation():
    """Test validation of invalid negative allocations."""
    p = {
        "total_value_inr": 1_000_000,
        "monthly_expenses_inr": 50_000,
        "assets": [{"name": "BTC", "allocation_pct": -10, "expected_crash_pct": -80}]
    }
    with pytest.raises(ValueError, match="Negative allocation"):
        compute_risk_metrics(p)

def test_all_crash_to_zero():
    """Test catastrophic crash where all value goes to zero."""
    p = {
        "total_value_inr": 1_000_000,
        "monthly_expenses_inr": 50_000,
        "assets": [{"name": "SHITCOIN", "allocation_pct": 100, "expected_crash_pct": -100}]
    }
    metrics = compute_risk_metrics(p)
    assert metrics["post_crash_value"] == 0
    assert metrics["runway_months"] == 0
    assert metrics["ruin_test"] == "FAIL"

def test_concentration_warning():
    """Test that concentration warning triggers exactly > 40%."""
    p = {
        "total_value_inr": 1_000_000,
        "monthly_expenses_inr": 50_000,
        "assets": [
            {"name": "NIFTY50", "allocation_pct": 40.1, "expected_crash_pct": -40},
            {"name": "GOLD", "allocation_pct": 59.9, "expected_crash_pct": -15}
        ]
    }
    metrics = compute_risk_metrics(p)
    assert metrics["concentration_warning"] is True

def test_multi_scenario(standard_portfolio):
    """Test the bonus multi-scenario analyzer."""
    multi = compute_multi_scenario(standard_portfolio)
    
    assert "worst_case" in multi
    assert "moderate_case" in multi
    
    # Moderate case should lose half as much value as the worst case
    assert multi["moderate_case"]["post_crash_value"] > multi["worst_case"]["post_crash_value"]
    
    # Runway should be longer in moderate scenario
    assert multi["moderate_case"]["runway_months"] > multi["worst_case"]["runway_months"]

def test_allocations_not_summing_to_100():
    """Test that the calculator handles portfolios where allocations don't sum to 100%."""
    p = {
        "total_value_inr": 1_000_000,
        "monthly_expenses_inr": 50_000,
        "assets": [
            {"name": "BTC", "allocation_pct": 20, "expected_crash_pct": -80},
            {"name": "CASH", "allocation_pct": 30, "expected_crash_pct": 0},
        ]
    }
    metrics = compute_risk_metrics(p)
    # BTC: 200k * 0.2 = 40k; CASH: 300k * 1.0 = 300k => 340k post-crash
    assert pytest.approx(metrics["post_crash_value"]) == 340_000
    assert metrics["runway_months"] == pytest.approx(6.8)
    assert metrics["ruin_test"] == "FAIL"  # 6.8 < 12

def test_single_asset_portfolio():
    """Test a portfolio with only one asset."""
    p = {
        "total_value_inr": 5_000_000,
        "monthly_expenses_inr": 100_000,
        "assets": [
            {"name": "NIFTY50", "allocation_pct": 100, "expected_crash_pct": -40},
        ]
    }
    metrics = compute_risk_metrics(p)
    # 5M * 0.6 = 3M post-crash
    assert pytest.approx(metrics["post_crash_value"]) == 3_000_000
    assert metrics["runway_months"] == pytest.approx(30.0)
    assert metrics["ruin_test"] == "PASS"
    assert metrics["largest_risk_asset"] == "NIFTY50"
    assert metrics["concentration_warning"] is True

