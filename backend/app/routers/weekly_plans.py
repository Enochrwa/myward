from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict
from datetime import datetime, date
from sqlalchemy.orm import Session, joinedload

from .. import model as models
from .. import tables as schemas
from ..security import get_current_user # get_current_user returns schemas.User
from ..db.database import get_db

router = APIRouter(
    prefix="/weekly-plans",
    tags=["Weekly Plans"],
    responses={404: {"description": "Not found"}},
)


def transform_plan_to_response(db_plan: models.WeeklyPlan) -> schemas.WeeklyPlan:
    daily_outfits_dict = {do.day_of_week: do.outfit_id for do in db_plan.daily_outfits}
    return schemas.WeeklyPlan(
        id=db_plan.id,
        user_id=db_plan.user_id,
        name=db_plan.name,
        start_date=db_plan.start_date,
        end_date=db_plan.end_date,
        daily_outfits=daily_outfits_dict,
        created_at=db_plan.created_at,
        updated_at=db_plan.updated_at
    )


@router.post("/", response_model=schemas.WeeklyPlan, status_code=status.HTTP_201_CREATED)
async def create_weekly_plan(
    plan: schemas.WeeklyPlanCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_plan = models.WeeklyPlan(
        name=plan.name,
        start_date=plan.start_date,
        end_date=plan.end_date,
        user_id=current_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    # Must add and commit db_plan first to get its ID for WeeklyPlanDayOutfit entries
    db.add(db_plan)
    db.commit()
    # db.refresh(db_plan) # Refresh to get ID, though commit usually handles this for auto-increment.

    day_outfit_entries = []
    if plan.daily_outfits:
        for day, outfit_id in plan.daily_outfits.items():
            if outfit_id:
                outfit = db.query(models.Outfit).filter(models.Outfit.id == outfit_id, models.Outfit.user_id == current_user.id).first()
                if not outfit:
                    # Rollback: Delete the plan created if any outfit is invalid
                    db.delete(db_plan)
                    # Also delete any day_outfit_entries already added if this loop was partially successful
                    # For simplicity, this example deletes the plan and raises. Proper transaction management would be better.
                    db.commit()
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Outfit with ID {outfit_id} for {day} not found or does not belong to user.")

            day_outfit_entry = models.WeeklyPlanDayOutfit(
                weekly_plan_id=db_plan.id, # Use the ID from the committed plan
                day_of_week=day,
                outfit_id=outfit_id
            )
            day_outfit_entries.append(day_outfit_entry)

        db.add_all(day_outfit_entries)
        db.commit()

    db.refresh(db_plan) # Refresh to load relationships like daily_outfits
    return transform_plan_to_response(db_plan)


@router.get("/", response_model=List[schemas.WeeklyPlan])
async def read_weekly_plans(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    # Use joinedload to efficiently fetch related daily_outfits
    db_plans = db.query(models.WeeklyPlan).filter(models.WeeklyPlan.user_id == current_user.id)        .options(joinedload(models.WeeklyPlan.daily_outfits))        .order_by(models.WeeklyPlan.start_date.desc())        .offset(skip).limit(limit).all()

    return [transform_plan_to_response(plan) for plan in db_plans]

@router.get("/{plan_id}", response_model=schemas.WeeklyPlan)
async def read_weekly_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_plan = db.query(models.WeeklyPlan).filter(models.WeeklyPlan.id == plan_id, models.WeeklyPlan.user_id == current_user.id)        .options(joinedload(models.WeeklyPlan.daily_outfits))        .first()
    if db_plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weekly plan not found")

    return transform_plan_to_response(db_plan)


@router.put("/{plan_id}", response_model=schemas.WeeklyPlan)
async def update_weekly_plan(
    plan_id: int,
    plan_update: schemas.WeeklyPlanUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_plan = db.query(models.WeeklyPlan).filter(models.WeeklyPlan.id == plan_id, models.WeeklyPlan.user_id == current_user.id)        .options(joinedload(models.WeeklyPlan.daily_outfits))        .first()

    if db_plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weekly plan not found")

    update_data = plan_update.model_dump(exclude_unset=True)

    if "daily_outfits" in update_data:
        new_daily_outfits_dict = update_data.pop("daily_outfits")

        # Simple approach: Delete existing and add new ones
        # More sophisticated: Compare and update, add, delete individual entries
        for existing_day_outfit in db_plan.daily_outfits: # db_plan.daily_outfits is a list of WeeklyPlanDayOutfit objects
            db.delete(existing_day_outfit)
        # db.commit() # Commit deletions or do it once at the end

        if new_daily_outfits_dict: # If new daily_outfits are provided
            new_day_entries = []
            for day, outfit_id in new_daily_outfits_dict.items():
                if outfit_id:
                    outfit = db.query(models.Outfit).filter(models.Outfit.id == outfit_id, models.Outfit.user_id == current_user.id).first()
                    if not outfit:
                        # Consider rollback strategy for atomicity if any outfit is invalid
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Outfit with ID {outfit_id} for {day} not found or does not belong to user.")
                new_day_entries.append(models.WeeklyPlanDayOutfit(weekly_plan_id=db_plan.id, day_of_week=day, outfit_id=outfit_id))
            db.add_all(new_day_entries)

    for key, value in update_data.items():
        setattr(db_plan, key, value)

    db_plan.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_plan) # Refresh to get the updated state, including new/modified daily_outfits

    # Re-query to ensure all relationships are correctly loaded for the response after modifications
    updated_db_plan = db.query(models.WeeklyPlan).filter(models.WeeklyPlan.id == plan_id)        .options(joinedload(models.WeeklyPlan.daily_outfits)).first()
    return transform_plan_to_response(updated_db_plan)

@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_weekly_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_plan = db.query(models.WeeklyPlan).filter(models.WeeklyPlan.id == plan_id, models.WeeklyPlan.user_id == current_user.id).first()

    if db_plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weekly plan not found")

    # Associated WeeklyPlanDayOutfit entries will be deleted due to cascade="all, delete-orphan"
    # set on the WeeklyPlan.daily_outfits relationship in models.py.

    db.delete(db_plan)
    db.commit()
    return
