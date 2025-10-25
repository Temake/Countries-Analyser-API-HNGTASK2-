from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CountryResponse(BaseModel):
    id: int
    name: str
    capital: Optional[str] = None
    region: Optional[str] = None
    population: int
    currency_code: Optional[str] = None
    exchange_rate: Optional[float] = None
    estimated_gdp: Optional[float] = None
    flag_url: Optional[str] = None
    last_refreshed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None


class ValidationErrorResponse(BaseModel):
    error: str = "Validation failed"
    details: dict


class StatusResponse(BaseModel):
    total_countries: int
    last_refreshed_at: Optional[str] = None


class MessageResponse(BaseModel):
    message: str
