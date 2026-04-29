import pytest
from unittest.mock import patch, MagicMock
import requests
from task02_market_data.providers.base import AssetPrice
from task02_market_data.providers.coingecko_provider import CoinGeckoProvider
from task02_market_data.providers.yfinance_provider import YFinanceProvider
from task02_market_data.fetcher import fetch_all_prices

def test_coingecko_success():
    """Test CoinGecko provider successfully parses a valid API response."""
    provider = CoinGeckoProvider()
    with patch('requests.get') as mock_get:
        # Mock the HTTP response
        mock_response = MagicMock()
        mock_response.json.return_value = {"bitcoin": {"usd": 65000.0}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        price = provider.fetch_price("bitcoin")
        
        assert price.name == "BTC"
        assert price.price == 65000.0
        assert price.currency == "USD"
        assert price.source == "CoinGecko"
        assert price.error is None

def test_coingecko_network_error():
    """Test CoinGecko provider throws correct exception on network failure."""
    provider = CoinGeckoProvider()
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError("Network down")
        
        with pytest.raises(requests.exceptions.ConnectionError):
            provider.fetch_price("bitcoin")

def test_yfinance_success():
    """Test yfinance provider correctly parses fast_info."""
    provider = YFinanceProvider()
    with patch('yfinance.Ticker') as mock_ticker:
        # Mock the yfinance Ticker object
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.fast_info = {'last_price': 22500.0}
        mock_ticker.return_value = mock_ticker_instance
        
        price = provider.fetch_price("^NSEI")
        
        assert price.name == "NIFTY 50"
        assert price.price == 22500.0
        assert price.currency == "INR"
        assert price.source == "yfinance"
        assert price.error is None

def test_fetcher_retries_and_graceful_fail():
    """
    Test the main orchestrator's error handling:
    1. It should retry failed requests.
    2. It should NOT crash the script if a provider fails completely.
    3. It should return a graceful Error object.
    """
    # Patch time.sleep so the test runs instantly instead of waiting for retries
    with patch('time.sleep', return_value=None), \
         patch('task02_market_data.providers.coingecko_provider.CoinGeckoProvider.fetch_price') as mock_cg, \
         patch('task02_market_data.providers.yfinance_provider.YFinanceProvider.fetch_price') as mock_yf:
             
        # Make CoinGecko fail completely for both BTC and ETH
        mock_cg.side_effect = Exception("API completely down")
        
        # Make YFinance succeed
        mock_yf.return_value = AssetPrice(name="NIFTY", price=20000, currency="INR", source="yfinance")
        
        # Run the orchestrator
        results = fetch_all_prices()
        
        # We fetch 5 assets total in fetch_all_prices()
        assert len(results) == 5
        
        # CoinGecko failed: should have gracefully generated an error object
        btc_result = next(r for r in results if r.name == "BITCOIN")
        assert btc_result.error == "API Unavailable"
        assert btc_result.price == 0.0
        
        # yfinance succeeded
        nifty_result = next(r for r in results if r.name == "NIFTY")
        assert nifty_result.price == 20000.0
        assert nifty_result.error is None
        
        # Verify retries happened (BTC failed 3 times, ETH failed 3 times = 6 calls)
        assert mock_cg.call_count == 6
