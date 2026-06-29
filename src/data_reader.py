# src/data_reader.py
"""Модуль data_reader предоставляет функционал для чтения транзакций из CSV и Excel-файлов,
а также фильтрации транзакций по статусу.

Основные возможности:
- загрузка транзакций из CSV-файла (с автоматической конвертацией поля 'date' в datetime);
- загрузка транзакций из Excel-файла (с аналогичной обработкой даты);
- фильтрация списка транзакций по допустимым статусам.

Для работы требуется установленная библиотека pandas.
"""

import pandas as pd
from typing import List, Dict, Any, Optional

AVAILABLE_STATUSES = ["pending", "completed", "failed", "refunded"]


def read_csv_transactions(
    path: str,
    sep: str = ";",
    encoding: str = "utf-8"
) -> List[Dict[str, Any]]:
    """Загрузить транзакции из CSV-файла и вернуть их в виде списка словарей.

    Функция читает CSV-файл с указанными разделителем и кодировкой, преобразует
    столбец 'date' (если присутствует) в формат datetime с UTC-временем.
    Некорректные даты заменяются на NaT (Not a Time).

    Args:
        path (str): Путь к CSV-файлу с транзакциями.
        sep (str, optional): Разделитель полей в CSV-файле. По умолчанию — ";".
        encoding (str, optional): Кодировка файла. По умолчанию — "utf-8".

    Returns:
        List[Dict[str, Any]]: Список словарей, где каждый словарь представляет одну транзакцию.

    Raises:
        FileNotFoundError: Если файл по указанному пути не найден.
        pd.errors.EmptyDataError: Если CSV-файл пуст.
        Exception: Другие возможные ошибки при чтении CSV.
    """
    df = pd.read_csv(path, sep=sep, encoding=encoding)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], utc=True, errors="coerce")
    return df.to_dict(orient="records")


def read_xlsx_transactions(
    path: str,
    sheet_name: Optional[str | int] = 0,
    engine: str = "openpyxl"
) -> List[Dict[str, Any]]:
    """Загрузить транзакции из Excel-файла и вернуть их в виде списка словарей.

    Функция читает Excel-файл с указанным листом и движком, преобразует столбец
    'date' (если присутствует) в формат datetime с UTC-временем.
    Некорректные даты заменяются на NaT.

    Args:
        path (str): Путь к Excel-файлу (.xlsx) с транзакциями.
        sheet_name (Optional[str | int], optional): Имя или индекс листа для чтения.
            По умолчанию — 0 (первый лист).
        engine (str, optional): Движок для чтения Excel. По умолчанию — "openpyxl".

    Returns:
        List[Dict[str, Any]]: Список словарей, где каждый словарь представляет одну транзакцию.

    Raises:
        FileNotFoundError: Если файл по указанному пути не найден.
        ValueError: Если указанный лист не существует в файле.
        Exception: Другие возможные ошибки при чтении Excel.
    """
    df = pd.read_excel(path, sheet_name=sheet_name, engine=engine)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], utc=True, errors="coerce")
    return df.to_dict(orient="records")


def filter_by_status(
    transactions: List[Dict[str, Any]],
    status: str
) -> List[Dict[str, Any]]:
    """Отфильтровать транзакции по статусу.

    Возвращает список транзакций, у которых поле 'status' совпадает с переданным значением.
    Если переданный статус не входит в список допустимых (AVAILABLE_STATUSES),
    функция возвращает пустой список.

    Args:
        transactions (List[Dict[str, Any]]): Список транзакций (словарей) для фильтрации.
        status (str): Статус транзакции для фильтрации (например, "completed").

    Returns:
        List[Dict[str, Any]]: Отфильтрованный список транзакций. Пустой список, если статус недопустим.
    """
    if status not in AVAILABLE_STATUSES:
        return []
    return [t for t in transactions if t.get("status") == status]