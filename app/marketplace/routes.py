from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
from app.core.database import get_session
from . import schemas, services    
from app.prompts import models
from sqlalchemy import func, select, desc
from app.socialfeed import models as socialfeed_models
from app.core.helpers import paginate
from app.core.enums.premium_filters import PremiumPromptFilterType
from app.socialfeed.services import update_user_stats



router = APIRouter()



@router.post("/add-premium-prompts/", response_model=schemas.PremiumPromptResponse)
async def add_premium_prompt(premium_data: schemas.PremiumPromptCreate, db: Session = Depends(get_session)):
    """
    Add a new premium prompt in the marketplace.

    - **ipfs_image_url**: IPFS URL for the image.
    - **account_address**: Address of the creator.
    - **prompt**: Encrypted Prompt text.
    - **post_name**: Name of the post.
    - **cid**: CID of the image.
    - **collection_name**: Name of the collection.
    - **max_supply**: Maximum supply for the NFT.
    - **prompt_nft_price**: Price of the NFT in the collection.
    """
    if not premium_data.prompt_tag:
        raise HTTPException(status_code=400, detail="prompt_tag is required")

    try:
        new_premium_prompt = models.Prompt(
            ipfs_image_url=premium_data.ipfs_image_url,
            prompt=premium_data.prompt,
            post_name=premium_data.post_name,
            ai_model=premium_data.ai_model,
            chain=premium_data.chain,  # Ensure chain is passed correctly
            cid=premium_data.cid,
            prompt_tag=premium_data.prompt_tag,
            prompt_type=models.PromptTypeEnum.PREMIUM,
            account_address=premium_data.account_address,
            public=False,
            collection_name=premium_data.collection_name,
            max_supply=premium_data.max_supply,
            prompt_nft_price=premium_data.prompt_nft_price
        )

        db.add(new_premium_prompt)
        db.commit()
        db.refresh(new_premium_prompt)

        # Update user stats (generation count and XP)
        update_user_stats(new_premium_prompt.account_address, db)
        likes_count = db.query(socialfeed_models.PostLike).filter(socialfeed_models.PostLike.prompt_id == new_premium_prompt.id).count()
        comments_count = db.query(socialfeed_models.PostComment).filter(socialfeed_models.PostComment.prompt_id == new_premium_prompt.id).count()

        # Return the response using the Pydantic model schema
        return schemas.PremiumPromptResponse(
            id=new_premium_prompt.id,
            ipfs_image_url=new_premium_prompt.ipfs_image_url,
            prompt=new_premium_prompt.prompt,
            post_name=new_premium_prompt.post_name,
            ai_model=new_premium_prompt.ai_model,
            chain=new_premium_prompt.chain,  
            public=new_premium_prompt.public,  
            account_address=new_premium_prompt.account_address,
            cid=new_premium_prompt.cid,
            collection_name=new_premium_prompt.collection_name,
            max_supply=new_premium_prompt.max_supply,
            prompt_nft_price=new_premium_prompt.prompt_nft_price,
            likes=likes_count or 0,
            comments=comments_count or 0,
            grant_access=new_premium_prompt.grant_access or False
        )
    except Exception as e:
        detail = {
            "info": "Failed to add premium prompt",
            "error": str(e),
        }
        raise HTTPException(status_code=500, detail=detail)






@router.get("/get-premium-prompts/", response_model=schemas.PremiumPromptListResponse)
async def get_premium_prompts(page: int = 1, page_size: int = 10, db: Session = Depends(get_session)):
    """
    Get all premium prompts.
    """
    try:
        # Query for premium prompts and order by created_at in descending order
        query = db.query(models.Prompt).filter(models.Prompt.prompt_type == models.PromptTypeEnum.PREMIUM).order_by(models.Prompt.created_at.desc())
    
        total_prompts = query.count()
        paginated_prompts = query.offset((page - 1) * page_size).limit(page_size).all()

        prompts_with_counts = []
        for prompt in paginated_prompts:
            likes_count = db.query(socialfeed_models.PostLike).filter(socialfeed_models.PostLike.prompt_id == prompt.id).count()
            comments_count = db.query(socialfeed_models.PostComment).filter(socialfeed_models.PostComment.prompt_id == prompt.id).count()

            prompts_with_counts.append(
                schemas.PremiumPromptResponse(
                    id=prompt.id,
                    ipfs_image_url=prompt.ipfs_image_url,
                    prompt=prompt.prompt,
                    post_name=prompt.post_name,
                    ai_model=prompt.ai_model,
                    chain=prompt.chain,  
                    public=prompt.public,  
                    account_address=prompt.account_address,
                    cid=prompt.cid,
                    collection_name=prompt.collection_name,
                    max_supply=prompt.max_supply,
                    prompt_nft_price=prompt.prompt_nft_price,
                    likes=likes_count or 0,
                    comments=comments_count or 0,
                    grant_access=prompt.grant_access or False
                )
            )

        
        return schemas.PremiumPromptListResponse(
            prompts=prompts_with_counts,
            total=total_prompts,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        detail = {
            "info": "Failed to get premium prompts",
            "error": str(e),
        }
        raise HTTPException(status_code=500, detail=detail)



@router.get("/premium-prompt-filters/")
async def get_premium_prompt_filters():
    """
    Get all available premium prompt filters.
    """
    try:
        filters = [filter_type.value for filter_type in PremiumPromptFilterType]
        return {"premium_prompt_filters": filters}
    except Exception as e:
        detail = {
            "info": "Failed to get premium prompt filters",
            "error": str(e),
        }
        raise HTTPException(status_code=500, detail=detail)



@router.post("/filter-premium-prompts/", response_model=schemas.PremiumPromptListResponse)
async def filter_premium_prompts(filter_data: schemas.PremiumPromptFilterRequest, db: Session = Depends(get_session)):
    try:
        query = db.query(models.Prompt).filter(models.Prompt.prompt_type == models.PromptTypeEnum.PREMIUM)

        # Filter by `recent`, `popular`, or `trending`
        if filter_data.filter_type == PremiumPromptFilterType.RECENT:
            last_24_hours = datetime.utcnow() - timedelta(hours=24)
            query = query.filter(models.Prompt.created_at >= last_24_hours)
        elif filter_data.filter_type == PremiumPromptFilterType.POPULAR:
            query = query.order_by(func.random())
        elif filter_data.filter_type == PremiumPromptFilterType.TRENDING:
            query = query.outerjoin(socialfeed_models.PostLike).group_by(models.Prompt.id).order_by(func.count(socialfeed_models.PostLike.id).desc())

        total_prompts = query.count()
        paginated_prompts = query.offset((filter_data.page - 1) * filter_data.page_size).limit(filter_data.page_size).all()

        prompt_ids = [prompt.id for prompt in paginated_prompts]

        # Batch query for likes and comments count
        likes_comments_data = (
            db.query(
                models.Prompt.id,
                func.count(socialfeed_models.PostLike.id).label('likes_count'),
                func.count(socialfeed_models.PostComment.id).label('comments_count')
            )
            .outerjoin(socialfeed_models.PostLike, socialfeed_models.PostLike.prompt_id == models.Prompt.id)
            .outerjoin(socialfeed_models.PostComment, socialfeed_models.PostComment.prompt_id == models.Prompt.id)
            .filter(models.Prompt.id.in_(prompt_ids))
            .group_by(models.Prompt.id)
            .all()
        )

        # Map likes and comments count by prompt ID, with index-based access
        likes_comments_map = {lc[0]: {'likes_count': lc[1], 'comments_count': lc[2]} for lc in likes_comments_data}

        # Prepare the response
        prompts_with_counts = []
        for prompt in paginated_prompts:
            likes_comments = likes_comments_map.get(prompt.id, {'likes_count': 0, 'comments_count': 0})
            prompts_with_counts.append(
                schemas.PremiumPromptResponse(
                    id=prompt.id,
                    ipfs_image_url=prompt.ipfs_image_url,
                    prompt=prompt.prompt,
                    post_name=prompt.post_name,
                    ai_model=prompt.ai_model,
                    chain=prompt.chain,  
                    public=prompt.public,  
                    account_address=prompt.account_address,
                    cid=prompt.cid,
                    collection_name=prompt.collection_name,
                    max_supply=prompt.max_supply,
                    prompt_nft_price=prompt.prompt_nft_price,
                    likes=likes_comments['likes_count'],
                    comments=likes_comments['comments_count'],
                    grant_access=prompt.grant_access
                )
            )

        return schemas.PremiumPromptListResponse(
            prompts=prompts_with_counts,
            total=total_prompts,
            page=filter_data.page,
            page_size=filter_data.page_size
        )
    except Exception as e:
        detail = {
            "info": "Failed to filter premium prompts",
            "error": str(e),
        }
        raise HTTPException(status_code=500, detail=detail)
