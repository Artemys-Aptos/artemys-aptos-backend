from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Enum, Float, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base  # Assuming you're using a Base class from SQLAlchemy setup
from app.core.enums.tags import PromptTagEnum, PromptTypeEnum


class Prompt(Base):
    __tablename__ = 'prompts'

    id = Column(Integer, primary_key=True, index=True)
    ipfs_image_url = Column(String, nullable=False)
    prompt = Column(String, nullable=False)
    account_address = Column(String, nullable=False, index=True)
    post_name = Column(String, nullable=False, index=True)
    public = Column(Boolean, default=True, index=True)
    cid = Column(String, nullable=True, index=True, default=None) # only relevant for PREMIUM prompts
    prompt_tag = Column(Enum(PromptTagEnum), nullable=False, index=True)
    chain = Column(String, nullable=True, index=True)
    ai_model = Column(String, index=True, nullable=True)
    prompt_type = Column(Enum(PromptTypeEnum), nullable=False, index=True)  # PUBLIC or PREMIUM
    collection_name = Column(String, nullable=True, index=True)  # Only relevant for PREMIUM prompts
    max_supply = Column(Integer, nullable=True, index=True)  # Only relevant for PREMIUM prompts
    prompt_nft_price = Column(Float, nullable=True, index=True)  # Only relevant for PREMIUM prompts
    grant_access = Column(Boolean, default=False, index=True) # Only relevant for PREMIUM prompts
    video_url = Column(String, nullable=True, index=True) # Only premium promots
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    comments = relationship('PostComment', back_populates='prompt', cascade="all, delete-orphan")
    likes = relationship('PostLike', back_populates='prompt', cascade="all, delete-orphan")