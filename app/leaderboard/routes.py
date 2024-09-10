from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.core.database import get_session
from app.core.helpers import paginate
from . import schemas, services, models



router = APIRouter()

@router.get("/generations-24h/")
def leaderboard_generations_24h(page: int = 1, page_size: int = 10, db: Session = Depends(get_session)):
    """
    Leaderboard based on the number of generations in the last 24 hours with pagination.
    """
    last_24_hours = datetime.utcnow() - timedelta(hours=24)

    query = db.query(models.UserStats).filter(models.UserStats.last_generation >= last_24_hours).order_by(models.UserStats.total_generations.desc())
    total_count = query.count()
    users = paginate(query, page, page_size)

    return {
        "results": [{"user_account": user.user_account, "total_generations": user.total_generations} for user in users],
        "total": total_count,
        "page": page,
        "page_size": page_size
    }



@router.get("/streaks/")
def leaderboard_streaks(page: int = 1, page_size: int = 10, db: Session = Depends(get_session)):
    """
    Leaderboard based on the number of consecutive days with generations, with pagination.
    """
    query = db.query(models.UserStats).order_by(models.UserStats.streak_days.desc())
    
    # Get total count for pagination
    total_users = query.count()

    # Apply pagination
    users = query.offset((page - 1) * page_size).limit(page_size).all()

    # Return paginated streak leaderboard
    return {
        "results": [{"user_account": user.user_account, "streak_days": user.streak_days} for user in users],
        "total": total_users,
        "page": page,
        "page_size": page_size
    }



@router.get("/xp/")
def leaderboard_xp(page: int = 1, page_size: int = 10, db: Session = Depends(get_session)):
    """
    Leaderboard based on XP with pagination.
    """
    query = db.query(models.UserStats).order_by(models.UserStats.xp.desc())
    total_count = query.count()
    users = paginate(query, page, page_size)

    return {
        "results": [{"user_account": user.user_account, "xp": user.xp} for user in users],
        "total": total_count,
        "page": page,
        "page_size": page_size
    }