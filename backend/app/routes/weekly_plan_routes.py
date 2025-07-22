from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from ..model import User, WeeklyPlan, WeeklyPlanDayOutfit
from ..db.database import get_db
from ..security import get_current_user
from pydantic import BaseModel
from sqlalchemy.orm import joinedload
from ..model import Outfit, WardrobeItem, ClothingCategory, User
import os
from ..services.occasion_weather_outfits import WeatherService, SmartOutfitRecommender, WeatherData, WeatherOccasionRequest
import json

router = APIRouter(prefix="/weekly-plan", tags=["Weekly Plan"])

class WeeklyPlanCreate(BaseModel):
    name: str
    start_date: str
    end_date: str
    days: List[Dict[str, Any]]

class OutfitItemResponse(BaseModel):
    id: int
    image_url: str
    category: str
    name: str
    brand: Optional[str]
    material: Optional[str]
    style: Optional[str]
    dominant_color_name: Optional[str]

class DayOutfitResponse(BaseModel):
    id: int
    name: str
    items: List[OutfitItemResponse]

class DayResponse(BaseModel):
    id: int
    day_of_week: str
    date: str
    occasion: str
    outfit: Optional[DayOutfitResponse]
    weather_forecast: Optional[Dict[str, Any]]

class WeeklyPlanResponse(BaseModel):
    id: int
    name: str
    start_date: str
    end_date: str
    days: List[DayResponse]

    class Config:
        ofrom_attributes = True

@router.post("/", response_model=WeeklyPlanResponse)
def create_weekly_plan(
    plan_data: WeeklyPlanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_plan = WeeklyPlan(
        user_id=current_user.id,
        name=plan_data.name,
        start_date=plan_data.start_date,
        end_date=plan_data.end_date,
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)

    days = []
    for day_data in plan_data.days:
        db_day = WeeklyPlanDayOutfit(
            weekly_plan_id=db_plan.id,
            day_of_week=day_data['day_of_week'],
            date=day_data['date'],
            occasion=day_data['occasion'],
            outfit_id=day_data.get('outfit_id'),
            weather_forecast=json.dumps(day_data.get('weather_forecast'))
        )
        db.add(db_day)
        days.append(db_day)
    
    db.commit()
    db.refresh(db_plan)

    # After committing, the 'days' objects are stale. We need to refetch them.
    db.refresh(db_plan)
    
    # Construct the full response with nested outfit details
    days_response = []
    for day in db_plan.daily_outfits:
        outfit_response = None
        if day.outfit:
            outfit_response = DayOutfitResponse(
                id=day.outfit.id,
                name=day.outfit.name,
                items=[
                    OutfitItemResponse(
                        id=item.id,
                        image_url=item.image_url,
                        category=item.category_obj.name,
                        name=item.name,
                        brand=item.brand,
                        material=item.material,
                        style=item.style,
                        dominant_color_name=item.dominant_color_name,
                    )
                    for item in day.outfit.items
                ],
            )
        days_response.append(
            DayResponse(
                id=day.id,
                day_of_week=day.day_of_week,
                date=str(day.date),
                occasion=day.occasion,
                outfit=outfit_response,
                weather_forecast=json.loads(day.weather_forecast)
                if day.weather_forecast
                else None,
            )
        )

    return WeeklyPlanResponse(
        id=db_plan.id,
        name=db_plan.name,
        start_date=str(db_plan.start_date),
        end_date=str(db_plan.end_date),
        days=days_response,
    )



@router.get("/", response_model=List[WeeklyPlanResponse])
def get_weekly_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    plans = (
        db.query(WeeklyPlan)
        .filter(WeeklyPlan.user_id == current_user.id)
        .options(
            joinedload(WeeklyPlan.daily_outfits)
            .joinedload(WeeklyPlanDayOutfit.outfit)
            .joinedload(Outfit.items)
            .joinedload(WardrobeItem.category_obj)
        )
        .all()
    )

    response = []
    for plan in plans:
        days_response = []
        for day in plan.daily_outfits:
            outfit_response = None
            if day.outfit:
                outfit_response = DayOutfitResponse(
                    id=day.outfit.id,
                    name=day.outfit.name,
                    items=[
                        OutfitItemResponse(
                            id=item.id,
                            image_url=item.image_url,
                            category=item.category_obj.name,
                            name=item.name,
                            brand=item.brand,
                            material=item.material,
                            style=item.style,
                            dominant_color_name=item.dominant_color_name,
                        )
                        for item in day.outfit.items
                    ],
                )
            days_response.append(
                DayResponse(
                    id=day.id,
                    day_of_week=day.day_of_week,
                    date=str(day.date),
                    occasion=day.occasion,
                    outfit=outfit_response,
                    weather_forecast=json.loads(day.weather_forecast)
                    if day.weather_forecast
                    else None,
                )
            )
        response.append(
            WeeklyPlanResponse(
                id=plan.id,
                name=plan.name,
                start_date=str(plan.start_date),
                end_date=str(plan.end_date),
                days=days_response,
            )
        )
    return response


@router.get("/{plan_id}", response_model=WeeklyPlanResponse)
def get_weekly_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    plan = (
        db.query(WeeklyPlan)
        .filter(WeeklyPlan.id == plan_id, WeeklyPlan.user_id == current_user.id)
        .options(
            joinedload(WeeklyPlan.daily_outfits)
            .joinedload(WeeklyPlanDayOutfit.outfit)
            .joinedload(Outfit.items)
            .joinedload(WardrobeItem.category_obj)
        )
        .first()
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    days_response = []
    for day in plan.daily_outfits:
        outfit_response = None
        if day.outfit:
            outfit_response = DayOutfitResponse(
                id=day.outfit.id,
                name=day.outfit.name,
                items=[
                    OutfitItemResponse(
                        id=item.id,
                        image_url=item.image_url,
                        category=item.category_obj.name,
                        name=item.name,
                        brand=item.brand,
                        material=item.material,
                        style=item.style,
                        dominant_color_name=item.dominant_color_name,
                    )
                    for item in day.outfit.items
                ],
            )
        days_response.append(
            DayResponse(
                id=day.id,
                day_of_week=day.day_of_week,
                date=str(day.date),
                occasion=day.occasion,
                outfit=outfit_response,
                weather_forecast=json.loads(day.weather_forecast)
                if day.weather_forecast
                else None,
            )
        )

    return WeeklyPlanResponse(
        id=plan.id,
        name=plan.name,
        start_date=str(plan.start_date),
        end_date=str(plan.end_date),
        days=days_response,
    )


@router.put("/{plan_id}", response_model=WeeklyPlanResponse)
def update_weekly_plan(
    plan_id: int,
    plan_data: WeeklyPlanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_plan = (
        db.query(WeeklyPlan)
        .filter(WeeklyPlan.id == plan_id, WeeklyPlan.user_id == current_user.id)
        .first()
    )
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    db_plan.name = plan_data.name
    db_plan.start_date = plan_data.start_date
    db_plan.end_date = plan_data.end_date

    # Clear existing days and add new ones
    db.query(WeeklyPlanDayOutfit).filter(
        WeeklyPlanDayOutfit.weekly_plan_id == plan_id
    ).delete()

    days = []
    for day_data in plan_data.days:
        db_day = WeeklyPlanDayOutfit(
            weekly_plan_id=db_plan.id,
            day_of_week=day_data["day_of_week"],
            date=day_data["date"],
            occasion=day_data["occasion"],
            outfit_id=day_data.get("outfit_id"),
            weather_forecast=json.dumps(day_data.get("weather_forecast")),
        )
        db.add(db_day)
        days.append(db_day)

    db.commit()
    db.refresh(db_plan)
    db.refresh(db_plan)

    # Construct the full response with nested outfit details
    days_response = []
    for day in db_plan.daily_outfits:
        outfit_response = None
        if day.outfit:
            outfit_response = DayOutfitResponse(
                id=day.outfit.id,
                name=day.outfit.name,
                items=[
                    OutfitItemResponse(
                        id=item.id,
                        image_url=item.image_url,
                        category=item.category_obj.name,
                        name=item.name,
                        brand=item.brand,
                        material=item.material,
                        style=item.style,
                        dominant_color_name=item.dominant_color_name,
                    )
                    for item in day.outfit.items
                ],
            )
        days_response.append(
            DayResponse(
                id=day.id,
                day_of_week=day.day_of_week,
                date=str(day.date),
                occasion=day.occasion,
                outfit=outfit_response,
                weather_forecast=json.loads(day.weather_forecast)
                if day.weather_forecast
                else None,
            )
        )

    return WeeklyPlanResponse(
        id=db_plan.id,
        name=db_plan.name,
        start_date=str(db_plan.start_date),
        end_date=str(db_plan.end_date),
        days=days_response,
    )

@router.delete("/{plan_id}")
def delete_weekly_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    plan = db.query(WeeklyPlan).filter(WeeklyPlan.id == plan_id, WeeklyPlan.user_id == current_user.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    db.delete(plan)
    db.commit()
    return {"message": "Plan deleted successfully"}

class WeeklyPlanRequest(BaseModel):
    location: str
    weekly_plan: Dict[str, Dict[str, str]]
    wardrobe_items: List[Dict[str, Any]]
    creativity: float = 0.5


@router.post("/recommendations")
def plan_weekly_outfits_route(request: WeeklyPlanRequest):
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    if not api_key:
        raise HTTPException(500, "Weather API key not configured.")

    weather_service = WeatherService(api_key)
    recommender = SmartOutfitRecommender(weather_service)
    recommender.load_wardrobe(request.wardrobe_items)

    # Instead of get_daily_forecast(lat, lon), call:
    daily_forecasts = weather_service.get_daily_forecast(request.location, None)

    # Build a forecast dict for quick lookup
    forecast_map = {d["date"]: d for d in daily_forecasts}

    # Inject weather_override into weekly_plan items if missing
    for date_str, plan in request.weekly_plan.items():
        if "weather_override" not in plan:
            plan["weather_override"] = forecast_map.get(date_str)

    response_data = {"recommendations": {}, "weather": {}}
    for date_str, plan_info in request.weekly_plan.items():
        weather_override = plan_info.get("weather_override")
        if weather_override:
            weather = WeatherData(
                temperature=(weather_override["temp_min"] + weather_override["temp_max"]) / 2,
                feels_like=(weather_override["temp_min"] + weather_override["temp_max"]) / 2,
                humidity=0,
                pressure=0,
                visibility=0,
                wind_speed=0,
                weather_condition=weather_override["weather"],
                description=weather_override["description"],
                cloud_coverage=0,
                sunrise=0,
                sunset=0,
            )
            response_data["weather"][date_str] = weather_override
        else:
            weather = None

        if weather:
            outfits = recommender.generate_outfit_combinations(
                weather, plan_info['occasion'], max_combinations=1, creativity=request.creativity
            )
            response_data["recommendations"][date_str] = [
                {
                    "score": outfit.overall_score(),
                    "items": [
                        {
                            "id": item.id,
                            "name": item.original_name,
                            "category": item.category,
                            "material": item.material,
                            "style": item.style,
                            "dominant_color_name": item.dominant_color,
                            "image_url": f"http://127.0.0.1:8000/uploads/{item.filename}",
                        }
                        for item in outfit.items
                    ],
                }
                for outfit in outfits
            ]
        else:
            response_data["recommendations"][date_str] = []

    return response_data
