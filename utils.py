import requests
import random
from typing import Optional
# from config import get_settings

# settings = get_settings()


import requests
import random
from typing import Optional
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os


def fetch_countries_data():
    try:
        response = requests.get(
            'https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies',
            timeout=30
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
            'https://open.er-api.com/v6/latest/USD',
            timeout=30
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


def calculate_estimated_gdp(population: int, exchange_rate: Optional[float], currency_code: Optional[str]) -> Optional[float]:
    if currency_code is None:
        return 0.0
    if exchange_rate is None:
        return None
    if exchange_rate == 0:
        return None
    multiplier = random.uniform(1000, 2000)
    return (population * multiplier) / exchange_rate


def generate_summary_image(total_countries: int, top_countries: list, last_refreshed: str):
    img_width = 800
    img_height = 600
    bg_color = (255, 255, 255)
    text_color = (0, 0, 0)
    
    image = Image.new('RGB', (img_width, img_height), bg_color)
    draw = ImageDraw.Draw(image)
    
    try:
        font_large = ImageFont.truetype("arial.ttf", 36)
        font_medium = ImageFont.truetype("arial.ttf", 24)
        font_small = ImageFont.truetype("arial.ttf", 18)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    y_position = 50
    
    draw.text((50, y_position), "Country Data Summary", fill=text_color, font=font_large)
    y_position += 80
    
    draw.text((50, y_position), f"Total Countries: {total_countries}", fill=text_color, font=font_medium)
    y_position += 60
    
    draw.text((50, y_position), "Top 5 Countries by GDP:", fill=text_color, font=font_medium)
    y_position += 40
    
    for i, country in enumerate(top_countries[:5], 1):
        gdp_formatted = f"{country.estimated_gdp:,.2f}" if country.estimated_gdp else "0.00"
        text = f"{i}. {country.name}: ${gdp_formatted}"
        draw.text((70, y_position), text, fill=text_color, font=font_small)
        y_position += 35
    
    y_position += 30
    draw.text((50, y_position), f"Last Refreshed: {last_refreshed}", fill=text_color, font=font_small)
    
    os.makedirs("cache", exist_ok=True)
    image.save("cache/summary.png")

