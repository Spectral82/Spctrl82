import logging
from typing import Any

# --- Настройка логгера для модуля masks ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

file_handler = logging.FileHandler("masks.log", encoding="utf-8")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
# -----------------------------------------


def _to_digits(value: Any) -> str:
    """
    Извлекает цифры из входного значения.

    Функция преобразует переданное значение в строку и оставляет только
    цифровые символы. Если в значении нет ни одной цифры, выбрасывается
    исключение ValueError.

    Args:
        value: Входное значение любого типа, которое будет преобразовано
            в строку для извлечения цифр.

    Returns:
        str: Строка, содержащая только цифры из входного значения.

    Raises:
        ValueError: Если во входном значении не найдено ни одной цифры.
    """
    s = str(value)
    digits = "".join(ch for ch in s if ch.isdigit())

    if not digits:
        error_msg = "Value must contain digits"
        logger.error(error_msg)
        raise ValueError(error_msg)

    logger.debug("Successfully extracted digits from value: %r -> %s", value, digits)
    return digits


def mask_card_number(card_number: Any) -> str:
    """
    Маскирует номер карты в формате 'XXXX XX** **** XXXX'.

    Функция извлекает цифры из переданного значения, проверяет, что их ровно 16,
    и возвращает номер карты с маскированными средними цифрами.

    Args:
        card_number: Номер карты (может быть любого типа; будет преобразован
            в строку и очищен от нецифровых символов).

    Returns:
        str: Маскированный номер карты в формате 'XXXX XX** **** XXXX'.

    Raises:
        ValueError: Если после извлечения цифр их количество не равно 16.
        Exception: Пробрасывается дальше, если произошла непредвиденная ошибка
            (с записью в лог через logger.exception).
    """
    try:
        digits = _to_digits(card_number)
        if len(digits) != 16:
            error_msg = f"Card number must contain exactly 16 digits, got {len(digits)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        block1 = digits[:4]
        block2 = digits[4:6]
        block4 = digits[12:16]

        masked = f"{block1} {block2}** **** {block4}"
        logger.info("Card number masked successfully: last 4 digits %s", block4)
        return masked

    except Exception:
        # logger.exception() автоматически добавит информацию об ошибке и стек вызовов
        logger.exception("Error while masking card number for input: %r", card_number)
        raise


def mask_account_number(account_number: Any) -> str:
    """
    Маскирует номер счёта в формате '**XXXX'.

    Функция извлекает цифры из переданного значения, проверяет, что их не менее 4,
    и возвращает последние 4 цифры с префиксом '**'.

    Args:
        account_number: Номер счёта (может быть любого типа; будет преобразован
            в строку и очищен от нецифровых символов).

    Returns:
        str: Маскированный номер счёта в формате '**XXXX', где XXXX — последние
            4 цифры номера.

    Raises:
        ValueError: Если после извлечения цифр их количество меньше 4.
        Exception: Пробрасывается дальше, если произошла непредвиденная ошибка
            (с записью в лог через logger.exception).
    """
    try:
        digits = _to_digits(account_number)
        if len(digits) < 4:
            error_msg = f"Account number must contain at least 4 digits, got {len(digits)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        masked = f"**{digits[-4:]}"
        logger.info("Account number masked successfully: %s", masked)
        return masked

    except Exception:
        logger.exception("Error while masking account number for input: %r", account_number)
        raise


def get_mask_card_number(card_number: Any) -> str:
    """
    Обёртка для получения маскированного номера карты.

    Вызывает mask_card_number и добавляет логирование на уровне вызова.

    Args:
        card_number: Номер карты для маскирования.

    Returns:
        str: Маскированный номер карты.
    """
    logger.debug("Calling get_mask_card_number with input: %r", card_number)
    result = mask_card_number(card_number)
    logger.info("get_mask_card_number returned masked value")
    return result


def get_mask_account(account_number: Any) -> str:
    """
    Обёртка для получения маскированного номера счёта.

    Вызывает mask_account_number и добавляет логирование на уровне вызова.

    Args:
        account_number: Номер счёта для маскирования.

    Returns:
        str: Маскированный номер счёта.
    """
    logger.debug("Calling get_mask_account with input: %r", account_number)
    result = mask_account_number(account_number)
    logger.info("get_mask_account returned masked value")
    return result