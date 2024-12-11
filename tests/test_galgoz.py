import pytest
from unittest.mock import patch, MagicMock
from galgoz import Galgoz, Config

def test_config_initialization():
    with patch.dict('os.environ', {'OANDA_PRACTICE_ACCOUNT_ID': 'test_account_id', 'OANDA_PRACTICE_ACCESS_TOKEN': 'test_access_token'}):
        config = Config()
        assert config.account_id == 'test_account_id'
        assert config.access_token == 'test_access_token'

def test_galgoz_initialization():
    with patch.dict('os.environ', {'OANDA_PRACTICE_ACCOUNT_ID': 'test_account_id', 'OANDA_PRACTICE_ACCESS_TOKEN': 'test_access_token'}):
        galgoz = Galgoz()
        assert galgoz.config.account_id == 'test_account_id'
        assert galgoz.config.access_token == 'test_access_token'

def test_galgoz_initialization_live_account():
    with patch.dict('os.environ', {'OANDA_LIVE_ACCOUNT_ID': 'live_account_id', 'OANDA_LIVE_ACCESS_TOKEN': 'live_access_token'}):
        galgoz = Galgoz(use_live_account=True)
        assert galgoz.config.account_id == 'live_account_id'
        assert galgoz.config.access_token == 'live_access_token'

@patch('oandapyV20.API')
@patch('oandapyV20.endpoints.accounts.AccountInstruments')
def test_fetch_instruments(mock_account_instruments, mock_api):
    mock_client = MagicMock()
    mock_api.return_value = mock_client
    mock_response = {
        "instruments": [
            {"name": "EUR_USD"},
            {"name": "USD_JPY"}
        ]
    }
    mock_client.request.return_value = mock_response

    with patch.dict('os.environ', {'OANDA_PRACTICE_ACCOUNT_ID': 'test_account_id', 'OANDA_PRACTICE_ACCESS_TOKEN': 'test_access_token'}):
        galgoz = Galgoz()
        instruments = galgoz.fetch_instruments()

    assert instruments == ["EUR_USD", "USD_JPY"]
    mock_account_instruments.assert_called_once_with(accountID='test_account_id')
    mock_client.request.assert_called_once()

@patch('oandapyV20.API')
@patch('oandapyV20.endpoints.accounts.AccountInstruments')
def test_fetch_instruments_with_metadata(mock_account_instruments, mock_api):
    mock_client = MagicMock()
    mock_api.return_value = mock_client
    mock_response = {
        "instruments": [
            {"name": "EUR_USD", "type": "currency", "displayName": "Euro/US Dollar"},
            {"name": "USD_JPY", "type": "currency", "displayName": "US Dollar/Japanese Yen"}
        ]
    }
    mock_client.request.return_value = mock_response

    with patch.dict('os.environ', {'OANDA_PRACTICE_ACCOUNT_ID': 'test_account_id', 'OANDA_PRACTICE_ACCESS_TOKEN': 'test_access_token'}):
        galgoz = Galgoz()
        instruments = galgoz.fetch_instruments(fetch_all_metadata=True)

    assert instruments == mock_response
    mock_account_instruments.assert_called_once_with(accountID='test_account_id')
    mock_client.request.assert_called_once()