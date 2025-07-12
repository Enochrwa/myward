"""
Pydantic schemas for ML features API endpoints

This module defines the request and response schemas for the ML-powered
wardrobe features including classification, color detection, and recommendations.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime

class ClassificationResponse(BaseModel):
    """Response schema for clothing classification."""
    predicted_category: str = Field(..., description="Predicted clothing category")
    confidence_score: float = Field(..., description="Confidence score (0-1)")
    detailed_predictions: Dict[str, float] = Field(..., description="Detailed prediction scores for all categories")
    model_name: str = Field(..., description="Name of the ML model used")

class ColorAnalysisResponse(BaseModel):
    """Response schema for color analysis."""
    dominant_color_rgb: List[int] = Field(..., description="RGB values [r, g, b]")
    dominant_color_hex: str = Field(..., description="Hex color code #RRGGBB")
    dominant_color_name: str = Field(..., description="Human-readable color name")
    color_properties: Dict[str, str] = Field(..., description="Color properties (brightness, saturation, temperature)")

class ColorPaletteResponse(BaseModel):
    """Response schema for color palette extraction."""
    palette: List[Dict[str, Any]] = Field(..., description="List of colors in the palette")
    dominant_color: Optional[Dict[str, Any]] = Field(None, description="Dominant color information")
    harmony_analysis: Dict[str, str] = Field(..., description="Color harmony analysis")
    color_count: int = Field(..., description="Number of colors in the palette")

class UserPreferences(BaseModel):
    """User style preferences for recommendations."""
    preferred_colors: Optional[List[str]] = Field(None, description="List of preferred colors")
    avoided_colors: Optional[List[str]] = Field(None, description="List of colors to avoid")
    preferred_styles: Optional[List[str]] = Field(None, description="List of preferred styles")
    preferred_brands: Optional[List[str]] = Field(None, description="List of preferred brands")
    size_preferences: Optional[Dict[str, str]] = Field(None, description="Size preferences by category")
    budget_range: Optional[Tuple[float, float]] = Field(None, description="Budget range (min, max)")

class RecommendationRequest(BaseModel):
    """Request schema for outfit recommendations."""
    user_preferences: Optional[UserPreferences] = Field(None, description="User style preferences")
    occasion: str = Field("casual", description="Target occasion for the outfit")
    num_recommendations: int = Field(5, ge=1, le=20, description="Number of recommendations to return")
    weather_conditions: Optional[Dict[str, Any]] = Field(None, description="Weather conditions to consider")
    color_scheme: Optional[str] = Field(None, description="Preferred color scheme")

class OutfitItemResponse(BaseModel):
    """Response schema for outfit items."""
    id: int
    name: str
    category: str
    brand: Optional[str]
    dominant_color_name: Optional[str]
    image_url: Optional[str]
    similarity_score: Optional[float] = Field(None, description="Similarity score for recommendations")

class OutfitResponse(BaseModel):
    """Response schema for outfit recommendations."""
    id: Optional[int] = Field(None, description="Outfit ID if saved")
    name: Optional[str] = Field(None, description="Outfit name")
    items: List[OutfitItemResponse] = Field(..., description="List of clothing items in the outfit")
    score: float = Field(..., description="Overall recommendation score")
    color_score: Optional[float] = Field(None, description="Color harmony score")
    style_score: Optional[float] = Field(None, description="Style consistency score")
    occasion_score: Optional[float] = Field(None, description="Occasion appropriateness score")
    recommendation_reason: Optional[str] = Field(None, description="Explanation for the recommendation")

class SimilarItemResponse(BaseModel):
    """Response schema for similar items."""
    id: int
    name: str
    category: str
    brand: Optional[str]
    dominant_color_name: Optional[str]
    image_url: Optional[str]
    similarity_score: float = Field(..., description="Similarity score (0-1)")
    similarity_reasons: Optional[List[str]] = Field(None, description="Reasons for similarity")

class WardrobeItemCreate(BaseModel):
    """Schema for creating wardrobe items."""
    name: str = Field(..., min_length=1, max_length=255)
    brand: Optional[str] = Field(None, max_length=255)
    category: str = Field(..., max_length=255)
    size: Optional[str] = Field(None, max_length=50)
    price: Optional[float] = Field(None, ge=0)
    material: Optional[str] = Field(None, max_length=255)
    season: Optional[str] = Field(None, max_length=50)
    tags: Optional[List[str]] = Field(None, description="List of tags")

class WardrobeItemResponse(BaseModel):
    """Response schema for wardrobe items."""
    id: int
    name: str
    brand: Optional[str]
    category: str
    size: Optional[str]
    price: Optional[float]
    material: Optional[str]
    season: Optional[str]
    image_url: Optional[str]
    dominant_color_rgb: Optional[List[int]]
    dominant_color_hex: Optional[str]
    dominant_color_name: Optional[str]
    ai_classification: Optional[Dict[str, Any]]
    color_properties: Optional[Dict[str, str]]
    style_features: Optional[Dict[str, Any]]
    tags: Optional[List[str]]
    favorite: bool
    times_worn: int
    date_added: datetime
    last_worn: Optional[datetime]

    class Config:
        from_attributes = True

# Schemas for "Find Matching Clothing Items" Feature (Objective ii)
class FindMatchesForItemBodyRequest(BaseModel): # Renamed: target_item_id will come from path
    num_suggestions: int = Field(5, ge=1, le=20, description="Number of matching suggestions to return.")
    occasion: Optional[str] = Field(None, description="Optional: Filter matches for a specific occasion (e.g., 'casual', 'work').")
    suggest_categories: Optional[List[str]] = Field(None, description="Optional: Specific categories of items to suggest as matches.")

class SuggestedItemMatch(BaseModel):
    item: WardrobeItemResponse # Use the existing detailed WardrobeItemResponse
    match_score: float = Field(..., description="Overall compatibility score (0-1).")
    match_type: str = Field(..., description="Type of match (e.g., 'color_coordinated', 'style_similar', 'category_complement').")
    reason: Optional[str] = Field(None, description="Brief explanation of why this item is a good match.")

class FindMatchesForItemResponse(BaseModel):
    target_item: WardrobeItemResponse
    suggested_matches: List[SuggestedItemMatch] = Field(..., description="List of suggested matching items.")
    message: Optional[str] = Field(None, description="Additional information or summary.")

class MLProcessingStatus(BaseModel):
    """Response schema for ML processing status."""
    status: str = Field(..., description="Processing status (success, failed, skipped)")
    message: str = Field(..., description="Status message")
    processed_features: Optional[List[str]] = Field(None, description="List of successfully processed features")
    errors: Optional[List[str]] = Field(None, description="List of errors encountered")

class ColorSuggestionResponse(BaseModel):
    """Response schema for color suggestions."""
    complementary: List[Dict[str, Any]] = Field(..., description="Complementary colors")
    analogous: List[Dict[str, Any]] = Field(..., description="Analogous colors")
    neutrals: List[Dict[str, Any]] = Field(..., description="Neutral colors that work well")

class StyleAnalysisResponse(BaseModel):
    """Response schema for style analysis."""
    style_keywords: List[str] = Field(..., description="Extracted style keywords")
    style_scores: Dict[str, float] = Field(..., description="Style category scores")
    seasonal_appropriateness: Dict[str, float] = Field(..., description="Seasonal appropriateness scores")
    occasion_appropriateness: Dict[str, float] = Field(..., description="Occasion appropriateness scores")

class TrainingStatusResponse(BaseModel):
    """Response schema for model training status."""
    status: str = Field(..., description="Training status")
    message: str = Field(..., description="Training message")
    items_processed: Optional[int] = Field(None, description="Number of items used for training")
    training_time: Optional[float] = Field(None, description="Training time in seconds")

# Additional schemas for enhanced functionality

class WeatherConditions(BaseModel):
    """Schema for weather conditions."""
    temperature: Optional[float] = Field(None, description="Temperature in Celsius")
    humidity: Optional[float] = Field(None, description="Humidity percentage")
    weather_type: Optional[str] = Field(None, description="Weather type (sunny, rainy, cloudy, etc.)")
    season: Optional[str] = Field(None, description="Current season")

class OccasionDetails(BaseModel):
    """Schema for occasion details."""
    occasion_type: str = Field(..., description="Type of occasion")
    formality_level: Optional[str] = Field(None, description="Formality level (casual, semi-formal, formal)")
    duration: Optional[int] = Field(None, description="Duration in hours")
    location: Optional[str] = Field(None, description="Location type (indoor, outdoor, etc.)")
    time_of_day: Optional[str] = Field(None, description="Time of day (morning, afternoon, evening)")

class AdvancedRecommendationRequest(BaseModel):
    """Advanced request schema for outfit recommendations."""
    user_preferences: Optional[UserPreferences] = Field(None, description="User style preferences")
    occasion_details: OccasionDetails = Field(..., description="Detailed occasion information")
    weather_conditions: Optional[WeatherConditions] = Field(None, description="Weather conditions")
    num_recommendations: int = Field(5, ge=1, le=20, description="Number of recommendations to return")
    include_new_combinations: bool = Field(True, description="Include new outfit combinations")
    exclude_recently_worn: bool = Field(True, description="Exclude recently worn items")
    color_coordination_weight: float = Field(0.3, ge=0, le=1, description="Weight for color coordination")
    style_consistency_weight: float = Field(0.3, ge=0, le=1, description="Weight for style consistency")
    occasion_appropriateness_weight: float = Field(0.4, ge=0, le=1, description="Weight for occasion appropriateness")

class BatchProcessingRequest(BaseModel):
    """Request schema for batch processing multiple items."""
    item_ids: List[int] = Field(..., description="List of wardrobe item IDs to process")
    features_to_process: List[str] = Field(..., description="List of features to process (classification, color, style)")
    force_reprocess: bool = Field(False, description="Force reprocessing even if data exists")

class BatchProcessingResponse(BaseModel):
    """Response schema for batch processing."""
    total_items: int = Field(..., description="Total number of items processed")
    successful_items: int = Field(..., description="Number of successfully processed items")
    failed_items: int = Field(..., description="Number of failed items")
    processing_time: float = Field(..., description="Total processing time in seconds")
    detailed_results: List[Dict[str, Any]] = Field(..., description="Detailed results for each item")

class UserStyleProfileResponse(BaseModel):
    """Response schema for user style profile."""
    user_id: int
    style_vector: Optional[List[float]] = Field(None, description="Learned style feature vector")
    preferred_colors: Optional[List[str]] = Field(None, description="Learned color preferences")
    preferred_categories: Optional[List[str]] = Field(None, description="Preferred clothing categories")
    preferred_brands: Optional[List[str]] = Field(None, description="Preferred brands")
    style_keywords: Optional[List[str]] = Field(None, description="Extracted style keywords")
    seasonal_preferences: Optional[Dict[str, List[str]]] = Field(None, description="Seasonal style preferences")
    occasion_preferences: Optional[Dict[str, List[str]]] = Field(None, description="Occasion-based preferences")
    last_updated: datetime

    class Config:
        from_attributes = True

