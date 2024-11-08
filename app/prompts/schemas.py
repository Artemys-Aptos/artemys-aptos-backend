from pydantic import BaseModel, Field
from typing import List, Optional
from app.core.enums.tags import PromptTagEnum, PromptTypeEnum

class PublicPromptCreate(BaseModel):
    ipfs_image_url: str
    prompt: str
    account_address: str
    post_name: str
    public: bool
    prompt_tag: PromptTagEnum

    class Config:
        from_attributes = True


class PublicPromptResponse(BaseModel):
    id: int
    ipfs_image_url: str
    prompt: str
    account_address: str
    post_name: str
    public: bool
    prompt_tag: PromptTagEnum
    likes_count: Optional[int] = 0
    comments_count: Optional[int] = 0

    class Config:
        from_attributes = True


class PublicPromptListResponse(BaseModel):
    prompts: List[PublicPromptResponse]
    total: int  # Total number of prompts available
    page: int  # Current page number
    page_size: int  # Number of prompts per page

    class Config:
        from_attributes = True


class PublicPromptFilterRequest(BaseModel):
    prompt_tag: Optional[str] = "all"  # Allow 'all' as a valid string
    public: Optional[bool] = Field(True, description="Filter by visibility flag (public)")
    page: Optional[int] = Field(1, description="Page number for pagination")
    page_size: Optional[int] = Field(10, description="Number of prompts per page")



