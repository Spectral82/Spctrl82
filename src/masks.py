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
    """Extract digits from input value.

    Args:
        value: Input value of any type

    Returns:
        String containing only digits from input

    Raises:
        ValueError: If no digits found in input
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
    """Mask card number in format 'XXXX XX** **** XXXX'.

    Args:
        card_number: Card number (any type, will be converted to string)

    Returns:
        Masked card number string

    Raises:
        ValueError: If card number doesn't contain exactly 16 digits
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
        # logger.exception() сам добавит информацию об ошибке и стек вызовов
        logger.exception("Error while masking card number for input: %r", card_number)
        raise


def mask_account_number(account_number: Any) -> str:
    """Mask account number in format '**XXXX'.

    Args:
        account_number: Account number (any type, will be converted to string)

    Returns:
        Masked account number string

    Raises:
        ValueError: If account number contains less than 4 digits
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
    """Get masked card number.

    Args:
        card_number: Card number to mask

    Returns:
        Masked card number
    """
    logger.debug("Calling get_mask_card_number with input: %r", card_number)
    result = mask_card_number(card_number)
    logger.info("get_mask_card_number returned masked value")
    return result


def get_mask_account(account_number: Any) -> str:
    """Get masked account number.

    Args:
        account_number: Account number to mask

    Returns:
        Masked account number
    """
    logger.debug("Calling get_mask_account with input: %r", account_number)
    result = mask_account_number(account_number)
    logger.info("get_mask_account returned masked value")
    return result