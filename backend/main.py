from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Session, create_engine, select, Field
from pydantic import BaseModel
from typing import Optional, List
import requests

app = FastAPI()

# 1. CORS Settings (Frontend se connection ke liye)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Database Setup
DATABASE_URL = "sqlite:///./todo.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# 3. Aapki Verified API Key
API_KEY = "AIzaSyCWaKYy46jU9n7_5AyMlWN6n9RzKRUBAYw"

# 4. Database Model
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    completed: bool = False

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# 5. Routes
@app.get("/api/tasks")
def get_tasks():
    with Session(engine) as session:
        return session.exec(select(Task)).all()

@app.post("/api/chat")
async def chat_with_tasks(user_message: str = Query(...)):
    try:
        # Context ke liye database se tasks nikaalna
        with Session(engine) as session:
            tasks = session.exec(select(Task)).all()
            task_info = ", ".join([t.title for t in tasks]) or "No tasks currently."

        # VERIFIED MODEL: Aapki list ke mutabiq Gemini 2.5 Flash set kar diya hai
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{"text": f"System: User has these tasks: {task_info}. Answer based on this. User: {user_message}"}]
            }]
        }

        # Request bhej rahe hain
        response = requests.post(url, json=payload, timeout=15)
        data = response.json()

        if response.status_code == 200:
            # AI ka jawab extract karna
            ai_reply = data['candidates'][0]['content']['parts'][0]['text']
            return {"response": ai_reply}
        else:
            # Error handling agar Google ki taraf se kuch masla ho
            print(f"DEBUG ERROR: {data}")
            return {"response": f"Google Error: {data.get('error', {}).get('message', 'Unknown Error')}"}

    except Exception as e:
        return {"response": f"Backend Error: {str(e)}"}

# 6. Debugging Routes
@app.get("/api/test-ai")
def test_ai():
    # Seedha test karne ke liye: http://127.0.0.1:8000/api/test-ai
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
    payload = {"contents": [{"parts": [{"text": "Say Hello"}]}]}
    try:
        res = requests.post(url, json=payload, timeout=10)
        return res.json()
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/list-models")
def list_models():
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
    res = requests.get(url)
    return res.json()