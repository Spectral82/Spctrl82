def get_mask_card_number(card_number: str) -> str:
    """
    Маскирует номер банковской карты в формате XXXX XX** **** XXXX.
    Показывает первые 6 и последние 4 цифры, остальные скрывает.
    """
    digits = ''.join(filter(str.isdigit, card_number))
    if len(digits) != 16:
        raise ValueError("Номер карты должен содержать 16 цифр")
    return f"{digits[:4]} {digits[4:6]}** **** {digits[-4:]}"


def get_mask_account(account_number: str) -> str:
    """
    Маскирует номер банковского счёта в формате **XXXX (последние 4 цифры).
    """
    digits = ''.join(filter(str.isdigit, account_number))
    if len(digits) < 4:
        raise ValueError("Номер счёта должен содержать хотя бы 4 цифры")
    return f"**{digits[-4:]}"
