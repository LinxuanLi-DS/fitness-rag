from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date
import json
from ..models.user import get_db
from ..models.daily_log import DailyLog
from ..models.schemas import DailyLogCreate, DailyLogOut
from ..routers.users import get_current_user_id

router = APIRouter(prefix="/daily", tags=["daily"])


@router.post("/log", response_model=DailyLogOut)
async def create_or_update_daily_log(
    log_data: DailyLogCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """创建或更新每日状态记录"""
    log_date = datetime.strptime(log_data.log_date, "%Y-%m-%d").date()

    # 检查是否已存在该日期的记录
    existing = db.query(DailyLog).filter(
        DailyLog.user_id == user_id,
        DailyLog.log_date == log_date
    ).first()

    if existing:
        # 更新现有记录
        existing.flow = log_data.flow
        existing.color = log_data.color
        existing.symptoms = json.dumps(log_data.symptoms) if log_data.symptoms else None
        existing.temperature = log_data.temperature
        existing.water = log_data.water
        existing.weight = log_data.weight
        db.commit()
        db.refresh(existing)
        log_record = existing
    else:
        # 创建新记录
        new_log = DailyLog(
            user_id=user_id,
            log_date=log_date,
            flow=log_data.flow,
            color=log_data.color,
            symptoms=json.dumps(log_data.symptoms) if log_data.symptoms else None,
            temperature=log_data.temperature,
            water=log_data.water,
            weight=log_data.weight,
            created_at=date.today(),
        )
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
        log_record = new_log

    return DailyLogOut(
        id=log_record.id,
        log_date=log_record.log_date.strftime("%Y-%m-%d"),
        flow=log_record.flow,
        color=log_record.color,
        symptoms=json.loads(log_record.symptoms) if log_record.symptoms else None,
        temperature=log_record.temperature,
        water=log_record.water,
        weight=log_record.weight,
    )


@router.get("/log/{log_date}", response_model=DailyLogOut)
async def get_daily_log(
    log_date: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """获取指定日期的记录"""
    date_obj = datetime.strptime(log_date, "%Y-%m-%d").date()
    log = db.query(DailyLog).filter(
        DailyLog.user_id == user_id,
        DailyLog.log_date == date_obj
    ).first()

    if not log:
        raise HTTPException(status_code=404, detail="该日期无记录")

    return DailyLogOut(
        id=log.id,
        log_date=log.log_date.strftime("%Y-%m-%d"),
        flow=log.flow,
        color=log.color,
        symptoms=json.loads(log.symptoms) if log.symptoms else None,
        temperature=log.temperature,
        water=log.water,
        weight=log.weight,
    )


@router.get("/logs", response_model=list[DailyLogOut])
async def get_daily_logs(
    start_date: str,
    end_date: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """获取日期范围内的所有记录"""
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()

    logs = db.query(DailyLog).filter(
        DailyLog.user_id == user_id,
        DailyLog.log_date >= start,
        DailyLog.log_date <= end,
    ).order_by(DailyLog.log_date.desc()).all()

    return [
        DailyLogOut(
            id=log.id,
            log_date=log.log_date.strftime("%Y-%m-%d"),
            flow=log.flow,
            color=log.color,
            symptoms=json.loads(log.symptoms) if log.symptoms else None,
            temperature=log.temperature,
            water=log.water,
            weight=log.weight,
        )
        for log in logs
    ]
