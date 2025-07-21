from pydantic import BaseModel, model_validator, Field
from datetime import datetime, date
from typing import List, Optional, Dict,Any

# Forward declaration for Outfit used in Occasion

class UserBase(BaseModel):
    email: str
    is_active: bool = True
    is_admin: bool = False

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = Field(None, alias="fullName")
    gender: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = Field(None, alias="fullName")
    gender: Optional[str] = None
    role: str
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    class Config:
        from_attributes = True
        populate_by_name = True


class ClothingCategoryCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None
    deepfashion_category_id: Optional[int] = None
    level: int = 0

class ClothingCategoryResponse(BaseModel):
    id: int
    name: str
    parent_id: Optional[int]
    deepfashion_category_id: Optional[int]
    level: int

class ClothingAttributeCreate(BaseModel):
    name: str
    attribute_type: str
    deepfashion_attribute_id: Optional[int] = None
    description: Optional[str] = None

class ClotheItemResponse(BaseModel):
    id: str
    filename: str
    original_name: str
    file_size: int
    image_width: int
    image_height: int
    dominant_color: str
    color_palette: List[str]  # Assuming color_palette is a list of hex colors
    resnet_features: List[float]  # Assuming it's a list of floats (embeddings)
    opencv_features: List[float]  # Same as above
    upload_date: datetime
    batch_id: Optional[str] = None
    category: Optional[str] = None
    background_removed: bool = False
    foreground_pixel_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True

class ClothingAttributeResponse(BaseModel):
    id: int
    name: str
    attribute_type: str
    deepfashion_attribute_id: Optional[int]
    description: Optional[str]

class WardrobeItemCreate(BaseModel):
    name: str
    brand: Optional[str] = None
    category_id: int
    subcategory: Optional[str] = None
    size: Optional[str] = None
    price: Optional[float] = None
    currency: str = "USD"
    material: Optional[str] = None
    season: Optional[str] = None
    weather_suitability: Optional[List[str]] = None
    formality_level: int = 3
    image_url: Optional[str] = None
    source: Optional[str] = None
    purchase_date: Optional[date] = None
    color: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    condition: str = "good"

class WardrobeItemResponse(BaseModel):
    id: int
    user_id: int
    name: str
    brand: Optional[str]
    category_id: int
    subcategory: Optional[str]
    size: Optional[str]
    price: Optional[float]
    currency: str
    material: Optional[str]
    season: Optional[str]
    weather_suitability: Optional[List[str]]
    formality_level: int
    image_url: Optional[str]
    source: Optional[str]
    purchase_date: Optional[date]
    color: Optional[str]
    notes: Optional[str]
    tags: Optional[List[str]]
    favorite: bool
    times_worn: int
    condition: str
    date_added: datetime
    last_worn: Optional[datetime]
    updated_at: datetime

    class Config:
        from_attributes = True

class OutfitCreate(BaseModel):
    name: str
    description: Optional[str] = None
    season: Optional[str] = None
    weather_suitability: Optional[List[str]] = None
    formality_level: int = 3
    occasion_type: Optional[str] = None
    item_ids: List[int]
    attribute_ids: Optional[List[int]] = None
    tags: Optional[List[str]] = None
    is_template: bool = False

class OutfitResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    season: Optional[str]
    weather_suitability: Optional[List[str]]
    formality_level: int
    occasion_type: Optional[str]
    style_score: Optional[float]
    color_harmony_score: Optional[float]
    image_url: Optional[str]
    tags: Optional[List[str]]
    times_worn: int
    avg_rating: Optional[float]
    is_template: bool
    created_at: datetime
    updated_at: datetime

class WeeklyPlanCreate(BaseModel):
    name: str
    start_date: date
    end_date: date
    plan_type: str = "general"
    weather_location: Optional[str] = None

class WeeklyPlanResponse(BaseModel):
    id: int
    user_id: int
    name: str
    start_date: date
    end_date: date
    plan_type: str
    weather_location: Optional[str]
    created_at: datetime
    updated_at: datetime

class WeeklyPlanDayOutfitCreate(BaseModel):
    day_of_week: str
    date: Optional[date] = None
    outfit_id: Optional[int] = None
    weather_forecast: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class User(BaseModel):
    id: int
    username: str
    email: str
    role: str
    # hashed_password: str # Should not be in response model
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True



class Token(BaseModel):
    access_token: str
    token_type: str

    class Config:
        from_attributes = True

class EventDetailsInput(BaseModel):
    event_type: str = Field(..., description="Type or name of the event (e.g., 'Wedding Guest', 'Casual Brunch', 'Work Meeting'). This is the primary input for matching.")
    location: Optional[str] = Field(None, description="General location of the event (e.g., 'outdoor', 'office', 'restaurant').")
    weather: Optional[str] = Field(None, description="Expected weather conditions (e.g., 'hot', 'mild', 'cold', 'rainy').")
    time_of_day: Optional[str] = Field(None, description="Time of the event (e.g., 'morning', 'afternoon', 'evening', 'night').")
    formality: Optional[str] = Field(None, description="Formality level of the event (e.g., 'casual', 'smart_casual', 'business_casual', 'semi-formal', 'formal', 'black_tie').")
    notes: Optional[str] = Field(None, description="Any additional notes or keywords describing the event context or user's specific needs for the outfit.")

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class WardrobeItem(BaseModel):
    id: int
    user_id: int
    name: str
    brand: Optional[str] = None
    category: str
    size: Optional[str] = None
    price: Optional[float] = None
    material: Optional[str] = None
    season: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[List[str]] = None
    favorite: bool = False
    times_worn: int = 0
    date_added: datetime
    last_worn: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    ai_embedding: Optional[List[float]] = None
    ai_dominant_colors: Optional[List[str]] = None

    class Config:
        from_attributes = True

class WardrobeItemUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    size: Optional[str] = None
    price: Optional[float] = None
    material: Optional[str] = None
    season: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[List[str]] = None
    favorite: Optional[bool] = None

class Outfit(BaseModel): # Actual definition of Outfit
    id: int
    user_id: int
    name: str
    item_ids: List[int]
    created_at: datetime
    updated_at: Optional[datetime] = None
    tags: Optional[List[str]] = None
    image_url: Optional[str] = None
    feedbacks: List['Feedback'] = [] # Added feedbacks list with forward reference

    class Config:
        from_attributes = True



class OutfitUpdate(BaseModel):
    name: Optional[str] = None
    item_ids: Optional[List[int]] = None
    tags: Optional[List[str]] = None
    image_url: Optional[str] = None

class OutfitCreate(BaseModel):
    name: str
    gender: str
    clothing_parts: Dict[str, str]
    clothing_items: List[str]
    preview_image: Optional[str] = None

class OutfitResponse(BaseModel):
    id: str
    user_id: str
    name: str
    gender: str
    clothing_parts: Dict[str, str]
    clothing_items: List[str]
    created_at: datetime
    preview_image: Optional[str] = None

class WeeklyPlan(BaseModel):
    id: int
    user_id: int
    name: str
    start_date: date
    end_date: date
    daily_outfits: Dict[str, Optional[int]]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class WeeklyPlanCreate(BaseModel):
    name: str
    start_date: date
    end_date: date
    daily_outfits: Dict[str, Optional[int]]

class WeeklyPlanUpdate(BaseModel):
    name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    daily_outfits: Optional[Dict[str, Optional[int]]] = None

class Occasion(BaseModel):
    id: int
    user_id: int
    name: str
    date: Optional[datetime] = None
    outfit_id: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    suggested_outfits: Optional[List[Outfit]] = None # Correctly referencing Outfit

    class Config:
        from_attributes = True

class OccasionCreate(BaseModel):
    name: str
    date: Optional[datetime] = None
    outfit_id: Optional[int] = None
    notes: Optional[str] = None

class OccasionUpdate(BaseModel):
    name: Optional[str] = None
    date: Optional[datetime] = None
    outfit_id: Optional[int] = None
    notes: Optional[str] = None

class StyleHistoryBase(BaseModel):
    item_id: Optional[int] = None
    outfit_id: Optional[int] = None
    date_worn: datetime
    notes: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def check_item_or_outfit_id(cls, values):
        item_id, outfit_id = values.get('item_id'), values.get('outfit_id')
        if (item_id is None and outfit_id is None) or \
           (item_id is not None and outfit_id is not None):
            raise ValueError('Either item_id or outfit_id must be provided, but not both.')
        return values

class StyleHistoryCreate(StyleHistoryBase):
    pass

class StyleHistory(StyleHistoryBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# Statistics Schemas
class WardrobeStats(BaseModel):
    total_items: int
    total_outfits: int
    items_by_category: Dict[str, int]
    items_by_season: Dict[str, int]
    most_worn_items: List[WardrobeItem]
    least_worn_items: List[WardrobeItem]
    favorite_items_count: int

    class Config:
        from_attributes = True

class ItemWearFrequency(BaseModel):
    item: WardrobeItem
    wear_count: int

    class Config:
        from_attributes = True

class CategoryUsage(BaseModel):
    category: str
    item_count: int
    usage_percentage: float

    class Config:
        from_attributes = True

# AI Service Schemas
class ColorPaletteItem(BaseModel):
    color: str
    name: str
    percentage: float

class StyleInsightItem(BaseModel):
    category: str
    score: int # Or float
    description: str

class OutfitAnalysisResponse(BaseModel):
    fileName: Optional[str] = None
    contentType: Optional[str] = None
    style: str
    dominantColors: List[str]
    identifiedItems: List[str]
    occasionSuitability: str
    confidenceScore: float
    recommendations: List[str]
    colorPalette: Optional[List[ColorPaletteItem]] = None
    styleInsights: Optional[List[StyleInsightItem]] = None

    class Config:
        from_attributes = True

class TrendDataItem(BaseModel):
    id: str
    name: str
    category: str
    popularity: int
    growth: int
    description: str
    colors: List[str]
    season: str
    confidence: int
    outfitImages: Optional[List[str]] = None
    celebrities: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None
    priceRange: Optional[str] = None
    occasion: Optional[List[str]] = None

class PersonalizedRecommendations(BaseModel): # Used by TrendForecastResponse
    mustHave: List[str]
    avoid: List[str]
    investIn: List[str]

class SeasonalPredictions(BaseModel): # Used by TrendForecastResponse
    emerging: List[str]
    declining: List[str]
    stable: List[str]

class TrendForecastResponse(BaseModel):
    trends: List[TrendDataItem]
    personalizedRecommendations: PersonalizedRecommendations
    seasonalPredictions: SeasonalPredictions

    class Config:
        from_attributes = True

# Recommendation Service Schemas
class PersonalizedWardrobeSuggestions(BaseModel):
    newOutfitIdeas: List[str]
    itemsToAcquire: List[str]

    class Config:
        from_attributes = True

# AI Style Insights Schemas
class StyleProfileData(BaseModel):
    primary_style: Optional[str] = None
    secondary_styles: Optional[List[str]] = None
    color_preferences: Optional[List[str]] = None
    body_type: Optional[str] = None
    lifestyle: Optional[str] = None
    brand_alignment: Optional[List[str]] = None
    fashion_goals: Optional[List[str]] = None

    class Config:
        from_attributes = True

class StyleProfileInsights(BaseModel):
    style_confidence_score: Optional[float] = None # e.g., 0.0 to 1.0
    wardrobe_versatility_score: Optional[float] = None # e.g., 0.0 to 1.0
    style_summary: Optional[str] = None # Textual summary of overall style

    class Config:
        from_attributes = True

class UserStyleProfileResponse(BaseModel):
    profile_data: StyleProfileData
    generated_insights: StyleProfileInsights

    class Config:
        from_attributes = True

class WardrobeAnalysisDetails(BaseModel):
    total_items: int
    category_breakdown: Dict[str, int]
    color_distribution: Dict[str, int]
    brand_diversity_score: Optional[float] = None # Score from 0.0 to 1.0
    average_item_price: Optional[float] = None
    style_consistency_score: Optional[float] = None # Score from 0.0 to 1.0
    wardrobe_gaps: Optional[List[str]] = None # e.g., ["Formal Evening Wear", "Summer Tops"]
    improvement_suggestions: Optional[List[str]] = None

    class Config:
        from_attributes = True

class PersonalizedGeneralInsight(BaseModel):
    id: str
    insight_type: str # e.g., "style", "color", "fit", "occasion", "trend_alignment"
    title: str
    description: str
    actionable_advice: str
    confidence_score: float # e.g., 0.0 to 1.0
    impact_level: str # e.g., "high", "medium", "low"

    class Config:
        from_attributes = True

class AIStyleInsightOutfitRecommendation(BaseModel):
    outfit_id: Optional[int] = None # If it's an existing outfit
    outfit_name: str
    description: str # Why this outfit is recommended
    image_url: Optional[str] = None
    items: List[WardrobeItem] # List of items in the recommended outfit - Direct reference
    confidence_score: float
    style_match_notes: Optional[str] = None
    occasion_suitability: Optional[str] = None

    class Config:
        from_attributes = True

class FullAIStyleInsightsResponse(BaseModel):
    user_profile: UserStyleProfileResponse
    wardrobe_analysis: WardrobeAnalysisDetails
    personalized_insights: List[PersonalizedGeneralInsight]
    suggested_outfits: List[AIStyleInsightOutfitRecommendation]

    class Config:
        from_attributes = True

# User Profile Schemas
class UserProfileBase(BaseModel):
    preferred_styles: Optional[List[str]] = None
    preferred_colors: Optional[List[str]] = None
    avoided_colors: Optional[List[str]] = None
    sizes: Optional[Dict[str, str]] = None

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileUpdate(UserProfileBase):
    pass # All fields already optional in UserProfileBase

class UserProfile(UserProfileBase):
    user_id: int
    updated_at: datetime

    class Config:
        from_attributes = True

# Forward declaration for Feedback schema to be used in Outfit schema later
class Feedback(BaseModel):
    pass

class FeedbackBase(BaseModel):
    feedback_text: Optional[str] = None
    rating: Optional[int] = None

    @model_validator(mode='before')
    @classmethod
    def check_at_least_one_field(cls, values):
        feedback_text = values.get('feedback_text')
        rating = values.get('rating')
        if not feedback_text and rating is None: # Check if both are None or empty string for text
            raise ValueError('At least one of feedback_text or rating must be provided')
        if rating is not None and not (1 <= rating <= 5):
            raise ValueError('Rating must be between 1 and 5')
        return values

class FeedbackCreate(FeedbackBase):
    pass



##IMAGE PROCESSING


# Pydantic models
class ImageMetadata(BaseModel):
    id: str
    filename: str
    original_name: str
    file_size: int
    image_width: int
    image_height: int
    dominant_color: str
    color_palette: List[str]
    resnet_features: List[float]
    opencv_features: Dict[str, Any]
    upload_date: str
    category: Optional[str] = None
    style: Optional[str] = None
    occasion: Optional[List[str]] = None
    season: Optional[List[str]] = None
    temperature_range: Optional[Dict[str, int]] = None
    gender: Optional[str] = None
    material: Optional[str] = None
    pattern: Optional[str] = None

class ImageResponse(BaseModel):
    message: str
    image_id: str
    image_url: str
    metadata: ImageMetadata

class BatchUploadResponse(BaseModel):
    message: str
    total_images: int
    successful_uploads: int
    failed_uploads: int
    batch_id: str
    results: List[Dict[str, Any]]
    processing_time: float

class BatchImageMetadata(BaseModel):
    batch_id: str
    total_images: int
    successful_images: int
    failed_images: int
    upload_date: str
    processing_time: float

class UpdateCategoryRequest(BaseModel):
    image_id: str
    new_category: str

class Feedback(FeedbackBase): # Actual definition of Feedback schema
    id: int
    outfit_id: int
    user_id: int
    created_at: datetime
    commenter_username: Optional[str] = None # Will be populated in the router

    class Config:
        from_attributes = True





# Update forward references if Pydantic v1 style is strictly needed
# For Pydantic v2, this is often handled more automatically.
# If issues arise, call Model.model_rebuild() for models with forward refs
# after all definitions. This is typically done once at application startup.
# For now, we assume Pydantic v2 handles it or this structure is fine.
User.model_rebuild()
Token.model_rebuild()
WardrobeItem.model_rebuild()
Outfit.model_rebuild()
WeeklyPlan.model_rebuild()
Occasion.model_rebuild()
StyleHistory.model_rebuild()
UserProfile.model_rebuild() # Added UserProfile
Feedback.model_rebuild() # Added Feedback
WardrobeStats.model_rebuild()
ItemWearFrequency.model_rebuild()
CategoryUsage.model_rebuild()
OutfitAnalysisResponse.model_rebuild()
TrendForecastResponse.model_rebuild()
PersonalizedWardrobeSuggestions.model_rebuild()

# AI Style Insights Schemas Rebuild
StyleProfileData.model_rebuild()
StyleProfileInsights.model_rebuild()
UserStyleProfileResponse.model_rebuild()
WardrobeAnalysisDetails.model_rebuild()
PersonalizedGeneralInsight.model_rebuild()
AIStyleInsightOutfitRecommendation.model_rebuild()
FullAIStyleInsightsResponse.model_rebuild()

EventDetailsInput.model_rebuild() # Added EventDetailsInput

UserLogin.model_rebuild() # Add UserLogin to model_rebuild
