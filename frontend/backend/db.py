from sqlmodel import SQLModel, create_engine

DATABASE_URL = "postgresql://postgres:123@localhost:5432/postgres"

engine = create_engine(DATABASE_URL)

def init_db():
    SQLModel.metadata.create_all(engine)
