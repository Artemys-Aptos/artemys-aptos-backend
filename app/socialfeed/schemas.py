from pydantic import BaseModel
from app.prompts.schemas import PromptTypeEnum
from typing import List
class LikePromptRequest(BaseModel):
    prompt_id: int
    prompt_type: PromptTypeEnum
    user_account: str

class CommentPromptRequest(BaseModel):
    prompt_id: int
    prompt_type: PromptTypeEnum
    user_account: str
    comment: str

class CommentResponse(BaseModel):
    user_account: str
    comment: str

    class Config:
        from_attributes = True

class CommentsListResponse(BaseModel):
    comments: List[CommentResponse]
    total_comments: int

    class Config:
        from_attributes = True