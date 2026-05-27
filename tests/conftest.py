import pytest


@pytest.fixture
def sample_data():
    return [
        {"id": 1, "state": "active"},
        {"id": 2, "state": "inactive"},
        {"id": 3, "state": "active"},
    ]


@pytest.fixture
def date_data():
    return [
        {"id": 1, "date": "2023-01-01"},
        {"id": 2, "date": "2022-12-31"},
        {"id": 3, "date": "invalid-date"},
    ]


from src.masks import mask_card_number, mask_account_number
from src.processing import filter_by_state, sort_by_date
from src.widget import get_date, mask_account_card


@pytest.mark.parametrize(
    "card_number, expected_output",
    [
        ("1234567890123456", "1234 56** **** 3456"),
        ("1234 5678 9012 3456", "1234 56** **** 3456"),
        ("1234-5678-9012-3456", "1234 56** **** 3456"),
        ("0000000000000000", "0000 00** **** 0000"),
    ],
)
def test_mask_card_number(card_number, expected_output) -> None:
    assert mask_card_number(card_number) == expected_output


@pytest.mark.parametrize(
    "account_number, expected_output",
    [
        ("1234567890123456", "**3456"),
        ("1234 5678 9012 3456", "**3456"),
        ("1234", "**1234"),
    ],
)
def test_mask_account_number(account_number, expected_output) -> None:
    assert mask_account_number(account_number) == expected_output


@pytest.mark.parametrize(
    "state, expected_output",
    [
        ("active", [{"id": 1, "state": "active"}, {"id": 3, "state": "active"}]),
        ("inactive", [{"id": 2, "state": "inactive"}]),
        ("pending", []),
    ],
)
def test_filter_by_state(state, sample_data, expected_output) -> None:
    assert filter_by_state(sample_data, state) == expected_output


@pytest.mark.parametrize(
    "input_data, expected_output",
    [
        ([{"id": 1, "date": "2023-01-01"}, {"id": 2, "date": "2022-12-31"}], [{"id": 1, "date": "2023-01-01"}, {"id": 2, "date": "2022-12-31"}]),
        ([{"id": 1, "date": "invalid-date"}, {"id": 2, "date": "2023-01-01"}], [{"id": 2, "date": "2023-01-01"}, {"id": 1, "date": "invalid-date"}]),
    ],
)
def test_sort_by_date(input_data, expected_output) -> None:
    assert sort_by_date(input_data) == expected_output
