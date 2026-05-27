from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from api.routers.users import router as users_router
from api.routers.chat import router as chat_router

app = FastAPI(title="FitRAG API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)
app.include_router(chat_router)


@app.get("/")
def root():
    return {"status": "ok", "message": "FitRAG API is running!"}