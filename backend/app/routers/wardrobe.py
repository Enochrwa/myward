"""
Wardrobe management routes for Digital Wardrobe System
"""
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from typing import List, Optional
from pydantic import BaseModel

from app.models.database_models import (
    User, ClothingItemResponse, ClothingItemUpdate,
    ClothingType, Color, Brand, Pattern, Occasion
)
from app.services.auth_service import get_current_active_user
from app.services.database_service import db_service

router = APIRouter()

# Response models
class WardrobeStatsResponse(BaseModel):
    total_items: int
    favorite_items: int
    available_items: int
    categories_breakdown: dict
    colors_breakdown: dict
    brands_breakdown: dict

class LookupDataResponse(BaseModel):
    clothing_types: List[ClothingType]
    colors: List[Color]
    brands: List[Brand]
    patterns: List[Pattern]
    occasions: List[Occasion]

@router.get("/items", response_model=List[ClothingItemResponse])
async def get_wardrobe_items(
    limit: int = 100,
    offset: int = 0,
    category_id: Optional[int] = None,
    color_id: Optional[int] = None,
    brand_id: Optional[int] = None,
    is_favorite: Optional[bool] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Get user's wardrobe items with optional filters"""
    try:
        items = db_service.get_clothing_items_by_user(
            user_id=current_user.id,
            limit=limit,
            offset=offset
        )

        # Apply filters if provided
        if category_id is not None:
            items = [item for item in items if item.clothing_type_id == category_id]

        if color_id is not None:
            items = [item for item in items if item.primary_color_id == color_id or item.secondary_color_id == color_id]

        if brand_id is not None:
            items = [item for item in items if item.brand_id == brand_id]

        if is_favorite is not None:
            items = [item for item in items if item.is_favorite == is_favorite]

        return items

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve wardrobe items"
        )

@router.get("/items/{item_id}", response_model=ClothingItemResponse)
async def get_clothing_item(
    item_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get specific clothing item"""
    try:
        item = db_service.get_clothing_item_by_id(item_id)
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Clothing item not found"
            )

        # Check if item belongs to current user
        if item.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        return item

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve clothing item"
        )

@router.put("/items/{item_id}", response_model=ClothingItemResponse)
async def update_clothing_item(
    item_id: str,
    item_update: ClothingItemUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update clothing item"""
    try:
        # Check if item exists and belongs to user
        existing_item = db_service.get_clothing_item_by_id(item_id)
        if not existing_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Clothing item not found"
            )

        if existing_item.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        # Update item
        success = db_service.update_clothing_item(item_id, item_update)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update clothing item"
            )

        # Return updated item
        updated_item = db_service.get_clothing_item_by_id(item_id)
        return updated_item

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update clothing item"
        )

@router.delete("/items/{item_id}")
async def delete_clothing_item(
    item_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete clothing item"""
    try:
        # Check if item exists and belongs to user
        existing_item = db_service.get_clothing_item_by_id(item_id)
        if not existing_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Clothing item not found"
            )

        if existing_item.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        # Delete item
        success = db_service.delete_clothing_item(item_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete clothing item"
            )

        return {"message": "Clothing item deleted successfully", "item_id": item_id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete clothing item"
        )

@router.get("/stats", response_model=WardrobeStatsResponse)
async def get_wardrobe_stats(
    current_user: User = Depends(get_current_active_user)
):
    """Get wardrobe statistics"""
    try:
        items = db_service.get_clothing_items_by_user(current_user.id, limit=1000)

        total_items = len(items)
        favorite_items = len([item for item in items if item.is_favorite])
        available_items = len([item for item in items if item.is_available])

        # Categories breakdown
        categories_breakdown = {}
        for item in items:
            category_id = item.clothing_type_id
            categories_breakdown[category_id] = categories_breakdown.get(category_id, 0) + 1

        # Colors breakdown
        colors_breakdown = {}
        for item in items:
            color_id = item.primary_color_id
            colors_breakdown[color_id] = colors_breakdown.get(color_id, 0) + 1

        # Brands breakdown
        brands_breakdown = {}
        for item in items:
            if item.brand_id:
                brand_id = item.brand_id
                brands_breakdown[brand_id] = brands_breakdown.get(brand_id, 0) + 1

        return WardrobeStatsResponse(
            total_items=total_items,
            favorite_items=favorite_items,
            available_items=available_items,
            categories_breakdown=categories_breakdown,
            colors_breakdown=colors_breakdown,
            brands_breakdown=brands_breakdown
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve wardrobe statistics"
        )

@router.get("/lookup-data", response_model=LookupDataResponse)
async def get_lookup_data():
    """Get lookup data for dropdowns and filters"""
    try:
        clothing_types = db_service.get_clothing_types()
        colors = db_service.get_colors()
        brands = db_service.get_brands()
        patterns = db_service.get_patterns()
        occasions = db_service.get_occasions()

        return LookupDataResponse(
            clothing_types=clothing_types,
            colors=colors,
            brands=brands,
            patterns=patterns,
            occasions=occasions
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve lookup data"
        )
