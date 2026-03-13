"""Initial schema for Guadalajara Wine Finder

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # users
    op.create_table(
        'users',
        sa.Column('id', sa.String(1), primary_key=True),
        sa.Column('display_name', sa.String(255), nullable=False),
        sa.Column('locale', sa.String(5), nullable=False, server_default='en'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # stores
    op.create_table(
        'stores',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),  # supermarket/specialty
        sa.Column('base_url', sa.String(512), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true'),
    )

    # wines (canonical entity)
    op.create_table(
        'wines',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('canonical_name', sa.String(512), nullable=False),
        sa.Column('producer', sa.String(255), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('region', sa.String(255), nullable=True),
        sa.Column('type', sa.String(50), nullable=True),  # red/white/rose/sparkling/other
        sa.Column('grapes', ARRAY(sa.String()), nullable=True),
        sa.Column('sweetness', sa.String(50), nullable=True, server_default='unknown'),
        sa.Column('is_grape_wine', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # offers
    op.create_table(
        'offers',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('store_id', sa.Integer(), sa.ForeignKey('stores.id'), nullable=False),
        sa.Column('wine_id', sa.Integer(), sa.ForeignKey('wines.id'), nullable=True),
        sa.Column('listed_name', sa.String(512), nullable=False),
        sa.Column('price_mxn', sa.Numeric(10, 2), nullable=False),
        sa.Column('discount_text', sa.String(255), nullable=True),
        sa.Column('volume_ml', sa.Integer(), nullable=True),
        sa.Column('availability', sa.String(50), nullable=True),  # in_stock/unknown/out_of_stock
        sa.Column('product_url', sa.String(1024), nullable=True),
        sa.Column('captured_at', sa.DateTime(), nullable=False),
    )

    # price_history
    op.create_table(
        'price_history',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('wine_id', sa.Integer(), sa.ForeignKey('wines.id'), nullable=False),
        sa.Column('store_id', sa.Integer(), sa.ForeignKey('stores.id'), nullable=False),
        sa.Column('price_mxn', sa.Numeric(10, 2), nullable=False),
        sa.Column('captured_at', sa.DateTime(), nullable=False),
    )

    # raw_pages
    op.create_table(
        'raw_pages',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('store_id', sa.Integer(), sa.ForeignKey('stores.id'), nullable=False),
        sa.Column('url', sa.String(1024), nullable=False),
        sa.Column('fetched_at', sa.DateTime(), nullable=False),
        sa.Column('content_ref', sa.String(512), nullable=True),
        sa.Column('content_hash', sa.String(64), nullable=True),
        sa.Column('fetch_status', sa.String(50), nullable=True),
    )

    # external_reviews
    op.create_table(
        'external_reviews',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('wine_id', sa.Integer(), sa.ForeignKey('wines.id'), nullable=False),
        sa.Column('source_name', sa.String(255), nullable=True),
        sa.Column('source_url', sa.String(1024), nullable=True),
        sa.Column('fetched_at', sa.DateTime(), nullable=False),
        sa.Column('raw_ref', sa.String(512), nullable=True),
        sa.Column('extracted_json', JSONB, nullable=True),
    )

    # review_aggregates
    op.create_table(
        'review_aggregates',
        sa.Column('wine_id', sa.Integer(), sa.ForeignKey('wines.id'), primary_key=True),
        sa.Column('avg_rating', sa.Numeric(3, 2), nullable=True),
        sa.Column('rating_scale', sa.String(50), nullable=True),
        sa.Column('descriptors', JSONB, nullable=True),
        sa.Column('pros', JSONB, nullable=True),
        sa.Column('cons', JSONB, nullable=True),
        sa.Column('disagreement_summary', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # user_ratings
    op.create_table(
        'user_ratings',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.String(1), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('wine_id', sa.Integer(), sa.ForeignKey('wines.id'), nullable=False),
        sa.Column('rating_1_5', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('tried_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # recommendation_runs
    op.create_table(
        'recommendation_runs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('mode', sa.String(50), nullable=False),  # daily/weekly/manual
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(50), nullable=True),  # success/fail
        sa.Column('logs_ref', sa.String(512), nullable=True),
    )

    # recommendations
    op.create_table(
        'recommendations',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('run_id', sa.Integer(), sa.ForeignKey('recommendation_runs.id'), nullable=False),
        sa.Column('user_id', sa.String(1), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('kind', sa.String(50), nullable=False),  # recommended_buys/cheapest_favorites
        sa.Column('rank', sa.Integer(), nullable=False),
        sa.Column('wine_id', sa.Integer(), sa.ForeignKey('wines.id'), nullable=False),
        sa.Column('offer_id', sa.Integer(), sa.ForeignKey('offers.id'), nullable=True),
        sa.Column('score', sa.Numeric(10, 4), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('explanation_locale', sa.String(5), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table('recommendations')
    op.drop_table('recommendation_runs')
    op.drop_table('user_ratings')
    op.drop_table('review_aggregates')
    op.drop_table('external_reviews')
    op.drop_table('raw_pages')
    op.drop_table('price_history')
    op.drop_table('offers')
    op.drop_table('wines')
    op.drop_table('stores')
    op.drop_table('users')
