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
    db.commit()

    # Get the updated number of likes
    total_likes = db.query(models.PostLike).filter(
        models.PostLike.prompt_id == like_data.prompt_id,
        models.PostLike.prompt_type == like_data.prompt_type
    ).count()

    return {
        "message": "Prompt liked successfully",
        "total_likes": total_likes
    }



@router.post("/comment-prompt/")
def comment_prompt(comment_data: schemas.CommentPromptRequest, db: Session = Depends(get_session)):
    """
    Add a comment to a public or premium prompt.

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
    db.commit()

    # Get updated total comments count
    total_comments = db.query(models.PostComment).filter(
        models.PostComment.prompt_id == comment_data.prompt_id,
        models.PostComment.prompt_type == comment_data.prompt_type
    ).count()

    # Get the latest comments (e.g., top 2)
    top_comments = db.query(models.PostComment).filter(
        models.PostComment.prompt_id == comment_data.prompt_id,
        models.PostComment.prompt_type == comment_data.prompt_type
    ).order_by(models.PostComment.created_at.desc()).limit(2).all()

    # Commit the changes to the database
    db.commit()

    return {
        "message": "Comment added successfully",
        "total_comments": total_comments,
        "latest_comments": [
            {
                "user_account": comment.user_account,
                "comment": comment.comment,
                "created_at": comment.created_at
            }
            for comment in top_comments
        ]
    }


@router.get("/get-prompt-comments/", response_model=schemas.CommentsListResponse)
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


@router.delete("/unfollow-creator/")
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


@router.get("/creator-followers/")
def get_creator_followers(creator_account: str, db: Session = Depends(get_session)):
    """
    Get a list of followers for a specific creator along with their top 5 most liked prompts.
    
    - **creator_account**: The account of the creator whose followers are being retrieved.
    """
    followers = db.query(models.Follow).filter(models.Follow.creator_account == creator_account).all()

    if not followers:
        return {"message": "This creator has no followers"}

    result = []
    for follow in followers:
        # Get follower's top 5 most liked prompts
        prompts = (
            db.query(Prompt, func.count(models.PostLike.id).label('likes_count'))
            .outerjoin(models.PostLike, models.PostLike.prompt_id == Prompt.id)
            .filter(Prompt.account_address == follow.follower_account)
            .group_by(Prompt.id)
            .order_by(func.count(models.PostLike.id).desc())  # Sort by the number of likes
            .limit(5)
            .all()
        )

        result.append({
            "follower_account": follow.follower_account,
            "top_5_prompts": [
                {
                    "prompt": prompt.prompt,
                    "likes": likes_count,
                    "comments": len(prompt.comments),
                    "created_at": prompt.created_at
                } for prompt, likes_count in prompts
            ]
        })

    return {"creator_account": creator_account, "followers_with_top_prompts": result}



@router.get("/user-following/")
def get_user_following(follower_account: str, db: Session = Depends(get_session)):
    """
    Get a list of creators a user is following along with their top 5 most liked prompts.
    
    - **follower_account**: The account of the user whose following list is being retrieved.
    """
    following = db.query(models.Follow).filter(models.Follow.follower_account == follower_account).all()

    if not following:
        return {"message": "This user is not following any creators"}

    result = []
    for follow in following:
        # Get the top 5 most liked prompts for the creator being followed
        prompts = (
            db.query(Prompt, func.count(models.PostLike.id).label('likes_count'))
            .outerjoin(models.PostLike, models.PostLike.prompt_id == Prompt.id)
            .filter(Prompt.account_address == follow.creator_account)
            .group_by(Prompt.id)
            .order_by(func.count(models.PostLike.id).desc())
            .limit(5)
            .all()
        )

        result.append({
            "creator_account": follow.creator_account,
            "top_5_prompts": [
                {
                    "prompt": prompt.prompt,
                    "likes": likes_count,
                    "comments": len(prompt.comments),
                    "created_at": prompt.created_at
                } for prompt, likes_count in prompts
            ]
        })

    return {"follower_account": follower_account, "following_with_top_prompts": result}



@router.get("/feed/")
def social_feed(user_account: str, page: int = 1, page_size: int = 10, db: Session = Depends(get_session)):
    """
    Social feed: Return prompts from creators the user is following and random new creators, along with total number
    of comments and likes, as well as the top 2 comments for each prompt.

    - **user_account**: The account wallet address of the user requesting the feed.
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
    feed = []
    for prompt in paginated_prompts:
        # Get the total number of comments for the prompt
        total_comments = db.query(models.PostComment).filter(
            models.PostComment.prompt_id == prompt.id,
            models.PostComment.prompt_type == prompt.prompt_type
        ).count()

        # Get the top 2 comments for the prompt
        top_comments = db.query(models.PostComment).filter(
            models.PostComment.prompt_id == prompt.id,
            models.PostComment.prompt_type == prompt.prompt_type
        ).order_by(models.PostComment.created_at.desc()).limit(2).all()

        # Get the total number of likes for the prompt
        total_likes = db.query(models.PostLike).filter(
            models.PostLike.prompt_id == prompt.id,
            models.PostLike.prompt_type == prompt.prompt_type
        ).count()

        feed.append({
            "ipfs_image_url": prompt.ipfs_image_url,
            "prompt": prompt.prompt,
            "account_address": prompt.account_address,
            "post_name": prompt.post_name,
            "likes_count": total_likes,
            "comments_count": total_comments,
            "top_comments": [
                {
                    "user_account": comment.user_account,
                    "comment": comment.comment,
                    "created_at": comment.created_at
                } for comment in top_comments
            ],
            "public": prompt.public
        })

    return {
        "results": feed,
        "total": total_prompts,
        "page": page,
        "page_size": page_size
    }



@router.get("/feed/followers/")
def get_feed_for_followers(user_account: str, db: Session = Depends(get_session), page: int = 1, page_size: int = 10):
    """
    Get a randomized feed consisting of the prompts from accounts following a given user.
    
    - **user_account**: The account of the user to get the followers' feed for.
    - **page**: Page number for pagination.
    - **page_size**: Number of prompts per page.
    """
    followers = db.query(models.Follow.follower_account).filter(models.Follow.creator_account == user_account).all()
    followers_accounts = [follower.follower_account for follower in followers]

    # Fetch prompts from followers with random ordering
    query = db.query(Prompt).filter(Prompt.account_address.in_(followers_accounts)).order_by(func.random())
    total_prompts = query.count()
    paginated_prompts = query.offset((page - 1) * page_size).limit(page_size).all()

    feed = []
    for prompt in paginated_prompts:
        feed.append({
            "prompt": prompt.prompt,
            "likes": len(prompt.likes),
            "comments": len(prompt.comments),
            "created_at": prompt.created_at,
            "account_address": prompt.account_address
        })

    return {"total": total_prompts, "page": page, "page_size": page_size, "feed": feed}


@router.get("/feed/following/")
def get_feed_for_following(user_account: str, db: Session = Depends(get_session), page: int = 1, page_size: int = 10):
    """
    Get a randomized feed consisting of the prompts from accounts the user is following.
    
    - **user_account**: The account of the user to get the following feed for.
    - **page**: Page number for pagination.
    - **page_size**: Number of prompts per page.
    """
    following = db.query(models.Follow.creator_account).filter(models.Follow.follower_account == user_account).all()
    following_accounts = [follow.creator_account for follow in following]

    # Fetch prompts from the creators the user is following with random ordering
    query = db.query(Prompt).filter(Prompt.account_address.in_(following_accounts)).order_by(func.random())
    total_prompts = query.count()
    paginated_prompts = query.offset((page - 1) * page_size).limit(page_size).all()

    feed = []
    for prompt in paginated_prompts:
        feed.append({
            "prompt": prompt.prompt,
            "likes": len(prompt.likes),
            "comments": len(prompt.comments),
            "created_at": prompt.created_at,
            "account_address": prompt.account_address
        })

    return {"total": total_prompts, "page": page, "page_size": page_size, "feed": feed}



@router.get("/feed/combined/")
def get_combined_feed(user_account: str, db: Session = Depends(get_session), page: int = 1, page_size: int = 10):
    """
    Get a randomized combined feed consisting of prompts from both the user's followers and the accounts the user is following.
    
    - **user_account**: The account of the user to get the combined feed for.
    - **page**: Page number for pagination.
    - **page_size**: Number of prompts per page.
    """
    # Get followers' accounts
    followers = db.query(models.Follow.follower_account).filter(models.Follow.creator_account == user_account).all()
    followers_accounts = [follower.follower_account for follower in followers]

    # Get following accounts
    following = db.query(models.Follow.creator_account).filter(models.Follow.follower_account == user_account).all()
    following_accounts = [follow.creator_account for follow in following]

    # Combine followers and following accounts
    all_accounts = list(set(followers_accounts + following_accounts))

    # Fetch prompts from all combined accounts with random ordering
    query = db.query(Prompt).filter(Prompt.account_address.in_(all_accounts)).order_by(func.random())
    total_prompts = query.count()
    paginated_prompts = query.offset((page - 1) * page_size).limit(page_size).all()

    feed = []
    for prompt in paginated_prompts:
        feed.append({
            "prompt": prompt.prompt,
            "likes": len(prompt.likes),
            "comments": len(prompt.comments),
            "created_at": prompt.created_at,
            "account_address": prompt.account_address
        })

    return {"total": total_prompts, "page": page, "page_size": page_size, "feed": feed}
