from typing import Any, Dict, List

import pytest

from src.processing import filter_by_state, mask_account_number, mask_card_number, sort_by_date
from src.widget import get_date


@pytest.fixture
def sample_data() -> List[Dict[str, Any]]:
    return [
        {"id": 1, "state": "active"},
        {"id": 2, "state": "inactive"},
        {"id": 3, "state": "active"},
    ]


@pytest.fixture
def date_data() -> List[Dict[str, Any]]:
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
def test_mask_card_number(input_card: str, expected_output: str) -> None:
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
def test_mask_account_number(account_number, expected):
    assert mask_account_number(account_number) == expected


@pytest.mark.parametrize(
    "state, input_data, expected_output",
    [
        (
            "active",
            [{"id": 1, "state": "active"}, {"id": 2, "state": "inactive"}, {"id": 3, "state": "active"}],
            [{"id": 1, "state": "active"}, {"id": 3, "state": "active"}],
        ),
        (
            "inactive",
            [{"id": 1, "state": "active"}, {"id": 2, "state": "inactive"}, {"id": 3, "state": "active"}],
            [{"id": 2, "state": "inactive"}],
        ),
        ("pending", [{"id": 1, "state": "active"}, {"id": 2, "state": "inactive"}], []),  # отсутствует статус
    ],
)
def test_filter_by_state(state, input_data, expected_output):
    assert filter_by_state(input_data, state) == expected_output


def test_filter_by_state_empty():
    assert filter_by_state([], "active") == []  # пустой список


@pytest.mark.parametrize(
    "input_data, expected_output",
    [
        (
            [{"id": 1, "date": "2023-01-01"}, {"id": 2, "date": "2022-12-31"}],
            [{"id": 1, "date": "2023-01-01"}, {"id": 2, "date": "2022-12-31"}],
        ),
        (
            [{"id": 1, "date": "2022-12-31"}, {"id": 2, "date": "2023-01-01"}],
            [{"id": 2, "date": "2023-01-01"}, {"id": 1, "date": "2022-12-31"}],
        ),
    ],
)
def test_sort_by_date(input_data: List[Dict[str, Any]], expected_output: List[Dict[str, Any]]) -> None:
    result = sort_by_date(input_data)
    assert result == expected_output


def test_sort_by_date_empty() -> None:
    assert sort_by_date([]) == []  # пустой список


def test_sort_by_date_invalid_format() -> None:
    invalid_data = [{"id": 1, "date": "invalid-date"}]
    with pytest.raises(ValueError):
        sort_by_date(invalid_data)


def test_sort_by_date_ascending(date_data: List[Dict[str, Any]]) -> None:
    result = sort_by_date(date_data, reverse=False)
    assert result[0]["id"] == 2  # 2022-12-31
    assert result[1]["id"] == 1  # 2023-01-01


def test_sort_by_date_descending(date_data: List[Dict[str, Any]]) -> None:
    result = sort_by_date(date_data, reverse=True)
    assert result[0]["id"] == 1  # 2023-01-01
    assert result[1]["id"] == 2  # 2022-12-31


def test_sort_by_date_invalid_format() -> None:
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
    assert get_date(date_input) == expected_output


def test_get_date_invalid() -> None:
    with pytest.raises(ValueError):
        get_date("abcd")
    with pytest.raises(ValueError):
        get_date("")
    with pytest.raises(ValueError):
        get_date("2023/01/01")
