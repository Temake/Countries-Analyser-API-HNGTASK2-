from sqlmodel import Field, Session, SQLModel, create_engine, select
from datetime import datetime, timezone
from config import get_settings


class Country(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)  # Required, indexed for fast lookups
    capital: str | None = None
    region: str | None = Field(default=None, index=True)  # Added missing field, indexed for filtering
    population: int  # Required field (not nullable)
    currency_code: str | None = Field(default=None, index=True)  # Indexed for filtering
    exchange_rate: float | None = None
    estimated_gdp: float | None = None
    flag_url: str | None = None
    last_refreshed_at: datetime | None = None
    
sqlite_file_name = "database.db"
database_url = f"sqlite:///{sqlite_file_name}"



connect_args = {"check_same_thread": False}
engine = create_engine(database_url, echo=True, connect_args=connect_args,pool_reset_on_return='commit')



def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

    
def get_session():
    with Session(engine) as session:
        yield session