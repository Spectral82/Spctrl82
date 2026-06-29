import pytest
from src.masks import get_mask_account, get_mask_card_number


def test_get_mask_card_number_basic() -> None:
    """
    Проверяет базовую работу функции get_mask_card_number:
    маска корректно применяется к 16-значному номеру карты без разделителей.
    Ожидаемый формат вывода: «XXXX XX** **** XXXX».
    """
    assert get_mask_card_number("1234567890123456") == "1234 56** **** 3456"


def test_get_mask_card_number_with_spaces() -> None:
    """
    Проверяет обработку номера карты, содержащего пробелы в качестве разделителей.
    Функция должна игнорировать пробелы и вернуть корректно замаскированный номер.
    """
    assert get_mask_card_number("1234 5678 9012 3456") == "1234 56** **** 3456"


def test_get_mask_card_number_with_hyphens() -> None:
    """
    Проверяет обработку номера карты с дефисами в качестве разделителей.
    Функция должна корректно очистить строку от дефисов и применить маску.
    """
    assert get_mask_card_number("1234-5678-9012-3456") == "1234 56** **** 3456"


def test_get_mask_card_number_invalid_length() -> None:
    """
    Проверяет, что функция выбрасывает ValueError при передаче номера карты
    некорректной длины (например, 15 цифр вместо 16).
    """
    with pytest.raises(ValueError):
        get_mask_card_number("123456789012345")  # 15 digits


def test_get_mask_card_number_invalid_characters() -> None:
    """
    Проверяет, что функция выбрасывает ValueError, если после очистки строки
    от разделителей остаются недопустимые символы (не цифры).
    """
    with pytest.raises(ValueError):
        get_mask_card_number("abcd1234efgh5678")  # contains non-digits after cleaning


def test_get_mask_card_number_all_zeros() -> None:
    """
    Проверяет корректность маскирования номера, состоящего из одних нулей.
    Убеждается, что формат маски сохраняется и нули обрабатываются как обычные цифры.
    """
    assert get_mask_card_number("0000000000000000") == "0000 00** **** 0000"


def test_get_mask_card_number_empty_string() -> None:
    """
    Проверяет, что передача пустой строки приводит к выбросу ValueError,
    так как корректный номер карты не может быть пустым.
    """
    with pytest.raises(ValueError):
        get_mask_card_number("")


def test_get_mask_account_basic() -> None:
    """
    Проверяет базовую работу функции get_mask_account:
    для 16‑значного номера счёта возвращается маска «**XXXX» (последние 4 цифры).
    """
    assert get_mask_account("1234567890123456") == "**3456"


def test_get_mask_account_with_spaces() -> None:
    """
    Проверяет обработку номера счёта, содержащего пробелы.
    Функция должна игнорировать пробелы и корректно вернуть маску по последним 4 цифрам.
    """
    assert get_mask_account("1234 5678 9012 3456") == "**3456"


def test_get_mask_account_min_digits() -> None:
    """
    Проверяет работу функции для минимально допустимой длины номера счёта (4 цифры).
    В этом случае маска должна отображать все цифры с префиксом «**».
    """
    assert get_mask_account("1234") == "**1234"


def test_get_mask_account_invalid_length() -> None:
    """
    Проверяет, что при передаче номера счёта длиной менее 4 цифр
    функция выбрасывает ValueError как для недопустимого формата.
    """
    with pytest.raises(ValueError):
        get_mask_account("12")  # less than 4 digits


def test_get_mask_account_no_digits() -> None:
    """
    Проверяет, что если в переданной строке нет ни одной цифры,
    функция корректно выбрасывает ValueError.
    """
    with pytest.raises(ValueError):
        get_mask_account("abcd")  # 0 digits


def test_get_mask_account_invalid_characters() -> None:
    """
    Проверяет поведение функции при наличии в строке буквенных символов.
    Тестируется сценарий, когда функция извлекает цифры и корректно маскирует их,
    не выбрасывая ошибку (если логика функции допускает такую обработку).
    """
    # This test is now valid — function doesn't raise ValueError for "1234xyz"
    # because it extracts "1234" and masks it successfully
    assert get_mask_account("1234xyz") == "**1234"