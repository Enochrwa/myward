from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, distinct
from typing import List, Dict

from .. import tables as schemas
from .. import model as models
from ..security import get_current_user # get_current_user returns schemas.User
from ..db.database import get_db

router = APIRouter(
    prefix="/statistics",
    tags=["Statistics"],
    responses={404: {"description": "Not found"}},
)

@router.get("/wardrobe-stats/", response_model=schemas.WardrobeStats)
async def get_wardrobe_statistics(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    user_id = current_user.id

    total_items = db.query(func.count(models.WardrobeItem.id)).filter(models.WardrobeItem.user_id == user_id).scalar()
    total_outfits = db.query(func.count(models.Outfit.id)).filter(models.Outfit.user_id == user_id).scalar()

    items_by_category_query = db.query(models.WardrobeItem.category, func.count(models.WardrobeItem.id).label("count")).filter(models.WardrobeItem.user_id == user_id).group_by(models.WardrobeItem.category).all()
    items_by_category = {cat if cat else "Uncategorized": count for cat, count in items_by_category_query}


    items_by_season_query = db.query(models.WardrobeItem.season, func.count(models.WardrobeItem.id).label("count")).filter(models.WardrobeItem.user_id == user_id, models.WardrobeItem.season != None, models.WardrobeItem.season != "").group_by(models.WardrobeItem.season).all()
    items_by_season = {season if season else "Unspecified": count for season, count in items_by_season_query}


    most_worn_items_db = db.query(models.WardrobeItem).filter(models.WardrobeItem.user_id == user_id, models.WardrobeItem.times_worn > 0).order_by(desc(models.WardrobeItem.times_worn)).limit(5).all()
    # For least worn, include items with times_worn = 0 or NULL
    least_worn_items_db = db.query(models.WardrobeItem).filter(models.WardrobeItem.user_id == user_id).order_by(func.coalesce(models.WardrobeItem.times_worn, 0)).limit(5).all()

    favorite_items_count = db.query(func.count(models.WardrobeItem.id)).filter(models.WardrobeItem.user_id == user_id, models.WardrobeItem.favorite == True).scalar()

    return schemas.WardrobeStats(
        total_items=total_items if total_items is not None else 0,
        total_outfits=total_outfits if total_outfits is not None else 0,
        items_by_category=items_by_category,
        items_by_season=items_by_season,
        most_worn_items=[schemas.WardrobeItem.model_validate(item) for item in most_worn_items_db],
        least_worn_items=[schemas.WardrobeItem.model_validate(item) for item in least_worn_items_db],
        favorite_items_count=favorite_items_count if favorite_items_count is not None else 0
    )

@router.get("/item-wear-frequency/", response_model=List[schemas.ItemWearFrequency])
async def get_item_wear_frequency(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    user_id = current_user.id
    # Query items and their wear counts, including those never worn (times_worn is 0 or NULL)
    items_with_wear_count = db.query(models.WardrobeItem)        .filter(models.WardrobeItem.user_id == user_id)        .order_by(desc(func.coalesce(models.WardrobeItem.times_worn, 0)))        .all()

    response = []
    for item in items_with_wear_count:
        response.append(schemas.ItemWearFrequency(
            item=schemas.WardrobeItem.model_validate(item),
            wear_count=item.times_worn if item.times_worn is not None else 0
        ))
    return response

@router.get("/category-usage/", response_model=List[schemas.CategoryUsage])
async def get_category_usage(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    user_id = current_user.id

    total_user_items_count = db.query(func.count(distinct(models.WardrobeItem.id)))        .filter(models.WardrobeItem.user_id == user_id).scalar()

    # Handle case where total_user_items_count might be 0 to avoid division by zero
    if not total_user_items_count or total_user_items_count == 0:
        # If user has no items, return empty list or handle as appropriate
        return []

    category_counts_query = db.query(
        models.WardrobeItem.category,
        func.count(models.WardrobeItem.id).label("item_count"),
        (func.count(models.WardrobeItem.id) * 100.0 / total_user_items_count).label("usage_percentage")
    ).filter(models.WardrobeItem.user_id == user_id)     .group_by(models.WardrobeItem.category)     .all()

    response = []
    for category_name, item_count, usage_percentage in category_counts_query:
        response.append(schemas.CategoryUsage(
            category=category_name if category_name else "Uncategorized",
            item_count=item_count,
            usage_percentage=round(usage_percentage, 2) if usage_percentage is not None else 0.0
        ))
    return response
