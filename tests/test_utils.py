import json
from pathlib import Path
from typing import Any, Dict
from unittest.mock import patch

import pytest

from src.utils import get_transaction_amount_rub, read_transactions


class TestReadTransactions:
    """Тесты для read_transactions."""

    @pytest.fixture
    def temp_json_path(self, tmp_path: Path) -> Path:
        return tmp_path / "transactions.json"

    def test_valid_list_returns_list(self, temp_json_path: Path) -> None:
        data = [
            {"amount": 100, "currency": "RUB"},
            {"amount": 50, "currency": "USD"},
        ]
        temp_json_path.write_text(json.dumps(data), encoding="utf-8")

        result = read_transactions(str(temp_json_path))
        assert isinstance(result, list)
        assert len(result) == 2
        assert result == data

    def test_empty_file_returns_empty_list(self, temp_json_path: Path) -> None:
        temp_json_path.write_text("", encoding="utf-8")
        assert read_transactions(str(temp_json_path)) == []

    def test_file_not_found_returns_empty_list(self) -> None:
        assert read_transactions("/nonexistent/path/transactions.json") == []

    def test_invalid_json_returns_empty_list(self, temp_json_path: Path) -> None:
        temp_json_path.write_text("{ not valid json }", encoding="utf-8")
        assert read_transactions(str(temp_json_path)) == []

    def test_non_list_json_returns_empty_list(self, temp_json_path: Path) -> None:
        temp_json_path.write_text('{"total": 123}', encoding="utf-8")
        assert read_transactions(str(temp_json_path)) == []


class TestGetTransactionAmountRub:
    """Тесты для get_transaction_amount_rub."""

    @patch("src.utils.convert_currency")
    def test_rub_currency_returns_amount_as_float(self, mock_convert_currency: Any) -> None:
        transaction: Dict[str, Any] = {"amount": 150, "currency": "RUB"}
        result = get_transaction_amount_rub(transaction)

        mock_convert_currency.assert_not_called()
        assert result == 150.0
        assert isinstance(result, float)

    @patch("src.utils.convert_currency")
    def test_usd_currency_calls_convert_and_returns_multiplied(self, mock_convert_currency: Any) -> None:
        mock_convert_currency.return_value = 90.5

        transaction: Dict[str, Any] = {"amount": 100, "currency": "USD"}
        result = get_transaction_amount_rub(transaction)

        mock_convert_currency.assert_called_once_with("USD")
        assert result == 100 * 90.5
        assert isinstance(result, float)

    @patch("src.utils.convert_currency")
    def test_eur_currency_calls_convert_and_returns_multiplied(self, mock_convert_currency: Any) -> None:
        mock_convert_currency.return_value = 100.25
        transaction: Dict[str, Any] = {"amount": 3, "currency": "EUR"}
        result = get_transaction_amount_rub(transaction)

        mock_convert_currency.assert_called_once_with("EUR")
        assert result == pytest.approx(3 * 100.25)

    @patch("src.utils.convert_currency")
    def test_convert_currency_none_returns_zero(self, mock_convert_currency: Any) -> None:
        mock_convert_currency.return_value = None
        transaction: Dict[str, Any] = {"amount": 10, "currency": "USD"}
        result = get_transaction_amount_rub(transaction)
        assert result == 0.0

    def test_missing_amount_returns_zero(self) -> None:
        transaction: Dict[str, Any] = {"currency": "USD"}
        assert get_transaction_amount_rub(transaction) == 0.0

    def test_amount_not_numeric_returns_zero(self) -> None:
        transaction: Dict[str, Any] = {"amount": "not_a_number", "currency": "RUB"}
        assert get_transaction_amount_rub(transaction) == 0.0

    def test_unknown_currency_returns_zero(self) -> None:
        transaction: Dict[str, Any] = {"amount": 50, "currency": "JPY"}
        # convert_currency не должен вызываться для неизвестных валют
        with patch("src.utils.convert_currency") as mock_convert:
            result = get_transaction_amount_rub(transaction)
            mock_convert.assert_not_called()
            assert result == 0.0

    def test_currency_case_insensitive(self) -> None:
        with patch("src.utils.convert_currency") as mock_convert:
            mock_convert.return_value = 85.0
            transaction: Dict[str, Any] = {"amount": 4, "currency": "eur"}  # lower
            result = get_transaction_amount_rub(transaction)
            mock_convert.assert_called_once_with("EUR")
            assert result == pytest.approx(4 * 85.0)
