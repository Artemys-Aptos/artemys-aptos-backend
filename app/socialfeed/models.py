from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.core.database import Base  # Assuming you have a Base model class

class SocialFeedPost(Base):
    __tablename__ = 'social_feed_posts'

    id = Column(Integer, primary_key=True, index=True)
    user_account = Column(String, nullable=False)
    content = Column(String, nullable=False)
    likes = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
