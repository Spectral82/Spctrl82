import os
from unittest.mock import MagicMock, patch

from src.external_api import convert_currency


class TestConvertCurrency:
    @patch("src.external_api.requests.get")
    def test_success_returns_float(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {
            "rates": {"RUB": 90.5},
        }
        mock_get.return_value = mock_resp

        with patch.dict(os.environ, {"EXCHANGE_RATES_API_KEY": "test-key"}):
            result = convert_currency("USD")

        assert result == 90.5
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs["params"]["access_key"] == "test-key"
        assert kwargs["params"]["base"] == "USD"
        assert kwargs["params"]["symbols"] == "RUB"

    @patch("src.external_api.requests.get")
    def test_missing_api_key_returns_none(self, mock_get: MagicMock) -> None:
        # Убираем переменную окружения
        with patch.dict(os.environ, {}, clear=True):
            result = convert_currency("EUR")

        assert result is None
        mock_get.assert_not_called()

    @patch("src.external_api.requests.get")
    def test_request_exception_returns_none(self, mock_get: MagicMock) -> None:
        mock_get.side_effect = Exception("Network error")

        with patch.dict(os.environ, {"EXCHANGE_RATES_API_KEY": "test-key"}):
            result = convert_currency("EUR")

        assert result is None

    @patch("src.external_api.requests.get")
    def test_http_error_returns_none(self, mock_get: MagicMock) -> None:
        from requests.exceptions import HTTPError

        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = HTTPError("401 Unauthorized")
        mock_get.return_value = mock_resp

        with patch.dict(os.environ, {"EXCHANGE_RATES_API_KEY": "test-key"}):
            result = convert_currency("EUR")

        assert result is None

    @patch("src.external_api.requests.get")
    def test_invalid_json_returns_none(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        # Эмулируем невалидный JSON: raise ValueError при .json()
        mock_resp.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_resp

        with patch.dict(os.environ, {"EXCHANGE_RATES_API_KEY": "test-key"}):
            result = convert_currency("EUR")

        assert result is None

    @patch("src.external_api.requests.get")
    def test_missing_rates_returns_none(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {}  # нет поля rates
        mock_get.return_value = mock_resp

        with patch.dict(os.environ, {"EXCHANGE_RATES_API_KEY": "test-key"}):
            result = convert_currency("EUR")

        assert result is None

    @patch("src.external_api.requests.get")
    def test_missing_rub_rate_returns_none(self, mock_get: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {"rates": {"USD": 80.0}}  # нет RUB
        mock_get.return_value = mock_resp

        with patch.dict(os.environ, {"EXCHANGE_RATES_API_KEY": "test-key"}):
            result = convert_currency("EUR")

        assert result is None
