from pydantic import BaseModel, Field
from typing import Optional
from app.core.enums.premium_filters import PremiumPromptFilterType

class PremiumPromptCreate(BaseModel):
    ipfs_image_url: str
    account_address: str
    # public: bool
    collection_name: str
    max_supply: int
    prompt_nft_price: str

    class Config:
        orm_mode = True

class PremiumPromptResponse(BaseModel):
    ipfs_image_url: str
    account_address: str
    public: bool
    collection_name: str
    max_supply: int
    prompt_nft_price: str
    likes: int = 0  # Number of likes
    comments: int = 0  # Number of comments

    class Config:
        orm_mode = True

class PremiumPromptListResponse(BaseModel):
    prompts: list[PremiumPromptResponse]
    total: int  # Total number of premium prompts
    page: int  # Current page number
    page_size: int  # Number of prompts per page

    class Config:
        orm_mode = True

class PremiumPromptFilterRequest(BaseModel):
    filter_type: Optional[PremiumPromptFilterType] = Field(None, description="Filter by 'recent', 'popular', or 'trending'")
    page: Optional[int] = Field(1, description="Page number for pagination")
    page_size: Optional[int] = Field(10, description="Number of premium prompts per page")