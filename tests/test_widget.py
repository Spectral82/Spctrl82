import pytest
from src.widget import get_date, mask_account_card


class TestMaskAccountCard:
    """Тестовый класс для проверки функции mask_account_card."""

    @pytest.mark.parametrize(
        "input_data, expected_output",
        [
            ("1234567890123456", "1234 56** **** 3456"),  # номер карты
            ("12345678901234567890", "**7890"),  # номер счёта (20 цифр)
            ("1234 5678 9012 3456", "1234 56** **** 3456"),  # карта с пробелами
            ("1234-5678-9012-3456", "1234 56** **** 3456"),  # карта с дефисами
            ("98765432101234567890", "**7890"),  # счёт с 20 цифрами
        ],
    )
    def test_mask_account_card(self, input_data: str, expected_output: str) -> None:
        """
        Проверяет корректность маскирования номеров карт и счетов.

        Тестируются различные форматы входных данных:
        - стандартный 16‑значный номер карты;
        - 20‑значный номер счёта;
        - номера с разделителями (пробелы, дефисы).

        :param input_data: Исходная строка с номером карты или счёта.
        :param expected_output: Ожидаемый замаскированный результат.
        """
        assert mask_account_card(input_data) == expected_output

    def test_mask_account_card_invalid(self) -> None:
        """
        Проверяет, что функция mask_account_card корректно обрабатывает
        некорректные входные данные, выбрасывая ValueError.

        Тестируемые случаи:
        - нечисловая строка;
        - пустая строка;
        - слишком короткий номер.
        """
        with pytest.raises(ValueError):
            mask_account_card("abcd")  # некорректный ввод

        with pytest.raises(ValueError):
            mask_account_card("")  # пустая строка

        with pytest.raises(ValueError):
            mask_account_card("123")  # слишком короткий номер


class TestGetDate:
    """Тестовый класс для проверки функции get_date."""

    @pytest.mark.parametrize(
        "input_date, expected_output",
        [
            ("2023-01-01T00:00:00", "2023-01-01"),
            ("2023-01-01", "2023-01-01"),  # уже в нужном формате
            ("01/01/2023", "2023-01-01"),  # тест для другого формата
            ("January 1, 2023", "2023-01-01"),  # тест для текстового формата
        ],
    )
    def test_get_date_valid(self, input_date: str, expected_output: str) -> None:
        """
        Проверяет корректное преобразование различных форматов даты
        в стандартный формат YYYY-MM-DD.

        Поддерживаемые форматы на входе:
        - ISO 8601 с временем;
        - ISO 8601 без времени;
        - MM/DD/YYYY;
        - текстовое представление (например, «January 1, 2023»).

        :param input_date: Исходная строка с датой в одном из поддерживаемых форматов.
        :param expected_output: Ожидаемая дата в формате YYYY-MM-DD.
        """
        assert get_date(input_date) == expected_output

    def test_get_date_invalid(self) -> None:
        """
        Проверяет, что функция get_date корректно обрабатывает
        некорректные входные данные, выбрасывая ValueError.

        Тестируемые случаи:
        - строка, не являющаяся датой;
        - пустая строка.
        """
        with pytest.raises(ValueError):
            get_date("invalid-date")

        with pytest.raises(ValueError):
            get_date("")  # пустая строка