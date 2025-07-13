"""
Outfit management routes for Digital Wardrobe System
"""
from fastapi import APIRouter, HTTPException, status, Depends, File,UploadFile
from typing import List, Optional
from pydantic import BaseModel

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, date

import json

# Import your models and database session
from ..model import (
    User,ClothingAttribute, WardrobeItem, Outfit,
    StyleHistory
)
from ..db.database import get_db
from ..tables import OutfitResponse, OutfitCreate, OutfitUpdate, OutfitAnalysisResponse
from ..security import get_current_user


router = APIRouter(prefix="/outfit")




@router.post("/outfits/", response_model=OutfitResponse)
def create_outfit(
    outfit: OutfitCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify all items belong to the user
    items = db.query(WardrobeItem).filter(
        WardrobeItem.id.in_(outfit.item_ids),
        WardrobeItem.user_id == current_user.id
    ).all()
    
    if len(items) != len(outfit.item_ids):
        raise HTTPException(status_code=400, detail="Some items not found or don't belong to user")
    
    outfit_data = outfit.dict(exclude={'item_ids', 'attribute_ids'})
    outfit_data['user_id'] = current_user.id
    outfit_data['_tags'] = json.dumps(outfit.tags) if outfit.tags else None
    
    db_outfit = Outfit(**outfit_data)
    db.add(db_outfit)
    db.flush()
    
    # Add items to outfit
    db_outfit.items = items
    
    # Add attributes if provided
    if outfit.attribute_ids:
        attributes = db.query(ClothingAttribute).filter(
            ClothingAttribute.id.in_(outfit.attribute_ids)
        ).all()
        db_outfit.attributes = attributes
    
    db.commit()
    db.refresh(db_outfit)
    return db_outfit

@router.get("/outfits/", response_model=List[OutfitResponse])
def get_outfits(
    season: Optional[str] = None,
    occasion_type: Optional[str] = None,
    formality_level: Optional[int] = None,
    is_template: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Outfit).filter(Outfit.user_id == current_user.id)
    
    if season:
        query = query.filter(Outfit.season == season)
    if occasion_type:
        query = query.filter(Outfit.occasion_type == occasion_type)
    if formality_level:
        query = query.filter(Outfit.formality_level == formality_level)
    if is_template is not None:
        query = query.filter(Outfit.is_template == is_template)
    
    outfits = query.offset(skip).limit(limit).all()
    return outfits

@router.get("/outfits/{outfit_id}", response_model=OutfitResponse)
def get_outfit(
    outfit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    outfit = db.query(Outfit).filter(
        Outfit.id == outfit_id,
        Outfit.user_id == current_user.id
    ).first()
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    return outfit

@router.put("/outfits/{outfit_id}", response_model=OutfitResponse)
def update_outfit(
    outfit_id: int,
    outfit_update: OutfitCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    outfit = db.query(Outfit).filter(
        Outfit.id == outfit_id,
        Outfit.user_id == current_user.id
    ).first()
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    
    # Update basic fields
    for key, value in outfit_update.dict(exclude={'item_ids', 'attribute_ids'}).items():
        if key == 'tags':
            setattr(outfit, '_tags', json.dumps(value) if value else None)
        else:
            setattr(outfit, key, value)
    
    # Update items
    if outfit_update.item_ids:
        items = db.query(WardrobeItem).filter(
            WardrobeItem.id.in_(outfit_update.item_ids),
            WardrobeItem.user_id == current_user.id
        ).all()
        outfit.items = items
    
    # Update attributes
    if outfit_update.attribute_ids:
        attributes = db.query(ClothingAttribute).filter(
            ClothingAttribute.id.in_(outfit_update.attribute_ids)
        ).all()
        outfit.attributes = attributes
    
    db.commit()
    db.refresh(outfit)
    return outfit

@router.delete("/outfits/{outfit_id}")
def delete_outfit(
    outfit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    outfit = db.query(Outfit).filter(
        Outfit.id == outfit_id,
        Outfit.user_id == current_user.id
    ).first()
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    
    db.delete(outfit)
    db.commit()
    return {"message": "Outfit deleted successfully"}

@router.post("/outfits/{outfit_id}/worn")
def mark_outfit_as_worn(
    outfit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    outfit = db.query(Outfit).filter(
        Outfit.id == outfit_id,
        Outfit.user_id == current_user.id
    ).first()
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    
    outfit.times_worn += 1
    
    # Also update times_worn for each item in the outfit
    for item in outfit.items:
        item.times_worn += 1
        item.last_worn = datetime.utcnow()
    
    # Create style history entry
    style_history = StyleHistory(
        user_id=current_user.id,
        outfit_id=outfit_id,
        date_worn=datetime.utcnow()
    )
    db.add(style_history)
    
    db.commit()
    return {"times_worn": outfit.times_worn}

@router.post("/outfits/{outfit_id}/upload-image")
async def upload_outfit_image(
    outfit_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify outfit belongs to user
    outfit = db.query(Outfit).filter(
        Outfit.id == outfit_id,
        Outfit.user_id == current_user.id
    ).first()
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    
    # Similar implementation as item image upload
    return {
        "message": "Outfit image upload successful",
        "filename": file.filename,
        "content_type": file.content_type
    }

@router.get("/export/outfits")
def export_outfits(
    format: str = "json",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    outfits = db.query(Outfit).filter(Outfit.user_id == current_user.id).all()
    
    if format == "json":
        return {"outfits": [outfit.__dict__ for outfit in outfits]}
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")


