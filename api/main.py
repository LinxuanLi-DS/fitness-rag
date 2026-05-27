from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.rag_pipeline import ask
from api.routers.users import router as users_router

app = FastAPI(title="FitRAG API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(users_router)


class ChatRequest(BaseModel):
    query: str
    user_profile: Optional[dict] = None


class ChatResponse(BaseModel):
    answer: str


@app.get("/")
def root():
    return {"status": "ok", "message": "FitRAG API is running!"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    answer = ask(request.query, request.user_profile)
    return ChatResponse(answer=answer)