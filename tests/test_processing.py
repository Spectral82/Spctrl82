from typing import Any, Dict, List

import pytest

from src.processing import (
    filter_by_state,
    mask_account_number,
    mask_card_number,
    sort_by_date,
)
from src.widget import get_date


@pytest.fixture
def sample_data() -> List[Dict[str, Any]]:
    """
    Возвращает набор тестовых данных с операциями и их статусами.

    :return: список словарей, каждый из которых содержит поля 'id' и 'state'
    """
    return [
        {"id": 1, "state": "active"},
        {"id": 2, "state": "inactive"},
        {"id": 3, "state": "active"},
    ]


@pytest.fixture
def date_data() -> List[Dict[str, Any]]:
    """
    Возвращает тестовые данные с датами для проверки сортировки.

    :return: список словарей, каждый из которых содержит поля 'id' и 'date'
             в формате YYYY-MM-DD
    """
    return [
        {"id": 1, "date": "2023-01-01"},
        {"id": 2, "date": "2022-12-31"},
    ]


@pytest.mark.parametrize(
    "input_card, expected_output",
    [
        ("1234567890123456", "1234 **** **** 3456"),
        ("1234 5678 9012 3456", "1234 **** **** 3456"),
        ("1234-5678-9012-3456", "1234 **** **** 3456"),
        ("0000000000000000", "0000 **** **** 0000"),
    ],
)
def test_mask_card_number(
    input_card: str,
    expected_output: str,
) -> None:
    """
    Проверяет корректность маскирования номера карты функцией mask_card_number.

    Тестируются различные форматы входных данных (без разделителей, с пробелами,
    с дефисами) и проверяется соответствие ожидаемому формату маски.

    :param input_card: исходный номер карты (в разных форматах)
    :param expected_output: ожидаемый результат маскирования
    """
    result = mask_card_number(input_card)
    assert result == expected_output


@pytest.mark.parametrize(
    "account_number, expected",
    [
        ("1234567890123456", "**3456"),
        ("12 34 56 78", "**5678"),
        ("0000", "**0000"),
    ],
)
def test_mask_account_number(
    account_number: str,
    expected: str,
) -> None:
    """
    Проверяет корректность маскирования номера счёта функцией mask_account_number.

    Тестируется сохранение последних цифр и применение маски к остальной части
    номера, включая обработку разных форматов ввода.

    :param account_number: исходный номер счёта
    :param expected: ожидаемый результат маскирования
    """
    assert mask_account_number(account_number) == expected


@pytest.mark.parametrize(
    "state, input_data, expected_output",
    [
        (
            "active",
            [
                {"id": 1, "state": "active"},
                {"id": 2, "state": "inactive"},
                {"id": 3, "state": "active"},
            ],
            [
                {"id": 1, "state": "active"},
                {"id": 3, "state": "active"},
            ],
        ),
        (
            "inactive",
            [
                {"id": 1, "state": "active"},
                {"id": 2, "state": "inactive"},
                {"id": 3, "state": "active"},
            ],
            [{"id": 2, "state": "inactive"}],
        ),
        (
            "pending",
            [
                {"id": 1, "state": "active"},
                {"id": 2, "state": "inactive"},
            ],
            [],
        ),
    ],
)
def test_filter_by_state(
    state: str,
    input_data: List[Dict[str, Any]],
    expected_output: List[Dict[str, Any]],
) -> None:
    """
    Проверяет фильтрацию списка операций по статусу с помощью filter_by_state.

    Тестируются случаи наличия искомого статуса, его отсутствия и разных
    комбинаций статусов в списке.

    :param state: искомый статус операции
    :param input_data: исходный список операций со статусами
    :param expected_output: ожидаемый отфильтрованный список операций
    """
    assert filter_by_state(input_data, state) == expected_output


def test_filter_by_state_empty() -> None:
    """
    Проверяет поведение filter_by_state при передаче пустого списка.

    Ожидается, что функция вернёт пустой список независимо от указанного статуса.
    """
    assert filter_by_state([], "active") == []


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
                {"id": 1, "date": "2022-12-31"},
                {"id": 2, "date": "2023-01-01"},
            ],
            [
                {"id": 2, "date": "2023-01-01"},
                {"id": 1, "date": "2022-12-31"},
            ],
        ),
    ],
)
def test_sort_by_date(
    input_data: List[Dict[str, Any]],
    expected_output: List[Dict[str, Any]],
) -> None:
    """
    Проверяет сортировку списка операций по дате с помощью sort_by_date.

    По умолчанию сортировка выполняется по убыванию (новые даты первыми).
    Тестируются разные комбинации дат и проверка соответствия ожидаемому порядку.

    :param input_data: список операций с датами в формате YYYY-MM-DD
    :param expected_output: ожидаемый отсортированный список
    """
    result = sort_by_date(input_data)
    assert result == expected_output


def test_sort_by_date_empty() -> None:
    """
    Проверяет поведение sort_by_date при передаче пустого списка.

    Ожидается, что функция вернёт пустой список без ошибок.
    """
    assert sort_by_date([]) == []  # пустой список


def test_sort_by_date_invalid_format() -> None:
    """
    Проверяет, что sort_by_date выбрасывает ValueError при некорректном формате даты.

    Передаётся запись с невалидной датой, ожидается исключение.
    """
    invalid_data = [{"id": 1, "date": "invalid-date"}]
    with pytest.raises(ValueError):
        sort_by_date(invalid_data)


def test_sort_by_date_ascending(date_data: List[Dict[str, Any]]) -> None:
    """
    Проверяет сортировку по возрастанию дат (reverse=False).

    Используется фикстура date_data. Ожидается, что более ранняя дата
    будет первой в списке.

    :param date_data: тестовые данные с датами
    """
    result = sort_by_date(date_data, reverse=False)
    assert result[0]["id"] == 2  # 2022-12-31
    assert result[1]["id"] == 1  # 2023-01-01


def test_sort_by_date_descending(date_data: List[Dict[str, Any]]) -> None:
    """
    Проверяет сортировку по убыванию дат (reverse=True).

    Используется фикстура date_data. Ожидается, что более поздняя дата
    будет первой в списке.

    :param date_data: тестовые данные с датами
    """
    result = sort_by_date(date_data, reverse=True)
    assert result[0]["id"] == 1  # 2023-01-01
    assert result[1]["id"] == 2  # 2022-12-31


# Обратите внимание: в исходном коде был дублирующийся тест test_sort_by_date_invalid_format.
# Здесь он оставлен как есть, но в реальном проекте дубликаты следует удалить.
def test_sort_by_date_invalid_format() -> None:
    """
    Повторная проверка, что sort_by_date выбрасывает ValueError
    при некорректном формате даты (дублирующий тест).

    Передаётся запись с невалидной датой, ожидается исключение.
    """
    invalid_data = [{"id": 1, "date": "invalid-date"}]
    with pytest.raises(ValueError):
        sort_by_date(invalid_data)


@pytest.mark.parametrize(
    "date_input, expected_output",
    [
        ("01/01/2023", "2023-01-01"),
        ("January 1, 2023", "2023-01-01"),
        ("Jan 1, 2023", "2023-01-01"),
        ("2023-01-01", "2023-01-01"),
    ],
)
def test_get_date_valid(date_input: str, expected_output: str) -> None:
    """
    Проверяет конвертацию различных форматов даты в единый формат YYYY-MM-DD.

    Тестируются разные варианты написания даты (числовой, текстовый, смешанный)
    и проверяется, что функция get_date возвращает корректный ISO-формат.

    :param date_input: входная дата в одном из поддерживаемых форматов
    :param expected_output: ожидаемая дата в формате YYYY-MM-DD
    """
    assert get_date(date_input) == expected_output

    def process_bank_operations(data: List[Dict[str, Any]], categories: List[str]) -> Dict[str, int]:
        """
        Подсчитывает количество банковских операций по заданным категориям.

        Категория сопоставляется с операцией по наличию соответствующей подстроки
        в поле description. Сравнение регистронезависимое. Одна операция может
        быть учтена сразу в нескольких категориях.
        """
        counts = {category: 0 for category in categories}

        for operation in data:
            description = str(operation.get("description", ""))
            desc_lower = description.lower()
            for category in categories:
                if category.lower() in desc_lower:
                    counts[category] += 1  # <-- было: counts[category] = 1

        return counts
