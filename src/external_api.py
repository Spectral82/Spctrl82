import logging
import os
from typing import Optional

import requests

API_URL = "https://api.apilayer.com/exchangerates_data/latest"

# Кэш курсов валют
_RATE_CACHE: dict[str, float] = {}
logger = logging.getLogger(__name__)


def convert_currency(currency: str) -> Optional[float]:
    if not currency or not isinstance(currency, str):
        return None
    currency = currency.upper()
    # Попытаться взять из кэша
    if currency in _RATE_CACHE:
        return _RATE_CACHE[currency]
    api_key = os.getenv("EXCHANGE_RATES_API_KEY")
    if not api_key:
        return None
    try:
        resp = requests.get(
            API_URL,
            params={
                "access_key": api_key,
                "base": currency,
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
        rate = float(rub_rate)
        _RATE_CACHE[currency] = rate
        return rate
    except Exception as e:
        logger.debug("Ошибка получения курса %s: %s", currency, e)
        return None
