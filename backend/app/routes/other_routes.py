

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from fastapi import APIRouter, HTTPException, status, Depends, File,UploadFile
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field

import json
from ..security import get_current_user
# Import your models and database session
from ..model import (
    User, ClothingCategory, ClothingAttribute, WardrobeItem, Outfit,
    WeatherPreference, WeeklyPlan, WeeklyPlanDayOutfit, Occasion,
    StyleHistory, UserProfile, UserStyleProfile, OutfitRecommendation,
    ColorAnalysis, ItemClassification, Feedback, WeatherData
)
from ..db.database import get_db


router = APIRouter(prefix="/other")

@router.get("/analytics/wardrobe-stats")
def get_wardrobe_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    stats = {}
    
    # Total items
    stats['total_items'] = db.query(WardrobeItem).filter(WardrobeItem.user_id == current_user.id).count()
    
    # Items by category
    category_stats = db.query(
        ClothingCategory.name,
        func.count(WardrobeItem.id)
    ).join(WardrobeItem).filter(
        WardrobeItem.user_id == current_user.id
    ).group_by(ClothingCategory.name).all()
    
    stats['by_category'] = dict(category_stats)
    
    # Most worn items
    most_worn = db.query(WardrobeItem).filter(
        WardrobeItem.user_id == current_user.id
    ).order_by(desc(WardrobeItem.times_worn)).limit(10).all()
    
    stats['most_worn'] = [{"name": item.name, "times_worn": item.times_worn} for item in most_worn]
    
    # Favorite items count
    stats['favorite_items'] = db.query(WardrobeItem).filter(
        WardrobeItem.user_id == current_user.id,
        WardrobeItem.favorite == True
    ).count()
    
    return stats

@router.get("/analytics/outfit-stats")
def get_outfit_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    stats = {}
    
    # Total outfits
    stats['total_outfits'] = db.query(Outfit).filter(Outfit.user_id == current_user.id).count()
    
    # Outfits by occasion
    occasion_stats = db.query(
        Outfit.occasion_type,
        func.count(Outfit.id)
    ).filter(
        Outfit.user_id == current_user.id,
        Outfit.occasion_type.isnot(None)
    ).group_by(Outfit.occasion_type).all()
    
    stats['by_occasion'] = dict(occasion_stats)
    
    # Most worn outfits
    most_worn_outfits = db.query(Outfit).filter(
        Outfit.user_id == current_user.id
    ).order_by(desc(Outfit.times_worn)).limit(10).all()
    
    stats['most_worn_outfits'] = [{"name": outfit.name, "times_worn": outfit.times_worn} for outfit in most_worn_outfits]
    
    # Average ratings
    avg_rating = db.query(func.avg(Outfit.avg_rating)).filter(
        Outfit.user_id == current_user.id,
        Outfit.avg_rating.isnot(None)
    ).scalar()
    
    stats['average_rating'] = float(avg_rating) if avg_rating else None
    
    return stats

# RECOMMENDATIONS ROUTES
@router.get("/recommendations/outfits")
def get_outfit_recommendations(
    occasion: Optional[str] = None,
    weather: Optional[str] = None,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(OutfitRecommendation).filter(
        OutfitRecommendation.user_id == current_user.id
    )
    
    if occasion:
        query = query.filter(OutfitRecommendation.occasion == occasion)
    
    recommendations = query.order_by(desc(OutfitRecommendation.confidence_score)).limit(limit).all()
    return recommendations

@router.post("/recommendations/generate")
def generate_recommendations(
    occasion: Optional[str] = None,
    weather_conditions: Optional[Dict[str, Any]] = None,
    formality_level: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # This would integrate with your ML recommendation engine
    # For now, return a placeholder response
    return {
        "message": "Recommendation generation triggered",
        "parameters": {
            "occasion": occasion,
            "weather_conditions": weather_conditions,
            "formality_level": formality_level
        }
    }

# WEATHER ROUTES
@router.get("/weather/{location}")
def get_weather_data(
    location: str,
    date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    query = db.query(WeatherData).filter(WeatherData.location == location)
    
    if date:
        query = query.filter(WeatherData.date == date)
    else:
        # Get latest weather data
        query = query.order_by(desc(WeatherData.date))
    
    weather = query.first()
    if not weather:
        raise HTTPException(status_code=404, detail="Weather data not found")
    
    return weather

@router.post("/weather/")
def create_weather_data(
    weather_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    # This would typically be called by a weather service integration
    db_weather = WeatherData(**weather_data)
    db.add(db_weather)
    db.commit()
    db.refresh(db_weather)
    return db_weather

# USER PROFILE ROUTES
@router.get("/profile/")
def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        # Create default profile
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

@router.put("/profile/")
def update_user_profile(
    profile_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
    
    for key, value in profile_data.items():
        if hasattr(profile, key):
            setattr(profile, key, value)
    
    db.commit()
    db.refresh(profile)
    return profile

# STYLE PROFILE ROUTES
@router.get("/style-profile/")
def get_style_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    style_profile = db.query(UserStyleProfile).filter(
        UserStyleProfile.user_id == current_user.id
    ).first()
    if not style_profile:
        raise HTTPException(status_code=404, detail="Style profile not found")
    return style_profile

@router.put("/style-profile/")
def update_style_profile(
    style_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    style_profile = db.query(UserStyleProfile).filter(
        UserStyleProfile.user_id == current_user.id
    ).first()
    
    if not style_profile:
        style_profile = UserStyleProfile(user_id=current_user.id)
        db.add(style_profile)
    
    for key, value in style_data.items():
        if hasattr(style_profile, key):
            setattr(style_profile, key, value)
    
    db.commit()
    db.refresh(style_profile)
    return style_profile

# WEATHER PREFERENCES ROUTES
@router.get("/weather-preferences/")
def get_weather_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    preferences = db.query(WeatherPreference).filter(
        WeatherPreference.user_id == current_user.id
    ).all()
    return preferences

@router.post("/weather-preferences/")
def create_weather_preference(
    preference_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    preference_data['user_id'] = current_user.id
    preference = WeatherPreference(**preference_data)
    db.add(preference)
    db.commit()
    db.refresh(preference)
    return preference

