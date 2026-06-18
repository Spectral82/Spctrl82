import os
from typing import Optional

import requests

API_URL = "https://api.apilayer.com/exchangerates_data/latest"


def convert_currency(currency: str) -> Optional[float]:
    """
    Получает текущий курс целевой валюты (USD/EUR) к RUB.
    Возвращает курс (сколько рублей за 1 единицу currency),
    либо None при ошибке.
    """
    api_key = os.getenv("EXCHANGE_RATES_API_KEY")
    if not api_key:
        return None

    try:
        resp = requests.get(
            API_URL,
            params={
                "access_key": api_key,
                "base": currency,  # было target_currency — исправлено на currency
                "symbols": "RUB",
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        rates = data.get("rates", {})
        rub_rate = rates.get("RUB")
        if rub_rate is None:
            return None
        return float(rub_rate)
    except Exception:
        return None
