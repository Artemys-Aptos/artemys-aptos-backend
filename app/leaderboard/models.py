from sqlalchemy import Column, Integer, String, DateTime
from app.core.database import Base  # Assuming you have a Base model class

class UserStats(Base):
    __tablename__ = 'user_stats'

    id = Column(Integer, primary_key=True, index=True)
    user_account = Column(String, unique=True, nullable=False)  # User's account address
    total_generations = Column(Integer, default=0)  # Total image generations
    streak_days = Column(Integer, default=0)  # Number of consecutive days with generations
    xp = Column(Integer, default=0)  # XP for the user
    last_generation = Column(DateTime, nullable=True)  # The time of the last generation

    def grant_xp(self, xp_amount: int = 2):
        self.xp += xp_amount