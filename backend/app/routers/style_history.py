from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
import logging # Added logging

from .. import tables as schemas
from .. import model as models
from ..security import get_current_user
from ..db.database import get_db
from ..services import user_style_profile_service # Import the new service

logger = logging.getLogger(__name__) # Added logger

router = APIRouter(
    prefix="/style-history",
    tags=["Style History"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.StyleHistory, status_code=status.HTTP_201_CREATED)
async def log_style_history_entry(
    entry: schemas.StyleHistoryCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    # Ensure date_worn is set, default to now if not provided by client
    # Pydantic model StyleHistoryCreate should have `date_worn: datetime`
    # If it can be optional, then default it here or in Pydantic model.
    # For this example, assume date_worn is required in StyleHistoryCreate.

    if entry.item_id:
        item = db.query(models.WardrobeItem).filter(models.WardrobeItem.id == entry.item_id, models.WardrobeItem.user_id == current_user.id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Wardrobe Item with ID {entry.item_id} not found or does not belong to user.")
        item.last_worn = entry.date_worn
        item.times_worn = (item.times_worn or 0) + 1
        item.updated_at = datetime.utcnow()

    if entry.outfit_id:
        outfit = db.query(models.Outfit).options(joinedload(models.Outfit.items)).filter(models.Outfit.id == entry.outfit_id, models.Outfit.user_id == current_user.id).first()
        if not outfit:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Outfit with ID {entry.outfit_id} not found or does not belong to user.")
        # Update last_worn and times_worn for all items in the outfit
        for item_in_outfit in outfit.items:
            # Ensure this item also belongs to the current user if there's any doubt, though relationship should ensure this.
            item_in_outfit.last_worn = entry.date_worn
            item_in_outfit.times_worn = (item_in_outfit.times_worn or 0) + 1
            item_in_outfit.updated_at = datetime.utcnow()


    db_entry_data = entry.model_dump()

    db_entry = models.StyleHistory(
        **db_entry_data,
        user_id=current_user.id
    )

    db.add(db_entry)
    
    try:
        db.commit()
        db.refresh(db_entry)
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving StyleHistory entry for user {current_user.id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not save style history.")

    # After successfully logging the history, update the style profile
    if db_entry.outfit_id: # Only update if it's an outfit history
        try:
            user_style_profile_service.update_style_profile_from_outfit_history(
                db=db,
                user_id=current_user.id,
                outfit_id=db_entry.outfit_id,
                style_history_entry=db_entry 
            )
            db.commit() # Commit UserStyleProfile changes
        except Exception as e:
            db.rollback() # Rollback UserStyleProfile changes only
            logger.error(f"Error updating style profile from outfit history for user {current_user.id}, outfit {db_entry.outfit_id}: {e}")
            # Do not raise HTTPException here, as the primary operation (logging history) was successful.
            # This failure is secondary.

    return db_entry


@router.get("/", response_model=List[schemas.StyleHistory])
async def read_style_history_entries(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    entries = db.query(models.StyleHistory).filter(models.StyleHistory.user_id == current_user.id).order_by(models.StyleHistory.date_worn.desc()).offset(skip).limit(limit).all()
    return entries

@router.get("/{entry_id}", response_model=schemas.StyleHistory)
async def read_style_history_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_entry = db.query(models.StyleHistory).filter(models.StyleHistory.id == entry_id, models.StyleHistory.user_id == current_user.id).first()
    if db_entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Style history entry not found")
    return db_entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_style_history_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_entry = db.query(models.StyleHistory).filter(models.StyleHistory.id == entry_id, models.StyleHistory.user_id == current_user.id).first()

    if db_entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Style history entry not found")

    # Decrement times_worn if applicable
    if db_entry.item_id:
        item = db.query(models.WardrobeItem).filter(models.WardrobeItem.id == db_entry.item_id, models.WardrobeItem.user_id == current_user.id).first()
        if item and item.times_worn and item.times_worn > 0:
             item.times_worn -= 1
             item.updated_at = datetime.utcnow()
    elif db_entry.outfit_id:
        outfit = db.query(models.Outfit).options(joinedload(models.Outfit.items)).filter(models.Outfit.id == db_entry.outfit_id, models.Outfit.user_id == current_user.id).first()
        if outfit:
            for item_in_outfit in outfit.items:
                 if item_in_outfit.times_worn and item_in_outfit.times_worn > 0:
                    item_in_outfit.times_worn -=1
                    item_in_outfit.updated_at = datetime.utcnow()

    db.delete(db_entry)
    db.commit()
    return
