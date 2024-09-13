from pydantic import BaseModel, Field
from typing import Optional
from app.core.enums.tags import PromptTagEnum
from app.core.enums.premium_filters import PremiumPromptFilterType

class PremiumPromptCreate(BaseModel):
    ipfs_image_url: str
    account_address: str
    prompt: str
    post_name: str
    # public: bool
    prompt_tag: PromptTagEnum
    collection_name: str
    max_supply: int
    prompt_nft_price: float

    class Config:
        from_attributes = True


class PremiumPromptResponse(BaseModel):
    ipfs_image_url: str
    account_address: str
    public: bool
    collection_name: str
    max_supply: int
    prompt_nft_price: float
    likes: Optional[int]
    comments: Optional[int]

    class Config:
        from_attributes = True


class PremiumPromptListResponse(BaseModel):
    prompts: list[PremiumPromptResponse]
    total: int  # Total number of premium prompts
    page: int  # Current page number
    page_size: int  # Number of prompts per page

    class Config:
        from_attributes = True

class PremiumPromptFilterRequest(BaseModel):
    filter_type: Optional[PremiumPromptFilterType] = Field(None, description="Filter by 'recent', 'popular', or 'trending'")
    page: Optional[int] = Field(1, description="Page number for pagination")
    page_size: Optional[int] = Field(10, description="Number of premium prompts per page")