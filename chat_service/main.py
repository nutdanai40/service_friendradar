from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app.api.v1.endpoints import chat
import uvicorn
import os

app = FastAPI(title="Chat Service")

# Create API Router
api_router = APIRouter()
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Mount static files
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", tags=["root"])
def read_root():
    return {"message": "Chat Service is running"}

@app.get("/chat-ui", response_class=HTMLResponse, tags=["ui"])
async def chat_page():
    """Serve chat interface"""
    with open("static/chat.html", "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
