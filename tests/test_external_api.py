import os
from unittest.mock import MagicMock, patch
from src.external_api import convert_currency


class TestConvertCurrency:
    """Тестовый класс для проверки функции convert_currency из модуля external_api.

    Класс содержит набор тестов, покрывающих различные сценарии работы функции:
      - успешный запрос и получение курса;
      - отсутствие API‑ключа;
      - исключения при выполнении HTTP‑запроса;
      - ошибки HTTP‑статусов;
      - невалидный JSON‑ответ;
      - отсутствие ожидаемых данных в ответе (поля rates или курса RUB).
    """

    @patch("src.external_api.requests.get")
    def test_success_returns_float(self, mock_get: MagicMock) -> None:
        """Тест успешного получения курса валюты.

        Проверяет, что при корректном ответе API функция возвращает float
        со значением курса RUB. Также проверяется, что запрос был выполнен
        ровно один раз и с правильными параметрами: access_key (из переменной
        окружения), base (запрашиваемая валюта) и symbols (RUB).

        Args:
            mock_get: Мок-объект для requests.get, используемый для эмуляции
                      HTTP‑запроса.
        """
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
        """Тест поведения функции при отсутствии API‑ключа в переменных окружения.

        Проверяется, что при отсутствии переменной EXCHANGE_RATES_API_KEY
        функция не выполняет HTTP‑запрос и возвращает None.

        Args:
            mock_get: Мок-объект для requests.get, который не должен быть вызван.
        """
        # Убираем переменную окружения
        with patch.dict(os.environ, {}, clear=True):
            result = convert_currency("EUR")
            assert result is None
            mock_get.assert_not_called()

    @patch("src.external_api.requests.get")
    def test_request_exception_returns_none(self, mock_get: MagicMock) -> None:
        """Тест обработки исключения при выполнении запроса.

        Проверяется, что при возникновении любого исключения во время выполнения
        HTTP‑запроса функция корректно обрабатывает ошибку и возвращает None,
        не прерывая работу программы.

        Args:
            mock_get: Мок-объект для requests.get, настроенный на выброс исключения.
        """
        mock_get.side_effect = Exception("Network error")

        with patch.dict(os.environ, {"EXCHANGE_RATES_API_KEY": "test-key"}):
            result = convert_currency("EUR")
            assert result is None

    @patch("src.external_api.requests.get")
    def test_http_error_returns_none(self, mock_get: MagicMock) -> None:
        """Тест обработки HTTP‑ошибок (например, 401 Unauthorized).

        Проверяется, что при получении HTTP‑ошибки (через raise_for_status)
        функция корректно обрабатывает ситуацию и возвращает None вместо
        проброса исключения.

        Args:
            mock_get: Мок-объект для requests.get с эмуляцией HTTPError.
        """
        from requests.exceptions import HTTPError

        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = HTTPError("401 Unauthorized")
        mock_get.return_value = mock_resp

        with patch.dict(os.environ, {"EXCHANGE_RATES_API_KEY": "test-key"}):
            result = convert_currency("EUR")
            assert result is None

    @patch("src.external_api.requests.get")
    def test_invalid_json_returns_none(self, mock_get: MagicMock) -> None:
        """Тест обработки невалидного JSON‑ответа от API.

        Проверяется, что при ошибке парсинга JSON (или при ответе, который нельзя
        преобразовать в ожидаемую структуру) функция корректно обрабатывает
        ситуацию и возвращает None, а не пробрасывает исключение.

        Args:
            mock_get: Мок-объект для requests.get, возвращающий ответ,
                      при вызове .json() которого будет выброшено исключение.
        """
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_resp

        with patch.dict(os.environ, {"EXCHANGE_RATES_API_KEY": "test-key"}):
            result = convert_currency("EUR")
            assert result is None

    @patch("src.external_api.requests.get")
    def test_missing_rates_field_returns_none(self, mock_get: MagicMock) -> None:
        """Тест обработки ответа без ожидаемого поля 'rates'.

        Проверяется, что если в ответе API отсутствует поле 'rates' (или оно не
        содержит ожидаемую структуру), функция возвращает None, вместо попытки
        обратиться к несуществующим данным.

        Args:
            mock_get: Мок-объект для requests.get, возвращающий JSON без поля rates.
        """
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {
            "other_data": "some value"
        }
        mock_get.return_value = mock_resp

        with patch.dict(os.environ, {"EXCHANGE_RATES_API_KEY": "test-key"}):
            result = convert_currency("EUR")
            assert result is None

    @patch("src.external_api.requests.get")
    def test_missing_rub_rate_returns_none(self, mock_get: MagicMock) -> None:
        """Тест обработки ситуации, когда в rates нет курса для RUB.

        Проверяется, что если поле rates присутствует, но в нём нет ключа 'RUB',
        функция возвращает None, а не выбрасывает KeyError.

        Args:
            mock_get: Мок-объект для requests.get, возвращающий rates без RUB.
        """
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {
            "rates": {"USD": 1.0, "EUR": 0.85}
        }
        mock_get.return_value = mock_resp

        with patch.dict(os.environ, {"EXCHANGE_RATES_API_KEY": "test-key"}):
            result = convert_currency("EUR")
            assert result is None