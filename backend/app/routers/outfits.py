from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
import os # Added for file deletion
import logging # Added for logging
from sqlalchemy.orm import Session

from .. import tables as schemas, models
from ..security import get_current_user # get_current_user returns schemas.User
from ..db.database import get_db

router = APIRouter(
    prefix="/outfits",
    tags=["Outfits"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__) # Added logger

@router.post("/", response_model=schemas.Outfit, status_code=status.HTTP_201_CREATED)
async def create_outfit(
    outfit: schemas.OutfitCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_items = db.query(models.WardrobeItem).filter(
        models.WardrobeItem.id.in_(outfit.item_ids),
        models.WardrobeItem.user_id == current_user.id
    ).all()

    if len(db_items) != len(outfit.item_ids):
        # Identify missing or unauthorized items for a more specific error message if desired
        found_ids = {item.id for item in db_items}
        missing_ids = [item_id for item_id in outfit.item_ids if item_id not in found_ids]
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"One or more wardrobe items not found or do not belong to the user. Missing or unauthorized item IDs: {missing_ids}")


    db_outfit = models.Outfit(
        name=outfit.name,
        user_id=current_user.id,
        image_url=outfit.image_url,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    if outfit.tags: # Assuming model setter handles JSON conversion for tags
        db_outfit.tags = outfit.tags

    db_outfit.items.extend(db_items)

    db.add(db_outfit)
    db.commit()
    db.refresh(db_outfit)
    return db_outfit

@router.get("/", response_model=List[schemas.Outfit])
async def read_outfits(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    outfits = db.query(models.Outfit).filter(models.Outfit.user_id == current_user.id).offset(skip).limit(limit).all()
    return outfits

@router.get("/{outfit_id}", response_model=schemas.Outfit)
async def read_outfit(
    outfit_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_outfit = db.query(models.Outfit).filter(models.Outfit.id == outfit_id, models.Outfit.user_id == current_user.id).first()
    if db_outfit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outfit not found")
    return db_outfit

@router.put("/{outfit_id}", response_model=schemas.Outfit)
async def update_outfit(
    outfit_id: int,
    outfit_update: schemas.OutfitUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_outfit = db.query(models.Outfit).filter(models.Outfit.id == outfit_id, models.Outfit.user_id == current_user.id).first()

    if db_outfit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outfit not found")

    update_data = outfit_update.model_dump(exclude_unset=True)

    if "item_ids" in update_data:
        new_item_ids = update_data.pop("item_ids")
        if new_item_ids is not None: # Check if item_ids is actually provided for update
            db_items = db.query(models.WardrobeItem).filter(
                models.WardrobeItem.id.in_(new_item_ids),
                models.WardrobeItem.user_id == current_user.id
            ).all()
            if len(db_items) != len(new_item_ids):
                found_ids = {item.id for item in db_items}
                missing_ids = [item_id for item_id in new_item_ids if item_id not in found_ids]
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"One or more new wardrobe items not found or do not belong to the user for update. Missing or unauthorized item IDs: {missing_ids}")
            db_outfit.items = db_items
        else: # item_ids is explicitly set to null or not provided for update
            db_outfit.items = [] # Clear items if item_ids is None

    for key, value in update_data.items():
        setattr(db_outfit, key, value)

    db_outfit.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_outfit)
    return db_outfit

@router.delete("/{outfit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_outfit(
    outfit_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_outfit = db.query(models.Outfit).filter(models.Outfit.id == outfit_id, models.Outfit.user_id == current_user.id).first()

    if db_outfit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outfit not found")

    # Delete the image file if it exists
    if db_outfit.image_url:
        # Assuming image_url stores a relative path like /static/outfit_images/filename.ext
        # Adjust WARDROBE_IMAGES_DIR or define OUTFIT_IMAGES_DIR if paths differ structurally
        image_path_on_disk = db_outfit.image_url.lstrip("/") # Remove leading '/'
        if os.path.exists(image_path_on_disk):
            try:
                os.remove(image_path_on_disk)
            except FileNotFoundError:
                logger.warning(f"Outfit image file not found: {image_path_on_disk}")
            except Exception as e:
                logger.error(f"Error deleting outfit image file {image_path_on_disk}: {e}")
        else:
            logger.warning(f"Outfit image path not found, but listed in DB: {image_path_on_disk}")


    # Many-to-many relationships like outfit.items are typically handled by SQLAlchemy
    # and do not require manual deletion of association table entries if cascade is set correctly
    # or if the relationship is cleared (e.g., db_outfit.items = []) before deleting db_outfit.
    # However, direct delete of db_outfit should suffice.

    db.delete(db_outfit)
    db.commit()
    return
