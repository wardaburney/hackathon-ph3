from sqlmodel import SQLModel, Field
from datetime import datetime

class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    email: str
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Task(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: str
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
