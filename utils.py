import requests
import random
from typing import Optional
from config import get_settings

settings = get_settings()


def fetch_countries_data():
    try:
        response = requests.get(
            settings.countries_api_url,
            timeout=settings.api_timeout
        )
        response.raise_for_status()
        return response.json()
    except requests.Timeout:
        raise Exception("Countries API timeout")
    except requests.RequestException as e:
        raise Exception(f"Countries API error: {str(e)}")


def fetch_exchange_rates():
    try:
        response = requests.get(
            settings.exchange_rate_api_url,
            timeout=settings.api_timeout
        )
        response.raise_for_status()
        data = response.json()
        return data.get("rates", {})
    except requests.Timeout:
        raise Exception("Exchange rate API timeout")
    except requests.RequestException as e:
        raise Exception(f"Exchange rate API error: {str(e)}")


def get_first_currency_code(currencies: list) -> Optional[str]:
    if not currencies or len(currencies) == 0:
        return None
    first_currency = currencies[0]
    return first_currency.get("code")


def calculate_estimated_gdp(population: int, exchange_rate: Optional[float]) -> Optional[float]:
    if exchange_rate is None or exchange_rate == 0:
        return None
    multiplier = random.uniform(1000, 2000)
    return (population * multiplier) / exchange_rate
