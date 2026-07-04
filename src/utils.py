import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from src.external_api import convert_currency

"""
Модуль utils предоставляет вспомогательные функции для работы с транзакциями:
- чтение транзакций из JSON‑файла;
- конвертация суммы транзакции в рубли с учётом валюты.

Для логирования используется логгер с именем модуля (__name__).
Логи пишутся в файл utils.log в формате:
    %(asctime)s | %(name)s | %(levelname)s | %(message)s
Уровень логирования установлен на DEBUG и выше.
"""

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Уровень не ниже DEBUG

# Формат записи: метка времени, название модуля, уровень серьёзности, сообщение
file_formatter = logging.Formatter(
    fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

# FileHandler: логирование в файл (например, utils.log)
file_handler = logging.FileHandler("utils.log", encoding="utf-8")
file_handler.setFormatter(file_formatter)

# Добавляем handler к логгеру
logger.addHandler(file_handler)


def read_transactions(file_path: str) -> List[Dict[str, Any]]:
    """
    Читает JSON‑файл и возвращает список словарей с транзакциями.

    Функция безопасно обрабатывает возможные ошибки:
    - отсутствие файла;
    - некорректный JSON;
    - неверный тип данных в файле.

    В случае любой ошибки возвращается пустой список.

    Args:
        file_path (str): Путь к JSON‑файлу с транзакциями.

    Returns:
        List[Dict[str, Any]]: Список транзакций (словарей). Если произошла ошибка
        или файл пуст/некорректен, возвращается пустой список.

    Examples:
        >>> transactions = read_transactions("transactions.json")
        >>> len(transactions)
        10
    """
    path = Path(file_path)
    logger.debug("Попытка чтения транзакций из файла: %s", file_path)

    if not path.exists():
        logger.error("Файл не найден: %s", file_path)
        return []

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        logger.error("Ошибка декодирования JSON в файле %s: %s", file_path, e)
        return []
    except OSError as e:
        logger.error("Ошибка доступа к файлу %s: %s", file_path, e)
        return []

    if not isinstance(data, list):
        logger.error(
            "Содержимое файла %s не является списком (тип: %s)",
            file_path,
            type(data).__name__,
        )
        return []

    logger.info("Успешно прочитано %d транзакций из файла: %s", len(data), file_path)
    return data


def sort_transactions(transactions: List[Dict[str, Any]], ascending: bool = True) -> List[Dict[str, Any]]:
    """
    Сортирует список транзакций по полю 'date'.
    ascending=True → от старых к новым; ascending=False → от новых к старым.
    """
    return sorted(
        transactions,
        key=lambda t: t.get("date", ""),
        reverse=not ascending
    )


def get_transaction_amount_rub(transaction: Dict[str, Any]) -> float:
    """
    Возвращает сумму транзакции в рублях (float) с учётом конвертации валюты.

    Логика работы:
    - Если валюта RUB: сумма возвращается без изменений.
    - Если валюта USD или EUR: сумма конвертируется в рубли по курсу,
      полученному через внешний API convert_currency.
    - В остальных случаях (неизвестная валюта, отсутствие данных, ошибки)
      возвращается 0.0.

    Предполагается, что в словаре transaction присутствуют ключи:
    - "amount": числовое значение суммы;
    - "currency": строка с кодом валюты (например, "RUB", "USD", "EUR").

    Args:
        transaction (Dict[str, Any]): Словарь с данными транзакции.

    Returns:
        float: Сумма транзакции в рублях. При ошибках или неизвестных валютах
        возвращается 0.0.

    Notes:
        - Функция чувствительна к регистру валюты: значения нормализуются
          к верхнему регистру (например, "usd" → "USD").
        - При отсутствии ключа "amount" или невозможности привести его к типу
          float возвращается 0.0 с записью в лог.
        - Если convert_currency возвращает None, конвертация считается неудачной,
          и функция также возвращает 0.0.
    """
    amount = transaction.get("amount")
    currency = transaction.get("currency")

    # Нормализация валюты к верхнему регистру
    if isinstance(currency, str):
        currency = currency.upper()
    else:
        logger.warning(
            "В транзакции отсутствует корректный ключ 'currency' или он не является строкой: %s",
            transaction,
        )
        return 0.0

    # Валидация и приведение суммы к float
    try:
        amount_value = float(amount) if amount is not None else 0.0
    except (TypeError, ValueError) as e:
        logger.error(
            "Не удалось преобразовать поле 'amount' в float в транзакции: %s. Ошибка: %s",
            transaction,
            e,
        )
        return 0.0

    # Логика конвертации
    if currency == "RUB":
        logger.debug(
            "Валюта RUB — конвертация не требуется, сумма: %.2f",
            amount_value,
        )
        return amount_value

    if currency in ("USD", "EUR"):
        rate = convert_currency(currency)
        if rate is None:
            logger.error(
                "Не удалось получить курс для валюты %s — конвертация невозможна",
                currency,
            )
            return 0.0
        converted_amount = amount_value * rate
        logger.info(
            "Конвертация %s %.2f по курсу %.4f → %.2f RUB",
            currency,
            amount_value,
            rate,
            converted_amount,
        )
        return converted_amount

    logger.warning("Неизвестная валюта %s — сумма не конвертируется, возвращается 0.0", currency)
    return 0.0
