from typing import Any, Dict, Generator, List


def filter_by_currency(
    transactions: List[Dict[str, Any]], currency_code: str
) -> Generator[Dict[str, Any], None, None]:
    """
    Генератор, фильтрующий транзакции по коду валюты.

    Args:
        transactions: Список словарей с транзакциями.
        currency_code: Код валюты для фильтрации (например, "USD").

    Yields:
        Транзакция (dict), где валюта операции соответствует заданной.
    """
    for transaction in transactions:
        operation_amount = transaction.get("operationAmount") or {}
        currency = operation_amount.get("currency") or {}
        if currency.get("code") == currency_code:
            yield transaction


def transaction_descriptions(transactions: List[Dict[str, Any]]) -> Generator[str, None, None]:
    """
    Генератор, возвращающий описания транзакций по очереди.

    Args:
        transactions: Список словарей с транзакциями.

    Yields:
        Описание операции (str).
    """
    for transaction in transactions:
        yield transaction.get("description", "")


def card_number_generator(start: int, end: int) -> Generator[str, None, None]:
    """
    Генератор номеров банковских карт в формате XXXX XXXX XXXX XXXX.

    Args:
        start: Начальное значение диапазона (от 1 до 9999999999999999).
        end: Конечное значение диапазона (до 9999999999999999), должно быть >= start.

    Yields:
        Номер карты в формате "XXXX XXXX XXXX XXXX".

    Raises:
        ValueError: Если start или end вне допустимого диапазона.
    """
    max_value = 9999999999999999

    if not (1 <= start <= max_value):
        raise ValueError("start должен быть в диапазоне от 1 до 9999999999999999")
    if not (1 <= end <= max_value):
        raise ValueError("end должен быть в диапазоне от 1 до 9999999999999999")
    if start > end:
        return  # пустой итератор

    for number in range(start, end + 1):
        num_str = f"{number:016d}"
        formatted_number = f"{num_str[:4]} {num_str[4:8]} {num_str[8:12]} {num_str[12:]}"
        yield formatted_number
