import json
from typing import Any, Dict, List, Optional
import pandas as pd

AVAILABLE_STATUSES = ["EXECUTED", "CANCELED", "PENDING"]


def read_csv_transactions(path: str, sep: str = ";", encoding: str = "utf-8") -> List[Dict[str, Any]]:
    df = pd.read_csv(path, sep=sep, encoding=encoding)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], utc=True, errors="coerce")
    return df.to_dict(orient="records")


def read_xlsx_transactions(
    path: str, sheet_name: Optional[str | int] = 0, engine: str = "openpyxl"
) -> List[Dict[str, Any]]:
    df = pd.read_excel(path, sheet_name=sheet_name, engine=engine)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], utc=True, errors="coerce")
    return df.to_dict(orient="records")


def read_json_transactions(file_path: str) -> List[Dict[str, Any]]:
    """Читает транзакции из JSON-файла и возвращает список словарей."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Если JSON — это список транзакций, возвращаем как есть
    if isinstance(data, list):
        return data
    # Если это объект с ключом, например {"transactions": [...]}
    return data.get("transactions", [])


def filter_by_status(transactions: List[Dict[str, Any]], status: str) -> List[Dict[str, Any]]:
    normalized_status = status.strip().upper()
    if normalized_status not in AVAILABLE_STATUSES:
        return []
    return [
        t for t in transactions
        if str(t.get("status", "")).strip().upper() == normalized_status
    ]