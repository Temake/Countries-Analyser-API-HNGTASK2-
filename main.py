from fastapi import FastAPI, Depends, Query, HTTPException, status
from fastapi.responses import FileResponse, JSONResponse
from contextlib import asynccontextmanager
from typing import Optional
from datetime import datetime, timezone
from database import get_session, create_db_and_tables, Country
from sqlmodel import Session, select, func
from utils import (
    fetch_countries_data,
    fetch_exchange_rates,
    get_first_currency_code,
    calculate_estimated_gdp,
    generate_summary_image
)
from schemas import (
    CountryResponse,
    ErrorResponse,
    StatusResponse,
    MessageResponse
)
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Country Info API",
    description="RESTful API for country data with currency exchange rates",
    version="1.0.0",
    lifespan=lifespan
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error"}
    )


@app.post(
    '/countries/refresh',
    status_code=200,
    response_model=MessageResponse,
    responses={
        503: {"model": ErrorResponse, "description": "External API unavailable"}
    }
)
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
    
    total_countries = session.exec(select(func.count(Country.id))).first()
    top_countries = session.exec(
        select(Country).order_by(Country.estimated_gdp.desc()).limit(5)
    ).all()
    last_refreshed_str = refresh_timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
    
    generate_summary_image(total_countries, top_countries, last_refreshed_str)
    
    return {"message": "Country data refreshed successfully."}


@app.get(
    '/countries',
    status_code=200,
    response_model=list[CountryResponse],
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
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


@app.get(
    '/countries/image',
    status_code=200,
    responses={
        404: {"model": ErrorResponse, "description": "Image not found"}
    }
)
async def image_summary():
    image_path = "cache/summary.png"
    
    if not os.path.exists(image_path):
        raise HTTPException(
            status_code=404,
            detail={"error": "Summary image not found"}
        )
    
    return FileResponse(image_path, media_type="image/png")


@app.get(
    '/countries/{name}',
    status_code=200,
    response_model=CountryResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Country not found"}
    }
)
async def get_country_by_name(name: str, session: Session = Depends(get_session)):
    country = session.exec(
        select(Country).where(func.lower(Country.name) == name.lower())
    ).first()
    
    if not country:
        raise HTTPException(
            status_code=404,
            detail={"error": "Country not found", "details": f"No data found for country '{name}'"}
        )
    
    return country


@app.delete(
    '/countries/{name}',
    status_code=200,
    response_model=MessageResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Country not found"}
    }
)
async def delete_country_by_name(name: str, session: Session = Depends(get_session)):
    country = session.exec(
        select(Country).where(func.lower(Country.name) == name.lower())
    ).first()
    
    if not country:
        raise HTTPException(
            status_code=404,
            detail={"error": "Country not found", "details": f"No data found for country '{name}'"}
        )
    
    session.delete(country)
    session.commit()
    return {"message": "Country deleted successfully."}


@app.get(
    '/status',
    status_code=200,
    response_model=StatusResponse
)
async def get_status(session: Session = Depends(get_session)):
    total_countries = session.exec(select(func.count(Country.id))).first()
    last_refreshed_at = session.exec(select(func.max(Country.last_refreshed_at))).first()
    
    return {
        "total_countries": total_countries or 0,
        "last_refreshed_at": last_refreshed_at.isoformat() if last_refreshed_at else None
    }