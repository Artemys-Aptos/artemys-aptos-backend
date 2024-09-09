from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_session
from . import schemas, services, models
from app.prompts.models import Prompt

router = APIRouter()


@router.post("/like-prompt/")
def like_prompt(like_data: schemas.LikePromptRequest, db: Session = Depends(get_session)):
    """
    Like a public or premium prompt.

    - **prompt_id**: ID of the prompt (public or premium).
    - **prompt_type**: Whether the prompt is public or premium.
    - **user_account**: The account of the user liking the prompt.
    """
    # Check if the prompt exists
    prompt = db.query(Prompt).filter(
        Prompt.id == like_data.prompt_id,
        Prompt.prompt_type == like_data.prompt_type
    ).first()

    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    # Check if the user has already liked the prompt
    existing_like = db.query(models.PostLike).filter(
        models.PostLike.prompt_id == like_data.prompt_id,
        models.PostLike.prompt_type == like_data.prompt_type,
        models.PostLike.user_account == like_data.user_account
    ).first()

    if existing_like:
        raise HTTPException(status_code=400, detail="User has already liked this prompt")

    # Create a new like
    new_like = models.PostLike(
        prompt_id=like_data.prompt_id,
        prompt_type=like_data.prompt_type,
        user_account=like_data.user_account
    )
    db.add(new_like)
    prompt.likes += 1  # Increment like count
    db.commit()
    return {"message": "Prompt liked successfully"}


@router.post("/comment-prompt/")
def comment_prompt(comment_data: schemas.CommentPromptRequest, db: Session = Depends(get_session)):
    """
    Comment on a public or premium prompt.

    - **prompt_id**: ID of the prompt (public or premium).
    - **prompt_type**: Whether the prompt is public or premium.
    - **user_account**: The account of the user commenting.
    - **comment**: The comment text.
    """
    # Check if the prompt exists
    prompt = db.query(Prompt).filter(
        Prompt.id == comment_data.prompt_id,
        Prompt.prompt_type == comment_data.prompt_type
    ).first()

    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    # Create a new comment
    new_comment = models.PostComment(
        prompt_id=comment_data.prompt_id,
        prompt_type=comment_data.prompt_type,
        user_account=comment_data.user_account,
        comment=comment_data.comment
    )
    db.add(new_comment)
    prompt.comments += 1  # Increment comment count
    db.commit()
    return {"message": "Comment added successfully"}
