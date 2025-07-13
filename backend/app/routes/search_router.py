from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from pydantic import BaseModel

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from ..security import get_current_user
from ..model import (
    User, ClothingCategory, WardrobeItem, Outfit,
  
)
from ..db.database import get_db

router = APIRouter(prefix="/search")



@router.get("/search/items")
def search_items(
    query: str,
    category: Optional[str] = None,
    color: Optional[str] = None,
    brand: Optional[str] = None,
    season: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    search_query = db.query(WardrobeItem).filter(WardrobeItem.user_id == current_user.id)
    
    # Full-text search on name, brand, notes
    if query:
        search_query = search_query.filter(
            or_(
                WardrobeItem.name.ilike(f"%{query}%"),
                WardrobeItem.brand.ilike(f"%{query}%"),
                WardrobeItem.notes.ilike(f"%{query}%"),
                WardrobeItem.color.ilike(f"%{query}%")
            )
        )
    
    # Apply filters
    if category:
        search_query = search_query.join(ClothingCategory).filter(
            ClothingCategory.name.ilike(f"%{category}%")
        )
    
    if color:
        search_query = search_query.filter(WardrobeItem.color.ilike(f"%{color}%"))
    
    if brand:
        search_query = search_query.filter(WardrobeItem.brand.ilike(f"%{brand}%"))
    
    if season:
        search_query = search_query.filter(WardrobeItem.season == season)
    
    items = search_query.offset(skip).limit(limit).all()
    return items

@router.get("/search/outfits")
def search_outfits(
    query: str,
    occasion: Optional[str] = None,
    season: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    search_query = db.query(Outfit).filter(Outfit.user_id == current_user.id)
    
    # Full-text search
    if query:
        search_query = search_query.filter(
            or_(
                Outfit.name.ilike(f"%{query}%"),
                Outfit.description.ilike(f"%{query}%"),
                Outfit.occasion_type.ilike(f"%{query}%")
            )
        )
    
    # Apply filters
    if occasion:
        search_query = search_query.filter(Outfit.occasion_type == occasion)
    
    if season:
        search_query = search_query.filter(Outfit.season == season)
    
    outfits = search_query.offset(skip).limit(limit).all()
    return outfits
