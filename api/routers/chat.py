from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from api.models.user import User, get_db
from api.models.schemas import ChatRequest, ChatResponse
from src.rag_pipeline import ask

router = APIRouter(prefix="/chat", tags=["chat"])
security = HTTPBearer(auto_error=False)

SECRET_KEY = os.getenv("SECRET_KEY", "fitrag-secret-2024")
ALGORITHM = "HS256"


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """从 token 中解析用户，没有 token 也允许（匿名使用）"""
    if not credentials:
        return None
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        return db.query(User).filter(User.id == user_id).first()
    except (JWTError, Exception):
        return None


def build_user_profile(user: User) -> dict:
    """把数据库用户对象转成 RAG pipeline 用的 dict"""
    if not user:
        return None
    return {
        "gender": user.gender,
        "age": user.age,
        "height": user.height,
        "weight": user.weight,
        "goal": user.goal,
        "dietary": user.dietary,
        "life_stage": user.life_stage,
        "cycle_phase": user.cycle_phase,
        "fitness_level": user.fitness_level,
    }


@router.post("", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    # 优先用请求里带的 user_profile，没有就从数据库读
    profile = request.user_profile or build_user_profile(current_user)
    answer = ask(request.query, profile)
    return ChatResponse(answer=answer)