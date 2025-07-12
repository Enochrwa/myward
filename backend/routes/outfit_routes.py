"""
Outfit management routes for Digital Wardrobe System
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from pydantic import BaseModel

from models.database_models import (
    User, OutfitResponse, OutfitCreate, OutfitUpdate
)
from services.auth_service import get_current_active_user
from services.outfit_matching_service import outfit_matching_service

router = APIRouter()

# Request/Response models
class OutfitSuggestionRequest(BaseModel):
    base_item_id: str
    occasion_id: Optional[int] = None
    max_suggestions: int = 5

class OutfitSuggestionResponse(BaseModel):
    base_item: dict
    suggestions: List[dict]
    total_suggestions: int

class CreateOutfitFromSuggestionRequest(BaseModel):
    item_ids: List[str]
    outfit_name: str
    occasion_id: Optional[int] = None

@router.post("/suggestions", response_model=OutfitSuggestionResponse)
async def get_outfit_suggestions(
    request: OutfitSuggestionRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Get intelligent outfit suggestions based on a base clothing item"""
    try:
        suggestions = outfit_matching_service.get_outfit_suggestions(
            user_id=current_user.id,
            base_item_id=request.base_item_id,
            occasion_id=request.occasion_id,
            max_suggestions=request.max_suggestions
        )
        
        return OutfitSuggestionResponse(**suggestions)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate outfit suggestions"
        )

@router.post("/create-from-suggestion")
async def create_outfit_from_suggestion(
    request: CreateOutfitFromSuggestionRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Create a saved outfit from an AI suggestion"""
    try:
        outfit_id = outfit_matching_service.create_outfit_from_suggestion(
            user_id=current_user.id,
            item_ids=request.item_ids,
            outfit_name=request.outfit_name,
            occasion_id=request.occasion_id
        )
        
        if not outfit_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create outfit"
            )
        
        return {
            "message": "Outfit created successfully",
            "outfit_id": outfit_id,
            "outfit_name": request.outfit_name
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create outfit"
        )

@router.get("/", response_model=List[OutfitResponse])
async def get_outfits(
    limit: int = 50,
    offset: int = 0,
    occasion_id: Optional[int] = None,
    season: Optional[str] = None,
    is_favorite: Optional[bool] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Get user's outfits with optional filters"""
    # TODO: Implement outfit retrieval from database
    return []

@router.post("/", response_model=OutfitResponse)
async def create_outfit(
    outfit_data: OutfitCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new outfit manually"""
    # TODO: Implement manual outfit creation
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Manual outfit creation will be implemented in Phase 6"
    )

@router.get("/{outfit_id}", response_model=OutfitResponse)
async def get_outfit(
    outfit_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get specific outfit"""
    # TODO: Implement outfit retrieval
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Outfit retrieval will be implemented in Phase 6"
    )

@router.put("/{outfit_id}", response_model=OutfitResponse)
async def update_outfit(
    outfit_id: str,
    outfit_update: OutfitUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update outfit"""
    # TODO: Implement outfit update
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Outfit update will be implemented in Phase 6"
    )

@router.delete("/{outfit_id}")
async def delete_outfit(
    outfit_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete outfit"""
    # TODO: Implement outfit deletion
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Outfit deletion will be implemented in Phase 6"
    )

