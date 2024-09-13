from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, select
from datetime import datetime, timedelta
from app.core.database import get_session
from . import schemas, services, models
from app.prompts.models import Prompt
from app.core.helpers import paginate
router = APIRouter()


@router.post("/like-prompt/")
async def like_prompt(like_data: schemas.LikePromptRequest, db: Session = Depends(get_session)):
    """
    Like a public or premium prompt.

    - **prompt_id**: ID of the prompt (public or premium).
    - **prompt_type**: Whether the prompt is public or premium.
    - **user_account**: The account of the user liking the prompt.
    """
    try:
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
            raise HTTPException(status_code=409, detail="User has already liked this prompt")

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
    except Exception as e:
        detail = {
            "info": "Failed to like prompt",
            "error": str(e),
        }
        raise HTTPException(status_code=500, detail=detail)



@router.post("/comment-prompt/")
async def comment_prompt(comment_data: schemas.CommentPromptRequest, db: Session = Depends(get_session)):
    """
    Add a comment to a public or premium prompt.

    - **prompt_id**: ID of the prompt (public or premium).
    - **prompt_type**: Whether the prompt is public or premium.
    - **user_account**: The account of the user commenting.
    - **comment**: The comment text.
    """
    try:
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
    except Exception as e:
        detail = {
            "info": "Failed to comment on prompt",
            "error": str(e),
        }
        raise HTTPException(status_code=500, detail=detail)


@router.get("/get-prompt-comments/", response_model=schemas.CommentsListResponse)
async def get_prompt_comments(prompt_id: int, prompt_type: schemas.PromptTypeEnum, limit: int = 2, db: Session = Depends(get_session)):
    """
    Retrieve comments for a specific public or premium prompt.
    
    By default, only the top 2 comments are returned. You can specify a different limit via the query parameter.

    - **prompt_id**: ID of the prompt (public or premium).
    - **prompt_type**: Whether the prompt is public or premium.
    - **limit**: The number of comments to return (default is 2).
    """
    try:
        # Fetch the prompt and its comments in a single query using join
        prompt_with_comments = (
            db.query(Prompt, models.PostComment)
            .outerjoin(models.PostComment, models.PostComment.prompt_id == Prompt.id)
            .filter(
                Prompt.id == prompt_id,
                Prompt.prompt_type == prompt_type
            )
            .limit(limit)
            .all()
        )

        # Check if the prompt exists
        if not prompt_with_comments:
            raise HTTPException(status_code=404, detail="Prompt not found")

        # Extract the prompt and comments
        prompt = prompt_with_comments[0][0]  # The prompt itself
        comments = [pc[1] for pc in prompt_with_comments if pc[1] is not None]

        # Fetch total comments count in one go
        total_comments = db.query(func.count(models.PostComment.id)).filter(
            models.PostComment.prompt_id == prompt_id,
            models.PostComment.prompt_type == prompt_type
        ).scalar()

        # Return the response with comments and total count
        return schemas.CommentsListResponse(
            comments=[
                schemas.CommentResponse(
                    user_account=comment.user_account,
                    comment=comment.comment
                ) for comment in comments
            ],
            total_comments=total_comments
        )
    except Exception as e:
        detail = {
            "info": "Failed to get prompt comments",
            "error": str(e),
        }
        raise HTTPException(status_code=500, detail=detail)






@router.post("/follow-creator/")
async def follow_creator(follower_account: str, creator_account: str, db: Session = Depends(get_session)):
    """
    Follow a creator.
    
    - **follower_account**: The account of the user who wants to follow.
    - **creator_account**: The account of the creator to be followed.
    """
    try:
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
    except Exception as e:
        detail = {
            "info": "Failed to follow creator",
            "error": str(e),
        }
        raise HTTPException(status_code=500, detail=detail)


@router.delete("/unfollow-creator/")
async def unfollow_creator(follower_account: str, creator_account: str, db: Session = Depends(get_session)):
    """
    Unfollow a creator.
    
    - **follower_account**: The account of the user who wants to unfollow.
    - **creator_account**: The account of the creator to be unfollowed.
    """
    try:
        follow_relationship = db.query(models.Follow).filter(
            models.Follow.follower_account == follower_account,
            models.Follow.creator_account == creator_account
        ).first()

        if not follow_relationship:
            raise HTTPException(status_code=404, detail="Not following this creator")

        db.delete(follow_relationship)
        db.commit()

        return {"message": "Successfully unfollowed the creator"}
    except Exception as e:
        detail = {
            "info": "Failed to unfollow creator",
            "error": str(e),
        }
        raise HTTPException(status_code=500, detail=detail)


@router.get("/creator-followers/")
async def get_creator_followers(creator_account: str, db: Session = Depends(get_session)):
    """
    Get a list of followers for a specific creator along with their top 5 most liked prompts.
    
    - **creator_account**: The account of the creator whose followers are being retrieved.
    """
    try:
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
                        "prompt_id": prompt.id,
                        "ipfs_image_url": prompt.ipfs_image_url,
                        "likes": likes_count,
                        "comments": len(prompt.comments),
                        "created_at": prompt.created_at
                    } for prompt, likes_count in prompts
                ]
            })

        return {"creator_account": creator_account, "followers_with_top_prompts": result}
    except Exception as e:
        detail = {
            "info": "Failed to get creator followers",
            "error": str(e),
        }
        raise HTTPException(status_code=500, detail=detail)



@router.get("/user-following/")
async def get_user_following(follower_account: str, db: Session = Depends(get_session)):
    """
    Get a list of creators a user is following along with their top 5 most liked prompts.
    
    - **follower_account**: The account of the user whose following list is being retrieved.
    """
    try:
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
                        "prompt_id": prompt.id,
                        "ipfs_image_url": prompt.ipfs_image_url,
                        "likes": likes_count,
                        "comments": len(prompt.comments),
                        "created_at": prompt.created_at
                    } for prompt, likes_count in prompts
                ]
            })

        return {"follower_account": follower_account, "following_with_top_prompts": result}
    except Exception as e:
        detail = {
            "info": "Failed to get user following",
            "error": str(e),
        }
        raise HTTPException(status_code=500, detail=detail)




@router.get("/feed/")
async def social_feed(user_account: str, page: int = 1, page_size: int = 10, db: Session = Depends(get_session)):
    """
    Social feed: Return prompts from creators the user is following and random new creators, along with total number
    of comments and likes, as well as the top 2 comments for each prompt.
    """
    try:

        # Get the list of creators the user is following
        followed_creators_subquery = (
            db.query(models.Follow.creator_account)
            .filter(models.Follow.follower_account == user_account)
            .subquery()
        )

        # Fetch prompts from followed creators
        followed_prompts_query = (
            db.query(Prompt)
            .filter(Prompt.account_address.in_(followed_creators_subquery))
        )

        # Fetch random creators (excluding those already followed)
        random_creators_query = (
            db.query(Prompt)
            .filter(~Prompt.account_address.in_(followed_creators_subquery))
            .order_by(func.random())
        )

        # Combine both followed prompts and random creator prompts
        combined_query = followed_prompts_query.union(random_creators_query)

        # Paginate the feed
        total_prompts = combined_query.count()
        paginated_prompts = combined_query.order_by(desc(Prompt.created_at)).offset((page - 1) * page_size).limit(page_size).all()

        # Fetch all necessary data (likes, comments, top 2 comments) in one go
        prompt_ids = [prompt.id for prompt in paginated_prompts]

        # Fetch total likes and comments counts for all prompts in a single batch query
        likes_comments_data = (
            db.query(
                Prompt.id,
                func.count(models.PostLike.id).label('likes_count'),
                func.count(models.PostComment.id).label('comments_count')
            )
            .outerjoin(models.PostLike, models.PostLike.prompt_id == Prompt.id)
            .outerjoin(models.PostComment, models.PostComment.prompt_id == Prompt.id)
            .filter(Prompt.id.in_(prompt_ids))
            .group_by(Prompt.id)
            .all()
        )

        # Fetch top 2 comments for each prompt in a single batch query
        top_comments_data = (
            db.query(
                models.PostComment.prompt_id,
                models.PostComment.user_account,
                models.PostComment.comment,
                models.PostComment.created_at
            )
            .filter(models.PostComment.prompt_id.in_(prompt_ids))
            .order_by(models.PostComment.prompt_id, models.PostComment.created_at.desc())
            .limit(2 * len(prompt_ids))
            .all()
        )

        # Convert top_comments_data to a more usable structure (group by prompt_id)
        from collections import defaultdict
        top_comments_by_prompt = defaultdict(list)
        for comment in top_comments_data:
            top_comments_by_prompt[comment.prompt_id].append({
                "user_account": comment.user_account,
                "comment": comment.comment,
                "created_at": comment.created_at
            })

        # Construct the final feed using the fetched data
        feed = []
        for prompt in paginated_prompts:
            # Get likes and comments data for the prompt
            likes_comments = next((lc for lc in likes_comments_data if lc[0] == prompt.id), None)
            likes_count = likes_comments.likes_count if likes_comments else 0
            comments_count = likes_comments.comments_count if likes_comments else 0

            # Get top 2 comments for the prompt
            top_comments = top_comments_by_prompt[prompt.id][:2]

            # Append the prompt data
            feed.append({
                "ipfs_image_url": prompt.ipfs_image_url,
                "prompt_id": prompt.id,
                "prompt": prompt.prompt,
                "prompt_type": prompt.prompt_type,
                "account_address": prompt.account_address,
                "post_name": prompt.post_name,
                "likes_count": likes_count,
                "comments_count": comments_count,
                "top_comments": top_comments,
                "public": prompt.public
            })

        return {
            "results": feed,
            "total": total_prompts,
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        detail = {
            "info": "Failed to get social feed",
            "error": str(e),
        }
        raise HTTPException(status_code=500, detail=detail)



@router.get("/feed/followers/")
async def get_feed_for_followers(user_account: str, db: Session = Depends(get_session), page: int = 1, page_size: int = 10):
    """
    Get a randomized feed consisting of the prompts from accounts following a given user.
    
    - **user_account**: The account of the user to get the followers' feed for.
    - **page**: Page number for pagination.
    - **page_size**: Number of prompts per page.
    """
    try:
        # Get list of followers
        followers_subquery = db.query(models.Follow.follower_account).filter(models.Follow.creator_account == user_account).subquery()

        # Fetch prompts from followers with random ordering
        query = db.query(Prompt).filter(Prompt.account_address.in_(followers_subquery))

        total_prompts = query.count()
        paginated_prompts = query.order_by(func.random()).offset((page - 1) * page_size).limit(page_size).all()

        # Fetch all necessary data (likes, comments) in one go
        prompt_ids = [prompt.id for prompt in paginated_prompts]

        likes_comments_data = (
            db.query(
                Prompt.id,
                func.count(models.PostLike.id).label('likes_count'),
                func.count(models.PostComment.id).label('comments_count')
            )
            .outerjoin(models.PostLike, models.PostLike.prompt_id == Prompt.id)
            .outerjoin(models.PostComment, models.PostComment.prompt_id == Prompt.id)
            .filter(Prompt.id.in_(prompt_ids))
            .group_by(Prompt.id)
            .all()
        )

        # Fetch top 2 comments for each prompt in a single batch query
        top_comments_data = (
            db.query(
                models.PostComment.prompt_id,
                models.PostComment.user_account,
                models.PostComment.comment,
                models.PostComment.created_at
            )
            .filter(models.PostComment.prompt_id.in_(prompt_ids))
            .order_by(models.PostComment.prompt_id, models.PostComment.created_at.desc())
            .limit(2 * len(prompt_ids))
            .all()
        )

        # Convert top_comments_data to a more usable structure (group by prompt_id)
        from collections import defaultdict
        top_comments_by_prompt = defaultdict(list)
        for comment in top_comments_data:
            top_comments_by_prompt[comment.prompt_id].append({
                "user_account": comment.user_account,
                "comment": comment.comment,
                "created_at": comment.created_at
            })

        feed = []
        for prompt in paginated_prompts:
            # Get likes and comments data for the prompt
            likes_comments = next((lc for lc in likes_comments_data if lc[0] == prompt.id), None)
            likes_count = likes_comments.likes_count if likes_comments else 0
            comments_count = likes_comments.comments_count if likes_comments else 0
            # Get top 2 comments for the prompt
            top_comments = top_comments_by_prompt[prompt.id][:2]

            feed.append({
                "ipfs_image_url": prompt.ipfs_image_url,
                "prompt_id": prompt.id,
                "prompt": prompt.prompt,
                "prompt_type": prompt.prompt_type,
                "likes": likes_count,
                "comments": comments_count,
                "top_comments": top_comments,
                "created_at": prompt.created_at,
                "account_address": prompt.account_address
            })

        return {"total": total_prompts, "page": page, "page_size": page_size, "feed": feed}
    except Exception as e:
        detail = {
            "info": "Failed to get feed for followers",
            "error": str(e),
        }
        raise HTTPException(status_code=500, detail=detail)


@router.get("/feed/following/")
async def get_feed_for_following(user_account: str, db: Session = Depends(get_session), page: int = 1, page_size: int = 10):
    """
    Get a randomized feed consisting of the prompts from accounts the user is following.
    
    - **user_account**: The account of the user to get the following feed for.
    - **page**: Page number for pagination.
    - **page_size**: Number of prompts per page.
    """
    try:
        # Get list of accounts the user is following
        following_subquery = db.query(models.Follow.creator_account).filter(models.Follow.follower_account == user_account).subquery()

        # Fetch prompts from the creators the user is following with random ordering
        query = db.query(Prompt).filter(Prompt.account_address.in_(following_subquery))

        total_prompts = query.count()
        paginated_prompts = query.order_by(func.random()).offset((page - 1) * page_size).limit(page_size).all()

        # Fetch all necessary data (likes, comments) in one go
        prompt_ids = [prompt.id for prompt in paginated_prompts]

        likes_comments_data = (
            db.query(
                Prompt.id,
                func.count(models.PostLike.id).label('likes_count'),
                func.count(models.PostComment.id).label('comments_count')
            )
            .outerjoin(models.PostLike, models.PostLike.prompt_id == Prompt.id)
            .outerjoin(models.PostComment, models.PostComment.prompt_id == Prompt.id)
            .filter(Prompt.id.in_(prompt_ids))
            .group_by(Prompt.id)
            .all()
        )

        # Fetch top 2 comments for each prompt in a single batch query
        top_comments_data = (
            db.query(
                models.PostComment.prompt_id,
                models.PostComment.user_account,
                models.PostComment.comment,
                models.PostComment.created_at
            )
            .filter(models.PostComment.prompt_id.in_(prompt_ids))
            .order_by(models.PostComment.prompt_id, models.PostComment.created_at.desc())
            .limit(2 * len(prompt_ids))
            .all()
        )

        # Convert top_comments_data to a more usable structure (group by prompt_id)
        from collections import defaultdict
        top_comments_by_prompt = defaultdict(list)
        for comment in top_comments_data:
            top_comments_by_prompt[comment.prompt_id].append({
                "user_account": comment.user_account,
                "comment": comment.comment,
                "created_at": comment.created_at
            })

        feed = []
        for prompt in paginated_prompts:
            # Get likes and comments data for the prompt
            likes_comments = next((lc for lc in likes_comments_data if lc[0] == prompt.id), None)
            likes_count = likes_comments.likes_count if likes_comments else 0
            comments_count = likes_comments.comments_count if likes_comments else 0
            # Get top 2 comments for the prompt
            top_comments = top_comments_by_prompt[prompt.id][:2]

            feed.append({
                "ipfs_image_url": prompt.ipfs_image_url,
                "prompt_id": prompt.id,
                "prompt": prompt.prompt,
                "prompt_type": prompt.prompt_type,
                "likes": likes_count,
                "comments": comments_count,
                "top_comments": top_comments,
                "created_at": prompt.created_at,
                "account_address": prompt.account_address
            })

        return {"total": total_prompts, "page": page, "page_size": page_size, "feed": feed}
    except Exception as e:
        detail = {
            "info": "Failed to get feed for following",
            "error": str(e),
        }
        raise HTTPException(status_code=500, detail=detail)




@router.get("/feed/combined/")
async def get_combined_feed(user_account: str, db: Session = Depends(get_session), page: int = 1, page_size: int = 10):
    """
    Get a randomized combined feed consisting of prompts from both the user's followers and the accounts the user is following.
    
    - **user_account**: The account of the user to get the combined feed for.
    - **page**: Page number for pagination.
    - **page_size**: Number of prompts per page.
    """
    try:
        # Get followers' accounts
        followers_query = db.query(models.Follow.follower_account).filter(models.Follow.creator_account == user_account)

        # Get following accounts
        following_query = db.query(models.Follow.creator_account).filter(models.Follow.follower_account == user_account)

        # Combine followers and following accounts using union
        all_accounts_query = followers_query.union(following_query).subquery()

        # Fetch prompts from all combined accounts with random ordering
        query = db.query(Prompt).filter(Prompt.account_address.in_(all_accounts_query))

        total_prompts = query.count()
        paginated_prompts = query.order_by(func.random()).offset((page - 1) * page_size).limit(page_size).all()

        # Fetch all necessary data (likes, comments) in one go
        prompt_ids = [prompt.id for prompt in paginated_prompts]

        likes_comments_data = (
            db.query(
                Prompt.id,
                func.count(models.PostLike.id).label('likes_count'),
                func.count(models.PostComment.id).label('comments_count')
            )
            .outerjoin(models.PostLike, models.PostLike.prompt_id == Prompt.id)
            .outerjoin(models.PostComment, models.PostComment.prompt_id == Prompt.id)
            .filter(Prompt.id.in_(prompt_ids))
            .group_by(Prompt.id)
            .all()
        )

        # Fetch top 2 comments for each prompt in a single batch query
        top_comments_data = (
            db.query(
                models.PostComment.prompt_id,
                models.PostComment.user_account,
                models.PostComment.comment,
                models.PostComment.created_at
            )
            .filter(models.PostComment.prompt_id.in_(prompt_ids))
            .order_by(models.PostComment.prompt_id, models.PostComment.created_at.desc())
            .limit(2 * len(prompt_ids))
            .all()
        )

        # Convert top_comments_data to a more usable structure (group by prompt_id)
        from collections import defaultdict
        top_comments_by_prompt = defaultdict(list)
        for comment in top_comments_data:
            top_comments_by_prompt[comment.prompt_id].append({
                "user_account": comment.user_account,
                "comment": comment.comment,
                "created_at": comment.created_at
            })


        feed = []
        for prompt in paginated_prompts:
            # Get likes and comments data for the prompt
            likes_comments = next((lc for lc in likes_comments_data if lc[0] == prompt.id), None)
            likes_count = likes_comments.likes_count if likes_comments else 0
            comments_count = likes_comments.comments_count if likes_comments else 0
            # Get top 2 comments for the prompt
            top_comments = top_comments_by_prompt[prompt.id][:2]

            feed.append({
                "ipfs_image_url": prompt.ipfs_image_url,
                "prompt_id": prompt.id,
                "prompt": prompt.prompt,
                "prompt_type": prompt.prompt_type,
                "likes": likes_count,
                "comments": comments_count,
                "top_comments": top_comments,
                "created_at": prompt.created_at,
                "account_address": prompt.account_address
            })

        return {"total": total_prompts, "page": page, "page_size": page_size, "feed": feed}
    except Exception as e:
        detail = {
            "info": "Failed to get combined feed",
            "error": str(e),
        }
        raise HTTPException(status_code=500, detail=detail)




@router.get("/prompt-likes/")
async def get_prompt_likes(prompt_id: int, account_address: str, db: Session = Depends(get_session)):
    """
    Retrieve the number of likes for a specific prompt and whether the user has liked it or not.

    - **prompt_id**: The ID of the prompt.
    - **account_address**: The account address of the user to check if they have liked the prompt.
    """
    try:
        # Check if the prompt exists
        prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")

        # Count the number of likes for the prompt
        likes_count = db.query(models.PostLike).filter(
            models.PostLike.prompt_id == prompt_id
        ).count()

        # Check if the user has liked the prompt
        user_liked = db.query(models.PostLike).filter(
            models.PostLike.prompt_id == prompt_id,
            models.PostLike.user_account == account_address
        ).first()

        return {
            "prompt_id": prompt_id,
            "likes_count": likes_count,
            "user_liked": bool(user_liked)  # Return True if the user has liked, False otherwise
        }
    except Exception as e:
        detail = {
            "info": "Failed to get prompt likes",
            "error": str(e),
        }
        raise HTTPException(status_code=500, detail=detail)