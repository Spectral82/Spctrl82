import pytest

from src.generators import card_number_generator, filter_by_currency, transaction_descriptions


# Фикстура с тестовыми транзакциями
@pytest.fixture
def sample_transactions():
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


# Тесты для filter_by_currency


class TestFilterByCurrency:

    @pytest.mark.parametrize("currency_code,expected_count", [("USD", 2), ("EUR", 1), ("RUB", 0)])
    def test_filter_by_currency(self, sample_transactions, currency_code, expected_count):
        """Проверка фильтрации транзакций по коду валюты."""
        filtered = list(filter_by_currency(sample_transactions, currency_code))
        assert len(filtered) == expected_count

    def test_filter_empty_list(self):
        """Проверка обработки пустого списка транзакций."""
        result = list(filter_by_currency([], "USD"))
        assert result == []

    def test_filter_no_matching_currency(self, sample_transactions):
        """Проверка случая, когда нет транзакций в заданной валюте."""
        result = list(filter_by_currency(sample_transactions, "GBP"))
        assert result == []


# Тесты для transaction_descriptions


class TestTransactionDescriptions:

    def test_transaction_descriptions_normal(self, sample_transactions):
        """Проверка корректного возврата описаний транзакций."""
        descriptions = list(transaction_descriptions(sample_transactions))
        expected = ["Перевод организации", "Перевод со счета на счет", "Оплата услуг"]
        assert descriptions == expected

    def test_transaction_descriptions_empty_list(self):
        """Проверка работы с пустым списком транзакций."""
        result = list(transaction_descriptions([]))
        assert result == []

    def test_transaction_descriptions_missing_description(self):
        """Проверка обработки транзакций без поля description."""
        transactions = [
            {"id": 1, "description": "Первая операция"},
            {"id": 2},  # Нет поля description
            {"id": 3, "description": "Третья операция"},
        ]
        result = list(transaction_descriptions(transactions))
        assert result == ["Первая операция", "", "Третья операция"]

    # Тесты для card_number_generator
    class TestCardNumberGenerator:
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
            generator = card_number_generator(start, end)
            result = list(generator)
            assert result == expected_numbers

    def test_card_number_format(self):
        """Проверка формата номера карты"""
        generator = card_number_generator(123456789012345, 123456789012345)
        result = next(generator)
        assert len(result) == 19  # 16 цифр + 3 пробела
        assert result.count(" ") == 3  # Ровно 3 пробела
        assert all(part.isdigit() for part in result.split())  # Все части — цифры

    def test_card_number_generator_edge_cases(self):
        # Тестируем минимальный допустимый start
        generator = card_number_generator(1, 1)
        result = list(generator)
        assert result == ["0000 0000 0000 0001"]

        # Тестируем пустой диапазон
        generator = card_number_generator(5, 3)
        result = list(generator)
        assert result == []

    def test_card_number_generator_empty_range(self):
        """Тест для пустого диапазона (start > end)."""
        result = list(card_number_generator(10, 5))
        assert result == []

    def test_card_number_generator_valid_range(self):
        """Тест для корректного диапазона."""
        result = list(card_number_generator(5, 5))
        expected = ["0000 0000 0000 0005"]
        assert result == expected

    def test_card_number_generator_multiple_numbers(self):
        generator = card_number_generator(1000, 1002)
        result = list(generator)
        expected = ["0000 0000 0000 1000", "0000 0000 0000 1001", "0000 0000 0000 1002"]
        assert result == expected

    @pytest.mark.parametrize(
        "start, end",
        [
            (0, 1),
            (-1, 5),
            (1, 0),
            (1, -5),
        ],
    )
    def test_card_number_generator_invalid_range(self, start, end):
        with pytest.raises(ValueError):
            list(card_number_generator(start, end))
