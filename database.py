from sqlmodel import Field, Session, SQLModel, create_engine, select
from datetime import datetime, timezone
from config import config

class Country(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)  
    capital: str | None = None
    region: str | None = Field(default=None, index=True)  
    population: int  
    currency_code: str | None = Field(default=None, index=True)  
    exchange_rate: float | None = None
    estimated_gdp: float | None = None
    flag_url: str | None = None
    last_refreshed_at: datetime | None = None
    
sqlite_file_name = "database.db"
print("Database URL:", config.DATABASE_URL)
database_url = config.DATABASE_URL

if config.ENV_STATE == 'prod':
     engine = create_engine(database_url, echo=True,)

else:

    connect_args = {"check_same_thread": False}
    engine = create_engine(database_url, echo=True, connect_args=connect_args,)



def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

    
def get_session():
    with Session(engine) as session:
        yield session