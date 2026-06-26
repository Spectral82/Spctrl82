
import pandas as pd
from typing import Optional

def load_transactions_from_csv(
    path: str,
    sep: str = ";",
    encoding: str = "utf-8"
) -> pd.DataFrame:
    df = pd.read_csv(path, sep=sep, encoding=encoding)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], utc=True, errors="coerce")

    return df


def load_transactions_from_excel(
    path: str,
    sheet_name: Optional[str | int] = 0,
    engine: str = "openpyxl"
) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name=sheet_name, engine=engine)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], utc=True, errors="coerce")

    return df