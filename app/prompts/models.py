from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Enum, Float, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base  # Assuming you're using a Base class from SQLAlchemy setup

class PromptTagEnum(str, Enum):
    ART_3D = "3D Art"
    ANIME = "Anime"
    PHOTOGRAPHY = "Photography"
    VECTOR = "Vector"
    OTHER = "Other"
    

class PromptTypeEnum(str, Enum):
    PUBLIC = "public"
    PREMIUM = "premium"

class Prompt(Base):
    __tablename__ = 'prompts'

    id = Column(Integer, primary_key=True, index=True)
    ipfs_image_url = Column(String, nullable=False)
    prompt = Column(String, nullable=False)
    account_address = Column(String, nullable=False)
    post_name = Column(String, nullable=False)
    public = Column(Boolean, default=True)
    prompt_tag = Column(Enum(PromptTagEnum), nullable=False)
    prompt_type = Column(Enum(PromptTypeEnum), nullable=False)  # PUBLIC or PREMIUM
    collection_name = Column(String, nullable=True)  # Only relevant for PREMIUM prompts
    max_supply = Column(Integer, nullable=True)  # Only relevant for PREMIUM prompts
    prompt_nft_price = Column(Float, nullable=True)  # Only relevant for PREMIUM prompts
    created_at = Column(DateTime, default=datetime.utcnow)



class PostLike(Base):
    __tablename__ = 'post_likes'

    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(Integer, nullable=False)  # ID of either PublicPrompt or PremiumPrompt
    prompt_type = Column(Enum(PromptTypeEnum), nullable=False)  # Type: public or premium
    user_account = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class PostComment(Base):
    __tablename__ = 'post_comments'

    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(Integer, nullable=False)  # ID of either PublicPrompt or PremiumPrompt
    prompt_type = Column(Enum(PromptTypeEnum), nullable=False)  # Type: public or premium
    user_account = Column(String, nullable=False)
    comment = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)