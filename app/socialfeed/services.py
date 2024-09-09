from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from . import models, schemas

def update_user_stats(user_account: str, db: Session):
    """
    Update the user stats after a generation:
    - Add 2 XP per generation.
    - Update the streak if generations happen on consecutive days.
    """
    user_stat = db.query(models.UserStat).filter(models.UserStat.user_account == user_account).first()
    
    if not user_stat:
        # Create new user stat if not present
        user_stat = models.UserStat(user_account=user_account)
        db.add(user_stat)
    
    # Calculate XP
    user_stat.xp += 2
    user_stat.total_generations += 1

    # Update streak if the last generation was yesterday
    if user_stat.last_generation:
        last_generation_date = user_stat.last_generation.date()
        today_date = datetime.utcnow().date()
        
        if today_date == last_generation_date + timedelta(days=1):
            user_stat.streak_days += 1
        elif today_date != last_generation_date:
            user_stat.streak_days = 1  # Reset streak if a day is skipped
    else:
        user_stat.streak_days = 1  # First day of streak

    # Update last generation timestamp
    user_stat.last_generation = datetime.utcnow()

    db.commit()
