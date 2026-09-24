import os
import asyncio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from google.adk.apps import App
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-02-98210aa7ee5c")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")

app = FastAPI(title="SousChef AI Frontend")

static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

from app.agent import root_agent
adk_app = App(name="souschef", root_agent=root_agent)
session_service = InMemorySessionService()
runner = Runner(app=adk_app, session_service=session_service)

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default_session"

@app.get("/", response_class=HTMLResponse)
async def read_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>SousChef AI Frontend</h1>"

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        session = await session_service.get_session(app_name="souschef", user_id="user", session_id=req.session_id)
        if not session:
            session = await session_service.create_session(app_name="souschef", user_id="user", session_id=req.session_id)

        content = types.Content(parts=[types.Part.from_text(text=req.message)])
        final_text = ""
        async for ev in runner.run_async(user_id="user", session_id=session.id, new_message=content):
            if hasattr(ev, "content") and ev.content:
                for part in getattr(ev.content, "parts", []) or []:
                    if getattr(part, "text", None):
                        final_text += part.text

        return {"reply": final_text or "Processed successfully."}
    except Exception as e:
        return {"reply": f"SousChef AI Error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
