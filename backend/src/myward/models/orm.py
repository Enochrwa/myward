"""
SQLAlchemy ORM models — PostgreSQL compatible.
Migrated from MySQL. Key changes:
  - JSON columns use native PostgreSQL JSONB for better performance & indexing
  - LargeBinary (BLOB) replaced with TEXT url references
  - All table-level options compatible with PostgreSQL
"""
from __future__ import annotations

import enum
import json
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from myward.db.base import Base

# ── Association tables ────────────────────────────────────────────────────────

outfit_item_association = Table(
    "outfit_item_association",
    Base.metadata,
    Column("outfit_id", Integer, ForeignKey("outfits.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "wardrobe_item_id",
        Integer,
        ForeignKey("wardrobe_items.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

outfit_attribute_association = Table(
    "outfit_attribute_association",
    Base.metadata,
    Column("outfit_id", Integer, ForeignKey("outfits.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "attribute_id",
        Integer,
        ForeignKey("clothing_attributes.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

item_attribute_association = Table(
    "item_attribute_association",
    Base.metadata,
    Column(
        "item_id", Integer, ForeignKey("wardrobe_items.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "attribute_id",
        Integer,
        ForeignKey("clothing_attributes.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


# ── Enums ─────────────────────────────────────────────────────────────────────


class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"
    superadmin = "superadmin"


# ── Models ────────────────────────────────────────────────────────────────────


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    gender = Column(String(50), nullable=True)
    role = Column(String(20), default=UserRole.user.value, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    wardrobe_items = relationship("WardrobeItem", back_populates="user", passive_deletes=True)
    outfits = relationship("Outfit", back_populates="user", passive_deletes=True)
    weekly_plans = relationship("WeeklyPlan", back_populates="user", passive_deletes=True)
    feedbacks = relationship("Feedback", back_populates="user", passive_deletes=True)
    occasions = relationship("Occasion", back_populates="user", passive_deletes=True)
    style_history = relationship("StyleHistory", back_populates="user", passive_deletes=True)
    profile = relationship(
        "UserProfile", uselist=False, back_populates="user", cascade="all, delete-orphan"
    )
    style_profile = relationship(
        "UserStyleProfile", uselist=False, back_populates="user", cascade="all, delete-orphan"
    )
    weather_preferences_rel = relationship(
        "WeatherPreference", back_populates="user", passive_deletes=True
    )


class ClothingCategory(Base):
    __tablename__ = "clothing_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    parent_id = Column(
        Integer, ForeignKey("clothing_categories.id", ondelete="SET NULL"), nullable=True
    )
    deepfashion_category_id = Column(Integer, nullable=True)
    level = Column(Integer, default=0, nullable=False)

    parent = relationship("ClothingCategory", remote_side=[id], back_populates="children")
    children = relationship("ClothingCategory", back_populates="parent")
    wardrobe_items = relationship("WardrobeItem", back_populates="category_obj")


class ClothingAttribute(Base):
    __tablename__ = "clothing_attributes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    attribute_type = Column(String(50), nullable=False)
    deepfashion_attribute_id = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)

    wardrobe_items = relationship(
        "WardrobeItem", secondary=item_attribute_association, back_populates="attributes"
    )
    outfits = relationship(
        "Outfit", secondary=outfit_attribute_association, back_populates="attributes"
    )


class WardrobeItem(Base):
    __tablename__ = "wardrobe_items"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_item_name"),
        Index("idx_category_season", "category_id", "season"),
        Index("idx_user_favorite", "user_id", "favorite"),
        Index("idx_wardrobe_user_id", "user_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name = Column(String(255), nullable=False)
    brand = Column(String(255), nullable=True, index=True)
    category_id = Column(
        Integer, ForeignKey("clothing_categories.id", ondelete="RESTRICT"), nullable=False
    )
    subcategory = Column(String(100), nullable=True)
    size = Column(String(50), nullable=True)
    price = Column(Float, nullable=True)
    currency = Column(String(10), default="USD")
    material = Column(String(255), nullable=True)
    season = Column(String(50), nullable=True, index=True)
    weather_suitability = Column(JSONB, nullable=True)
    formality_level = Column(Integer, default=3)

    image_url = Column(String(2048), nullable=True)
    source = Column(String(100), nullable=True)
    purchase_date = Column(Date, nullable=True)

    # ML fields
    resnet_features = Column(JSONB, nullable=True)
    style_embedding = Column(JSONB, nullable=True)

    # Color
    dominant_color_rgb = Column(JSONB, nullable=True)
    dominant_color_hex = Column(String(7), nullable=True)
    dominant_color_name = Column(String(50), nullable=True)
    color_palette = Column(JSONB, nullable=True)
    color_temperature = Column(String(20), nullable=True)
    brightness = Column(Float, nullable=True)
    saturation = Column(Float, nullable=True)

    # DeepFashion
    deepfashion_category_pred = Column(JSONB, nullable=True)
    deepfashion_attributes_pred = Column(JSONB, nullable=True)

    # User fields
    color = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    _tags = Column("tags", Text, nullable=True)
    favorite = Column(Boolean, default=False)
    times_worn = Column(Integer, default=0)
    condition = Column(String(50), default="good")

    date_added = Column(DateTime, default=datetime.utcnow)
    last_worn = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="wardrobe_items")
    category_obj = relationship("ClothingCategory", back_populates="wardrobe_items")
    attributes = relationship(
        "ClothingAttribute", secondary=item_attribute_association, back_populates="wardrobe_items"
    )
    outfits = relationship(
        "Outfit", secondary=outfit_item_association, back_populates="items"
    )
    style_history = relationship("StyleHistory", back_populates="item")
    outfit_recommendations = relationship("OutfitRecommendation", back_populates="target_item")
    color_analysis = relationship("ColorAnalysis", back_populates="wardrobe_item", uselist=False)
    item_classifications = relationship("ItemClassification", back_populates="wardrobe_item")

    @property
    def tags(self) -> list[str]:
        return json.loads(self._tags) if self._tags else []

    @tags.setter
    def tags(self, value: list[str]) -> None:
        self._tags = json.dumps(value)


class Outfit(Base):
    __tablename__ = "outfits"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_outfit_name"),
        Index("idx_user_season", "user_id", "season"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    season = Column(String(50), nullable=True)
    weather_suitability = Column(JSONB, nullable=True)
    formality_level = Column(Integer, default=3)
    occasion_type = Column(String(100), nullable=True)

    style_score = Column(Float, nullable=True)
    color_harmony_score = Column(Float, nullable=True)
    outfit_embedding = Column(JSONB, nullable=True)

    image_url = Column(String(2048), nullable=True)
    _tags = Column("tags", Text, nullable=True)

    times_worn = Column(Integer, default=0)
    avg_rating = Column(Float, nullable=True)
    is_template = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="outfits")
    items = relationship(
        "WardrobeItem", secondary=outfit_item_association, back_populates="outfits"
    )
    attributes = relationship(
        "ClothingAttribute", secondary=outfit_attribute_association, back_populates="outfits"
    )
    style_history = relationship("StyleHistory", back_populates="outfit")
    occasions = relationship("Occasion", back_populates="outfit")
    weekly_plan_days = relationship("WeeklyPlanDayOutfit", back_populates="outfit")
    feedbacks = relationship("Feedback", back_populates="outfit")
    recommendations = relationship("OutfitRecommendation", back_populates="recommended_outfit")

    @property
    def tags(self) -> list[str]:
        return json.loads(self._tags) if self._tags else []

    @tags.setter
    def tags(self, value: list[str]) -> None:
        self._tags = json.dumps(value)


class WeatherPreference(Base):
    __tablename__ = "weather_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    weather_condition = Column(String(50), nullable=False)
    temperature_min = Column(Float, nullable=True)
    temperature_max = Column(Float, nullable=True)
    preferred_categories = Column(JSONB, nullable=True)
    avoided_categories = Column(JSONB, nullable=True)

    user = relationship("User", back_populates="weather_preferences_rel")


class WeeklyPlan(Base):
    __tablename__ = "weekly_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    plan_type = Column(String(50), default="general")
    weather_location = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="weekly_plans")
    daily_outfits = relationship(
        "WeeklyPlanDayOutfit", back_populates="weekly_plan", cascade="all, delete-orphan"
    )


class WeeklyPlanDayOutfit(Base):
    __tablename__ = "weekly_plan_day_outfits"

    id = Column(Integer, primary_key=True, index=True)
    weekly_plan_id = Column(
        Integer, ForeignKey("weekly_plans.id", ondelete="CASCADE"), nullable=False
    )
    day_of_week = Column(String(10), nullable=False)
    date = Column(Date, nullable=True)
    occasion = Column(String(100), nullable=True)
    outfit_id = Column(Integer, ForeignKey("outfits.id", ondelete="SET NULL"), nullable=True)
    weather_forecast = Column(JSONB, nullable=True)
    notes = Column(Text, nullable=True)

    weekly_plan = relationship("WeeklyPlan", back_populates="daily_outfits")
    outfit = relationship("Outfit", back_populates="weekly_plan_days")


class Occasion(Base):
    __tablename__ = "occasions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    occasion_type = Column(String(100), nullable=False)
    date = Column(DateTime, nullable=True)
    location = Column(String(255), nullable=True)
    outfit_id = Column(Integer, ForeignKey("outfits.id", ondelete="SET NULL"), nullable=True)
    dress_code = Column(String(100), nullable=True)
    weather_considerations = Column(JSONB, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="occasions")
    outfit = relationship("Outfit", back_populates="occasions")


class StyleHistory(Base):
    __tablename__ = "style_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(Integer, ForeignKey("wardrobe_items.id", ondelete="SET NULL"), nullable=True)
    outfit_id = Column(Integer, ForeignKey("outfits.id", ondelete="SET NULL"), nullable=True)
    date_worn = Column(DateTime, nullable=False, default=datetime.utcnow)
    weather_conditions = Column(JSONB, nullable=True)
    occasion_type = Column(String(100), nullable=True)
    user_rating = Column(Integer, nullable=True)
    comfort_level = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)

    user = relationship("User", back_populates="style_history")
    item = relationship("WardrobeItem", back_populates="style_history")
    outfit = relationship("Outfit", back_populates="style_history")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    preferred_styles = Column(JSONB, nullable=True)
    preferred_colors = Column(JSONB, nullable=True)
    avoided_colors = Column(JSONB, nullable=True)
    sizes = Column(JSONB, nullable=True)
    budget_range = Column(JSONB, nullable=True)
    lifestyle = Column(String(100), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")


class UserStyleProfile(Base):
    __tablename__ = "user_style_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    style_vector = Column(JSONB, nullable=True)
    color_preferences = Column(JSONB, nullable=True)
    category_preferences = Column(JSONB, nullable=True)
    brand_preferences = Column(JSONB, nullable=True)
    style_keywords = Column(JSONB, nullable=True)
    seasonal_preferences = Column(JSONB, nullable=True)
    occasion_preferences = Column(JSONB, nullable=True)
    weather_preferences = Column(JSONB, nullable=True)
    color_harmony_preferences = Column(JSONB, nullable=True)
    formality_distribution = Column(JSONB, nullable=True)
    model_version = Column(String(50), nullable=True)
    confidence_score = Column(Float, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="style_profile")


class OutfitRecommendation(Base):
    __tablename__ = "outfit_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_item_id = Column(
        Integer, ForeignKey("wardrobe_items.id", ondelete="SET NULL"), nullable=True
    )
    recommended_outfit_id = Column(
        Integer, ForeignKey("outfits.id", ondelete="SET NULL"), nullable=True
    )
    recommendation_type = Column(String(50), nullable=False)
    occasion = Column(String(100), nullable=True)
    weather_context = Column(JSONB, nullable=True)
    similarity_score = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    recommendation_reason = Column(Text, nullable=True)
    model_version = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    target_item = relationship("WardrobeItem", back_populates="outfit_recommendations")
    recommended_outfit = relationship("Outfit", back_populates="recommendations")


class ColorAnalysis(Base):
    __tablename__ = "color_analyses"

    id = Column(Integer, primary_key=True, index=True)
    wardrobe_item_id = Column(
        Integer, ForeignKey("wardrobe_items.id", ondelete="CASCADE"), nullable=False
    )
    analysis_method = Column(String(50), nullable=False)
    dominant_colors = Column(JSONB, nullable=False)
    color_distribution = Column(JSONB, nullable=True)
    color_harmony_analysis = Column(JSONB, nullable=True)
    complementary_colors = Column(JSONB, nullable=True)
    analogous_colors = Column(JSONB, nullable=True)
    average_brightness = Column(Float, nullable=True)
    average_saturation = Column(Float, nullable=True)
    color_temperature = Column(String(20), nullable=True)
    analysis_timestamp = Column(DateTime, default=datetime.utcnow)

    wardrobe_item = relationship("WardrobeItem", back_populates="color_analysis")


class ItemClassification(Base):
    __tablename__ = "item_classifications"

    id = Column(Integer, primary_key=True, index=True)
    wardrobe_item_id = Column(
        Integer, ForeignKey("wardrobe_items.id", ondelete="CASCADE"), nullable=False
    )
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=True)
    predicted_category = Column(String(100), nullable=False)
    confidence_score = Column(Float, nullable=False)
    top_predictions = Column(JSONB, nullable=True)
    predicted_attributes = Column(JSONB, nullable=True)
    style_features = Column(JSONB, nullable=True)
    classification_timestamp = Column(DateTime, default=datetime.utcnow)

    wardrobe_item = relationship("WardrobeItem", back_populates="item_classifications")


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    outfit_id = Column(Integer, ForeignKey("outfits.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    feedback_type = Column(String(50), nullable=False)
    rating = Column(Integer, nullable=True)
    feedback_text = Column(Text, nullable=True)
    aspects_rated = Column(JSONB, nullable=True)
    context = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    outfit = relationship("Outfit", back_populates="feedbacks")
    user = relationship("User", back_populates="feedbacks")


class WeatherData(Base):
    __tablename__ = "weather_data"
    __table_args__ = (
        UniqueConstraint("location", "date", name="uq_weather_location_date"),
    )

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(100), nullable=False)
    date = Column(Date, nullable=False)
    temperature_min = Column(Float, nullable=True)
    temperature_max = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    weather_condition = Column(String(50), nullable=True)
    precipitation_chance = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Images table — keeps backward compat with existing upload pipeline
class Image(Base):
    __tablename__ = "images"
    __table_args__ = (
        Index("idx_images_batch_id", "batch_id"),
        Index("idx_images_upload_date", "upload_date"),
        Index("idx_images_category", "category"),
    )

    id = Column(String(36), primary_key=True)
    filename = Column(String(255), nullable=False)
    image_url = Column(String(255), nullable=True)
    original_name = Column(String(255), nullable=False)
    category = Column(String(255), nullable=True)
    category_confirmed = Column(Boolean, default=False)
    clothing_part = Column(String(255), nullable=True)
    color_palette = Column(JSONB, nullable=True)
    dominant_color = Column(String(7), nullable=True)
    style = Column(String(255), nullable=True)
    occasion = Column(JSONB, nullable=True)
    season = Column(JSONB, nullable=True)
    temperature_range = Column(JSONB, nullable=True)
    gender = Column(String(255), nullable=True)
    material = Column(String(255), nullable=True)
    pattern = Column(String(255), nullable=True)
    upload_date = Column(DateTime, nullable=False)
    background_removed = Column(Boolean, default=False)
    foreground_pixel_count = Column(Integer, default=0)
    cluster_id = Column(Integer, nullable=True)
    resnet_features = Column(JSONB, nullable=True)
    file_size = Column(Integer, nullable=True)
    image_width = Column(Integer, nullable=True)
    image_height = Column(Integer, nullable=True)
    opencv_features = Column(JSONB, nullable=True)
    batch_id = Column(String(36), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
