"""经期记录 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from typing import List, Optional
import json

from api.models.user import get_db
from api.models.period import PeriodRecord
from api.routers.chat import get_current_user

router = APIRouter(prefix="/period", tags=["period"])


# ========== Schemas ==========
class PeriodRecordIn:
    start_date: str  # YYYY-MM-DD
    end_date: Optional[str] = None
    symptoms: Optional[List[str]] = []
    notes: Optional[str] = ""


# ========== API Endpoints ==========

@router.post("/record")
def record_period(
    data: dict,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """记录经期"""
    if not current_user:
        raise HTTPException(status_code=401, detail="请先登录")

    start_date = date.fromisoformat(data["start_date"])
    end_date = date.fromisoformat(data["end_date"]) if data.get("end_date") else None
    symptoms = json.dumps(data.get("symptoms", []), ensure_ascii=False)
    notes = data.get("notes", "")

    # 检查是否已存在相同开始日期的记录
    existing = db.query(PeriodRecord).filter(
        PeriodRecord.user_id == current_user.id,
        PeriodRecord.start_date == start_date
    ).first()

    if existing:
        # 更新已有记录
        existing.end_date = end_date
        existing.symptoms = symptoms
        existing.notes = notes
        db.commit()
        db.refresh(existing)
        return {"message": "经期记录已更新", "id": existing.id}
    else:
        # 创建新记录
        record = PeriodRecord(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            symptoms=symptoms,
            notes=notes
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return {"message": "经期记录已保存", "id": record.id}


@router.get("/history")
def get_period_history(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取经期历史记录"""
    if not current_user:
        raise HTTPException(status_code=401, detail="请先登录")

    records = db.query(PeriodRecord).filter(
        PeriodRecord.user_id == current_user.id
    ).order_by(PeriodRecord.start_date.desc()).all()

    result = []
    for r in records:
        result.append({
            "id": r.id,
            "start_date": r.start_date.isoformat(),
            "end_date": r.end_date.isoformat() if r.end_date else None,
            "symptoms": json.loads(r.symptoms) if r.symptoms else [],
            "notes": r.notes or "",
            "duration": (r.end_date - r.start_date).days + 1 if r.end_date else None
        })

    return {"records": result, "total": len(result)}


@router.get("/stats")
def get_period_stats(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取周期统计信息"""
    if not current_user:
        raise HTTPException(status_code=401, detail="请先登录")

    records = db.query(PeriodRecord).filter(
        PeriodRecord.user_id == current_user.id,
        PeriodRecord.end_date != None
    ).order_by(PeriodRecord.start_date.asc()).all()

    if len(records) < 2:
        return {
            "message": "需要至少2条完整的经期记录才能统计",
            "records_count": len(records)
        }

    # 计算周期长度（两次经期开始日期的间隔）
    cycle_lengths = []
    for i in range(1, len(records)):
        cycle_length = (records[i].start_date - records[i-1].start_date).days
        if 20 <= cycle_length <= 45:  # 过滤异常值
            cycle_lengths.append(cycle_length)

    if not cycle_lengths:
        return {"message": "周期数据不足"}

    # 计算经期时长
    durations = [(r.end_date - r.start_date).days + 1 for r in records if r.end_date]

    avg_cycle = sum(cycle_lengths) / len(cycle_lengths)
    avg_duration = sum(durations) / len(durations) if durations else 0

    # 预测下次经期
    last_record = records[-1]
    next_start = last_record.start_date + timedelta(days=int(avg_cycle))
    days_until_next = (next_start - date.today()).days

    return {
        "avg_cycle_length": round(avg_cycle, 1),
        "avg_duration": round(avg_duration, 1),
        "total_records": len(records),
        "last_period_start": last_record.start_date.isoformat(),
        "last_period_end": last_record.end_date.isoformat() if last_record.end_date else None,
        "next_predicted_start": next_start.isoformat(),
        "days_until_next": days_until_next,
        "current_cycle_day": (date.today() - last_record.start_date).days + 1
    }


@router.get("/predict")
def predict_next_period(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """预测下次经期和当前周期阶段"""
    if not current_user:
        raise HTTPException(status_code=401, detail="请先登录")

    records = db.query(PeriodRecord).filter(
        PeriodRecord.user_id == current_user.id,
        PeriodRecord.end_date != None
    ).order_by(PeriodRecord.start_date.desc()).limit(6).all()

    if len(records) < 2:
        return {
            "message": "需要至少2条完整记录才能预测",
            "can_predict": False
        }

    # 计算平均周期
    records.reverse()
    cycle_lengths = []
    for i in range(1, len(records)):
        cycle_length = (records[i].start_date - records[i-1].start_date).days
        if 20 <= cycle_length <= 45:
            cycle_lengths.append(cycle_length)

    if not cycle_lengths:
        return {"message": "周期数据异常", "can_predict": False}

    avg_cycle = sum(cycle_lengths) / len(cycle_lengths)
    last_start = records[-1].start_date
    days_since_last = (date.today() - last_start).days

    # 预测下次经期
    next_start = last_start + timedelta(days=int(avg_cycle))
    days_until_next = (next_start - date.today()).days

    # 判断当前周期阶段
    current_day = days_since_last + 1
    phase = ""
    phase_desc = ""
    
    if current_day <= 5:
        phase = "经期"
        phase_desc = "注意休息，避免剧烈运动，多喝温水"
    elif current_day <= 13:
        phase = "卵泡期"
        phase_desc = "精力充沛，适合高强度训练，代谢旺盛"
    elif current_day <= 16:
        phase = "排卵期"
        phase_desc = "状态最佳，适合挑战新训练，注意补充蛋白质"
    elif current_day <= 21:
        phase = "黄体早期"
        phase_desc = "状态稳定，保持规律运动"
    else:
        phase = "黄体期"
        phase_desc = "可能情绪波动，适合瑜伽/拉伸，少吃盐防水肿"

    return {
        "can_predict": True,
        "current_cycle_day": current_day,
        "avg_cycle_length": round(avg_cycle, 1),
        "next_predicted_start": next_start.isoformat(),
        "days_until_next": days_until_next,
        "current_phase": phase,
        "phase_description": phase_desc
    }


@router.delete("/record/{record_id}")
def delete_period_record(
    record_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除经期记录"""
    if not current_user:
        raise HTTPException(status_code=401, detail="请先登录")

    record = db.query(PeriodRecord).filter(
        PeriodRecord.id == record_id,
        PeriodRecord.user_id == current_user.id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    db.delete(record)
    db.commit()
    return {"message": "记录已删除"}
