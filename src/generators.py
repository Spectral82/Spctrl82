def filter_by_currency(transactions, currency_code):
    """
    Генератор, фильтрующий транзакции по коду валюты.

    Args:
        transactions (list): Список словарей с транзакциями.
        currency_code (str): Код валюты для фильтрации (например, "USD").

    Yields:
        dict: Транзакция, где валюта операции соответствует заданной.
    """
    for transaction in transactions:
        operation_amount = transaction.get("operationAmount", {})
        currency = operation_amount.get("currency", {})
        if currency.get("code") == currency_code:
            yield transaction


def transaction_descriptions(transactions):
    """
    Генератор, возвращающий описания транзакций по очереди.

    Args:
        transactions (list): Список словарей с транзакциями.

    Yields:
        str: Описание операции.
    """
    for transaction in transactions:
        description = transaction.get("description", "")
        yield description


def card_number_generator(start, end):
    """
    Генератор номеров банковских карт в формате XXXX XXXX XXXX XXXX.

    Args:
        start (int): Начальное значение диапазона (от 1 до 9999999999999999).
        end (int): Конечное значение диапазона (до 9999999999999999), должно быть >= start.

    Yields:
        str: Номер карты в формате "XXXX XXXX XXXX XXXX".
    """
    # Валидация входных данных
    if not (1 <= start <= 9999999999999999):
        raise ValueError("start должен быть в диапазоне от 1 до 9999999999999999")
    if not (1 <= end <= 9999999999999999):
        raise ValueError("end должен быть в диапазоне от 1 до 9999999999999999")
    if start > end:
        return  # Возвращаем пустой итератор для пустого диапазона

    # Корректируем диапазон: включаем конечное значение
    for number in range(start, end + 1):
        # Преобразуем число в строку и дополняем нулями слева до 16 символов
        num_str = f"{number:016d}"
        # Форматируем в нужный вид: разбиваем на группы по 4 символа через пробел
        formatted_number = f"{num_str[:4]} {num_str[4:8]} {num_str[8:12]} {num_str[12:]}"
        yield formatted_number
