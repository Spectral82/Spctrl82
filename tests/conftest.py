from typing import Any, Dict, List
import pytest

from src.masks import mask_account_number, mask_card_number
from src.processing import filter_by_state, sort_by_date


@pytest.fixture
def sample_data() -> List[Dict[str, Any]]:
    """
    Фикстура для предоставления тестовых данных с полем 'state'.

    Возвращает список словарей с тестовыми операциями, содержащими поля:
        - id: уникальный идентификатор операции (int);
        - state: статус операции (str), например, 'active', 'inactive'.

    Используется в тестах для проверки фильтрации операций по статусу.

    Returns:
        List[Dict[str, Any]]: список тестовых операций.
    """
    return [
        {"id": 1, "state": "active"},
        {"id": 2, "state": "inactive"},
        {"id": 3, "state": "active"},
    ]


@pytest.fixture
def date_data() -> List[Dict[str, Any]]:
    """
    Фикстура для предоставления тестовых данных с полем 'date'.

    Возвращает список словарей с тестовыми операциями, содержащими поля:
        - id: уникальный идентификатор операции (int);
        - date: дата операции в формате YYYY-MM-DD (str).

    Может использоваться в тестах для проверки сортировки операций по дате.

    Returns:
        List[Dict[str, Any]]: список тестовых операций с датами.
    """
    return [
        {"id": 1, "date": "2023-01-15"},
        {"id": 2, "date": "2023-03-20"},
        {"id": 3, "date": "2022-12-01"},
    ]


@pytest.mark.parametrize(
    "card_number, expected_output",
    [
        ("1234567890123456", "1234 56** **** 3456"),
        ("1234 5678 9012 3456", "1234 56** **** 3456"),
        ("1234-5678-9012-3456", "1234 56** **** 3456"),
        ("0000000000000000", "0000 00** **** 0000"),
    ],
)
def test_mask_card_number(card_number: str, expected_output: str) -> None:
    """
    Тест функции mask_card_number.

    Проверяет корректность маскирования номера банковской карты:
        - первые 4 цифры остаются видимыми;
        - далее идут 2 видимые цифры, затем блок '** ****';
        - в конце — последние 4 цифры.

    Тестирует разные форматы входных данных (без разделителей, с пробелами, с дефисами).

    Args:
        card_number (str): входной номер карты в любом поддерживаемом формате.
        expected_output (str): ожидаемый результат маскирования.
    """
    assert mask_card_number(card_number) == expected_output


@pytest.mark.parametrize(
    "account_number, expected_output",
    [
        ("1234567890123456", "**3456"),
        ("1234 5678 9012 3456", "**3456"),
        ("1234", "**1234"),
    ],
)
def test_mask_account_number(account_number: str, expected_output: str) -> None:
    """
    Тест функции mask_account_number.

    Проверяет корректность маскирования номера счёта:
        - отображаются только последние 4 цифры;
        - перед ними ставится префикс '**'.

    Тестирует разные форматы входных данных и короткие номера.

    Args:
        account_number (str): входной номер счёта в любом поддерживаемом формате.
        expected_output (str): ожидаемый результат маскирования.
    """
    assert mask_account_number(account_number) == expected_output


@pytest.mark.parametrize(
    "state, expected_output",
    [
        (
            "active",
            [
                {"id": 1, "state": "active"},
                {"id": 3, "state": "active"},
            ],
        ),
        ("inactive", [{"id": 2, "state": "inactive"}]),
        ("pending", []),
    ],
)
def test_filter_by_state(
    state: str,
    sample_data: List[Dict[str, Any]],
    expected_output: List[Dict[str, Any]],
) -> None:
    """
    Тест функции filter_by_state.

    Проверяет, что функция корректно фильтрует список операций по значению ключа 'state'.

    Аргумент sample_data автоматически подставляется фикстурой.

    Args:
        state (str): значение статуса для фильтрации (например, 'active').
        sample_data (List[Dict[str, Any]]): список операций для фильтрации.
        expected_output (List[Dict[str, Any]]): ожидаемый отфильтрованный список.
    """
    assert filter_by_state(sample_data, state) == expected_output


@pytest.mark.parametrize(
    "input_data, expected_output",
    [
        (
            [
                {"id": 1, "date": "2023-01-01"},
                {"id": 2, "date": "2022-12-31"},
            ],
            [
                {"id": 1, "date": "2023-01-01"},
                {"id": 2, "date": "2022-12-31"},
            ],
        ),
        (
            [
                {"id": 1, "date": "invalid-date"},
                {"id": 2, "date": "2023-01-01"},
            ],
            [
                {"id": 2, "date": "2023-01-01"},
                {"id": 1, "date": "invalid-date"},
            ],
        ),
    ],
)
def test_sort_by_date(
    input_data: List[Dict[str, Any]],
    expected_output: List[Dict[str, Any]],
) -> None:
    """
    Тест функции sort_by_date.

    Проверяет корректность сортировки списка операций по полю 'date' (в формате YYYY-MM-DD).

    Учитывает случаи с валидными и некорректными датами: некорректные даты
    не выбрасывают ошибку, а участвуют в сортировке согласно логике функции.

    Args:
        input_data (List[Dict[str, Any]]): исходный список операций с полем 'date'.
        expected_output (List[Dict[str, Any]]): ожидаемый отсортированный список.
    """
    assert sort_by_date(input_data) == expected_output