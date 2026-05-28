from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# 开发阶段用 SQLite（不需要安装任何东西，直接本地文件）
DATABASE_URL = "sqlite:///./fitnessrag.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    # 基本信息
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    height = Column(Float, nullable=True)   # cm
    weight = Column(Float, nullable=True)   # kg

    # 目标
    goal = Column(String, nullable=True)    # 减脂/塑形/增肌/保持
    dietary = Column(String, nullable=True) # 饮食限制

    # 女性专属
    life_stage = Column(String, nullable=True)   # 普通/备孕/孕期/哺乳期
    cycle_phase = Column(String, nullable=True)  # 经期/卵泡期/排卵期/黄体期
    fitness_level = Column(String, nullable=True) # 新手/中级/进阶


def init_db():
    Base.metadata.create_all(bind=engine)
    # 确保经期记录表也被创建
    try:
        from api.models.period import PeriodRecord
        Base.metadata.create_all(bind=engine)
    except Exception:
        pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()