"""
Enhanced Search API Router for Digital Wardrobe System

This module provides intelligent search functionality for finding matching clothing items
with advanced filtering, compatibility scoring, and personalized recommendations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

from .. import tables as schemas
from .. import model as models
from ..security import get_current_user
from ..db.database import get_db
from ..services.intelligent_matching import IntelligentMatchingAlgorithm
from ..services.ml_personalized_recommendations import PersonalizedRecommendationModel

router = APIRouter(
    prefix="/search",
    tags=["Enhanced Search"],
    responses={404: {"description": "Not found"}},
)

# Initialize services
intelligent_matcher = IntelligentMatchingAlgorithm()
ml_recommender = PersonalizedRecommendationModel()

class SortBy(str, Enum):
    """Sorting options for search results"""
    COMPATIBILITY = "compatibility"
    NAME = "name"
    DATE_ADDED = "date_added"
    PRICE = "price"
    CATEGORY = "category"

class SearchFilters(BaseModel):
    """Search filters for wardrobe items"""
    colors: Optional[List[str]] = Field(None, description="Filter by colors (hex codes)")
    styles: Optional[List[str]] = Field(None, description="Filter by styles")
    categories: Optional[List[str]] = Field(None, description="Filter by categories")
    occasions: Optional[List[str]] = Field(None, description="Filter by occasions")
    price_min: Optional[float] = Field(None, description="Minimum price")
    price_max: Optional[float] = Field(None, description="Maximum price")
    brands: Optional[List[str]] = Field(None, description="Filter by brands")
    seasons: Optional[List[str]] = Field(None, description="Filter by seasons")

class MatchingRequest(BaseModel):
    """Request for finding matching items"""
    target_item_id: str = Field(..., description="ID of the item to find matches for")
    occasion: Optional[str] = Field(None, description="Occasion context")
    filters: Optional[SearchFilters] = Field(None, description="Additional filters")
    max_results: int = Field(5, description="Maximum number of results", ge=1, le=20)
    include_user_preferences: bool = Field(True, description="Include user preferences in matching")

class SearchRequest(BaseModel):
    """Request for general search"""
    query: Optional[str] = Field(None, description="Text search query")
    filters: Optional[SearchFilters] = Field(None, description="Search filters")
    sort_by: SortBy = Field(SortBy.NAME, description="Sort results by")
    sort_desc: bool = Field(False, description="Sort in descending order")
    page: int = Field(1, description="Page number", ge=1)
    page_size: int = Field(10, description="Items per page", ge=1, le=50)

class CompatibilityRequest(BaseModel):
    """Request for calculating compatibility between items"""
    item_ids: List[str] = Field(..., description="List of item IDs to check compatibility", min_items=2)
    occasion: Optional[str] = Field(None, description="Occasion context")

class SearchResult(BaseModel):
    """Search result with compatibility information"""
    item: schemas.WardrobeItem
    compatibility_score: Optional[float] = None
    match_reasons: Optional[List[str]] = None
    recommendation_score: Optional[float] = None

class SearchResponse(BaseModel):
    """Response for search requests"""
    results: List[SearchResult]
    total_count: int
    page: int
    page_size: int
    total_pages: int

class CompatibilityResponse(BaseModel):
    """Response for compatibility check"""
    overall_score: float
    style_cohesion_score: float
    color_harmony_score: float
    occasion_appropriateness: Optional[float] = None
    details: Dict[str, Any]

@router.post("/matching", response_model=List[SearchResult])
async def find_matching_items(
    request: MatchingRequest,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Find items that match well with a target item using intelligent matching algorithm
    """
    # Get the target item
    target_item = db.query(models.WardrobeItem).filter(
        models.WardrobeItem.id == request.target_item_id,
        models.WardrobeItem.user_id == current_user.id
    ).first()
    
    if not target_item:
        raise HTTPException(status_code=404, detail="Target item not found")
    
    # Get user's wardrobe items (excluding target item)
    query = db.query(models.WardrobeItem).filter(
        models.WardrobeItem.user_id == current_user.id,
        models.WardrobeItem.id != request.target_item_id
    )
    
    # Apply filters if provided
    if request.filters:
        query = _apply_filters(query, request.filters)
    
    wardrobe_items = query.all()
    
    # Convert to format expected by matching algorithm
    target_item_dict = _convert_item_to_dict(target_item)
    wardrobe_items_dict = [_convert_item_to_dict(item) for item in wardrobe_items]
    
    # Get user preferences if requested
    user_preferences = None
    if request.include_user_preferences:
        user_preferences = _get_user_preferences(db, current_user.id)
    
    # Find matches using intelligent algorithm
    matches = intelligent_matcher.find_matching_items(
        target_item=target_item_dict,
        wardrobe_items=wardrobe_items_dict,
        occasion=request.occasion,
        user_preferences=user_preferences,
        max_suggestions=request.max_results
    )
    
    # Convert back to response format
    results = []
    for match in matches:
        # Find the original item
        original_item = next((item for item in wardrobe_items if str(item.id) == match["id"]), None)
        if original_item:
            results.append(SearchResult(
                item=schemas.WardrobeItem.model_validate(original_item),
                compatibility_score=match["compatibility_score"],
                match_reasons=match["match_reasons"]
            ))
    
    return results

@router.post("/search", response_model=SearchResponse)
async def search_wardrobe(
    request: SearchRequest,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Search wardrobe items with advanced filtering and sorting
    """
    # Base query
    query = db.query(models.WardrobeItem).filter(
        models.WardrobeItem.user_id == current_user.id
    )
    
    # Apply text search if provided
    if request.query:
        search_term = f"%{request.query}%"
        query = query.filter(
            models.WardrobeItem.name.ilike(search_term) |
            models.WardrobeItem.description.ilike(search_term) |
            models.WardrobeItem.category.ilike(search_term) |
            models.WardrobeItem.brand.ilike(search_term)
        )
    
    # Apply filters
    if request.filters:
        query = _apply_filters(query, request.filters)
    
    # Get total count before pagination
    total_count = query.count()
    
    # Apply sorting
    if request.sort_by == SortBy.NAME:
        query = query.order_by(models.WardrobeItem.name.desc() if request.sort_desc else models.WardrobeItem.name)
    elif request.sort_by == SortBy.DATE_ADDED:
        query = query.order_by(models.WardrobeItem.created_at.desc() if request.sort_desc else models.WardrobeItem.created_at)
    elif request.sort_by == SortBy.PRICE:
        query = query.order_by(models.WardrobeItem.price.desc() if request.sort_desc else models.WardrobeItem.price)
    elif request.sort_by == SortBy.CATEGORY:
        query = query.order_by(models.WardrobeItem.category.desc() if request.sort_desc else models.WardrobeItem.category)
    
    # Apply pagination
    offset = (request.page - 1) * request.page_size
    items = query.offset(offset).limit(request.page_size).all()
    
    # Convert to response format
    results = [
        SearchResult(item=schemas.WardrobeItem.model_validate(item))
        for item in items
    ]
    
    total_pages = (total_count + request.page_size - 1) // request.page_size
    
    return SearchResponse(
        results=results,
        total_count=total_count,
        page=request.page,
        page_size=request.page_size,
        total_pages=total_pages
    )

@router.post("/compatibility", response_model=CompatibilityResponse)
async def check_compatibility(
    request: CompatibilityRequest,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Check compatibility between multiple items
    """
    # Get the items
    items = db.query(models.WardrobeItem).filter(
        models.WardrobeItem.id.in_(request.item_ids),
        models.WardrobeItem.user_id == current_user.id
    ).all()
    
    if len(items) != len(request.item_ids):
        raise HTTPException(status_code=404, detail="One or more items not found")
    
    # Convert to format expected by matching algorithm
    items_dict = [_convert_item_to_dict(item) for item in items]
    
    # Calculate compatibility using the outfit matching service
    from ..services.outfit_matching_service import OutfitMatchingService
    outfit_matcher = OutfitMatchingService()
    
    compatibility_result = outfit_matcher.calculate_compatibility_score(items_dict)
    
    # Calculate occasion appropriateness if occasion provided
    occasion_score = None
    if request.occasion:
        from ..services.intelligent_matching import OccasionMatcher
        occasion_matcher = OccasionMatcher()
        
        occasion_scores = []
        for item in items_dict:
            style = item.get("style", "casual")
            score = occasion_matcher.calculate_occasion_score(style, request.occasion)
            occasion_scores.append(score)
        
        occasion_score = sum(occasion_scores) / len(occasion_scores) if occasion_scores else 0.0
    
    return CompatibilityResponse(
        overall_score=compatibility_result["score"],
        style_cohesion_score=compatibility_result["style_cohesion_score"],
        color_harmony_score=compatibility_result["color_harmony_score"],
        occasion_appropriateness=occasion_score,
        details={
            "message": compatibility_result["message"],
            "item_count": len(items),
            "occasion": request.occasion
        }
    )

@router.get("/suggestions")
async def get_search_suggestions(
    query: str = Query(..., description="Search query for suggestions"),
    limit: int = Query(10, description="Maximum number of suggestions", ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Get search suggestions and autocomplete for wardrobe items
    """
    search_term = f"%{query}%"
    
    # Get suggestions from different fields
    suggestions = set()
    
    # Item names
    names = db.query(models.WardrobeItem.name).filter(
        models.WardrobeItem.user_id == current_user.id,
        models.WardrobeItem.name.ilike(search_term)
    ).limit(limit).all()
    suggestions.update([name[0] for name in names])
    
    # Categories
    categories = db.query(models.WardrobeItem.category).filter(
        models.WardrobeItem.user_id == current_user.id,
        models.WardrobeItem.category.ilike(search_term)
    ).distinct().limit(limit).all()
    suggestions.update([cat[0] for cat in categories if cat[0]])
    
    # Brands
    brands = db.query(models.WardrobeItem.brand).filter(
        models.WardrobeItem.user_id == current_user.id,
        models.WardrobeItem.brand.ilike(search_term)
    ).distinct().limit(limit).all()
    suggestions.update([brand[0] for brand in brands if brand[0]])
    
    # Convert to list and limit
    suggestion_list = list(suggestions)[:limit]
    
    return {"suggestions": suggestion_list}

@router.get("/filters")
async def get_available_filters(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Get available filter options based on user's wardrobe
    """
    # Get unique values for filter options
    categories = db.query(models.WardrobeItem.category).filter(
        models.WardrobeItem.user_id == current_user.id,
        models.WardrobeItem.category.isnot(None)
    ).distinct().all()
    
    brands = db.query(models.WardrobeItem.brand).filter(
        models.WardrobeItem.user_id == current_user.id,
        models.WardrobeItem.brand.isnot(None)
    ).distinct().all()
    
    seasons = db.query(models.WardrobeItem.season).filter(
        models.WardrobeItem.user_id == current_user.id,
        models.WardrobeItem.season.isnot(None)
    ).distinct().all()
    
    # Get price range
    price_stats = db.query(
        models.WardrobeItem.price
    ).filter(
        models.WardrobeItem.user_id == current_user.id,
        models.WardrobeItem.price.isnot(None)
    ).all()
    
    prices = [p[0] for p in price_stats if p[0] is not None]
    price_range = {
        "min": min(prices) if prices else 0,
        "max": max(prices) if prices else 1000
    }
    
    return {
        "categories": [cat[0] for cat in categories],
        "brands": [brand[0] for brand in brands],
        "seasons": [season[0] for season in seasons],
        "price_range": price_range,
        "styles": ["casual", "formal", "business", "sporty", "elegant", "trendy", "classic"],
        "occasions": ["work", "casual", "formal", "party", "date", "wedding", "church", "home"]
    }

def _apply_filters(query, filters: SearchFilters):
    """Apply search filters to the query"""
    if filters.colors:
        # This would need to be adapted based on how colors are stored
        # For now, assuming colors are stored in a searchable format
        color_conditions = []
        for color in filters.colors:
            color_conditions.append(models.WardrobeItem.dominant_color_hex == color)
        if color_conditions:
            query = query.filter(models.WardrobeItem.dominant_color_hex.in_(filters.colors))
    
    if filters.styles:
        # Assuming style is stored in a style_features JSON field or similar
        pass  # Implementation depends on how styles are stored
    
    if filters.categories:
        query = query.filter(models.WardrobeItem.category.in_(filters.categories))
    
    if filters.price_min is not None:
        query = query.filter(models.WardrobeItem.price >= filters.price_min)
    
    if filters.price_max is not None:
        query = query.filter(models.WardrobeItem.price <= filters.price_max)
    
    if filters.brands:
        query = query.filter(models.WardrobeItem.brand.in_(filters.brands))
    
    if filters.seasons:
        query = query.filter(models.WardrobeItem.season.in_(filters.seasons))
    
    return query

def _convert_item_to_dict(item: models.WardrobeItem) -> Dict[str, Any]:
    """Convert SQLAlchemy model to dictionary for matching algorithm"""
    return {
        "id": str(item.id),
        "name": item.name,
        "category": item.category or "unknown",
        "style": getattr(item, "style", "casual"),  # Default style if not present
        "colors": [item.dominant_color_hex] if item.dominant_color_hex else ["#808080"],
        "price": item.price or 0,
        "brand": item.brand or "unknown"
    }

def _get_user_preferences(db: Session, user_id: int) -> Dict[str, Any]:
    """Get user preferences for personalized matching"""
    # This would integrate with the user profile service
    # For now, return basic preferences
    return {
        "preferred_colors": [],
        "preferred_styles": [],
        "avoided_colors": []
    }

