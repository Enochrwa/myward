from fastapi import APIRouter, Depends, HTTPException, status,File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional, Any,Dict
from ..model import WardrobeItem, User
import json
from ..tables import WardrobeItemCreate, WardrobeItemUpdate,ClothingCategoryCreate,WardrobeItemResponse,ClothingAttributeCreate, ClothingAttributeResponse,ClothingCategoryResponse, WardrobeItem as WardrobeItemSchema
from ..db.database import get_db  # your session generator
from datetime import datetime, date

from ..model import (
    User, ClothingCategory, ClothingAttribute, WardrobeItem, Outfit,
    WeatherPreference, WeeklyPlan, WeeklyPlanDayOutfit, Occasion,
    StyleHistory, UserProfile, UserStyleProfile, OutfitRecommendation,
    ColorAnalysis, ItemClassification, Feedback, WeatherData
)
from ..db.database import get_db
from ..security import get_current_user

router = APIRouter(prefix="/wardrobe", tags=["Wardrobe"])



# CREATE
@router.post("/", response_model=WardrobeItemSchema)
def create_wardrobe_item(item: WardrobeItemCreate, db: Session = Depends(get_db), user_id: int = 1):
    db_item = WardrobeItem(user_id=user_id, **item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# READ ALL
@router.get("/", response_model=List[WardrobeItemSchema])
def get_all_items(db: Session = Depends(get_db), user_id: int = 1):
    return db.query(WardrobeItem).filter(WardrobeItem.user_id == user_id).all()

# READ ONE
@router.get("/{item_id}", response_model=WardrobeItemSchema)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(WardrobeItem).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# UPDATE
@router.put("/{item_id}", response_model=WardrobeItemSchema)
def update_item(item_id: int, update_data: WardrobeItemUpdate, db: Session = Depends(get_db)):
    item = db.query(WardrobeItem).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item

# DELETE
@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(WardrobeItem).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"detail": "Item deleted successfully"}



@router.post("/wardrobe-items/{item_id}/classifications")
def create_item_classification(
    item_id: int,
    classification_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify item belongs to user
    item = db.query(WardrobeItem).filter(
        WardrobeItem.id == item_id,
        WardrobeItem.user_id == current_user.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    classification_data['wardrobe_item_id'] = item_id
    classification = ItemClassification(**classification_data)
    db.add(classification)
    db.commit()
    db.refresh(classification)
    return classification


@router.post("/categories/", response_model=ClothingCategoryResponse)
def create_category(category: ClothingCategoryCreate, db: Session = Depends(get_db)):
    db_category = ClothingCategory(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/categories/", response_model=List[ClothingCategoryResponse])
def get_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = db.query(ClothingCategory).offset(skip).limit(limit).all()
    return categories

@router.get("/categories/{category_id}", response_model=ClothingCategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(ClothingCategory).filter(ClothingCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

# CLOTHING ATTRIBUTE ROUTES
@router.post("/attributes/", response_model=ClothingAttributeResponse)
def create_attribute(attribute: ClothingAttributeCreate, db: Session = Depends(get_db)):
    db_attribute = ClothingAttribute(**attribute.dict())
    db.add(db_attribute)
    db.commit()
    db.refresh(db_attribute)
    return db_attribute

@router.get("/attributes/", response_model=List[ClothingAttributeResponse])
def get_attributes(
    attribute_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(ClothingAttribute)
    if attribute_type:
        query = query.filter(ClothingAttribute.attribute_type == attribute_type)
    attributes = query.offset(skip).limit(limit).all()
    return attributes

# WARDROBE ITEM ROUTES
@router.post("/wardrobe-items/", response_model=WardrobeItemResponse)
def create_wardrobe_item(
    item: WardrobeItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item_data = item.dict()
    item_data['user_id'] = current_user.id
    item_data['tags'] = json.dumps(item.tags) if item.tags else None
    
    db_item = WardrobeItem(**item_data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/wardrobe-items/", response_model=List[WardrobeItemResponse])
def get_wardrobe_items(
    category_id: Optional[int] = None,
    season: Optional[str] = None,
    favorite: Optional[bool] = None,
    brand: Optional[str] = None,
    formality_level: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(WardrobeItem).filter(WardrobeItem.user_id == current_user.id)
    
    if category_id:
        query = query.filter(WardrobeItem.category_id == category_id)
    if season:
        query = query.filter(WardrobeItem.season == season)
    if favorite is not None:
        query = query.filter(WardrobeItem.favorite == favorite)
    if brand:
        query = query.filter(WardrobeItem.brand.ilike(f"%{brand}%"))
    if formality_level:
        query = query.filter(WardrobeItem.formality_level == formality_level)
    
    items = query.offset(skip).limit(limit).all()
    return items

@router.get("/wardrobe-items/{item_id}", response_model=WardrobeItemResponse)
def get_wardrobe_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(WardrobeItem).filter(
        WardrobeItem.id == item_id,
        WardrobeItem.user_id == current_user.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.put("/wardrobe-items/{item_id}", response_model=WardrobeItemResponse)
def update_wardrobe_item(
    item_id: int,
    item_update: WardrobeItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(WardrobeItem).filter(
        WardrobeItem.id == item_id,
        WardrobeItem.user_id == current_user.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    for key, value in item_update.dict(exclude_unset=True).items():
        if key == 'tags':
            setattr(item, '_tags', json.dumps(value) if value else None)
        else:
            setattr(item, key, value)
    
    db.commit()
    db.refresh(item)
    return item

@router.delete("/wardrobe-items/{item_id}")
def delete_wardrobe_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(WardrobeItem).filter(
        WardrobeItem.id == item_id,
        WardrobeItem.user_id == current_user.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(item)
    db.commit()
    return {"message": "Item deleted successfully"}

@router.post("/wardrobe-items/{item_id}/favorite")
def toggle_favorite(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(WardrobeItem).filter(
        WardrobeItem.id == item_id,
        WardrobeItem.user_id == current_user.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item.favorite = not item.favorite
    db.commit()
    return {"favorite": item.favorite}

@router.post("/wardrobe-items/{item_id}/worn")
def mark_as_worn(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(WardrobeItem).filter(
        WardrobeItem.id == item_id,
        WardrobeItem.user_id == current_user.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item.times_worn += 1
    item.last_worn = datetime.utcnow()
    db.commit()
    return {"times_worn": item.times_worn, "last_worn": item.last_worn}



@router.post("/wardrobe-items/{item_id}/upload-image")
async def upload_item_image(
    item_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify item belongs to user
    item = db.query(WardrobeItem).filter(
        WardrobeItem.id == item_id,
        WardrobeItem.user_id == current_user.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # In a real implementation, you'd:
    # 1. Validate file type and size
    # 2. Save to cloud storage (AWS S3, etc.)
    # 3. Generate thumbnails
    # 4. Run ML analysis (color, style, etc.)
    
    # For now, just return a placeholder
    return {
        "message": "Image upload successful",
        "filename": file.filename,
        "content_type": file.content_type
    }


@router.delete("/wardrobe-items/bulk-delete")
def bulk_delete_items(
    item_ids: List[int],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify all items belong to user and delete
    deleted_count = db.query(WardrobeItem).filter(
        WardrobeItem.id.in_(item_ids),
        WardrobeItem.user_id == current_user.id
    ).delete(synchronize_session=False)
    
    db.commit()
    return {"deleted_count": deleted_count}


@router.post("/wardrobe-items/{item_id}/color-analysis")
def create_color_analysis(
    item_id: int,
    analysis_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify item belongs to user
    item = db.query(WardrobeItem).filter(
        WardrobeItem.id == item_id,
        WardrobeItem.user_id == current_user.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    analysis_data['wardrobe_item_id'] = item_id
    color_analysis = ColorAnalysis(**analysis_data)
    db.add(color_analysis)
    db.commit()
    db.refresh(color_analysis)
    return color_analysis


@router.post("/wardrobe-items/bulk-update")
def bulk_update_items(
    item_ids: List[int],
    updates: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify all items belong to user
    items = db.query(WardrobeItem).filter(
        WardrobeItem.id.in_(item_ids),
        WardrobeItem.user_id == current_user.id
    ).all()
    
    if len(items) != len(item_ids):
        raise HTTPException(status_code=400, detail="Some items not found")
    
    # Apply updates
    for item in items:
        for key, value in updates.items():
            if hasattr(item, key):
                setattr(item, key, value)
    
    db.commit()
    return {"updated_count": len(items)}



@router.get("/export/wardrobe")
def export_wardrobe(
    format: str = "json",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    items = db.query(WardrobeItem).filter(WardrobeItem.user_id == current_user.id).all()
    
    if format == "json":
        return {"items": [item.__dict__ for item in items]}
    elif format == "csv":
        # In a real implementation, you'd generate CSV content
        return {"message": "CSV export not implemented yet"}
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")
