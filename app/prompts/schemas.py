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
        orm_mode = True


class PublicPromptResponse(BaseModel):
    ipfs_image_url: str
    prompt: str
    account_address: str
    post_name: str
    public: bool
    prompt_tag: PromptTagEnum

    class Config:
        orm_mode = True

# This schema will represent a list of public prompts
class PublicPromptListResponse(BaseModel):
    prompts: List[PublicPromptResponse]
    total: int  # Total number of prompts available
    page: int  # Current page number
    page_size: int  # Number of prompts per page

    class Config:
        orm_mode = True


class PublicPromptFilterRequest(BaseModel):
    prompt_tag: Optional[PromptTagEnum] = Field(None, description="Filter by prompt tag (3D Art, Anime)")
    public: Optional[bool] = Field(True, description="Filter by visibility flag (public)")
    page: Optional[int] = Field(1, description="Page number for pagination")
    page_size: Optional[int] = Field(10, description="Number of prompts per page")



class LikePromptRequest(BaseModel):
    prompt_id: int
    prompt_type: PromptTypeEnum
    user_account: str

class CommentPromptRequest(BaseModel):
    prompt_id: int
    prompt_type: PromptTypeEnum
    user_account: str
    comment: str