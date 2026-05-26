import pytest
from src.processing import filter_by_state, sort_by_date


# Тесты для filter_by_state
@pytest.mark.parametrize(
    "state, input_data, expected_output",
    [
        ("active", [
            {"id": 1, "state": "active"},
            {"id": 2, "state": "inactive"},
            {"id": 3, "state": "active"}
        ], [
            {"id": 1, "state": "active"},
            {"id": 3, "state": "active"}
        ]),
        ("inactive", [
            {"id": 1, "state": "active"},
            {"id": 2, "state": "inactive"},
            {"id": 3, "state": "active"}
        ], [
            {"id": 2, "state": "inactive"}
        ]),
        ("pending", [
            {"id": 1, "state": "active"},
            {"id": 2, "state": "inactive"}
        ], []),  # отсутствует статус
    ]
)
def test_filter_by_state(state, input_data, expected_output):
    assert filter_by_state(input_data, state) == expected_output


def test_filter_by_state_empty():
    assert filter_by_state([], "active") == []  # пустой список


# Тесты для sort_by_date
@pytest.mark.parametrize(
    "input_data, expected_output",
    [
        ([
            {"id": 1, "date": "2023-01-01"},
            {"id": 2, "date": "2022-12-31"},
            {"id": 3, "date": "2023-01-01"}
        ], [
            {"id": 1, "date": "2023-01-01"},
            {"id": 3, "date": "2023-01-01"},
            {"id": 2, "date": "2022-12-31"}
        ]),
        ([
            {"id": 1, "date": "2022-12-31"},
            {"id": 2, "date": "2023-01-01"}
        ], [
            {"id": 2, "date": "2023-01-01"},
            {"id": 1, "date": "2022-12-31"}
        ]),
        ([
            {"id": 1, "date": "invalid-date"},
            {"id": 2, "date": "2023-01-01"}
        ], [
            {"id": 2, "date": "2023-01-01"},
            {"id": 1, "date": "invalid-date"}
        ]),  # некорректные форматы
    ]
)
def test_sort_by_date(input_data, expected_output):
    assert sort_by_date(input_data) == expected_output


def test_sort_by_date_empty():
    assert sort_by_date([]) == []  # пустой список


def test_sort_by_date_invalid_format():
    with pytest.raises(ValueError):
        sort_by_date([{"id": 1, "date": "invalid-date"}])  # ошибка при некорректной дате
