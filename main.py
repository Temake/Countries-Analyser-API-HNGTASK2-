from fastapi import FastAPI, Depends, Query, HTTPException
from contextlib import asynccontextmanager
from typing import Optional
from datetime import datetime, timezone
from database import get_session, create_db_and_tables, Country
from sqlmodel import Session, select, func
from utils import (
    fetch_countries_data,
    fetch_exchange_rates,
    get_first_currency_code,
    calculate_estimated_gdp
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="Country Info API", lifespan=lifespan)


@app.post('/countries/refresh', status_code=200)
async def get_countries_data(session: Session = Depends(get_session)):
    try:
        country_data = fetch_countries_data()
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={"error": "External data source unavailable", "details": "Could not fetch data from REST Countries API"}
        )
    
    try:
        exchange_rates = fetch_exchange_rates()
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={"error": "External data source unavailable", "details": "Could not fetch data from Exchange Rate API"}
        )
    
    refresh_timestamp = datetime.now(timezone.utc)
    
    for country_info in country_data:
        name = country_info.get("name")
        capital = country_info.get("capital")
        region = country_info.get("region")
        population = country_info.get("population", 0)
        flag_url = country_info.get("flag")
        currencies = country_info.get("currencies", [])
        currency_code = get_first_currency_code(currencies)
        exchange_rate = exchange_rates.get(currency_code) if currency_code else None
        estimated_gdp = calculate_estimated_gdp(population, exchange_rate)
        
        country = session.exec(
            select(Country).where(func.lower(Country.name) == name.lower())
        ).first()
        
        if country:
            country.capital = capital
            country.region = region
            country.population = population
            country.currency_code = currency_code
            country.exchange_rate = exchange_rate
            country.estimated_gdp = estimated_gdp
            country.flag_url = flag_url
            country.last_refreshed_at = refresh_timestamp
        else:
            country = Country(
                name=name,
                capital=capital,
                region=region,
                population=population,
                currency_code=currency_code,
                exchange_rate=exchange_rate,
                estimated_gdp=estimated_gdp,
                flag_url=flag_url,
                last_refreshed_at=refresh_timestamp
            )
            session.add(country)
    
    session.commit()
    return {"message": "Country data refreshed successfully."}


@app.get('/countries', status_code=200)
async def get_countries(
    region: Optional[str] = Query(None),
    currency: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    session: Session = Depends(get_session)
):
    query = select(Country)
    
    if region:
        query = query.where(Country.region == region)
    
    if currency:
        query = query.where(Country.currency_code == currency)
    
    if sort:
        if sort == "gdp_desc":
            query = query.order_by(Country.estimated_gdp.desc())
        elif sort == "gdp_asc":
            query = query.order_by(Country.estimated_gdp.asc())
        elif sort == "population_desc":
            query = query.order_by(Country.population.desc())
        elif sort == "population_asc":
            query = query.order_by(Country.population.asc())
        elif sort == "name_asc":
            query = query.order_by(Country.name.asc())
        elif sort == "name_desc":
            query = query.order_by(Country.name.desc())
    
    countries = session.exec(query).all()
    return countries


@app.get('/countries/{name}', status_code=200)
async def get_country_by_name(name: str, session: Session = Depends(get_session)):
    pass


@app.delete('/countries/{name}')
async def delete_country_by_name(name: str, session: Session = Depends(get_session)):
    pass


@app.get('/status', status_code=200)
async def get_status(session: Session = Depends(get_session)):
    pass


@app.get('/countries/image', status_code=200)
async def image_summary(session: Session = Depends(get_session)):
    pass