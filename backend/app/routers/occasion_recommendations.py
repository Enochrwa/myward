"""
Enhanced Occasion-Based Recommendations System

This module provides comprehensive occasion-based outfit recommendations with
weather awareness, seasonal considerations, and event-specific planning.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime, timedelta
import json

from .. import tables as schemas
from .. import model as models
from ..security import get_current_user
from ..db.database import get_db
from ..services.intelligent_matching import IntelligentMatchingAlgorithm, OccasionMatcher
from ..services.ml_personalized_recommendations import PersonalizedRecommendationModel

router = APIRouter(
    prefix="/occasion-recommendations",
    tags=["Occasion-Based Recommendations"],
    responses={404: {"description": "Not found"}},
)

class OccasionType(str, Enum):
    """Predefined occasion types"""
    WORK = "work"
    CASUAL = "casual"
    FORMAL = "formal"
    PARTY = "party"
    DATE = "date"
    WEDDING = "wedding"
    CHURCH = "church"
    HOME = "home"
    SPORTS = "sports"
    TRAVEL = "travel"
    INTERVIEW = "interview"
    GRADUATION = "graduation"
    DINNER = "dinner"
    BRUNCH = "brunch"
    SHOPPING = "shopping"

class WeatherCondition(str, Enum):
    """Weather conditions"""
    SUNNY = "sunny"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    SNOWY = "snowy"
    WINDY = "windy"
    HOT = "hot"
    COLD = "cold"
    MILD = "mild"

class Season(str, Enum):
    """Seasons"""
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"

class FormalityLevel(str, Enum):
    """Formality levels"""
    VERY_CASUAL = "very_casual"
    CASUAL = "casual"
    SMART_CASUAL = "smart_casual"
    BUSINESS = "business"
    FORMAL = "formal"
    BLACK_TIE = "black_tie"

class OccasionRequest(BaseModel):
    """Request for occasion-based recommendations"""
    occasion_type: OccasionType = Field(..., description="Type of occasion")
    date_time: Optional[datetime] = Field(None, description="Date and time of the occasion")
    location: Optional[str] = Field(None, description="Location of the occasion")
    weather_condition: Optional[WeatherCondition] = Field(None, description="Expected weather")
    temperature: Optional[float] = Field(None, description="Temperature in Celsius")
    formality_level: Optional[FormalityLevel] = Field(None, description="Required formality level")
    duration: Optional[int] = Field(None, description="Duration in hours")
    notes: Optional[str] = Field(None, description="Additional notes or requirements")
    max_outfits: int = Field(3, description="Maximum number of outfit suggestions", ge=1, le=10)

class WeatherAwareRequest(BaseModel):
    """Request for weather-aware recommendations"""
    latitude: float = Field(..., description="Latitude for weather data")
    longitude: float = Field(..., description="Longitude for weather data")
    occasion_type: Optional[OccasionType] = Field(None, description="Type of occasion")
    date_time: Optional[datetime] = Field(None, description="Date and time")
    max_outfits: int = Field(3, description="Maximum number of outfit suggestions", ge=1, le=10)

class SeasonalRequest(BaseModel):
    """Request for seasonal recommendations"""
    season: Season = Field(..., description="Season for recommendations")
    occasion_type: Optional[OccasionType] = Field(None, description="Type of occasion")
    max_outfits: int = Field(5, description="Maximum number of outfit suggestions", ge=1, le=20)

class EventPlanningRequest(BaseModel):
    """Request for event planning recommendations"""
    event_name: str = Field(..., description="Name of the event")
    start_date: datetime = Field(..., description="Start date of the event")
    end_date: Optional[datetime] = Field(None, description="End date (for multi-day events)")
    occasion_type: OccasionType = Field(..., description="Type of occasion")
    location: Optional[str] = Field(None, description="Event location")
    formality_level: Optional[FormalityLevel] = Field(None, description="Required formality level")
    special_requirements: Optional[List[str]] = Field(None, description="Special requirements")

class OutfitRecommendation(BaseModel):
    """Outfit recommendation with context"""
    outfit_id: Optional[str] = None
    items: List[schemas.WardrobeItem]
    compatibility_score: float
    occasion_appropriateness: float
    weather_suitability: Optional[float] = None
    formality_match: Optional[float] = None
    reasons: List[str]
    styling_tips: Optional[List[str]] = None

class OccasionAnalysis(BaseModel):
    """Analysis of user's occasion history"""
    occasion_type: str
    frequency: int
    preferred_styles: List[str]
    preferred_colors: List[str]
    average_formality: float
    seasonal_patterns: Dict[str, int]

# Initialize services
intelligent_matcher = IntelligentMatchingAlgorithm()
occasion_matcher = OccasionMatcher()
ml_recommender = PersonalizedRecommendationModel()

@router.post("/occasion", response_model=List[OutfitRecommendation])
async def get_occasion_recommendations(
    request: OccasionRequest,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Get outfit recommendations for a specific occasion
    """
    # Get user's wardrobe items
    wardrobe_items = db.query(models.WardrobeItem).filter(
        models.WardrobeItem.user_id == current_user.id
    ).all()
    
    if not wardrobe_items:
        raise HTTPException(status_code=404, detail="No wardrobe items found")
    
    # Convert to format for matching algorithm
    items_dict = [_convert_item_to_dict(item) for item in wardrobe_items]
    
    # Get occasion-specific recommendations
    recommendations = _get_occasion_specific_outfits(
        items_dict, request, current_user.id, db
    )
    
    return recommendations[:request.max_outfits]

@router.post("/weather-aware", response_model=List[OutfitRecommendation])
async def get_weather_aware_recommendations(
    request: WeatherAwareRequest,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Get weather-aware outfit recommendations
    """
    # Get weather data (mock implementation - would integrate with weather API)
    weather_data = _get_weather_data(request.latitude, request.longitude)
    
    # Get user's wardrobe items
    wardrobe_items = db.query(models.WardrobeItem).filter(
        models.WardrobeItem.user_id == current_user.id
    ).all()
    
    if not wardrobe_items:
        raise HTTPException(status_code=404, detail="No wardrobe items found")
    
    # Filter items based on weather
    weather_appropriate_items = _filter_items_by_weather(wardrobe_items, weather_data)
    
    # Convert to format for matching algorithm
    items_dict = [_convert_item_to_dict(item) for item in weather_appropriate_items]
    
    # Create occasion request with weather context
    occasion_request = OccasionRequest(
        occasion_type=request.occasion_type or OccasionType.CASUAL,
        date_time=request.date_time,
        weather_condition=_map_weather_to_condition(weather_data),
        temperature=weather_data.get("temperature"),
        max_outfits=request.max_outfits
    )
    
    recommendations = _get_occasion_specific_outfits(
        items_dict, occasion_request, current_user.id, db
    )
    
    # Add weather suitability scores
    for rec in recommendations:
        rec.weather_suitability = _calculate_weather_suitability(rec.items, weather_data)
    
    return recommendations

@router.post("/seasonal", response_model=List[OutfitRecommendation])
async def get_seasonal_recommendations(
    request: SeasonalRequest,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Get seasonal outfit recommendations
    """
    # Get user's wardrobe items
    wardrobe_items = db.query(models.WardrobeItem).filter(
        models.WardrobeItem.user_id == current_user.id
    ).all()
    
    if not wardrobe_items:
        raise HTTPException(status_code=404, detail="No wardrobe items found")
    
    # Filter items by season
    seasonal_items = _filter_items_by_season(wardrobe_items, request.season)
    
    # Convert to format for matching algorithm
    items_dict = [_convert_item_to_dict(item) for item in seasonal_items]
    
    # Generate seasonal outfit combinations
    recommendations = _generate_seasonal_outfits(
        items_dict, request.season, request.occasion_type, current_user.id, db
    )
    
    return recommendations[:request.max_outfits]

@router.post("/event-planning", response_model=Dict[str, List[OutfitRecommendation]])
async def plan_event_outfits(
    request: EventPlanningRequest,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Plan outfits for multi-day events or special occasions
    """
    # Calculate event duration
    end_date = request.end_date or request.start_date
    event_days = (end_date - request.start_date).days + 1
    
    # Get user's wardrobe items
    wardrobe_items = db.query(models.WardrobeItem).filter(
        models.WardrobeItem.user_id == current_user.id
    ).all()
    
    if not wardrobe_items:
        raise HTTPException(status_code=404, detail="No wardrobe items found")
    
    # Plan outfits for each day
    event_plan = {}
    used_items = set()  # Track used items to avoid repetition
    
    for day in range(event_days):
        current_date = request.start_date + timedelta(days=day)
        day_key = f"day_{day + 1}_{current_date.strftime('%Y-%m-%d')}"
        
        # Get available items (excluding recently used ones)
        available_items = [
            item for item in wardrobe_items 
            if str(item.id) not in used_items
        ]
        
        if not available_items:
            # Reset used items if we run out
            available_items = wardrobe_items
            used_items.clear()
        
        # Convert to format for matching algorithm
        items_dict = [_convert_item_to_dict(item) for item in available_items]
        
        # Create occasion request for this day
        occasion_request = OccasionRequest(
            occasion_type=request.occasion_type,
            date_time=current_date,
            location=request.location,
            formality_level=request.formality_level,
            max_outfits=2  # Fewer options per day for multi-day events
        )
        
        day_recommendations = _get_occasion_specific_outfits(
            items_dict, occasion_request, current_user.id, db
        )
        
        # Mark items as used
        if day_recommendations:
            for item in day_recommendations[0].items:
                used_items.add(str(item.id))
        
        event_plan[day_key] = day_recommendations
    
    return event_plan

@router.get("/occasion-analysis", response_model=List[OccasionAnalysis])
async def analyze_occasion_history(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Analyze user's occasion history and preferences
    """
    # Get user's outfit history
    outfits = db.query(models.Outfit).filter(
        models.Outfit.user_id == current_user.id
    ).all()
    
    if not outfits:
        return []
    
    # Analyze patterns by occasion
    occasion_data = {}
    
    for outfit in outfits:
        occasion = getattr(outfit, 'occasion', 'casual') or 'casual'
        
        if occasion not in occasion_data:
            occasion_data[occasion] = {
                'frequency': 0,
                'styles': [],
                'colors': [],
                'formality_scores': [],
                'seasonal_counts': {'spring': 0, 'summer': 0, 'autumn': 0, 'winter': 0}
            }
        
        occasion_data[occasion]['frequency'] += 1
        
        # Analyze outfit items
        for item in outfit.items:
            if hasattr(item, 'style') and item.style:
                occasion_data[occasion]['styles'].append(item.style)
            
            if hasattr(item, 'dominant_color_name') and item.dominant_color_name:
                occasion_data[occasion]['colors'].append(item.dominant_color_name)
        
        # Determine season from date
        if hasattr(outfit, 'created_at') and outfit.created_at:
            season = _get_season_from_date(outfit.created_at)
            occasion_data[occasion]['seasonal_counts'][season] += 1
    
    # Convert to analysis format
    analyses = []
    for occasion, data in occasion_data.items():
        # Calculate most frequent styles and colors
        style_counts = {}
        for style in data['styles']:
            style_counts[style] = style_counts.get(style, 0) + 1
        
        color_counts = {}
        for color in data['colors']:
            color_counts[color] = color_counts.get(color, 0) + 1
        
        # Get top preferences
        preferred_styles = sorted(style_counts.keys(), key=lambda x: style_counts[x], reverse=True)[:3]
        preferred_colors = sorted(color_counts.keys(), key=lambda x: color_counts[x], reverse=True)[:3]
        
        analyses.append(OccasionAnalysis(
            occasion_type=occasion,
            frequency=data['frequency'],
            preferred_styles=preferred_styles,
            preferred_colors=preferred_colors,
            average_formality=0.5,  # Would calculate based on actual formality scores
            seasonal_patterns=data['seasonal_counts']
        ))
    
    return analyses

@router.get("/occasion-types")
async def get_occasion_types():
    """
    Get available occasion types with descriptions
    """
    occasion_descriptions = {
        "work": "Professional workplace attire",
        "casual": "Relaxed, everyday wear",
        "formal": "Formal events and ceremonies",
        "party": "Social gatherings and celebrations",
        "date": "Romantic or social outings",
        "wedding": "Wedding ceremonies and receptions",
        "church": "Religious services and gatherings",
        "home": "Comfortable home wear",
        "sports": "Athletic and fitness activities",
        "travel": "Travel and vacation wear",
        "interview": "Job interviews and professional meetings",
        "graduation": "Graduation ceremonies",
        "dinner": "Dinner parties and fine dining",
        "brunch": "Brunch and daytime social events",
        "shopping": "Shopping and errands"
    }
    
    return {
        "occasion_types": [
            {"value": occasion.value, "label": occasion.value.replace("_", " ").title(), 
             "description": occasion_descriptions.get(occasion.value, "")}
            for occasion in OccasionType
        ]
    }

def _get_occasion_specific_outfits(
    items_dict: List[Dict[str, Any]], 
    request: OccasionRequest, 
    user_id: int, 
    db: Session
) -> List[OutfitRecommendation]:
    """Generate occasion-specific outfit recommendations"""
    
    # Filter items by occasion appropriateness
    appropriate_items = []
    for item in items_dict:
        style = item.get("style", "casual")
        score = occasion_matcher.calculate_occasion_score(style, request.occasion_type.value)
        if score > 0.3:  # Minimum appropriateness threshold
            item["occasion_score"] = score
            appropriate_items.append(item)
    
    if not appropriate_items:
        return []
    
    # Generate outfit combinations
    outfit_combinations = _generate_outfit_combinations(appropriate_items)
    
    # Score and rank combinations
    recommendations = []
    for combination in outfit_combinations:
        # Calculate compatibility score
        compatibility_result = intelligent_matcher._calculate_item_compatibility(
            combination[0], combination[1] if len(combination) > 1 else combination[0],
            request.occasion_type.value
        )
        
        # Calculate occasion appropriateness
        occasion_scores = [item.get("occasion_score", 0.5) for item in combination]
        occasion_appropriateness = sum(occasion_scores) / len(occasion_scores)
        
        # Calculate formality match if specified
        formality_match = None
        if request.formality_level:
            formality_match = _calculate_formality_match(combination, request.formality_level)
        
        # Generate reasons and styling tips
        reasons = _generate_recommendation_reasons(combination, request)
        styling_tips = _generate_styling_tips(combination, request)
        
        # Convert back to WardrobeItem format (mock for now)
        items = [_create_mock_wardrobe_item(item) for item in combination]
        
        recommendations.append(OutfitRecommendation(
            items=items,
            compatibility_score=compatibility_result,
            occasion_appropriateness=occasion_appropriateness,
            formality_match=formality_match,
            reasons=reasons,
            styling_tips=styling_tips
        ))
    
    # Sort by overall score
    recommendations.sort(
        key=lambda x: (x.compatibility_score + x.occasion_appropriateness) / 2, 
        reverse=True
    )
    
    return recommendations

def _generate_outfit_combinations(items: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    """Generate valid outfit combinations from available items"""
    combinations = []
    
    # Group items by category
    items_by_category = {}
    for item in items:
        category = item.get("category", "unknown")
        if category not in items_by_category:
            items_by_category[category] = []
        items_by_category[category].append(item)
    
    # Define outfit structures
    outfit_structures = [
        ["tops", "bottoms"],
        ["tops", "bottoms", "shoes"],
        ["tops", "bottoms", "outerwear"],
        ["dresses"],
        ["dresses", "shoes"],
        ["dresses", "outerwear"]
    ]
    
    # Generate combinations based on structures
    for structure in outfit_structures:
        if all(cat in items_by_category for cat in structure):
            # Simple approach: take first item from each category
            combination = []
            for category in structure:
                if items_by_category[category]:
                    combination.append(items_by_category[category][0])
            
            if combination:
                combinations.append(combination)
    
    return combinations[:10]  # Limit combinations

def _convert_item_to_dict(item: models.WardrobeItem) -> Dict[str, Any]:
    """Convert SQLAlchemy model to dictionary"""
    return {
        "id": str(item.id),
        "name": item.name,
        "category": item.category or "unknown",
        "style": getattr(item, "style", "casual"),
        "colors": [item.dominant_color_hex] if item.dominant_color_hex else ["#808080"],
        "price": item.price or 0,
        "brand": item.brand or "unknown",
        "season": getattr(item, "season", "all")
    }

def _create_mock_wardrobe_item(item_dict: Dict[str, Any]) -> schemas.WardrobeItem:
    """Create a mock WardrobeItem from dictionary (for testing)"""
    # This would normally fetch the actual item from the database
    return schemas.WardrobeItem(
        id=int(item_dict["id"]),
        name=item_dict["name"],
        category=item_dict["category"],
        dominant_color_hex=item_dict["colors"][0] if item_dict["colors"] else "#808080",
        price=item_dict["price"],
        brand=item_dict["brand"],
        user_id=1,  # Mock user ID
        image_url="",
        description="",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

def _get_weather_data(latitude: float, longitude: float) -> Dict[str, Any]:
    """Get weather data (mock implementation)"""
    # This would integrate with a real weather API
    return {
        "temperature": 20.0,
        "condition": "sunny",
        "humidity": 60,
        "wind_speed": 10,
        "precipitation": 0
    }

def _filter_items_by_weather(items: List[models.WardrobeItem], weather_data: Dict[str, Any]) -> List[models.WardrobeItem]:
    """Filter items based on weather conditions"""
    temperature = weather_data.get("temperature", 20)
    condition = weather_data.get("condition", "mild")
    
    filtered_items = []
    for item in items:
        # Simple weather filtering logic
        category = item.category or ""
        
        if temperature < 10:  # Cold weather
            if category.lower() in ["coat", "jacket", "sweater", "boots", "scarf"]:
                filtered_items.append(item)
        elif temperature > 25:  # Hot weather
            if category.lower() in ["t-shirt", "shorts", "dress", "sandals", "tank top"]:
                filtered_items.append(item)
        else:  # Mild weather
            filtered_items.append(item)
    
    return filtered_items if filtered_items else items

def _filter_items_by_season(items: List[models.WardrobeItem], season: Season) -> List[models.WardrobeItem]:
    """Filter items by season"""
    seasonal_items = []
    for item in items:
        item_season = getattr(item, "season", "all")
        if item_season == "all" or item_season == season.value:
            seasonal_items.append(item)
    
    return seasonal_items if seasonal_items else items

def _generate_seasonal_outfits(
    items_dict: List[Dict[str, Any]], 
    season: Season, 
    occasion_type: Optional[OccasionType],
    user_id: int,
    db: Session
) -> List[OutfitRecommendation]:
    """Generate seasonal outfit recommendations"""
    # This would implement seasonal-specific logic
    # For now, use the general occasion logic
    occasion_request = OccasionRequest(
        occasion_type=occasion_type or OccasionType.CASUAL,
        max_outfits=5
    )
    
    return _get_occasion_specific_outfits(items_dict, occasion_request, user_id, db)

def _map_weather_to_condition(weather_data: Dict[str, Any]) -> WeatherCondition:
    """Map weather data to weather condition enum"""
    condition = weather_data.get("condition", "mild").lower()
    
    condition_map = {
        "sunny": WeatherCondition.SUNNY,
        "cloudy": WeatherCondition.CLOUDY,
        "rainy": WeatherCondition.RAINY,
        "snowy": WeatherCondition.SNOWY,
        "windy": WeatherCondition.WINDY
    }
    
    return condition_map.get(condition, WeatherCondition.MILD)

def _calculate_weather_suitability(items: List[schemas.WardrobeItem], weather_data: Dict[str, Any]) -> float:
    """Calculate how suitable an outfit is for the weather"""
    temperature = weather_data.get("temperature", 20)
    condition = weather_data.get("condition", "mild")
    
    suitability_score = 0.5  # Base score
    
    for item in items:
        category = item.category or ""
        
        # Temperature suitability
        if temperature < 10:  # Cold
            if category.lower() in ["coat", "jacket", "sweater", "boots"]:
                suitability_score += 0.2
        elif temperature > 25:  # Hot
            if category.lower() in ["t-shirt", "shorts", "dress", "sandals"]:
                suitability_score += 0.2
        
        # Condition suitability
        if condition == "rainy" and category.lower() in ["raincoat", "boots"]:
            suitability_score += 0.3
    
    return min(1.0, suitability_score)

def _calculate_formality_match(combination: List[Dict[str, Any]], formality_level: FormalityLevel) -> float:
    """Calculate how well the outfit matches the required formality level"""
    # Map formality levels to scores
    formality_scores = {
        FormalityLevel.VERY_CASUAL: 0.1,
        FormalityLevel.CASUAL: 0.3,
        FormalityLevel.SMART_CASUAL: 0.5,
        FormalityLevel.BUSINESS: 0.7,
        FormalityLevel.FORMAL: 0.9,
        FormalityLevel.BLACK_TIE: 1.0
    }
    
    target_score = formality_scores[formality_level]
    
    # Calculate outfit formality based on items
    outfit_formality = 0.0
    for item in combination:
        style = item.get("style", "casual")
        if style == "formal":
            outfit_formality += 0.3
        elif style == "business":
            outfit_formality += 0.25
        elif style == "smart-casual":
            outfit_formality += 0.15
        elif style == "casual":
            outfit_formality += 0.1
    
    outfit_formality = min(1.0, outfit_formality)
    
    # Calculate match score (closer to target = higher score)
    match_score = 1.0 - abs(target_score - outfit_formality)
    return max(0.0, match_score)

def _generate_recommendation_reasons(combination: List[Dict[str, Any]], request: OccasionRequest) -> List[str]:
    """Generate human-readable reasons for the recommendation"""
    reasons = []
    
    # Occasion appropriateness
    reasons.append(f"Perfect for {request.occasion_type.value} occasions")
    
    # Style coherence
    styles = [item.get("style", "casual") for item in combination]
    if len(set(styles)) == 1:
        reasons.append(f"Consistent {styles[0]} style throughout")
    
    # Weather considerations
    if request.weather_condition:
        reasons.append(f"Suitable for {request.weather_condition.value} weather")
    
    # Formality match
    if request.formality_level:
        reasons.append(f"Matches {request.formality_level.value.replace('_', ' ')} dress code")
    
    return reasons

def _generate_styling_tips(combination: List[Dict[str, Any]], request: OccasionRequest) -> List[str]:
    """Generate styling tips for the outfit"""
    tips = []
    
    # General tips based on occasion
    if request.occasion_type == OccasionType.WORK:
        tips.append("Keep accessories minimal and professional")
        tips.append("Ensure clothes are well-fitted and wrinkle-free")
    elif request.occasion_type == OccasionType.DATE:
        tips.append("Add a statement accessory for personality")
        tips.append("Choose comfortable shoes you can walk in")
    elif request.occasion_type == OccasionType.WEDDING:
        tips.append("Avoid white or overly flashy colors")
        tips.append("Consider the venue and time of day")
    
    # Weather-based tips
    if request.weather_condition == WeatherCondition.RAINY:
        tips.append("Bring an umbrella and wear waterproof shoes")
    elif request.weather_condition == WeatherCondition.SUNNY:
        tips.append("Don't forget sunglasses and sunscreen")
    
    return tips

def _get_season_from_date(date: datetime) -> str:
    """Determine season from date"""
    month = date.month
    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    else:
        return "autumn"

