from sqlmodel import Field, Session, SQLModel, create_engine, select
from datetime import datetime, timezone

class Country(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    capital: str | None = None
    population: int | None = None
    currency_code: str | None = None
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