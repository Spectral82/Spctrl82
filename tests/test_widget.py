import pytest
from src.widget import mask_account_card, get_date


# Тесты для mask_account_card
@pytest.mark.parametrize(
    "input_data, expected_output",
    [
        ("1234567890123456", "1234 56** **** 3456"),  # номер карты
        ("1234567890", "**7890"),  # номер счёта
        ("1234 5678 9012 3456", "1234 56** **** 3456"),  # номер карты с пробелами
        ("1234-5678-9012-3456", "1234 56** **** 3456"),  # номер карты с дефисами
        ("9876543210", "**3210"),  # номер счёта
    ]
)
def test_mask_account_card(input_data, expected_output):
    assert mask_account_card(input_data) == expected_output


def test_mask_account_card_invalid():
    with pytest.raises(ValueError):
        mask_account_card("abcd")  # некорректный ввод
    with pytest.raises(ValueError):
        mask_account_card("")  # пустая строка


# Тесты для get_date
@pytest.mark.parametrize(
    "input_date, expected_output",
    [
        ("2023-01-01", "2023-01-01"),  # стандартный формат
        ("01/01/2023", "2023-01-01"),  # другой формат
        ("January 1, 2023", "2023-01-01"),  # текстовый формат
        ("2023.01.01", "2023-01-01"),  # альтернативный разделитель
    ]
)
def test_get_date_valid(input_date, expected_output):
    assert get_date(input_date) == expected_output


def test_get_date_invalid():
    with pytest.raises(ValueError):
        get_date("abcd")  # некорректная дата
    with pytest.raises(ValueError):
        get_date("")  # пустая строка
    with pytest.raises(ValueError):
        get_date("2023/01/01")  # неподдерживаемый формат
