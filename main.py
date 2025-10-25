from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from typing import _NoDefaultType
from database import get_session
from sqlmodel import Session


# @asynccontextmanager
# def lifespan(app:FastAPI)
  

app = FastAPI()


@app.post('/countries/refresh', status_code=200)
async def get_countries_data():
    pass

@app.get('/countries',status_code=200)
async def get_countries():
    pass

@app.get('/countries/{name}' , status_code=200)
async def get_country_by_name(session: Session = Depends(get_session)):
    pass

@app.delete('/countries/{name}')
async def delete_country_by_name():
    pass

@app.get('/status',status_code=200)
async def get_status():
    pass

@app.post('/countries/image',status_code=200)
async def image_summary():
    pass