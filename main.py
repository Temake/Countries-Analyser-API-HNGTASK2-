from fastapi import FastAPI, Depends, Query
from contextlib import asynccontextmanager
from typing import Optional
from database import get_session, create_db_and_tables
from sqlmodel import Session






@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    create_db_and_tables()
    yield
    
  

app = FastAPI(title="Country Info API",lifespan=lifespan)


@app.post('/countries/refresh', status_code=200)
async def get_countries_data(session: Session = Depends(get_session)):
    pass

@app.get('/countries',status_code=200)
async def get_countries(region : Optional[str] = Query(None), session: Session = Depends(get_session)):
    pass

@app.get('/countries/{name}' , status_code=200)
async def get_country_by_name(name: str, session: Session = Depends(get_session)):
    pass

@app.delete('/countries/{name}')
async def delete_country_by_name(name: str, session: Session = Depends(get_session)):
    pass

@app.get('/status',status_code=200)
async def get_status(session: Session = Depends(get_session)):
    pass

@app.post('/countries/image',status_code=200)
async def image_summary(session: Session = Depends(get_session)):
    pass