import requests

COUNTRY_URL = " https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies"

async def get_country():
    response= requests.post(COUNTRY_URL)
    return response.json()

