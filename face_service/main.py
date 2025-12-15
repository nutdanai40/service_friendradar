from fastapi import FastAPI, APIRouter
from app.api.v1.endpoints import face
import uvicorn
import os

app = FastAPI(title="Face Recognition Service")

# Create API Router
api_router = APIRouter()
api_router.include_router(face.router, prefix="/face", tags=["face"])

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["root"])
def read_root():
    return {"message": "Face Recognition Service is running"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
