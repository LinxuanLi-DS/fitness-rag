"""调查问卷API"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import json
from pathlib import Path

router = APIRouter(prefix="/survey", tags=["survey"])

SURVEY_FILE = Path(__file__).parent.parent.parent / "data" / "survey_results.json"


class SurveyIn(BaseModel):
    q1_period_app: Optional[str] = ""
    q2_dissatisfaction: Optional[List[str]] = []
    q3_reminders: Optional[List[str]] = []
    q4_willing_to_track: Optional[List[str]] = []
    q5_combo_opinion: Optional[str] = ""
    q6_app_advantage: Optional[List[str]] = []
    q7_pain_point: Optional[str] = ""
    q8_age: Optional[str] = ""
    submitted_at: Optional[str] = ""


@router.post("")
def submit_survey(data: SurveyIn):
    """提交问卷"""
    # 确保目录存在
    SURVEY_FILE.parent.mkdir(exist_ok=True)

    # 读取已有数据
    surveys = []
    if SURVEY_FILE.exists():
        try:
            surveys = json.loads(SURVEY_FILE.read_text())
        except:
            surveys = []

    # 追加新数据
    surveys.append(data.model_dump())

    # 写回
    SURVEY_FILE.write_text(json.dumps(surveys, ensure_ascii=False, indent=2))

    return {"ok": True, "total": len(surveys), "message": "感谢参与！💕"}


@router.get("")
def list_surveys():
    """查看所有问卷结果"""
    if not SURVEY_FILE.exists():
        return {"surveys": [], "total": 0}

    surveys = json.loads(SURVEY_FILE.read_text())
    return {"surveys": surveys, "total": len(surveys)}


@router.get("/stats")
def survey_stats():
    """问卷统计"""
    if not SURVEY_FILE.exists():
        return {"total": 0}

    surveys = json.loads(SURVEY_FILE.read_text())
    total = len(surveys)

    stats = {
        "total": total,
        "q1_period_app": {},
        "q5_combo_opinion": {},
        "q8_age": {},
    }

    for s in surveys:
        # Q1
        app = s.get("q1_period_app", "")
        if app:
            stats["q1_period_app"][app] = stats["q1_period_app"].get(app, 0) + 1

        # Q5
        combo = s.get("q5_combo_opinion", "")
        if combo:
            stats["q5_combo_opinion"][combo] = stats["q5_combo_opinion"].get(combo, 0) + 1

        # Q8
        age = s.get("q8_age", "")
        if age:
            stats["q8_age"][age] = stats["q8_age"].get(age, 0) + 1

    return stats
