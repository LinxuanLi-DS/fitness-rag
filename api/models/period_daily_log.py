"""经期每日状态记录模型"""
from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from api.models.user import Base


class PeriodDailyLog(Base):
    __tablename__ = "period_daily_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    log_date = Column(Date, nullable=False)
    flow = Column(String(20), nullable=True)       # 少/中/多/极多
    pain_level = Column(Integer, nullable=True)     # 0-3
    mood = Column(String(20), nullable=True)        # emoji
    symptoms = Column(Text, nullable=True)          # JSON: ["头痛","疲劳",...]
    energy = Column(Integer, nullable=True)         # 1-5
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
