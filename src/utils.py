import json
from pathlib import Path
from typing import Any, Dict, List

from src.external_api import convert_currency


def read_transactions(file_path: str) -> List[Dict[str, Any]]:
    """
    Читает JSON-файл и возвращает список словарей с транзакциями.

    Возвращает пустой список, если:
      - файл не найден;
      - содержимое не является списком;
      - файл пустой.
    """
    path = Path(file_path)

    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

    if not isinstance(data, list):
        return []

    return data


def get_transaction_amount_rub(transaction: Dict[str, Any]) -> float:
    """
    Возвращает сумму транзакции в рублях (float).

    Логика:
      - Если валюта RUB: просто берём amount.
      - Если USD/EUR: конвертируем через внешний API.
      - В остальных случаях или при ошибках: возвращаем 0.0.

    Предполагается, что в transaction есть ключи:
      - "amount": число
      - "currency": строка, например "RUB", "USD", "EUR"
    """

    amount = transaction.get("amount")
    currency = (transaction.get("currency") or "").upper()

    if amount is None:
        return 0.0

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return 0.0

    if currency == "RUB":
        return amount

    if currency in ("USD", "EUR"):
        rate = convert_currency(currency)
        if rate is None:
            return 0.0
        return amount * rate

    # Неизвестная валюта — по ТЗ не описано, безопаснее вернуть 0.0
    return 0.0
