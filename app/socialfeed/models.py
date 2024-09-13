from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from app.prompts.schemas import PromptTypeEnum
from sqlalchemy.orm import relationship
from app.core.database import Base  # Assuming you have a Base model class

class SocialFeedPost(Base):
    __tablename__ = 'social_feed_posts'

    id = Column(Integer, primary_key=True, index=True)
    user_account = Column(String, nullable=False)
    content = Column(String, nullable=False)
    likes = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)



class PostLike(Base):
    __tablename__ = 'post_likes'

    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(Integer, ForeignKey('prompts.id', ondelete="CASCADE"), nullable=False) 
    prompt_type = Column(Enum(PromptTypeEnum), nullable=False)  # Type: public or premium
    user_account = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    prompt = relationship('Prompt', back_populates='likes')


class PostComment(Base):
    __tablename__ = 'post_comments'

    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(Integer, ForeignKey('prompts.id', ondelete="CASCADE"), nullable=False) 
    prompt_type = Column(Enum(PromptTypeEnum), nullable=False)  # Type: public or premium
    user_account = Column(String, nullable=False, index=True)
    comment = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    prompt = relationship('Prompt', back_populates='comments')


class Follow(Base):
    __tablename__ = 'follows'

    id = Column(Integer, primary_key=True, index=True)
    follower_account = Column(String, nullable=False, index=True)  # The account of the user who follows
    creator_account = Column(String, nullable=False, index=True)   # The account of the creator being followed