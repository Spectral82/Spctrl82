from datetime import datetime
from typing import Any, Dict, List
import re


def filter_by_state(operations: List[Dict[str, Any]], state: str = "EXECUTED") -> List[Dict[str, Any]]:
    """
    Фильтрует список операций по значению ключа 'state'.

    Args:
        operations (List[Dict[str, Any]]): Список операций (словарей), которые нужно отфильтровать.
        state (str): Значение статуса для фильтрации. По умолчанию — 'EXECUTED'.

    Returns:
        List[Dict[str, Any]]: Отфильтрованный список операций, где значение ключа 'state'
        совпадает с указанным.
    """
    return [op for op in operations if op.get("state") == state]


def sort_by_date(operations: List[Dict[str, Any]], reverse: bool = True) -> List[Dict[str, Any]]:
    """
    Сортирует список операций по ключу 'date'. Поддерживает ISO‑форматы дат, включая строки
    с суффиксом 'Z' (UTC).

    Args:
        operations (List[Dict[str, Any]]): Список операций (словарей) для сортировки.
        reverse (bool): Направление сортировки. Если True (по умолчанию), сортировка по убыванию
        (от новых к старым).

    Returns:
        List[Dict[str, Any]]: Отсортированный список операций.

    Raises:
        ValueError: Если в операции отсутствует поле 'date' или дата имеет некорректный формат.
    """

    def parse_date(op: Dict[str, Any]) -> datetime:
        date_str = op.get("date", "")
        if not date_str:
            raise ValueError("Missing date field")

        try:
            # Обработка формата с Z (UTC)
            if date_str.endswith("Z"):
                date_str = date_str[:-1]

            return datetime.fromisoformat(date_str)
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}")

    return sorted(operations, key=parse_date, reverse=reverse)


def mask_card_number(card_number: str) -> str:
    """
    Маскирует номер карты, оставляя видимыми первые 4 и последние 4 цифры.

    Функция удаляет все нецифровые символы из входной строки и проверяет, что итоговая длина —
    ровно 16 цифр.

    Args:
        card_number (str): Номер карты в произвольном формате (может содержать пробелы, дефисы
        и другие символы).

    Returns:
        str: Замаскированный номер карты в формате «XXXX **** **** XXXX», где X — цифры.

    Raises:
        ValueError: Если после очистки от нецифровых символов длина номера не равна 16.
    """
    # Удаляем все нецифровые символы
    digits = "".join(filter(str.isdigit, card_number))
    if len(digits) != 16:
        raise ValueError("Card number must contain exactly 16 digits")

    # Форматируем: первые 4, затем маска, последние 4
    return f"{digits[:4]} **** **** {digits[-4:]}"


def mask_account_number(account_number: str) -> str:
    """
    Маскирует номер счёта, показывая только последние 4 цифры.

    Функция удаляет все нецифровые символы и проверяет, что остаётся не менее 4 цифр.

    Args:
        account_number (str): Номер счёта в произвольном формате (может содержать пробелы
        и другие символы).

    Returns:
        str: Замаскированный номер счёта в формате «**XXXX», где X — последние 4 цифры номера.

    Raises:
        ValueError: Если после удаления нецифровых символов остаётся менее 4 цифр.
    """
    # Удаляем все нецифровые символы
    digits = "".join(filter(str.isdigit, account_number))
    if len(digits) < 4:
        raise ValueError("Account number must contain at least 4 digits")

    # Показываем только последние 4 цифры, остальные маскируем
    return f"**{digits[-4:]}"


def process_bank_search(data: List[Dict[str, Any]], search: str) -> List[Dict[str, Any]]:
    """
    Выполняет поиск банковских операций по подстроке в поле description.

    Поиск регистронезависимый, поддерживает частичное совпадение подстроки.
    Если search — пустая строка, возвращается исходный список операций.

    Args:
        data (List[Dict[str, Any]]): Список банковских операций (словарей). Ожидается, что
        каждая операция содержит поле 'description' (строка).
        search (str): Подстрока для поиска в описании операции.

    Returns:
        List[Dict[str, Any]]: Список операций, в которых поле 'description' содержит
        указанную подстроку (без учёта регистра).
    """
    if not search:
        return data

    search_lower = search.lower()
    result = []

    for op in data:
        description = op.get("description", "")
        if isinstance(description, str) and search_lower in description.lower():
            result.append(op)

    return result