import os
from typing import Union
from pydantic import BaseModel

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from google.adk.sessions import DatabaseSessionService
from google.adk.runners import Runner

from pardon_me.root_agent import root_agent
from utilities import run_session   

app = FastAPI()

# persistent session database setup
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(PROJECT_DIR, "data")
os.makedirs(DB_DIR, exist_ok=True)

DB_PATH = os.path.join(DB_DIR, "sessions.db")
DB_URL = f"sqlite+aiosqlite:///{DB_PATH}"

# Initialize the session service
session_service = DatabaseSessionService(db_url=DB_URL)

# Initialize the ADK Runner with the root agent and session service
runner = Runner(
    agent=root_agent,
    app_name="pardon_me",
    session_service=session_service
)

# cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


# serve static files (UI)
STATIC_DIR = os.path.join(PROJECT_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", include_in_schema=False)
def root():
    index = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index):
        return FileResponse(index)
    return {"status": "ok", "message": "UI not found. Add static/index.html"}


class UserMessage(BaseModel):
    message: Union[str, list]
    session_id: str

# main API endpoint to ask the agent
@app.post("/ask")
async def ask_agent(payload: UserMessage):
    response_text = await run_session(
        runner,
        payload.message,
        payload.session_id
    )
    return {"response": response_text}
