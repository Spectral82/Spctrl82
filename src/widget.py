from datetime import datetime


def mask_card_number(card_number: str) -> str:
    # Маскирует номер карты: первые 4, две цифры, потом ** ****, последние 4 цифры
    return f"{card_number[:4]} {card_number[4:6]}** **** {card_number[-4:]}"


def mask_account_number(account_number: str) -> str:
    # Маскирует номер счёта: только последние 4 цифры
    return f"**{account_number[-4:]}"


def mask_account_card(info: str) -> str:
    """
    Принимает строку с типом и номером карты или счёта, возвращает строку с замаскированным номером.
    """
    # Проверяем, начинается ли строка со слова 'Счет'
    if info.startswith('Счет'):
        parts = info.split()
        if len(parts) != 2:
            return info  # Некорректный формат, возвращаем как есть
        masked = mask_account_number(parts[1])
        return f"Счет {masked}"
    else:
        # Для карт: последние 16 символов — это номер карты
        parts = info.rsplit(' ', 1)
        if len(parts) != 2:
            return info  # Некорректный формат, возвращаем как есть
        card_name, card_number = parts
        masked = mask_card_number(card_number)
        return f"{card_name} {masked}"


def get_date(date_str: str) -> str:
    """
    Принимает строку с датой в формате '2024-03-11T02:26:18.671407' и возвращает '11.03.2024'
    """
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime('%d.%m.%Y')
    except ValueError:
        return date_str  # Если формат неправильный, возвращаем как есть
