from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
from app.core.database import get_session
from . import schemas, services    
from app.prompts import models
from app.core.helpers import paginate
from app.core.enums.premium_filters import PremiumPromptFilterType
from app.socialfeed.services import update_user_stats



router = APIRouter()



@router.post("/add-premium-prompts/", response_model=schemas.PremiumPromptResponse)
def add_premium_prompt(premium_data: schemas.PremiumPromptCreate, db: Session = Depends(get_session)):
    """
    Add a new premium prompt in the marketplace.

    - **ipfs_image_url**: IPFS URL for the image.
    - **account_address**: Address of the creator.
    - **collection_name**: Name of the collection.
    - **max_supply**: Maximum supply for the NFT.
    - **prompt_nft_price**: Price of the NFT in the collection.
    """
    if not premium_data.prompt_tag:
        raise HTTPException(status_code=400, detail="prompt_tag is required")

    new_premium_prompt = models.Prompt(
        ipfs_image_url=premium_data.ipfs_image_url,
        prompt=premium_data.prompt,
        post_name=premium_data.post_name,
        prompt_tag=premium_data.prompt_tag,  # Make sure this is included
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

    # Return the response using the Pydantic model schema
    return schemas.PremiumPromptResponse(
        ipfs_image_url=new_premium_prompt.ipfs_image_url,
        account_address=new_premium_prompt.account_address,
        public=new_premium_prompt.public,
        collection_name=new_premium_prompt.collection_name,
        max_supply=new_premium_prompt.max_supply,
        prompt_nft_price=new_premium_prompt.prompt_nft_price
    )






@router.get("/get-premium-prompts/", response_model=schemas.PremiumPromptListResponse)
def get_premium_prompts(page: int = 1, page_size: int = 10, db: Session = Depends(get_session)):
    """
    Retrieve premium prompts with pagination.

    - **page**: Page number for pagination (default: 1).
    - **page_size**: Number of premium prompts per page (default: 10).
    """
    query = db.query(models.Prompt).filter(models.Prompt.prompt_type == models.PromptTypeEnum.PREMIUM)
    
    total_prompts = query.count()
    paginated_prompts = paginate(query, page, page_size)

    return schemas.PremiumPromptListResponse(
        prompts=[
            schemas.PremiumPromptResponse(
                ipfs_image_url=prompt.ipfs_image_url,
                account_address=prompt.account_address,
                public=prompt.public,
                collection_name=prompt.collection_name,
                max_supply=prompt.max_supply,
                prompt_nft_price=prompt.prompt_nft_price,
                likes=prompt.likes,
                comments=prompt.comments
            )
            for prompt in paginated_prompts
        ],
        total=total_prompts,
        page=page,
        page_size=page_size
    )


@router.get("/premium-prompt-filters/")
def get_premium_prompt_filters():
    """
    Get all available premium prompt filters.
    """
    filters = [filter_type.value for filter_type in PremiumPromptFilterType]
    return {"premium_prompt_filters": filters}

@router.post("/filter-premium-prompts/", response_model=schemas.PremiumPromptListResponse)
def filter_premium_prompts(filter_data: schemas.PremiumPromptFilterRequest, db: Session = Depends(get_session)):
    """
    Filter premium prompts based on:
    
    - **recent**: Prompts created within the last 24 hours.
    - **popular**: Random selection of premium prompts.
    - **trending**: Prompts sorted by the number of likes.
    
    Supports pagination with `page` and `page_size`.
    """
    query = db.query(models.Prompt).filter(models.Prompt.prompt_type == models.PromptTypeEnum.PREMIUM)
    
    # Apply the filter based on the filter_type
    if filter_data.filter_type == PremiumPromptFilterType.RECENT:
        # Prompts created in the last 24 hours
        last_24_hours = datetime.utcnow() - timedelta(hours=24)
        query = query.filter(models.Prompt.created_at >= last_24_hours)
    
    elif filter_data.filter_type == PremiumPromptFilterType.POPULAR:
        # Random prompts
        premium_prompts = query.all()  # Fetch all prompts
        random.shuffle(premium_prompts)  # Shuffle the list to randomize
        paginated_prompts = premium_prompts[(filter_data.page - 1) * filter_data.page_size : filter_data.page * filter_data.page_size]
        total_prompts = len(premium_prompts)
        return schemas.PremiumPromptListResponse(
            prompts=[
                schemas.PremiumPromptResponse(
                    ipfs_image_url=prompt.ipfs_image_url,
                    account_address=prompt.account_address,
                    public=prompt.public,
                    collection_name=prompt.collection_name,
                    max_supply=prompt.max_supply,
                    prompt_nft_price=prompt.prompt_nft_price,
                    likes=prompt.likes,
                    comments=prompt.comments
                )
                for prompt in paginated_prompts
            ],
            total=total_prompts,
            page=filter_data.page,
            page_size=filter_data.page_size
        )
    
    elif filter_data.filter_type == PremiumPromptFilterType.TRENDING:
        # Sort by number of likes (descending order)
        query = query.order_by(models.Prompt.likes.desc())
    
    # For recent and trending, apply pagination
    total_prompts = query.count()
    paginated_prompts = paginate(query, filter_data.page, filter_data.page_size)

    return schemas.PremiumPromptListResponse(
        prompts=[
            schemas.PremiumPromptResponse(
                ipfs_image_url=prompt.ipfs_image_url,
                account_address=prompt.account_address,
                public=prompt.public,
                collection_name=prompt.collection_name,
                max_supply=prompt.max_supply,
                prompt_nft_price=prompt.prompt_nft_price,
                likes=prompt.likes,
                comments=prompt.comments
            )
            for prompt in paginated_prompts
        ],
        total=total_prompts,
        page=filter_data.page,
        page_size=filter_data.page_size
    )