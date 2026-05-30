from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from api.models.user import User, get_db
from api.models.schemas import ChatRequest, ChatResponse
from src.rag_pipeline import ask, retrieve, build_prompt, qwen

router = APIRouter(prefix="/chat", tags=["chat"])
security = HTTPBearer(auto_error=False)

SECRET_KEY = os.getenv("SECRET_KEY", "fitrag-secret-2024")
ALGORITHM = "HS256"

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    if not credentials:
        return None
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        return db.query(User).filter(User.id == user_id).first()
    except:
        return None

def build_user_profile(user):
    if not user:
        return None
    return {
        "gender": user.gender, "age": user.age,
        "height": user.height, "weight": user.weight,
        "goal": user.goal, "dietary": user.dietary,
        "life_stage": user.life_stage, "cycle_phase": user.cycle_phase,
        "fitness_level": user.fitness_level,
    }

def merge_profiles(frontend_profile, db_profile):
    """合并前端传来的profile和数据库的profile，前端优先"""
    if not db_profile:
        return frontend_profile
    if not frontend_profile:
        return db_profile
    merged = {**db_profile}
    for k, v in frontend_profile.items():
        if v is not None and v != "":
            merged[k] = v
    return merged

@router.post("", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    # 合并前端和数据库的profile，确保总有profile
    frontend_profile = request.user_profile
    db_profile = build_user_profile(current_user)
    profile = merge_profiles(frontend_profile, db_profile)

    # 从前端传来的profile中获取助手ID
    assistant_id = "xiaokang"
    if frontend_profile and "assistant" in frontend_profile:
        assistant_id = frontend_profile["assistant"]

    answer = ask(request.query, profile, assistant_id=assistant_id, chat_history=request.chat_history)
    return ChatResponse(answer=answer)


@router.post("/stream")
def chat_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """流式输出聊天回复 (SSE)"""
    frontend_profile = request.user_profile
    db_profile = build_user_profile(current_user)
    profile = merge_profiles(frontend_profile, db_profile)

    assistant_id = "xiaokang"
    if frontend_profile and "assistant" in frontend_profile:
        assistant_id = frontend_profile["assistant"]

    def generate():
        # 检索知识库
        foods, exercises = retrieve(request.query)
        prompt = build_prompt(request.query, foods, exercises, profile, assistant_id, request.chat_history)

        # 流式调用 Qwen
        stream = qwen.chat.completions.create(
            model="qwen-plus",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
        import json as _json
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                # 用JSON编码内容，避免换行符破坏SSE协议
                yield f"data: {_json.dumps(delta.content, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")