import pytest

from src.generators import card_number_generator, filter_by_currency, transaction_descriptions


@pytest.fixture
def sample_transactions():
    """
    Фикстура для предоставления набора тестовых транзакций.

    Возвращает список словарей, каждый из которых представляет транзакцию
    со следующими полями: id, state, date, operationAmount, description, from, to.

    Returns:
        List[Dict[str, Any]]: список тестовых транзакций для использования в тестах.
    """
    return [
        {
            "id": 939719570,
            "state": "EXECUTED",
            "date": "2018-06-30T02:08:58.425572",
            "operationAmount": {"amount": "9824.07", "currency": {"name": "USD", "code": "USD"}},
            "description": "Перевод организации",
            "from": "Счет 75106830613657916952",
            "to": "Счет 11776614605963066702",
        },
        {
            "id": 142264268,
            "state": "EXECUTED",
            "date": "2019-04-04T23:20:05.206878",
            "operationAmount": {"amount": "79114.93", "currency": {"name": "EUR", "code": "EUR"}},
            "description": "Перевод со счета на счет",
            "from": "Счет 19708645243227258542",
            "to": "Счет 75651667383060284188",
        },
        {
            "id": 54321,
            "state": "EXECUTED",
            "date": "2020-01-01T12:00:00.000000",
            "operationAmount": {"amount": "5000.00", "currency": {"name": "USD", "code": "USD"}},
            "description": "Оплата услуг",
            "from": "Карта 1234567890123456",
            "to": "Счет 9876543210987654",
        },
    ]


class TestFilterByCurrency:
    """Тестовый класс для проверки функциональности filter_by_currency."""

    @pytest.mark.parametrize("currency_code,expected_count", [("USD", 2), ("EUR", 1), ("RUB", 0)])
    def test_filter_by_currency(self, sample_transactions, currency_code, expected_count):
        """
        Проверка фильтрации транзакций по коду валюты.

        Проверяет, что функция filter_by_currency корректно возвращает транзакции
        с указанным кодом валюты и их количество соответствует ожидаемому.

        Args:
            sample_transactions: фикстура с тестовыми транзакциями.
            currency_code (str): код валюты для фильтрации (например, "USD").
            expected_count (int): ожидаемое количество транзакций в заданной валюте.
        """
        filtered = list(filter_by_currency(sample_transactions, currency_code))
        assert len(filtered) == expected_count

    def test_filter_empty_list(self):
        """
        Проверка обработки пустого списка транзакций.

        Убеждается, что при передаче пустого списка функция возвращает пустой результат.
        """
        result = list(filter_by_currency([], "USD"))
        assert result == []

    def test_filter_no_matching_currency(self, sample_transactions):
        """
        Проверка случая, когда нет транзакций в заданной валюте.

        Проверяет, что если в списке транзакций нет операций в указанной валюте,
        функция возвращает пустой список.

        Args:
            sample_transactions: фикстура с тестовыми транзакциями.
        """
        result = list(filter_by_currency(sample_transactions, "GBP"))
        assert result == []


class TestTransactionDescriptions:
    """Тестовый класс для проверки функциональности transaction_descriptions."""

    def test_transaction_descriptions_normal(self, sample_transactions):
        """
        Проверка корректного возврата описаний транзакций.

        Убеждается, что функция transaction_descriptions корректно извлекает
        описания из стандартного набора транзакций.

        Args:
            sample_transactions: фикстура с тестовыми транзакциями.
        """
        descriptions = list(transaction_descriptions(sample_transactions))
        expected = ["Перевод организации", "Перевод со счета на счет", "Оплата услуг"]
        assert descriptions == expected

    def test_transaction_descriptions_empty_list(self):
        """
        Проверка работы с пустым списком транзакций.

        Гарантирует, что при пустом входном списке функция возвращает пустой список описаний.
        """
        result = list(transaction_descriptions([]))
        assert result == []

    def test_transaction_descriptions_missing_description(self):
        """
        Проверка обработки транзакций без поля description.

        Проверяет поведение функции, если некоторые транзакции не содержат
        поля description: в таком случае должно возвращаться пустое значение
        для отсутствующего описания.
        """
        transactions = [
            {"id": 1, "description": "Первая операция"},
            {"id": 2},  # Нет поля description
            {"id": 3, "description": "Третья операция"},
        ]
        result = list(transaction_descriptions(transactions))
        assert result == ["Первая операция", "", "Третья операция"]


class TestCardNumberGenerator:
    """Тестовый класс для проверки функциональности card_number_generator."""

    @pytest.mark.parametrize(
        "start, end, expected_numbers",
        [
            (1, 3, ["0000 0000 0000 0001", "0000 0000 0000 0002", "0000 0000 0000 0003"]),
            (
                9999999999999997,
                9999999999999999,
                ["9999 9999 9999 9997", "9999 9999 9999 9998", "9999 9999 9999 9999"],
            ),
        ],
    )
    def test_card_number_generator_range(self, start, end, expected_numbers):
        """
        Проверка генерации номеров карт в заданном диапазоне.

        Тестирует, что card_number_generator корректно формирует номера карт
        в указанном диапазоне от start до end включительно, с форматированием
        в виде четырёх групп по 4 цифры, разделённых пробелами.

        Args:
            start (int): начальное число для генерации номеров карт.
            end (int): конечное число для генерации номеров карт (включительно).
            expected_numbers (List[str]): ожидаемый список сгенерированных номеров карт.
        """
        generator = card_number_generator(start, end)
        result = list(generator)
        assert result == expected_numbers
