from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_session
from . import schemas, services, models
from app.socialfeed import models as socialfeed_models
from app.core.helpers import paginate
from app.socialfeed.services import update_user_stats



router = APIRouter()


@router.post("/add-public-prompts/", response_model=schemas.PublicPromptResponse)
def add_public_prompt(public_data: schemas.PublicPromptCreate, db: Session = Depends(get_session)):
    """
    Add a new public prompt to the database.
    """
    # Create a new public prompt
    new_prompt = models.Prompt(
        ipfs_image_url=public_data.ipfs_image_url,
        prompt=public_data.prompt,
        account_address=public_data.account_address,
        post_name=public_data.post_name,
        public=True,
        prompt_tag=public_data.prompt_tag,
        prompt_type=models.PromptTypeEnum.PUBLIC
    )

    db.add(new_prompt)
    db.commit()
    db.refresh(new_prompt)

    # Count likes and comments (initially they are 0 since it's a new prompt)
    likes_count = db.query(socialfeed_models.PostLike).filter(socialfeed_models.PostLike.prompt_id == new_prompt.id).count()
    comments_count = db.query(socialfeed_models.PostComment).filter(socialfeed_models.PostComment.prompt_id == new_prompt.id).count()

    # Return the response
    return schemas.PublicPromptResponse(
        id=new_prompt.id,
        ipfs_image_url=new_prompt.ipfs_image_url,
        prompt=new_prompt.prompt,
        account_address=new_prompt.account_address,
        post_name=new_prompt.post_name,
        public=new_prompt.public,
        prompt_tag=new_prompt.prompt_tag,
        likes_count=likes_count,
        comments_count=comments_count
    )



@router.get("/prompt-tags/")
def get_prompt_tags():
    """
    Get all available prompt tags.
    """
    prompt_tags = [tag.value for tag in models.PromptTagEnum]
    return {"prompt_tags": prompt_tags}


@router.get("/get-public-prompts/", response_model=schemas.PublicPromptListResponse)
def get_public_prompts(page: int = 1, page_size: int = 10, db: Session = Depends(get_session)):
    # Query for all public prompts
    query = db.query(models.Prompt).filter(models.Prompt.prompt_type == models.PromptTypeEnum.PUBLIC).order_by(models.Prompt.created_at.desc())
    
    # Get total count for pagination
    total_prompts = query.count()
    
    # Apply pagination
    public_prompts = query.offset((page - 1) * page_size).limit(page_size).all()
    
    # For each prompt, count the number of likes and comments
    prompts_with_counts = []
    for prompt in public_prompts:
        likes_count = db.query(socialfeed_models.PostLike).filter(socialfeed_models.PostLike.prompt_id == prompt.id).count()
        comments_count = db.query(socialfeed_models.PostComment).filter(socialfeed_models.PostComment.prompt_id == prompt.id).count()
        
        prompts_with_counts.append(
            schemas.PublicPromptResponse(
                id=prompt.id,
                ipfs_image_url=prompt.ipfs_image_url,
                prompt=prompt.prompt,
                account_address=prompt.account_address,
                post_name=prompt.post_name,
                public=prompt.public,
                prompt_tag=prompt.prompt_tag,
                likes_count=likes_count,
                comments_count=comments_count
            )
        )
    
    # Return the list wrapped in the `PublicPromptListResponse` schema
    return schemas.PublicPromptListResponse(
        prompts=prompts_with_counts,
        total=total_prompts,
        page=page,
        page_size=page_size
    )

@router.post("/filter-public-prompts/", response_model=schemas.PublicPromptListResponse)
def filter_public_prompts(filter_data: schemas.PublicPromptFilterRequest, db: Session = Depends(get_session)):
    """
    Endpoint to filter public prompts with optional filtering by prompt tag and visibility.

    - **prompt_tag**: Filter by prompt tag (e.g., "3D Art", "Anime"). If set to "all", returns all public prompts.
    - **public**: Boolean flag to filter prompts by visibility. If `True`, returns only public prompts; if `False`, returns private ones.
    - **page**: Page number for pagination. Default is 1.
    - **page_size**: Number of prompts per page. Default is 10.

    Returns a paginated list of public prompts matching the provided criteria.
    """
    query = db.query(models.Prompt).filter(models.Prompt.prompt_type == models.PromptTypeEnum.PUBLIC)
    
    # Filter by prompt_tag if it's not set to "all"
    if filter_data.prompt_tag and filter_data.prompt_tag.lower() != 'all':
        query = query.filter(models.Prompt.prompt_tag == filter_data.prompt_tag)
    
    # Filter by public visibility
    if filter_data.public is not None:
        query = query.filter(models.Prompt.public == filter_data.public)
    
    # Apply pagination
    total_prompts = query.count()
    paginated_prompts = paginate(query, filter_data.page, filter_data.page_size)

    # Return the prompts with likes and comments count
    return schemas.PublicPromptListResponse(
        prompts=[
            schemas.PublicPromptResponse(
                id=prompt.id,
                ipfs_image_url=prompt.ipfs_image_url,
                prompt=prompt.prompt,
                account_address=prompt.account_address,
                post_name=prompt.post_name,
                public=prompt.public,
                prompt_tag=prompt.prompt_tag,
                likes_count=db.query(socialfeed_models.PostLike).filter(socialfeed_models.PostLike.prompt_id == prompt.id).count(),
                comments_count=db.query(socialfeed_models.PostComment).filter(socialfeed_models.PostComment.prompt_id == prompt.id).count()
            )
            for prompt in paginated_prompts
        ],
        total=total_prompts,
        page=filter_data.page,
        page_size=filter_data.page_size
    )
