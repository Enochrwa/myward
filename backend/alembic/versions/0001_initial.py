"""Initial schema — PostgreSQL.

Revision ID: 0001_initial
Revises:
Create Date: 2025-01-01 00:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable uuid extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("gender", sa.String(50), nullable=True),
        sa.Column("role", sa.String(20), nullable=False, server_default="user"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "clothing_categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("deepfashion_category_id", sa.Integer(), nullable=True),
        sa.Column("level", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["parent_id"], ["clothing_categories.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "clothing_attributes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("attribute_type", sa.String(50), nullable=False),
        sa.Column("deepfashion_attribute_id", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "wardrobe_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("brand", sa.String(255), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("subcategory", sa.String(100), nullable=True),
        sa.Column("size", sa.String(50), nullable=True),
        sa.Column("price", sa.Float(), nullable=True),
        sa.Column("currency", sa.String(10), server_default="USD"),
        sa.Column("material", sa.String(255), nullable=True),
        sa.Column("season", sa.String(50), nullable=True),
        sa.Column("weather_suitability", postgresql.JSONB(), nullable=True),
        sa.Column("formality_level", sa.Integer(), server_default="3"),
        sa.Column("image_url", sa.String(2048), nullable=True),
        sa.Column("source", sa.String(100), nullable=True),
        sa.Column("purchase_date", sa.Date(), nullable=True),
        sa.Column("resnet_features", postgresql.JSONB(), nullable=True),
        sa.Column("style_embedding", postgresql.JSONB(), nullable=True),
        sa.Column("dominant_color_rgb", postgresql.JSONB(), nullable=True),
        sa.Column("dominant_color_hex", sa.String(7), nullable=True),
        sa.Column("dominant_color_name", sa.String(50), nullable=True),
        sa.Column("color_palette", postgresql.JSONB(), nullable=True),
        sa.Column("color_temperature", sa.String(20), nullable=True),
        sa.Column("brightness", sa.Float(), nullable=True),
        sa.Column("saturation", sa.Float(), nullable=True),
        sa.Column("deepfashion_category_pred", postgresql.JSONB(), nullable=True),
        sa.Column("deepfashion_attributes_pred", postgresql.JSONB(), nullable=True),
        sa.Column("color", sa.String(255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("tags", sa.Text(), nullable=True),
        sa.Column("favorite", sa.Boolean(), server_default="false"),
        sa.Column("times_worn", sa.Integer(), server_default="0"),
        sa.Column("condition", sa.String(50), server_default="good"),
        sa.Column("date_added", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("last_worn", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["category_id"], ["clothing_categories.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "name", name="uq_user_item_name"),
    )
    op.create_index("idx_category_season", "wardrobe_items", ["category_id", "season"])
    op.create_index("idx_user_favorite", "wardrobe_items", ["user_id", "favorite"])
    op.create_index("idx_wardrobe_user_id", "wardrobe_items", ["user_id"])

    op.create_table(
        "outfits",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("season", sa.String(50), nullable=True),
        sa.Column("weather_suitability", postgresql.JSONB(), nullable=True),
        sa.Column("formality_level", sa.Integer(), server_default="3"),
        sa.Column("occasion_type", sa.String(100), nullable=True),
        sa.Column("style_score", sa.Float(), nullable=True),
        sa.Column("color_harmony_score", sa.Float(), nullable=True),
        sa.Column("outfit_embedding", postgresql.JSONB(), nullable=True),
        sa.Column("image_url", sa.String(2048), nullable=True),
        sa.Column("tags", sa.Text(), nullable=True),
        sa.Column("times_worn", sa.Integer(), server_default="0"),
        sa.Column("avg_rating", sa.Float(), nullable=True),
        sa.Column("is_template", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "name", name="uq_user_outfit_name"),
    )
    op.create_index("idx_user_season", "outfits", ["user_id", "season"])

    # Association tables
    op.create_table(
        "outfit_item_association",
        sa.Column("outfit_id", sa.Integer(), sa.ForeignKey("outfits.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("wardrobe_item_id", sa.Integer(), sa.ForeignKey("wardrobe_items.id", ondelete="CASCADE"), primary_key=True),
    )

    op.create_table(
        "outfit_attribute_association",
        sa.Column("outfit_id", sa.Integer(), sa.ForeignKey("outfits.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("attribute_id", sa.Integer(), sa.ForeignKey("clothing_attributes.id", ondelete="CASCADE"), primary_key=True),
    )

    op.create_table(
        "item_attribute_association",
        sa.Column("item_id", sa.Integer(), sa.ForeignKey("wardrobe_items.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("attribute_id", sa.Integer(), sa.ForeignKey("clothing_attributes.id", ondelete="CASCADE"), primary_key=True),
    )

    op.create_table(
        "images",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("image_url", sa.String(255), nullable=True),
        sa.Column("original_name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(255), nullable=True),
        sa.Column("category_confirmed", sa.Boolean(), server_default="false"),
        sa.Column("clothing_part", sa.String(255), nullable=True),
        sa.Column("color_palette", postgresql.JSONB(), nullable=True),
        sa.Column("dominant_color", sa.String(7), nullable=True),
        sa.Column("style", sa.String(255), nullable=True),
        sa.Column("occasion", postgresql.JSONB(), nullable=True),
        sa.Column("season", postgresql.JSONB(), nullable=True),
        sa.Column("temperature_range", postgresql.JSONB(), nullable=True),
        sa.Column("gender", sa.String(255), nullable=True),
        sa.Column("material", sa.String(255), nullable=True),
        sa.Column("pattern", sa.String(255), nullable=True),
        sa.Column("upload_date", sa.DateTime(), nullable=False),
        sa.Column("background_removed", sa.Boolean(), server_default="false"),
        sa.Column("foreground_pixel_count", sa.Integer(), server_default="0"),
        sa.Column("cluster_id", sa.Integer(), nullable=True),
        sa.Column("resnet_features", postgresql.JSONB(), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("image_width", sa.Integer(), nullable=True),
        sa.Column("image_height", sa.Integer(), nullable=True),
        sa.Column("opencv_features", postgresql.JSONB(), nullable=True),
        sa.Column("batch_id", sa.String(36), nullable=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_images_batch_id", "images", ["batch_id"])
    op.create_index("idx_images_upload_date", "images", ["upload_date"])
    op.create_index("idx_images_category", "images", ["category"])


def downgrade() -> None:
    op.drop_table("images")
    op.drop_table("item_attribute_association")
    op.drop_table("outfit_attribute_association")
    op.drop_table("outfit_item_association")
    op.drop_table("outfits")
    op.drop_table("wardrobe_items")
    op.drop_table("clothing_attributes")
    op.drop_table("clothing_categories")
    op.drop_table("users")
