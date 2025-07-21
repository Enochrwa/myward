from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Table, Text, JSON, Date, UniqueConstraint, Index
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import json
from .db.base import Base

# Association tables for many-to-many relationships
outfit_item_association = Table('outfit_item_association', Base.metadata,
    Column('outfit_id', Integer, ForeignKey('outfits.id'), primary_key=True),
    Column('wardrobe_item_id', Integer, ForeignKey('wardrobe_items.id'), primary_key=True)
)

outfit_attribute_association = Table('outfit_attribute_association', Base.metadata,
    Column('outfit_id', Integer, ForeignKey('outfits.id'), primary_key=True),
    Column('attribute_id', Integer, ForeignKey('clothing_attributes.id'), primary_key=True)
)

item_attribute_association = Table('item_attribute_association', Base.metadata,
    Column('item_id', Integer, ForeignKey('wardrobe_items.id'), primary_key=True),
    Column('attribute_id', Integer, ForeignKey('clothing_attributes.id'), primary_key=True)
)

import enum

class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"
    superadmin = "superadmin"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    gender = Column(String(50), nullable=True)
    role = Column(String(20), default=UserRole.user.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    wardrobe_items = relationship("WardrobeItem", back_populates="user")
    outfits = relationship("Outfit", back_populates="user")
    weekly_plans = relationship("WeeklyPlan", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="user")
    occasions = relationship("Occasion", back_populates="user")
    style_history = relationship("StyleHistory", back_populates="user")
    profile = relationship("UserProfile", uselist=False, back_populates="user", cascade="all, delete-orphan")
    style_profile = relationship("UserStyleProfile", uselist=False, back_populates="user", cascade="all, delete-orphan")
    weather_preferences_rel = relationship("WeatherPreference", back_populates="user")


class ClothingCategory(Base):
    __tablename__ = "clothing_categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("clothing_categories.id"), nullable=True)
    deepfashion_category_id = Column(Integer, nullable=True)  # Map to DeepFashion categories
    level = Column(Integer, default=0)  # 0=main, 1=sub, 2=detailed
    
    # Self-referential relationship for hierarchical categories
    parent = relationship("ClothingCategory", remote_side=[id], back_populates="children")
    children = relationship("ClothingCategory", back_populates="parent")
    wardrobe_items = relationship("WardrobeItem", back_populates="category_obj")


class ClothingAttribute(Base):
    __tablename__ = "clothing_attributes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    attribute_type = Column(String(50), nullable=False)  # "pattern", "texture", "sleeve", "neckline", "fit", etc.
    deepfashion_attribute_id = Column(Integer, nullable=True)  # Map to DeepFashion attributes
    description = Column(Text, nullable=True)
    
    # Many-to-many with items and outfits
    wardrobe_items = relationship("WardrobeItem", secondary=item_attribute_association, back_populates="attributes")
    outfits = relationship("Outfit", secondary=outfit_attribute_association, back_populates="attributes")


class WardrobeItem(Base):
    __tablename__ = "wardrobe_items"
    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uq_user_item_name'),
        Index('idx_category_season', 'category_id', 'season'),
        Index('idx_user_favorite', 'user_id', 'favorite'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    brand = Column(String(255), nullable=True, index=True)
    category_id = Column(Integer, ForeignKey("clothing_categories.id"), nullable=False)
    subcategory = Column(String(100), nullable=True)
    size = Column(String(50), nullable=True)
    price = Column(Float, nullable=True)
    currency = Column(String(10), default="USD")
    material = Column(String(255), nullable=True)
    season = Column(String(50), nullable=True, index=True)
    weather_suitability = Column(JSON, nullable=True)  # ["sunny", "rainy", "windy", "snowy"]
    formality_level = Column(Integer, default=3)  # 1-5 scale: 1=very casual, 5=very formal
    
    # Image and source info
    image_url = Column(String(2048), nullable=True)
    source = Column(String(100), nullable=True)  # "camera", "web", "manual", "upload"
    purchase_date = Column(Date, nullable=True)
    
    # ML and AI fields
    resnet_features = Column(JSON, nullable=True)  # ResNet50 feature vector
    style_embedding = Column(JSON, nullable=True)  # Style embedding vector
    
    # Color analysis (enhanced)
    dominant_color_rgb = Column(JSON, nullable=True)  # [r, g, b]
    dominant_color_hex = Column(String(7), nullable=True)  # #RRGGBB
    dominant_color_name = Column(String(50), nullable=True)
    color_palette = Column(JSON, nullable=True)  # Top 5 colors
    color_temperature = Column(String(20), nullable=True)  # "warm", "cool", "neutral"
    brightness = Column(Float, nullable=True)  # 0-1 scale
    saturation = Column(Float, nullable=True)  # 0-1 scale
    
    # DeepFashion predictions
    deepfashion_category_pred = Column(JSON, nullable=True)  # Category predictions with confidence
    deepfashion_attributes_pred = Column(JSON, nullable=True)  # Attribute predictions
    
    # User interaction data
    color = Column(String(255), nullable=True)  # User-defined color
    notes = Column(Text, nullable=True)
    _tags = Column("tags", Text, nullable=True)
    favorite = Column(Boolean, default=False)
    times_worn = Column(Integer, default=0)
    condition = Column(String(50), default="good")  # "excellent", "good", "fair", "poor"
    
    # Timestamps
    date_added = Column(DateTime, default=datetime.utcnow)
    last_worn = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="wardrobe_items")
    category_obj = relationship("ClothingCategory", back_populates="wardrobe_items")
    attributes = relationship("ClothingAttribute", secondary=item_attribute_association, back_populates="wardrobe_items")
    outfits = relationship("Outfit", secondary=outfit_item_association, back_populates="items")
    style_history = relationship("StyleHistory", back_populates="item")
    outfit_recommendations = relationship("OutfitRecommendation", back_populates="target_item")
    color_analysis = relationship("ColorAnalysis", back_populates="wardrobe_item", uselist=False)
    item_classifications = relationship("ItemClassification", back_populates="wardrobe_item")

    @property
    def tags(self):
        return json.loads(self._tags) if self._tags else []

    @tags.setter
    def tags(self, value):
        self._tags = json.dumps(value)


class Outfit(Base):
    __tablename__ = "outfits"
    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uq_user_outfit_name'),
        Index('idx_user_season', 'user_id', 'season'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    season = Column(String(50), nullable=True)
    weather_suitability = Column(JSON, nullable=True)  # Weather conditions this outfit works for
    formality_level = Column(Integer, default=3)  # 1-5 scale
    occasion_type = Column(String(100), nullable=True)  # "work", "casual", "formal", "party"
    
    # Style analysis
    style_score = Column(Float, nullable=True)  # Overall style compatibility score
    color_harmony_score = Column(Float, nullable=True)  # Color matching score
    outfit_embedding = Column(JSON, nullable=True)  # Combined outfit embedding
    
    # Images and metadata
    image_url = Column(String(2048), nullable=True)
    _tags = Column("tags", Text, nullable=True)
    
    # User interaction
    times_worn = Column(Integer, default=0)
    avg_rating = Column(Float, nullable=True)  # Average user rating
    is_template = Column(Boolean, default=False)  # Can be used as template for similar outfits
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="outfits")
    items = relationship("WardrobeItem", secondary=outfit_item_association, back_populates="outfits")
    attributes = relationship("ClothingAttribute", secondary=outfit_attribute_association, back_populates="outfits")
    style_history = relationship("StyleHistory", back_populates="outfit")
    occasions = relationship("Occasion", back_populates="outfit")
    weekly_plan_days = relationship("WeeklyPlanDayOutfit", back_populates="outfit")
    feedbacks = relationship("Feedback", back_populates="outfit")
    recommendations = relationship("OutfitRecommendation", back_populates="recommended_outfit")

    @property
    def tags(self):
        return json.loads(self._tags) if self._tags else []

    @tags.setter
    def tags(self, value):
        self._tags = json.dumps(value)


class WeatherPreference(Base):
    __tablename__ = "weather_preferences"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    weather_condition = Column(String(50), nullable=False)  # "sunny", "rainy", "cold", "hot"
    temperature_min = Column(Float, nullable=True)  # Min comfortable temperature
    temperature_max = Column(Float, nullable=True)  # Max comfortable temperature
    preferred_categories = Column(JSON, nullable=True)  # Preferred clothing categories for this weather
    avoided_categories = Column(JSON, nullable=True)  # Categories to avoid
    
    user = relationship("User", back_populates="weather_preferences_rel")


class WeeklyPlan(Base):
    __tablename__ = "weekly_plans"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    plan_type = Column(String(50), default="general")  # "work", "vacation", "general"
    weather_location = Column(String(100), nullable=True)  # City for weather-based recommendations
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="weekly_plans")
    daily_outfits = relationship("WeeklyPlanDayOutfit", back_populates="weekly_plan", cascade="all, delete-orphan")


class WeeklyPlanDayOutfit(Base):
    __tablename__ = "weekly_plan_day_outfits"
    id = Column(Integer, primary_key=True, index=True)
    weekly_plan_id = Column(Integer, ForeignKey("weekly_plans.id"), nullable=False)
    day_of_week = Column(String(10), nullable=False)
    date = Column(Date, nullable=True)  # Specific date for the outfit
    outfit_id = Column(Integer, ForeignKey("outfits.id"), nullable=True)
    weather_forecast = Column(JSON, nullable=True)  # Weather data for the day
    notes = Column(Text, nullable=True)

    weekly_plan = relationship("WeeklyPlan", back_populates="daily_outfits")
    outfit = relationship("Outfit", back_populates="weekly_plan_days")


class Occasion(Base):
    __tablename__ = "occasions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    occasion_type = Column(String(100), nullable=False)  # "wedding", "interview", "date", "work"
    date = Column(DateTime, nullable=True)
    location = Column(String(255), nullable=True)
    outfit_id = Column(Integer, ForeignKey("outfits.id"), nullable=True)
    dress_code = Column(String(100), nullable=True)  # "formal", "business", "casual"
    weather_considerations = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="occasions")
    outfit = relationship("Outfit", back_populates="occasions")


class StyleHistory(Base):
    __tablename__ = "style_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("wardrobe_items.id"), nullable=True)
    outfit_id = Column(Integer, ForeignKey("outfits.id"), nullable=True)
    date_worn = Column(DateTime, nullable=False, default=datetime.utcnow)
    weather_conditions = Column(JSON, nullable=True)  # Weather when worn
    occasion_type = Column(String(100), nullable=True)
    user_rating = Column(Integer, nullable=True)  # 1-5 rating
    comfort_level = Column(Integer, nullable=True)  # 1-5 comfort rating
    notes = Column(Text, nullable=True)

    user = relationship("User", back_populates="style_history")
    item = relationship("WardrobeItem", back_populates="style_history")
    outfit = relationship("Outfit", back_populates="style_history")


class UserProfile(Base):
    __tablename__ = "user_profiles"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    preferred_styles = Column(JSON, nullable=True)  # ["minimalist", "boho", "classic"]
    preferred_colors = Column(JSON, nullable=True)  # Color preferences
    avoided_colors = Column(JSON, nullable=True)  # Colors to avoid
    sizes = Column(JSON, nullable=True)  # Size preferences by category
    budget_range = Column(JSON, nullable=True)  # {"min": 0, "max": 1000}
    lifestyle = Column(String(100), nullable=True)  # "active", "professional", "casual"
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")


class UserStyleProfile(Base):
    __tablename__ = "user_style_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # ML-learned preferences
    style_vector = Column(JSON, nullable=True)  # Learned style embedding
    color_preferences = Column(JSON, nullable=True)  # Learned color preferences with scores
    category_preferences = Column(JSON, nullable=True)  # Preferred categories with scores
    brand_preferences = Column(JSON, nullable=True)  # Brand preferences
    style_keywords = Column(JSON, nullable=True)  # Extracted style descriptors
    
    # Seasonal and contextual preferences
    seasonal_preferences = Column(JSON, nullable=True)  # Seasonal style patterns
    occasion_preferences = Column(JSON, nullable=True)  # Occasion-based preferences
    weather_preferences = Column(JSON, nullable=True)  # Weather-based preferences
    
    # Compatibility scores
    color_harmony_preferences = Column(JSON, nullable=True)  # Preferred color combinations
    formality_distribution = Column(JSON, nullable=True)  # Formality level distribution
    
    # Model metadata
    model_version = Column(String(50), nullable=True)  # Version of the ML model used
    confidence_score = Column(Float, nullable=True)  # Overall confidence in the profile
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="style_profile")


class OutfitRecommendation(Base):
    __tablename__ = "outfit_recommendations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_item_id = Column(Integer, ForeignKey("wardrobe_items.id"), nullable=True)
    recommended_outfit_id = Column(Integer, ForeignKey("outfits.id"), nullable=True)
    recommendation_type = Column(String(50), nullable=False)  # "weather", "occasion", "style_match"
    occasion = Column(String(100), nullable=True)
    weather_context = Column(JSON, nullable=True)  # Weather conditions considered
    similarity_score = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    recommendation_reason = Column(Text, nullable=True)  # Explanation for the recommendation
    model_version = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    target_item = relationship("WardrobeItem", back_populates="outfit_recommendations")
    recommended_outfit = relationship("Outfit", back_populates="recommendations")


class ColorAnalysis(Base):
    __tablename__ = "color_analyses"
    id = Column(Integer, primary_key=True, index=True)
    wardrobe_item_id = Column(Integer, ForeignKey("wardrobe_items.id"), nullable=False)
    analysis_method = Column(String(50), nullable=False)  # "opencv", "colorthief", "kmeans"
    
    # Detailed color information
    dominant_colors = Column(JSON, nullable=False)  # Top 5 colors with percentages
    color_distribution = Column(JSON, nullable=True)  # Color histogram
    color_harmony_analysis = Column(JSON, nullable=True)  # Harmony analysis
    complementary_colors = Column(JSON, nullable=True)  # Suggested complementary colors
    analogous_colors = Column(JSON, nullable=True)  # Analogous color suggestions
    
    # Color properties
    average_brightness = Column(Float, nullable=True)
    average_saturation = Column(Float, nullable=True)
    color_temperature = Column(String(20), nullable=True)  # "warm", "cool", "neutral"
    
    analysis_timestamp = Column(DateTime, default=datetime.utcnow)
    
    wardrobe_item = relationship("WardrobeItem", back_populates="color_analysis")


class ItemClassification(Base):
    __tablename__ = "item_classifications"
    id = Column(Integer, primary_key=True, index=True)
    wardrobe_item_id = Column(Integer, ForeignKey("wardrobe_items.id"), nullable=False)
    model_name = Column(String(100), nullable=False)  # "ResNet50", "DeepFashion", "Custom"
    model_version = Column(String(50), nullable=True)
    
    # Classification results
    predicted_category = Column(String(100), nullable=False)
    confidence_score = Column(Float, nullable=False)
    top_predictions = Column(JSON, nullable=True)  # Top 5 predictions with scores
    
    # Attribute predictions
    predicted_attributes = Column(JSON, nullable=True)  # Predicted attributes with confidence
    style_features = Column(JSON, nullable=True)  # Extracted style features
    
    classification_timestamp = Column(DateTime, default=datetime.utcnow)
    
    wardrobe_item = relationship("WardrobeItem", back_populates="item_classifications")


class Feedback(Base):
    __tablename__ = "feedbacks"
    id = Column(Integer, primary_key=True, index=True)
    outfit_id = Column(Integer, ForeignKey("outfits.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    feedback_type = Column(String(50), nullable=False)  # "rating", "comment", "suggestion"
    rating = Column(Integer, nullable=True)  # 1-5 stars
    feedback_text = Column(Text, nullable=True)
    aspects_rated = Column(JSON, nullable=True)  # {"comfort": 4, "style": 5, "appropriateness": 3}
    context = Column(JSON, nullable=True)  # Context when feedback was given
    created_at = Column(DateTime, default=datetime.utcnow)

    outfit = relationship("Outfit", back_populates="feedbacks")
    user = relationship("User", back_populates="feedbacks")


# Weather integration table
class WeatherData(Base):
    __tablename__ = "weather_data"
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(100), nullable=False)
    date = Column(Date, nullable=False)
    temperature_min = Column(Float, nullable=True)
    temperature_max = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    weather_condition = Column(String(50), nullable=True)  # "sunny", "rainy", "cloudy"
    precipitation_chance = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('location', 'date', name='uq_weather_location_date'),
    )