from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Optional
from datetime import datetime
from fastapi.openapi.utils import get_openapi
from auth import verify_token  # ensure this function verifies JWT and returns user_id

# ---------------- APP ----------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- DATABASE ----------------
DATABASE_URL = "sqlite:///./todo.db"
engine = create_engine(DATABASE_URL, echo=True)

# ---------------- MODELS ----------------
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    completed: bool = False
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskCreate(SQLModel):
    title: str
    description: Optional[str] = None


class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

# ---------------- SECURITY ----------------
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_id = verify_token(token)  # return user_id if valid, else None
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id

# ---------------- DB INIT ----------------
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# ---------------- ROUTES ----------------

@app.get("/api/tasks")
def get_tasks(user_id: str = Depends(get_current_user)):
    with Session(engine) as session:
        tasks = session.exec(select(Task).where(Task.user_id == user_id)).all()
        return tasks

@app.get("/api/tasks/{task_id}")
def get_single_task(task_id: int, user_id: str = Depends(get_current_user)):
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        if task.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        return task

@app.post("/api/tasks")
def create_task(task_data: TaskCreate, user_id: str = Depends(get_current_user)):
    with Session(engine) as session:
        task = Task(title=task_data.title, description=task_data.description, user_id=user_id)
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

@app.put("/api/tasks/{task_id}")
def update_task(task_id: int, task_data: TaskUpdate, user_id: str = Depends(get_current_user)):
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        if task.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        if task_data.title is not None:
            task.title = task_data.title
        if task_data.description is not None:
            task.description = task_data.description
        if task_data.completed is not None:
            task.completed = task_data.completed
        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

@app.patch("/api/tasks/{task_id}/complete")
def toggle_task_complete(task_id: int, user_id: str = Depends(get_current_user)):
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        if task.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        task.completed = not task.completed
        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()
        session.refresh(task)
        return {"id": task.id, "completed": task.completed}

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int, user_id: str = Depends(get_current_user)):
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        if task.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        session.delete(task)
        session.commit()
        return {"message": "Task deleted successfully"}

# ---------------- CUSTOM OPENAPI (Swagger Authorize) ----------------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Task API",
        version="1.0.0",
        description="Task Manager API with JWT Auth",
        routes=app.routes,
    )
    # JWT Security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }
    # Apply security globally
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
