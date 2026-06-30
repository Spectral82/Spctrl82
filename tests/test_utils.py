import json
from pathlib import Path
from typing import Any, Dict
from unittest.mock import patch

import pytest

from src.utils import get_transaction_amount_rub, read_transactions


class TestReadTransactions:
    """Набор тестов для функции read_transactions.

    Класс проверяет корректность работы функции чтения транзакций из JSON-файла:
    - возврат валидного списка при корректных данных;
    - обработку пустых файлов;
    - поведение при отсутствии файла;
    - реакцию на невалидный JSON;
    - обработку JSON, не содержащего список транзакций.
    """

    @pytest.fixture
    def temp_json_path(self, tmp_path: Path) -> Path:
        """Создаёт путь к временному JSON-файлу в директории tmp_path.

        Args:
            tmp_path (Path): объект Path, предоставляемый фикстурой pytest,
                указывающий на временную директорию для тестов.

        Returns:
            Path: путь к файлу transactions.json внутри временной директории.
        """
        return tmp_path / "transactions.json"

    def test_valid_list_returns_list(self, temp_json_path: Path) -> None:
        """Проверяет, что при валидном JSON со списком транзакций функция
        возвращает список той же длины и с теми же данными.

        Сценарий:
            - Создаётся JSON-файл со списком из двух транзакций.
            - Вызывается read_transactions с путём к файлу.
            - Проверяется, что результат — список, его длина равна 2,
              и содержимое совпадает с исходными данными.
        """
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
        """Проверяет, что пустой JSON-файл приводит к возврату пустого списка.

        Сценарий:
            - Файл создаётся пустым.
            - Вызывается read_transactions.
            - Ожидается возврат пустого списка [].
        """
        temp_json_path.write_text("", encoding="utf-8")
        assert read_transactions(str(temp_json_path)) == []

    def test_file_not_found_returns_empty_list(self) -> None:
        """Проверяет, что при отсутствии файла функция возвращает пустой список.

        Сценарий:
            - Передаётся несуществующий путь.
            - Ожидается, что функция не выбросит исключение и вернёт [].
        """
        assert read_transactions("/nonexistent/path/transactions.json") == []

    def test_invalid_json_returns_empty_list(self, temp_json_path: Path) -> None:
        """Проверяет, что невалидный JSON приводит к возврату пустого списка.

        Сценарий:
            - В файл записывается строка, не являющаяся корректным JSON.
            - Вызывается read_transactions.
            - Ожидается возврат [].
        """
        temp_json_path.write_text("{ not valid json }", encoding="utf-8")
        assert read_transactions(str(temp_json_path)) == []

    def test_non_list_json_returns_empty_list(self, temp_json_path: Path) -> None:
        """Проверяет, что JSON, не представляющий собой список, приводит
        к возврату пустого списка.

        Сценарий:
            - В файл записывается JSON-объект (не список).
            - Вызывается read_transactions.
            - Ожидается возврат [].
        """
        temp_json_path.write_text('{"total": 123}', encoding="utf-8")
        assert read_transactions(str(temp_json_path)) == []


class TestGetTransactionAmountRub:
    """Набор тестов для функции get_transaction_amount_rub.

    Класс проверяет конвертацию суммы транзакции в рубли:
    - корректную обработку валюты RUB без вызова конвертера;
    - вызов convert_currency и расчёт для USD/EUR;
    - граничные случаи: None от конвертера, отсутствие amount,
      нечисловое значение amount, неизвестная валюта.
    """

    @patch("src.utils.convert_currency")
    def test_rub_currency_returns_amount_as_float(self, mock_convert_currency: Any) -> None:
        """Проверяет, что для валюты RUB функция возвращает сумму как float
        и не вызывает convert_currency.

        Сценарий:
            - Транзакция с currency="RUB" и amount=150.
            - Ожидаем, что convert_currency не был вызван.
            - Результат должен быть 150.0 типа float.
        """
        transaction: Dict[str, Any] = {"amount": 150, "currency": "RUB"}
        result = get_transaction_amount_rub(transaction)

        mock_convert_currency.assert_not_called()
        assert result == 150.0
        assert isinstance(result, float)

    @patch("src.utils.convert_currency")
    def test_usd_currency_calls_convert_and_returns_multiplied(self, mock_convert_currency: Any) -> None:
        """Проверяет, что для USD функция вызывает convert_currency("USD")
        и возвращает amount * курс.

        Сценарий:
            - Курс для USD задан как 90.5.
            - Транзакция: amount=100, currency="USD".
            - Ожидаем один вызов convert_currency с аргументом "USD".
            - Результат: 100 * 90.5 как float.
        """
        mock_convert_currency.return_value = 90.5

        transaction: Dict[str, Any] = {"amount": 100, "currency": "USD"}
        result = get_transaction_amount_rub(transaction)

        mock_convert_currency.assert_called_once_with("USD")
        assert result == 100 * 90.5
        assert isinstance(result, float)

    @patch("src.utils.convert_currency")
    def test_eur_currency_calls_convert_and_returns_multiplied(self, mock_convert_currency: Any) -> None:
        """Проверяет, что для EUR функция вызывает convert_currency("EUR")
        и возвращает amount * курс с допустимой погрешностью.

        Сценарий:
            - Курс для EUR задан как 100.25.
            - Транзакция: amount=3, currency="EUR".
            - Ожидаем один вызов convert_currency с аргументом "EUR".
            - Результат проверяется через pytest.approx.
        """
        mock_convert_currency.return_value = 100.25
        transaction: Dict[str, Any] = {"amount": 3, "currency": "EUR"}
        result = get_transaction_amount_rub(transaction)

        mock_convert_currency.assert_called_once_with("EUR")
        assert result == pytest.approx(3 * 100.25)

    @patch("src.utils.convert_currency")
    def test_convert_currency_none_returns_zero(self, mock_convert_currency: Any) -> None:
        """Проверяет, что если convert_currency возвращает None,
        функция возвращает 0.0.

        Сценарий:
            - convert_currency настроен на возврат None.
            - Транзакция: amount=10, currency="USD".
            - Ожидаемый результат: 0.0.
        """
        mock_convert_currency.return_value = None
        transaction: Dict[str, Any] = {"amount": 10, "currency": "USD"}
        result = get_transaction_amount_rub(transaction)
        assert result == 0.0

    def test_missing_amount_returns_zero(self) -> None:
        """Проверяет, что при отсутствии ключа "amount" функция возвращает 0.0.

        Сценарий:
            - Транзакция содержит только "currency".
            - Ожидаемый результат: 0.0.
        """
        transaction: Dict[str, Any] = {"currency": "USD"}
        assert get_transaction_amount_rub(transaction) == 0.0

    def test_amount_not_numeric_returns_zero(self) -> None:
        """Проверяет, что нечисловое значение "amount" приводит к возврату 0.0.

        Сценарий:
            - "amount" задан строкой "not_a_number".
            - Ожидаемый результат: 0.0.
        """
        transaction: Dict[str, Any] = {"amount": "not_a_number", "currency": "RUB"}
        assert get_transaction_amount_rub(transaction) == 0.0

    def test_unknown_currency_returns_zero(self) -> None:
        """Проверяет, что неизвестная валюта (например, JPY) приводит
        к возврату 0.0 без вызова convert_currency.

        Сценарий:
            - Транзакция: amount=50, currency="JPY".
            - Ожидаем, что convert_currency не будет вызван.
            - Результат: 0.0.
        """
        transaction: Dict[str, Any] = {"amount": 50, "currency": "JPY"}
        with patch("src.utils.convert_currency") as mock_convert:
            result = get_transaction_amount_rub(transaction)
            mock_convert.assert_not_called()
            assert result == 0.0
