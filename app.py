import os
from pydantic import BaseModel

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from google.adk.sessions import DatabaseSessionService
from google.adk.runners import Runner

from agent.root_agent import root_agent
from utilities import run_session   

app = FastAPI()

# cors - to allow all frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# persistent session database setup (inside data/ folder)
os.makedirs("data", exist_ok=True)
DB_URL = "sqlite+aiosqlite:///data/sessions.db"   # SQLite URL for session storage (automatically creates file if not exists)

# Initialize the session service
session_service = DatabaseSessionService(db_url=DB_URL)

# Initialize the ADK Runner with the root agent and session service
# NOTE: a runner instance is created everytime the app is loaded with uvicorn
runner = Runner(
    app_name="pardon_me",
    agent=root_agent,
    session_service=session_service
)
print(" Runner instance created with name:", runner.app_name)

# serve static files (UI) at "/" endpoint
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", include_in_schema=False)
def root():
    index = os.path.join("static", "index.html")
    if os.path.exists(index):
        return FileResponse(index)
    return {"status": "ok", "message": "UI not found. Add static/index.html"}

# Python object for user message payload (required for FastAPI) - using pydantic
class UserMessage(BaseModel):
    message: str
    session_id: str

# main API endpoint 'to ask' the agent
@app.post("/ask")
async def ask_agent(payload: UserMessage):
    response_text = await run_session(
        runner,
        payload.message,
        payload.session_id
    )
    return {"response": response_text}
