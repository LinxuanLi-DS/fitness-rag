"""反馈路由 - 提交到SQLite"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from api.models.user import get_db, Base, engine
from sqlalchemy import Column, Integer, String, Text, DateTime

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackIn(BaseModel):
    tags: Optional[List[str]] = None
    detail: Optional[str] = None
    contact: Optional[str] = None


class FeedbackRecord(Base):
    __tablename__ = "feedbacks"
    id = Column(Integer, primary_key=True, index=True)
    tags = Column(String, nullable=True)       # 逗号分隔的标签
    detail = Column(Text, nullable=True)
    contact = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# 建表
Base.metadata.create_all(bind=engine)


@router.post("")
def submit_feedback(data: FeedbackIn):
    """提交反馈，存入SQLite"""
    db = next(get_db())
    try:
        record = FeedbackRecord(
            tags=",".join(data.tags) if data.tags else None,
            detail=data.detail,
            contact=data.contact,
        )
        db.add(record)
        db.commit()
        return {"ok": True, "message": "反馈已收到，感谢！💕"}
    finally:
        db.close()


@router.get("")
def list_feedbacks(limit: int = 50):
    """查看所有反馈（管理用）"""
    db = next(get_db())
    try:
        records = db.query(FeedbackRecord).order_by(
            FeedbackRecord.created_at.desc()
        ).limit(limit).all()
        return [
            {
                "id": r.id,
                "tags": r.tags,
                "detail": r.detail,
                "contact": r.contact,
                "created_at": str(r.created_at),
            }
            for r in records
        ]
    finally:
        db.close()
