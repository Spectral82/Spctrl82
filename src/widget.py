from datetime import datetime


def mask_card_number(card_number: str) -> str:
    """
    Маскирует номер банковской карты по шаблону: первые 4 цифры, затем 2 цифры,
    далее звёздочки и последние 4 цифры.

    Пример результата: «1234 56** **** 3456».

    Args:
        card_number (str): Исходный номер карты (строка, содержащая цифры).

    Returns:
        str: Замаскированный номер карты в формате «XXXX XX** **** XXXX».

    Raises:
        IndexError: Если длина номера карты меньше 8 символов (недостаточно цифр
            для корректной маскировки).
    """
    return f"{card_number[:4]} {card_number[4:6]}** **** {card_number[-4:]}"


def mask_account_number(account_number: str) -> str:
    """
    Маскирует номер счёта, оставляя видимыми только последние 4 цифры.

    Пример результата: «**1234».

    Args:
        account_number (str): Исходный номер счёта (строка, содержащая цифры).

    Returns:
        str: Замаскированный номер счёта в формате «**XXXX».

    Raises:
        IndexError: Если длина номера счёта меньше 4 символов.
    """
    return f"**{account_number[-4:]}"


def mask_account_card(info: str) -> str:
    """
    Автоматически определяет тип номера (карта или счёт) по длине и маскирует его.

    Поддерживает входные данные с любыми разделителями (пробелы, тире и т. п.):
    все нецифровые символы удаляются перед обработкой.

    Логика определения типа:
        - 16 цифр — номер карты: маскируется как «XXXX XX** **** XXXX».
        - 20 цифр — номер счёта: маскируется как «**XXXX» (только последние 4 цифры).

    Примеры:
        - Ввод: «1234-5678-9012-3456» → вывод: «1234 56** **** 3456».
        - Ввод: «000011112222333344445555» → вывод: «**4444».

    Args:
        info (str): Строка, содержащая номер карты или счёта (может включать
            разделители и лишние символы).

    Returns:
        str: Замаскированная строка в соответствии с типом номера.

    Raises:
        ValueError: Если после очистки от нецифровых символов строка пуста
            или длина числа не равна 16 (карта) или 20 (счёт).
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
        raise ValueError(
            f"Invalid number length: {len(cleaned)}. "
            "Expected 16 digits for card or 20 digits for account."
        )


def get_date(date_string: str) -> str:
    """
    Преобразует строку с датой в канонический формат YYYY‑MM‑DD.

    Поддерживаемые входные форматы:
        - «2023-01-01» (%Y-%m-%d)
        - «01/01/2023» (%d/%m/%Y)
        - «January 1, 2023» (%B %d, %Y)
        - «Jan 1, 2023» (%b %d, %Y)
        - «2023-01-01T00:00:00» (%Y-%m-%dT%H:%M:%S)

    Функция последовательно пробует каждый формат; первый успешный результат
    возвращается в виде строки «YYYY-MM-DD».

    Args:
        date_string (str): Входная строка с датой в одном из поддерживаемых форматов.

    Returns:
        str: Дата в формате YYYY-MM-DD.

    Raises:
        ValueError: Если ни один из поддерживаемых форматов не подошёл к входной строке.
    """
    formats = [
        "%Y-%m-%d",          # 2023-01-01
        "%d/%m/%Y",         # 01/01/2023
        "%B %d, %Y",        # January 1, 2023
        "%b %d, %Y",        # Jan 1, 2023
        "%Y-%m-%dT%H:%M:%S",# 2023-01-01T00:00:00
    ]

    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_string, fmt)
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            continue

    raise ValueError(f"Invalid date format: {date_string}")