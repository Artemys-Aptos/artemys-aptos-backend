from sqlalchemy import Column, Integer, String
from app.core.database import Base  # Assuming you have a Base model class

class UserStats(Base):
    __tablename__ = 'user_stats'

    id = Column(Integer, primary_key=True, index=True)
    account_address = Column(String, nullable=False)
    generations_last_24h = Column(Integer, default=0)
    streak_days = Column(Integer, default=0)
    xp = Column(Integer, default=0)

    def grant_xp(self, xp_amount: int = 2):
        self.xp += xp_amount