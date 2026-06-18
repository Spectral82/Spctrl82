from datetime import datetime


def mask_card_number(card_number: str) -> str:
    """
    Маскирует номер карты: первые 4, две цифры, потом ** ****, последние 4 цифры.
    """
    return f"{card_number[:4]} {card_number[4:6]}** **** {card_number[-4:]}"


def mask_account_number(account_number: str) -> str:
    """
    Маскирует номер счёта: только последние 4 цифры.
    """
    return f"**{account_number[-4:]}"


def mask_account_card(info: str) -> str:
    """
    Принимает строку с номером карты или счёта, возвращает строку с замаскированным номером.
    Для карт: 16 цифр, маскируется как 1234 56** **** 3456
    Для счетов: 20 цифр, маскируется как **XXXX
    """
    # Удаляем все нецифровые символы
    cleaned = "".join(c for c in info if c.isdigit())

    # Валидация: должны быть только цифры после очистки
    if not cleaned:
        raise ValueError("Invalid input: no digits found")

    # Определяем тип по длине
    if len(cleaned) == 16:
        # Карта: маскируем первые 6 цифр, показываем последние 4
        masked = f"{cleaned[:4]} {cleaned[4:6]}** **** {cleaned[-4:]}"
        return masked
    elif len(cleaned) == 20:
        # Счёт: показываем только последние 4 цифры
        masked = f"**{cleaned[-4:]}"
        return masked
    else:
        raise ValueError(f"Invalid number length: {len(cleaned)}. Expected 16 (card) or 20 (account)")


def get_date(date_string: str) -> str:
    """
    Преобразует строку с датой в формат YYYY-MM-DD.

    Поддерживает форматы:
    - 2023-01-01
    - 01/01/2023
    - January 1, 2023
    - 2023-01-01T00:00:00

    :param date_string: str — входная строка с датой
    :return: str — дата в формате YYYY-MM-DD
    :raises ValueError: если формат даты не распознан
    """
    formats = [
        "%Y-%m-%d",  # 2023-01-01
        "%d/%m/%Y",  # 01/01/2023
        "%B %d, %Y",  # January 1, 2023
        "%b %d, %Y",  # Jan 1, 2023
        "%Y-%m-%dT%H:%M:%S",  # 2023-01-01T00:00:00
    ]

    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_string, fmt)
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            continue

    raise ValueError(f"Invalid date format: {date_string}")
