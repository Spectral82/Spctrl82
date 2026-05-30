from typing import Any


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
    digits = ''.join(ch for ch in s if ch.isdigit())
    if not digits:
        raise ValueError("Value must contain digits")
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
    digits = _to_digits(card_number)
    if len(digits) != 16:
        raise ValueError("Card number must contain exactly 16 digits")
    block1 = digits[:4]
    block2 = digits[4:6]
    block4 = digits[12:16]
    return f"{block1} {block2}** **** {block4}"

def mask_account_number(account_number: Any) -> str:
    """Mask account number in format '**XXXX'.

    Args:
        account_number: Account number (any type, will be converted to string)

    Returns:
        Masked account number string

    Raises:
        ValueError: If account number contains less than 4 digits
    """
    digits = _to_digits(account_number)
    if len(digits) < 4:
        raise ValueError("Account number must contain at least 4 digits")
    return f"**{digits[-4:]}"

def get_mask_card_number(card_number: Any) -> str:
    """Get masked card number.

    Args:
        card_number: Card number to mask

    Returns:
        Masked card number
    """
    return mask_card_number(card_number)

def get_mask_account(account_number: Any) -> str:
    """Get masked account number.

    Args:
        account_number: Account number to mask

    Returns:
        Masked account number
    """
    return mask_account_number(account_number)