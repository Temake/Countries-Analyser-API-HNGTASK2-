from sqlmodel import Field, Session, SQLModel, create_engine, select
from datetime import datetime, timezone


    

sqlite_file_name = "database.db"
database_url = f"sqlite:///{sqlite_file_name}"



connect_args = {"check_same_thread": False}
engine = create_engine(database_url, echo=True, connect_args=connect_args,pool_reset_on_return='commit')



def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

    
def get_session():
    with Session(engine) as session:
        yield session