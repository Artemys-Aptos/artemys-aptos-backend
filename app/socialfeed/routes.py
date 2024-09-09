from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.core.database import get_session
from . import schemas, services, models
from app.prompts.models import Prompt
from app.core.helpers import paginate
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


@router.get("/get-prompt-comments/{prompt_id}/", response_model=schemas.CommentsListResponse)
def get_prompt_comments(prompt_id: int, prompt_type: schemas.PromptTypeEnum, limit: int = 2, db: Session = Depends(get_session)):
    """
    Retrieve comments for a specific public or premium prompt.
    
    By default, only the top 2 comments are returned. You can specify a different limit via the query parameter.

    - **prompt_id**: ID of the prompt (public or premium).
    - **prompt_type**: Whether the prompt is public or premium.
    - **limit**: The number of comments to return (default is 2).
    """
    # Check if the prompt exists
    prompt = db.query(Prompt).filter(
        Prompt.id == prompt_id,
        Prompt.prompt_type == prompt_type
    ).first()

    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    # Get the top comments for the prompt, limited by the 'limit' parameter
    comments = db.query(models.PostComment).filter(
        models.PostComment.prompt_id == prompt_id,
        models.PostComment.prompt_type == prompt_type
    ).limit(limit).all()

    total_comments = db.query(models.PostComment).filter(
        models.PostComment.prompt_id == prompt_id,
        models.PostComment.prompt_type == prompt_type
    ).count()

    return schemas.CommentsListResponse(
        comments=[
            schemas.CommentResponse(
                user_account=comment.user_account,
                comment=comment.comment
            ) for comment in comments
        ],
        total_comments=total_comments
    )





@router.post("/update-generation-count/")
def update_generation_count(user_account: str, db: Session = Depends(get_session)):
    """
    Endpoint to update generation count and XP after a prompt (public or premium) is created.
    - **user_account**: The account of the user creating the prompt.
    """
    # Update user stats (XP and generation count)
    services.update_user_stats(user_account, db)
    
    return {"message": "Generation count and XP updated successfully"}


@router.post("/follow-creator/")
def follow_creator(follower_account: str, creator_account: str, db: Session = Depends(get_session)):
    """
    Follow a creator.
    
    - **follower_account**: The account of the user who wants to follow.
    - **creator_account**: The account of the creator to be followed.
    """
    # Check if already following
    existing_follow = db.query(models.Follow).filter(
        models.Follow.follower_account == follower_account,
        models.Follow.creator_account == creator_account
    ).first()

    if existing_follow:
        raise HTTPException(status_code=400, detail="Already following this creator")

    # Add new follow relationship
    new_follow = models.Follow(follower_account=follower_account, creator_account=creator_account)
    db.add(new_follow)
    db.commit()

    return {"message": "Successfully followed the creator"}


@router.post("/unfollow-creator/")
def unfollow_creator(follower_account: str, creator_account: str, db: Session = Depends(get_session)):
    """
    Unfollow a creator.
    
    - **follower_account**: The account of the user who wants to unfollow.
    - **creator_account**: The account of the creator to be unfollowed.
    """
    follow_relationship = db.query(models.Follow).filter(
        models.Follow.follower_account == follower_account,
        models.Follow.creator_account == creator_account
    ).first()

    if not follow_relationship:
        raise HTTPException(status_code=404, detail="Not following this creator")

    db.delete(follow_relationship)
    db.commit()

    return {"message": "Successfully unfollowed the creator"}


@router.get("/social-feed/")
def social_feed(user_account: str, page: int = 1, page_size: int = 10, db: Session = Depends(get_session)):
    """
    Social feed: Return prompts from creators the user is following and random new creators.
    
    - **user_account**: The account of the user requesting the feed.
    - **page**: Page number for pagination.
    - **page_size**: Number of prompts per page.
    """
    # Get the list of creators the user is following
    followed_creators = db.query(models.Follow.creator_account).filter(models.Follow.follower_account == user_account).all()
    followed_creators = [creator.creator_account for creator in followed_creators]

    # Fetch prompts from followed creators
    followed_prompts_query = db.query(Prompt).filter(Prompt.account_address.in_(followed_creators))

    # Fetch random creators (excluding those already followed)
    random_creators_query = db.query(Prompt).filter(~Prompt.account_address.in_(followed_creators)).order_by(func.random())

    # Combine both followed prompts and random creator prompts
    combined_query = followed_prompts_query.union(random_creators_query)

    # Paginate the feed
    total_prompts = combined_query.count()
    paginated_prompts = paginate(combined_query, page, page_size)

    # Return the feed
    return {
        "results": [
            {
                "ipfs_image_url": prompt.ipfs_image_url,
                "prompt": prompt.prompt,
                "account_address": prompt.account_address,
                "post_name": prompt.post_name,
                "likes": prompt.likes,
                "comments": prompt.comments,
                "public": prompt.public
            }
            for prompt in paginated_prompts
        ],
        "total": total_prompts,
        "page": page,
        "page_size": page_size
    }
