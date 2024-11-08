"""added db indexing on the models

Revision ID: 4bae3c93c3be
Revises: 15436d808394
Create Date: 2024-09-13 11:22:41.636177

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4bae3c93c3be'
down_revision: Union[str, None] = '15436d808394'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_follows_creator_account'), 'follows', ['creator_account'], unique=False)
    op.create_index(op.f('ix_follows_follower_account'), 'follows', ['follower_account'], unique=False)
    op.create_index(op.f('ix_post_comments_user_account'), 'post_comments', ['user_account'], unique=False)
    op.create_index(op.f('ix_post_likes_user_account'), 'post_likes', ['user_account'], unique=False)
    op.create_index(op.f('ix_prompts_account_address'), 'prompts', ['account_address'], unique=False)
    op.create_index(op.f('ix_prompts_collection_name'), 'prompts', ['collection_name'], unique=False)
    op.create_index(op.f('ix_prompts_max_supply'), 'prompts', ['max_supply'], unique=False)
    op.create_index(op.f('ix_prompts_post_name'), 'prompts', ['post_name'], unique=False)
    op.create_index(op.f('ix_prompts_prompt_nft_price'), 'prompts', ['prompt_nft_price'], unique=False)
    op.create_index(op.f('ix_prompts_prompt_tag'), 'prompts', ['prompt_tag'], unique=False)
    op.create_index(op.f('ix_prompts_prompt_type'), 'prompts', ['prompt_type'], unique=False)
    op.create_index(op.f('ix_prompts_public'), 'prompts', ['public'], unique=False)
    op.create_index(op.f('ix_user_stats_last_generation'), 'user_stats', ['last_generation'], unique=False)
    op.create_index(op.f('ix_user_stats_streak_days'), 'user_stats', ['streak_days'], unique=False)
    op.create_index(op.f('ix_user_stats_total_generations'), 'user_stats', ['total_generations'], unique=False)
    op.create_index(op.f('ix_user_stats_xp'), 'user_stats', ['xp'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_stats_xp'), table_name='user_stats')
    op.drop_index(op.f('ix_user_stats_total_generations'), table_name='user_stats')
    op.drop_index(op.f('ix_user_stats_streak_days'), table_name='user_stats')
    op.drop_index(op.f('ix_user_stats_last_generation'), table_name='user_stats')
    op.drop_index(op.f('ix_prompts_public'), table_name='prompts')
    op.drop_index(op.f('ix_prompts_prompt_type'), table_name='prompts')
    op.drop_index(op.f('ix_prompts_prompt_tag'), table_name='prompts')
    op.drop_index(op.f('ix_prompts_prompt_nft_price'), table_name='prompts')
    op.drop_index(op.f('ix_prompts_post_name'), table_name='prompts')
    op.drop_index(op.f('ix_prompts_max_supply'), table_name='prompts')
    op.drop_index(op.f('ix_prompts_collection_name'), table_name='prompts')
    op.drop_index(op.f('ix_prompts_account_address'), table_name='prompts')
    op.drop_index(op.f('ix_post_likes_user_account'), table_name='post_likes')
    op.drop_index(op.f('ix_post_comments_user_account'), table_name='post_comments')
    op.drop_index(op.f('ix_follows_follower_account'), table_name='follows')
    op.drop_index(op.f('ix_follows_creator_account'), table_name='follows')
    # ### end Alembic commands ###
