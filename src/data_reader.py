import pandas as pd
from typing import Optional, List, Dict, Any


def load_transactions_from_csv(
    path: str,
    sep: str = ";",
    encoding: str = "utf-8"
) -> List[Dict[str, Any]]:
    """
    Загрузить транзакции из CSV-файла и вернуть их в виде списка словарей.

    Функция читает CSV-файл с помощью pandas, при наличии колонки 'date'
    преобразует её значения в datetime с UTC-временем. Некорректные даты
    заменяются на NaT (благодаря errors="coerce"). Результат возвращается
    в формате списка словарей (orient="records"), где каждый словарь —
    одна строка таблицы.

    Параметры
    ---------
    path : str
        Путь к CSV-файлу с транзакциями.
    sep : str, по умолчанию ";"
        Разделитель полей в CSV-файле.
    encoding : str, по умолчанию "utf-8"
        Кодировка файла.

    Возвращает
    ----------
    List[Dict[str, Any]]
        Список словарей, где каждый словарь соответствует одной транзакции.

    Примеры
    --------
    >>> transactions = load_transactions_from_csv("transactions.csv")
    >>> len(transactions)
    100
    >>> transactions[0]["date"]
    Timestamp('2024-01-01 00:00:00+0000', tz='UTC')
    """
    df = pd.read_csv(path, sep=sep, encoding=encoding)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], utc=True, errors="coerce")

    return df.to_dict(orient="records")


def load_transactions_from_excel(
    path: str,
    sheet_name: Optional[str | int] = 0,
    engine: str = "openpyxl"
) -> List[Dict[str, Any]]:
    """
    Загрузить транзакции из Excel-файла и вернуть их в виде списка словарей.

    Функция читает Excel-файл с помощью pandas, при наличии колонки 'date'
    преобразует её значения в datetime с UTC-временем. Некорректные даты
    заменяются на NaT (благодаря errors="coerce"). Результат возвращается
    в формате списка словарей (orient="records"), где каждый словарь —
    одна строка таблицы.

    Параметры
    ---------
    path : str
        Путь к Excel-файлу (xlsx, xlsm и т.п.) с транзакциями.
    sheet_name : Optional[str | int], по умолчанию 0
        Имя или индекс листа, с которого нужно прочитать данные.
        Если None — будут прочитаны все листы (но в текущей реализации
        поддерживается один лист).
    engine : str, по умолчанию "openpyxl"
        Движок для чтения Excel-файлов.

    Возвращает
    ----------
    List[Dict[str, Any]]
        Список словарей, где каждый словарь соответствует одной транзакции.

    Примеры
    --------
    >>> transactions = load_transactions_from_excel("transactions.xlsx")
    >>> len(transactions)
    50
    >>> transactions[0]["amount"]
    1234.56
    """
    df = pd.read_excel(path, sheet_name=sheet_name, engine=engine)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], utc=True, errors="coerce")

    return df.to_dict(orient="records")