"""
Recommendation routes for Digital Wardrobe System
Handles outfit recommendations, weather-based suggestions, and occasion-specific recommendations
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
import logging

from models.database_models import User
from services.auth_service import get_current_user
from services.outfit_matching_service import outfit_matching_service
from services.weather_service import weather_service
from services.occasion_recommendation_service import occasion_recommendation_service
from services.preference_learning_service import preference_learning_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.get("/outfit-suggestions/{clothing_item_id}")
async def get_outfit_suggestions(
    clothing_item_id: str,
    occasion: Optional[str] = Query(None, description="Specific occasion for the outfit"),
    weather_location: Optional[str] = Query(None, description="Location for weather-based recommendations"),
    max_suggestions: int = Query(5, ge=1, le=10),
    current_user: User = Depends(get_current_user)
):
    """Get intelligent outfit suggestions based on a clothing item"""
    try:
        suggestions = outfit_matching_service.generate_outfit_suggestions(
            user_id=current_user.id,
            base_item_id=clothing_item_id,
            occasion=occasion,
            max_suggestions=max_suggestions
        )
        
        # Add weather considerations if location provided
        if weather_location:
            weather_data = weather_service.get_current_weather(weather_location)
            if weather_data:
                weather_recommendations = weather_service.generate_weather_clothing_recommendations(weather_data)
                suggestions["weather_considerations"] = weather_recommendations
        
        return suggestions
        
    except Exception as e:
        logger.error(f"Error getting outfit suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weather-based")
async def get_weather_based_recommendations(
    location: str = Query(..., description="City name or location for weather data"),
    country_code: Optional[str] = Query(None, description="Country code (e.g., 'US', 'UK')"),
    current_user: User = Depends(get_current_user)
):
    """Get clothing recommendations based on current weather"""
    try:
        # Get current weather
        weather_data = weather_service.get_current_weather(location, country_code)
        if not weather_data:
            raise HTTPException(status_code=404, detail=f"Weather data not found for location: {location}")
        
        # Generate weather-based recommendations
        weather_recommendations = weather_service.generate_weather_clothing_recommendations(weather_data)
        
        # Get user's wardrobe items that match weather recommendations
        matching_items = outfit_matching_service.find_weather_appropriate_items(
            user_id=current_user.id,
            weather_data=weather_data
        )
        
        return {
            "weather_data": {
                "location": weather_data.location,
                "temperature": weather_data.temperature,
                "feels_like": weather_data.feels_like,
                "description": weather_data.weather_description,
                "humidity": weather_data.humidity,
                "wind_speed": weather_data.wind_speed
            },
            "recommendations": weather_recommendations,
            "matching_wardrobe_items": matching_items
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting weather-based recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/occasion-based")
async def get_occasion_based_recommendations(
    occasion: str = Query(..., description="Type of occasion (e.g., 'job_interview', 'wedding_guest')"),
    weather_location: Optional[str] = Query(None, description="Location for weather considerations"),
    current_user: User = Depends(get_current_user)
):
    """Get outfit recommendations for specific occasions"""
    try:
        recommendations = occasion_recommendation_service.get_occasion_recommendations(
            user_id=current_user.id,
            occasion_name=occasion,
            weather_location=weather_location
        )
        
        if "error" in recommendations:
            raise HTTPException(status_code=400, detail=recommendations["error"])
        
        return recommendations
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting occasion-based recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/occasions")
async def get_available_occasions():
    """Get list of available occasions for recommendations"""
    try:
        occasions = occasion_recommendation_service.get_available_occasions()
        return {"occasions": occasions}
        
    except Exception as e:
        logger.error(f"Error getting available occasions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/seasonal")
async def get_seasonal_recommendations(
    season: str = Query(..., description="Season: spring, summer, fall, winter"),
    location: Optional[str] = Query(None, description="Location for regional considerations"),
    current_user: User = Depends(get_current_user)
):
    """Get seasonal clothing recommendations"""
    try:
        if season.lower() not in ["spring", "summer", "fall", "winter"]:
            raise HTTPException(status_code=400, detail="Season must be one of: spring, summer, fall, winter")
        
        seasonal_recommendations = weather_service.get_seasonal_recommendations(season, location)
        
        # Get user's wardrobe items suitable for the season
        seasonal_items = outfit_matching_service.find_seasonal_items(
            user_id=current_user.id,
            season=season
        )
        
        return {
            "season": season,
            "location": location,
            "recommendations": seasonal_recommendations,
            "wardrobe_items": seasonal_items
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting seasonal recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/personalized")
async def get_personalized_recommendations(
    max_recommendations: int = Query(10, ge=1, le=20),
    include_weather: bool = Query(False, description="Include weather-based filtering"),
    weather_location: Optional[str] = Query(None, description="Location for weather data"),
    current_user: User = Depends(get_current_user)
):
    """Get personalized outfit recommendations based on user preferences and behavior"""
    try:
        # Get user preferences and generate personalized recommendations
        personalized_recs = preference_learning_service.generate_personalized_recommendations(
            user_id=current_user.id,
            max_recommendations=max_recommendations
        )
        
        # Add weather filtering if requested
        if include_weather and weather_location:
            weather_data = weather_service.get_current_weather(weather_location)
            if weather_data:
                # Filter recommendations based on weather
                weather_filtered_recs = outfit_matching_service.filter_recommendations_by_weather(
                    recommendations=personalized_recs,
                    weather_data=weather_data
                )
                personalized_recs = weather_filtered_recs
        
        return personalized_recs
        
    except Exception as e:
        logger.error(f"Error getting personalized recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback")
async def provide_recommendation_feedback(
    recommendation_id: str,
    feedback_type: str = Query(..., description="Type of feedback: 'like', 'dislike', 'worn', 'not_worn'"),
    rating: Optional[int] = Query(None, ge=1, le=5, description="Rating from 1-5"),
    comments: Optional[str] = Query(None, description="Additional feedback comments"),
    current_user: User = Depends(get_current_user)
):
    """Provide feedback on outfit recommendations to improve future suggestions"""
    try:
        if feedback_type not in ["like", "dislike", "worn", "not_worn"]:
            raise HTTPException(status_code=400, detail="Invalid feedback type")
        
        # Record feedback for machine learning
        feedback_result = preference_learning_service.record_recommendation_feedback(
            user_id=current_user.id,
            recommendation_id=recommendation_id,
            feedback_type=feedback_type,
            rating=rating,
            comments=comments
        )
        
        return {
            "message": "Feedback recorded successfully",
            "feedback_id": feedback_result.get("feedback_id"),
            "learning_update": "Preferences updated for future recommendations"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording recommendation feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weather-forecast")
async def get_weather_forecast_recommendations(
    location: str = Query(..., description="City name or location"),
    days: int = Query(5, ge=1, le=7, description="Number of days for forecast"),
    current_user: User = Depends(get_current_user)
):
    """Get clothing recommendations for upcoming weather forecast"""
    try:
        # Get weather forecast
        forecast_data = weather_service.get_weather_forecast(location, days=days)
        if not forecast_data:
            raise HTTPException(status_code=404, detail=f"Weather forecast not found for location: {location}")
        
        # Generate recommendations for each day
        forecast_recommendations = []
        for day_weather in forecast_data:
            day_recommendations = weather_service.generate_weather_clothing_recommendations(day_weather)
            
            # Find matching items from user's wardrobe
            matching_items = outfit_matching_service.find_weather_appropriate_items(
                user_id=current_user.id,
                weather_data=day_weather
            )
            
            forecast_recommendations.append({
                "date": day_weather.timestamp.strftime("%Y-%m-%d"),
                "weather": {
                    "temperature": day_weather.temperature,
                    "description": day_weather.weather_description,
                    "humidity": day_weather.humidity,
                    "wind_speed": day_weather.wind_speed
                },
                "recommendations": day_recommendations,
                "suggested_items": matching_items[:5]  # Top 5 suggestions
            })
        
        return {
            "location": location,
            "forecast_period": f"{days} days",
            "daily_recommendations": forecast_recommendations
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting weather forecast recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/color-coordination")
async def get_color_coordination_suggestions(
    base_color: str = Query(..., description="Base color to coordinate with"),
    current_user: User = Depends(get_current_user)
):
    """Get color coordination suggestions for outfit planning"""
    try:
        color_suggestions = outfit_matching_service.get_color_coordination_suggestions(
            user_id=current_user.id,
            base_color=base_color
        )
        
        return color_suggestions
        
    except Exception as e:
        logger.error(f"Error getting color coordination suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

