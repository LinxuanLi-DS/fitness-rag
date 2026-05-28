"""经期记录模型"""
from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from api.models.user import Base


class PeriodRecord(Base):
    __tablename__ = "period_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    symptoms = Column(Text, nullable=True)  # JSON: ["痛经", "头痛", "情绪波动"]
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
