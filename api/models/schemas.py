from pydantic import BaseModel
from typing import Optional


class UserRegister(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class WxLogin(BaseModel):
    code: str


class ChangePassword(BaseModel):
    old_password: str
    new_password: str


class UserProfileUpdate(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    goal: Optional[str] = None
    dietary: Optional[str] = None
    life_stage: Optional[str] = None
    cycle_phase: Optional[str] = None
    fitness_level: Optional[str] = None


class UserOut(BaseModel):
    id: int
    username: str
    age: Optional[int]
    gender: Optional[str]
    height: Optional[float]
    weight: Optional[float]
    goal: Optional[str]
    dietary: Optional[str]
    life_stage: Optional[str]
    cycle_phase: Optional[str]
    fitness_level: Optional[str]

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class ChatRequest(BaseModel):
    query: str
    user_profile: Optional[dict] = None
    chat_history: Optional[list] = None


class ChatResponse(BaseModel):
    answer: str