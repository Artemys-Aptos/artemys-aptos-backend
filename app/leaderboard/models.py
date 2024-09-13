from sqlalchemy import Column, Integer, String, DateTime
from app.core.database import Base  # Assuming you have a Base model class

class UserStats(Base):
    __tablename__ = 'user_stats'

    id = Column(Integer, primary_key=True, index=True)
    user_account = Column(String, unique=True, nullable=False)
    xp = Column(Integer, default=0, index=True)  # Initialize XP to 0
    total_generations = Column(Integer, default=0, index=True)  # Initialize total_generations to 0
    streak_days = Column(Integer, default=0, index=True)  # Initialize streak_days to 0
    last_generation = Column(DateTime, nullable=True, index=True)  # Can be null initially