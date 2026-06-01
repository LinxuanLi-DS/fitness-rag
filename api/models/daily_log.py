from sqlalchemy import Column, Integer, String, Float, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from .user import Base
from datetime import date


class DailyLog(Base):
    __tablename__ = "daily_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    log_date = Column(Date, nullable=False)

    # 经期相关
    flow = Column(String, nullable=True)  # 无/少量/中等/多/大量
    color = Column(String, nullable=True)  # 鲜红/暗红/褐色/粉色
    symptoms = Column(Text, nullable=True)  # JSON数组: ["痛经", "头痛"]
    temperature = Column(Float, nullable=True)  # 基础体温

    # 日常记录
    water = Column(Integer, nullable=True, default=0)  # 喝水杯数
    weight = Column(Float, nullable=True)  # 今日体重

    created_at = Column(Date, nullable=False)

    user = relationship("User", backref="daily_logs")
