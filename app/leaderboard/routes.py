from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.core.database import get_session
from app.core.helpers import paginate
from . import schemas, services, models



router = APIRouter()

@router.get("/leaderboard/generations-24h/")
def leaderboard_generations_24h(page: int = 1, page_size: int = 10, db: Session = Depends(get_session)):
    """
    Leaderboard based on the number of generations in the last 24 hours with pagination.
    """
    last_24_hours = datetime.utcnow() - timedelta(hours=24)

    query = db.query(models.UserStat).filter(models.UserStat.last_generation >= last_24_hours).order_by(models.UserStat.total_generations.desc())
    total_count = query.count()
    users = paginate(query, page, page_size)

    return {
        "results": [{"user_account": user.user_account, "total_generations": user.total_generations} for user in users],
        "total": total_count,
        "page": page,
        "page_size": page_size
    }



@router.get("/leaderboard/streaks/")
def leaderboard_streaks(db: Session = Depends(get_session)):
    """
    Leaderboard based on the number of consecutive days with generations.
    """
    users = db.query(models.UserStat).order_by(models.UserStat.streak_days.desc()).all()

    return [{"user_account": user.user_account, "streak_days": user.streak_days} for user in users]


@router.get("/leaderboard/xp/")
def leaderboard_xp(page: int = 1, page_size: int = 10, db: Session = Depends(get_session)):
    """
    Leaderboard based on XP with pagination.
    """
    query = db.query(models.UserStat).order_by(models.UserStat.xp.desc())
    total_count = query.count()
    users = paginate(query, page, page_size)

    return {
        "results": [{"user_account": user.user_account, "xp": user.xp} for user in users],
        "total": total_count,
        "page": page,
        "page_size": page_size
    }