from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.rag_pipeline import ask

app = FastAPI(title="FitRAG API", version="1.0.0")

# 允许跨域（小程序调用需要）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求格式
class ChatRequest(BaseModel):
    query: str
    user_profile: Optional[dict] = None


# 响应格式
class ChatResponse(BaseModel):
    answer: str


@app.get("/")
def root():
    return {"status": "ok", "message": "FitRAG API is running!"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    answer = ask(request.query, request.user_profile)
    return ChatResponse(answer=answer)