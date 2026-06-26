import json
from pathlib import Path
from typing import Any, Dict, List
import logging

from src.external_api import convert_currency

# --- Настройка логгера для модуля utils ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Уровень не ниже DEBUG

# Формат записи: метка времени, название модуля, уровень серьезности, сообщение
file_formatter = logging.Formatter(
    fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# FileHandler: логирование в файл (например, utils.log)
file_handler = logging.FileHandler("utils.log", encoding="utf-8")
file_handler.setFormatter(file_formatter)

# Добавляем handler к логгеру
logger.addHandler(file_handler)
# ------------------------------------------


def read_transactions(file_path: str) -> List[Dict[str, Any]]:
    """
    Читает JSON-файл и возвращает список словарей с транзакциями.

    Возвращает пустой список, если:
      - файл не найден;
      - содержимое не является списком;
      - файл пустой.
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
        logger.error("Содержимое файла %s не является списком (тип: %s)", file_path, type(data).__name__)
        return []

    logger.info("Успешно прочитано %d транзакций из файла: %s", len(data), file_path)
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

    logger.debug(
        "Расчёт суммы в рублях: amount=%s, currency=%s",
        amount,
        currency
    )

    if amount is None:
        logger.warning("В транзакции отсутствует ключ 'amount', возвращаем 0.0")
        return 0.0

    try:
        amount = float(amount)
    except (TypeError, ValueError) as e:
        logger.error("Не удалось преобразовать amount в float: %s (значение: %r)", e, amount)
        return 0.0

    if currency == "RUB":
        logger.debug("Валюта RUB, конвертация не требуется, сумма: %.2f", amount)
        return amount

    if currency in ("USD", "EUR"):
        logger.info("Требуется конвертация валюты: %s", currency)
        rate = convert_currency(currency)
        if rate is None:
            logger.error("Не удалось получить курс для валюты %s (convert_currency вернул None)", currency)
            return 0.0
        result = amount * rate
        logger.info(
            "Конвертация выполнена: %s %.2f → RUB %.2f (курс: %.4f)",
            currency,
            amount,
            result,
            rate
        )
        return result

    # Неизвестная валюта
    logger.warning("Неизвестная валюта '%s', возвращаем 0.0", currency)
    return 0.0