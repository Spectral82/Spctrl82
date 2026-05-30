from typing import Any, Dict, List
from datetime import datetime

def filter_by_state(operations: List[Dict[str, Any]], state: str = "EXECUTED") -> List[Dict[str, Any]]:
    """
    Фильтрует список операций по значению ключа 'state'.

    :param operations: list[dict] — список операций
    :param state: str — значение статуса (по умолчанию 'EXECUTED')
    :return: list[dict] — отфильтрованный список
    """
    return [op for op in operations if op.get("state") == state]

def sort_by_date(operations: List[Dict[str, Any]], reverse: bool = True) -> List[Dict[str, Any]]:
    """
    Сортирует список операций по ключу 'date'.

    :param operations: list[dict] — список операций
    :param reverse: bool — сортировка по убыванию (по умолчанию True)
    :return: list[dict] — отсортированный список
    :raises ValueError: если дата имеет некорректный формат
    """

    def parse_date(op: Dict[str, Any]) -> datetime:
        date_str = op.get("date", "")
        if not date_str:
            raise ValueError("Missing date field")

        try:
            # Обработка формата с Z (UTC)
            if date_str.endswith("Z"):
                date_str = date_str[:-1] + " 00:00"
                return datetime.fromisoformat(date_str)

            # Парсинг ISO формата с микросекундами
            if "T" in date_str and "." in date_str:
                return datetime.fromisoformat(date_str)

            # Базовый ISO формат
            return datetime.fromisoformat(date_str)
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}")

    return sorted(operations, key=parse_date, reverse=reverse)
def mask_card_number(card_number: str) -> str:
    """
    Маскирует номер карты, оставляя видимыми первые 6 и последние 4 цифры.

    :param card_number: str — номер карты (может содержать пробелы/дефисы)
    :return: str — замаскированный номер в формате "1234 56** **** 3456"
    """
    # Удаляем все нецифровые символы
    digits = ''.join(filter(str.isdigit, card_number))

    if len(digits) != 16:
        raise ValueError("Card number must contain exactly 16 digits")

    # Форматируем: первые 4, следующие 2, затем маска, последние 4
    return f"{digits[:4]} **** **** {digits[-4:]}"


def mask_account_number(account_number: str) -> str:
    """
    Маскирует номер счёта, показывая только последние 4 цифры.

    :param account_number: str — номер счёта (может содержать пробелы)
    :return: str — замаскированный номер в формате "**3456"
    """
    # Удаляем все нецифровые символы
    digits = ''.join(filter(str.isdigit, account_number))

    if len(digits) < 4:
        raise ValueError("Account number must contain at least 4 digits")

    # Показываем только последние 4 цифры, остальные маскируем
    return f"**{digits[-4:]}"