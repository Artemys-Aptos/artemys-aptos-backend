from pydantic import BaseModel
from app.prompts.schemas import PromptTypeEnum
class LikePromptRequest(BaseModel):
    prompt_id: int
    prompt_type: PromptTypeEnum
    user_account: str

class CommentPromptRequest(BaseModel):
    prompt_id: int
    prompt_type: PromptTypeEnum
    user_account: str
    comment: str