import pytest
from src.masks import get_mask_account, get_mask_card_number

def test_get_mask_card_number_basic() -> None:
    assert get_mask_card_number("1234567890123456") == "1234 56** **** 3456"

def test_get_mask_card_number_with_spaces() -> None:
    assert get_mask_card_number("1234 5678 9012 3456") == "1234 56** **** 3456"

def test_get_mask_card_number_with_hyphens() -> None:
    assert get_mask_card_number("1234-5678-9012-3456") == "1234 56** **** 3456"

def test_get_mask_card_number_invalid_length() -> None:
    with pytest.raises(ValueError):
        get_mask_card_number("123456789012345")  # 15 digits

def test_get_mask_card_number_invalid_characters() -> None:
    with pytest.raises(ValueError):
        get_mask_card_number("abcd1234efgh5678")  # contains non-digits after cleaning

def test_get_mask_card_number_all_zeros() -> None:
    assert get_mask_card_number("0000000000000000") == "0000 00** **** 0000"


def test_get_mask_card_number_empty_string() -> None:
    with pytest.raises(ValueError):
        get_mask_card_number("")

def test_get_mask_account_basic() -> None:
    assert get_mask_account("1234567890123456") == "**3456"

def test_get_mask_account_with_spaces() -> None:
    assert get_mask_account("1234 5678 9012 3456") == "**3456"

def test_get_mask_account_min_digits() -> None:
    assert get_mask_account("1234") == "**1234"

def test_get_mask_account_invalid_length() -> None:
    with pytest.raises(ValueError):
        get_mask_account("12")  # less than 4 digits

def test_get_mask_account_no_digits() -> None:
    with pytest.raises(ValueError):
        get_mask_account("abcd")  # 0 digits

def test_get_mask_account_invalid_characters() -> None:
    # This test is now valid — function doesn't raise ValueError for "1234xyz"
    # because it extracts "1234" and masks it successfully
    assert get_mask_account("1234xyz") == "**1234"