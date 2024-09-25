from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.core.database import get_session
from app.core.helpers import paginate
from . import schemas, services, models
import random

router = APIRouter()

@router.get("/generations-24h/")
def leaderboard_generations_24h(page: int = 1, page_size: int = 10, db: Session = Depends(get_session)):
    """
    Leaderboard based on the number of generations in the last 24 hours with pagination.
    """
    try:
        last_24_hours = datetime.utcnow() - timedelta(hours=24)

        query = db.query(models.UserStats).filter(models.UserStats.last_generation >= last_24_hours).order_by(models.UserStats.total_generations.desc())
        total_count = query.count()
        users = paginate(query, page, page_size)

        results = [{"user_account": user.user_account, "total_generations": user.total_generations} for user in users]

        # Add 10 dummy entries with random wallet addresses
        for _ in range(10):
            # Generate a random hex string of 64 characters
            wallet_address = "0x" + ''.join(random.choice('0123456789abcdef') for _ in range(64))
            results.append({
                "user_account": wallet_address, 
                "total_generations": random.randint(1, 100)
            })

        return {
            "results": results,
            "total": total_count + 10,  # Adjust total count
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        detail = {
            "info": "Failed to get leaderboard based on the number of generations in the last 24 hours",
            "error": str(e),
        }
        raise HTTPException(status_code=500, detail=detail)



@router.get("/streaks/")
def leaderboard_streaks(page: int = 1, page_size: int = 10, db: Session = Depends(get_session)):
    """
    Leaderboard based on the number of consecutive days with generations, with pagination.
    """
    try:
        query = db.query(models.UserStats).order_by(models.UserStats.streak_days.desc())
        total_count = query.count()
        users = paginate(query, page, page_size)

        results = [{"user_account": user.user_account, "streak_days": user.streak_days} for user in users]

        # Add 10 dummy entries with random wallet addresses
        for _ in range(10):
            # Generate a random hex string of 64 characters
            wallet_address = "0x" + ''.join(random.choice('0123456789abcdef') for _ in range(64))
            results.append({
                "user_account": wallet_address,
                "streak_days": random.randint(1, 30)
            })

        return {
            "results": results,
            "total": total_count + 10,  # Adjust total count
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        detail = {
            "info": "Failed to get leaderboard based on the number of consecutive days with generations",
            "error": str(e),
        }
        raise HTTPException(status_code=500, detail=detail)



@router.get("/xp/")
def leaderboard_xp(page: int = 1, page_size: int = 10, db: Session = Depends(get_session)):
    """
    Leaderboard based on XP with pagination.
    """
    try:
        query = db.query(models.UserStats).order_by(models.UserStats.xp.desc())
        total_count = query.count()
        users = paginate(query, page, page_size)

        results = [{"user_account": user.user_account, "xp": user.xp} for user in users]

        # Add 10 dummy entries with random wallet addresses
        for _ in range(10):
            # Generate a random hex string of 64 characters
            wallet_address = "0x" + ''.join(random.choice('0123456789abcdef') for _ in range(64))
            results.append({
                "user_account": wallet_address,
                "xp": random.randint(1, 1000)
            })

        return {
            "results": results,
            "total": total_count + 10,  # Adjust total count
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        detail = {
            "info": "Failed to get leaderboard based on XP",
            "error": str(e),
        }
        raise HTTPException(status_code=500, detail=detail)