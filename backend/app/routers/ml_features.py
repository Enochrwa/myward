"""
API Endpoints for ML-Powered Wardrobe Features

This module provides FastAPI endpoints for clothing classification, color detection,
and outfit recommendations, integrating the new ML services.
"""

from fastapi import APIRouter, UploadFile,status, File, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Optional, Any
import logging
import asyncio # Ensure asyncio is imported

# Use async versions of services
from app.services.clothing_classifier import classify_clothing_image_async, get_clothing_classifier_async
from app.services.color_detector import detect_dominant_color_async,get_color_detector, extract_color_palette_async, get_color_detector_async
from app.services.outfit_recommendation_engine import get_outfit_recommendations, get_similar_items, get_recommendation_engine # These might need async versions too
from app.db.database import get_db
from app.model import WardrobeItem, Outfit, User, ItemClassification, ColorAnalysis, OutfitRecommendation # Assuming these are SQLAlchemy models
from app.security import get_current_user
from app.schemas.ml_features import (
    ClassificationResponse, ColorAnalysisResponse, ColorPaletteResponse,
    RecommendationRequest, OutfitResponse, SimilarItemResponse,
    WardrobeItemCreate, WardrobeItemResponse, MLProcessingStatus,
    TrainingStatusResponse, BatchProcessingRequest, BatchProcessingResponse
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ml",
    tags=["ML Features"],
    responses={404: {"description": "Not found"}}
)

@router.post("/classify-clothing", response_model=ClassificationResponse, summary="Classify Clothing Item Image")
async def classify_clothing_endpoint(
    file: UploadFile = File(..., description="Image file of the clothing item"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a clothing item image and get its classification using MobileNetV2.
    
    - **Image File**: Upload the image of the clothing item.
    - **Returns**: Classification results including category and confidence.
    """
    try:
        image_data = await file.read()
        if not image_data:
            raise HTTPException(status_code=400, detail="No image data provided")
        
        # Classify the image asynchronously
        classification_result = await classify_clothing_image_async(image_data)
        
        if not classification_result.get("success", False):
            # Error message might be in 'error' key or directly if service returns string on error
            error_detail = classification_result.get('error', 'Unknown classification error')
            if isinstance(classification_result, str) and "Error:" in classification_result: # Compatibility with some error returns
                error_detail = classification_result
            raise HTTPException(status_code=500, detail=f"Classification failed: {error_detail}")
        
        # Optionally, save classification to database (if item ID is provided or linked)
        # For now, just return the result
        
        return ClassificationResponse(
            predicted_category=classification_result["clothing_type"],
            confidence_score=classification_result["confidence"],
            detailed_predictions=classification_result["detailed_predictions"],
            model_name=classification_result["model_used"]
        )
        
    except HTTPException as he:
        logger.error(f"HTTP error in classify_clothing_endpoint: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Error in classify_clothing_endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/detect-dominant-color", response_model=ColorAnalysisResponse, summary="Detect Dominant Color from Image")
async def detect_dominant_color_endpoint(
    file: UploadFile = File(..., description="Image file of the clothing item"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a clothing item image and detect its dominant color using ColorThief.
    
    - **Image File**: Upload the image of the clothing item.
    - **Returns**: Dominant color information (RGB, hex, name) and color properties.
    """
    try:
        image_data = await file.read()
        if not image_data:
            raise HTTPException(status_code=400, detail="No image data provided")
        
        # Detect dominant color asynchronously
        color_result = await detect_dominant_color_async(image_data)
        
        if not color_result.get("success", False):
            error_detail = color_result.get('error', 'Unknown color detection error')
            if isinstance(color_result, str) and "Error:" in color_result:
                 error_detail = color_result
            raise HTTPException(status_code=500, detail=f"Color detection failed: {error_detail}")
        
        # Optionally, save color analysis to database
        
        return ColorAnalysisResponse(
            dominant_color_rgb=color_result["dominant_color"]["rgb"],
            dominant_color_hex=color_result["dominant_color"]["hex"],
            dominant_color_name=color_result["dominant_color"]["name"],
            color_properties=color_result["properties"]
        )
        
    except HTTPException as he:
        logger.error(f"HTTP error in detect_dominant_color_endpoint: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Error in detect_dominant_color_endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/extract-color-palette", summary="Extract Color Palette from Image")
async def extract_color_palette_endpoint(
    file: UploadFile = File(..., description="Image file of the clothing item"),
    color_count: int = Query(5, ge=2, le=10, description="Number of colors to extract in the palette"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a clothing item image and extract its color palette.
    
    - **Image File**: Upload the image of the clothing item.
    - **Color Count**: Number of colors to extract (default 5).
    - **Returns**: Full color palette information and harmony analysis.
    """
    try:
        image_data = await file.read()
        if not image_data:
            raise HTTPException(status_code=400, detail="No image data provided")
        
        # Extract color palette asynchronously
        palette_result = await extract_color_palette_async(image_data, color_count=color_count)
        
        if not palette_result.get("success", False):
            error_detail = palette_result.get('error', 'Unknown palette extraction error')
            if isinstance(palette_result, str) and "Error:" in palette_result:
                error_detail = palette_result
            raise HTTPException(status_code=500, detail=f"Palette extraction failed: {error_detail}")
        
        return palette_result
        
    except HTTPException as he:
        logger.error(f"HTTP error in extract_color_palette_endpoint: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Error in extract_color_palette_endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/outfit-recommendations", response_model=List[OutfitResponse], summary="Get Outfit Recommendations")
async def get_outfit_recommendations_endpoint(
    request: RecommendationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get personalized outfit recommendations based on user preferences, occasion, and available items.
    
    - **User Preferences**: Style preferences, color choices, etc.
    - **Occasion**: Target occasion for the outfit (e.g., "casual", "work", "wedding").
    - **Items**: List of available clothing items (can be fetched from user wardrobe).
    - **Returns**: List of recommended outfit combinations with scores.
    """
    try:
        # Fetch user items from database
        user_items_db = db.query(WardrobeItem).filter(WardrobeItem.user_id == current_user.id).all()
        
        if not user_items_db:
            return []
        
        # Convert DB items to dictionaries for the recommendation engine
        items_data = [
            {
                "id": item.id,
                "name": item.name,
                "category": item.category,
                "brand": item.brand,
                "dominant_color": {"rgb": item.dominant_color_rgb, "name": item.dominant_color_name} if item.dominant_color_rgb else None,
                "style": item.style_features.get("style_keywords", []) if item.style_features else [],
                "description": "", # Add description if available
                "tags": item.tags if hasattr(item, "tags") else []
            }
            for item in user_items_db
        ]
        
        # Get recommendations
        engine = get_recommendation_engine()
        recommendations = engine.get_outfit_recommendations(
            user_preferences=request.user_preferences.dict() if request.user_preferences else {},
            items=items_data,
            occasion=request.occasion,
            num_recommendations=request.num_recommendations
        )
        
        # Convert recommended outfits to OutfitResponse schema
        # This requires fetching full outfit details from DB or constructing them
        # For now, returning a simplified structure
        
        # Example: Save recommendations to database
        for rec in recommendations:
            # Create OutfitRecommendation entry
            pass
        
        # This part needs to be adapted to return proper OutfitResponse objects
        # For now, returning the raw recommendation structure
        return recommendations  # Placeholder - adapt to OutfitResponse
        
    except HTTPException as he:
        logger.error(f"HTTP error in get_outfit_recommendations_endpoint: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Error in get_outfit_recommendations_endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/similar-items", summary="Get Similar Clothing Items")
async def get_similar_items_endpoint(
    target_item_id: int = Query(..., description="ID of the target clothing item"),
    num_similar: int = Query(5, ge=1, le=20, description="Number of similar items to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get clothing items similar to a target item based on content features.
    
    - **Target Item ID**: ID of the item to find similar items for.
    - **Num Similar**: Number of similar items to retrieve.
    - **Returns**: List of similar items with similarity scores.
    """
    try:
        # Fetch target item
        target_item_db = db.query(WardrobeItem).filter(WardrobeItem.id == target_item_id, WardrobeItem.user_id == current_user.id).first()
        if not target_item_db:
            raise HTTPException(status_code=404, detail="Target item not found")
        
        # Fetch all user items for comparison
        user_items_db = db.query(WardrobeItem).filter(WardrobeItem.user_id == current_user.id, WardrobeItem.id != target_item_id).all()
        if not user_items_db:
            return []
        
        # Convert to dictionaries
        target_item_data = {
            "id": target_item_db.id,
            "name": target_item_db.name,
            "category": target_item_db.category,
            "brand": target_item_db.brand,
            "dominant_color": {"rgb": target_item_db.dominant_color_rgb, "name": target_item_db.dominant_color_name} if target_item_db.dominant_color_rgb else None,
            "style": target_item_db.style_features.get("style_keywords", []) if target_item_db.style_features else [],
            "description": "",
            "tags": target_item_db.tags if hasattr(target_item_db, "tags") else []
        }
        
        items_data = [
            {
                "id": item.id,
                "name": item.name,
                "category": item.category,
                "brand": item.brand,
                "dominant_color": {"rgb": item.dominant_color_rgb, "name": item.dominant_color_name} if item.dominant_color_rgb else None,
                "style": item.style_features.get("style_keywords", []) if item.style_features else [],
                "description": "",
                "tags": item.tags if hasattr(item, "tags") else []
            }
            for item in user_items_db
        ]
        
        # Get similar items
        engine = get_recommendation_engine()
        similar_items = engine.get_similar_items(target_item_data, items_data, num_similar=num_similar)
        
        # This part needs to be adapted to return proper WardrobeItemResponse objects
        # For now, returning the raw similar items structure
        return similar_items  # Placeholder - adapt to WardrobeItemResponse
        
    except HTTPException as he:
        logger.error(f"HTTP error in get_similar_items_endpoint: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Error in get_similar_items_endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/train-recommendation-model", response_model=TrainingStatusResponse, status_code=status.HTTP_202_ACCEPTED, summary="Train Outfit Recommendation Model")
async def train_recommendation_model_endpoint(
    background_tasks: BackgroundTasks, # Add BackgroundTasks dependency
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Triggers background training of the outfit recommendation model with the user's current wardrobe items.
    This should be called periodically or when significant changes occur in the wardrobe.
    
    - **Returns**: Acceptance status, training will proceed in the background.
    """
    # Fetch all items for the current user (this part is quick)
    user_items_db = db.query(WardrobeItem).filter(WardrobeItem.user_id == current_user.id).all()
    if not user_items_db or len(user_items_db) < 5:
        # Return a different status if not training, or just accept and log
        # For simplicity, we can still return 202 but log that no training was needed.
        logger.info(f"Recommendation model training skipped for user {current_user.id}: not enough items.")
        return TrainingStatusResponse(status="skipped", message="Not enough items to train model, training skipped.")

    # Convert to dictionaries (also relatively quick)
    items_data = [
        {
            "id": item.id, "name": item.name, "category": item.category, "brand": item.brand,
            "dominant_color": {"rgb": item.dominant_color_rgb, "name": item.dominant_color_name} if item.dominant_color_rgb else None,
            "style": item.style_features.get("style_keywords", []) if item.style_features else [],
            "description": "", "tags": item.tags if hasattr(item, "tags") else []
        }
        for item in user_items_db
    ]
    
    # Add the time-consuming training task to background
    engine = get_recommendation_engine()
    background_tasks.add_task(engine.train_recommendation_model, items_data)
    
    logger.info(f"Recommendation model training initiated in background for user {current_user.id}.")
    return TrainingStatusResponse(status="pending", message="Recommendation model training has been initiated in the background.")

# Helper function to integrate ML results into WardrobeItem creation/update
# This function itself also calls synchronous AI service functions.
# It should be refactored to use their _async versions if called from an async route.
# For now, assuming it's called from wardrobe.py which was refactored.
# However, the calls inside process_and_update_item_ml_data are still to sync versions.
# This needs to be addressed if this helper is used by new async code.
async def process_and_update_item_ml_data(
    item: WardrobeItem, 
    image_data: bytes, 
    db: Session
):
    """
    Process ML data for a wardrobe item and update the database.
    """
    try:
        # Classify clothing item
        classification_result = classify_clothing_image(image_data)
        if classification_result.get("success"):
            item.ai_classification = {
                "category": classification_result["clothing_type"],
                "confidence": classification_result["confidence"],
                "details": classification_result["detailed_predictions"]
            }
            # Store detailed classification result
            new_classification = ItemClassification(
                wardrobe_item_id=item.id,
                model_name=classification_result["model_used"],
                predicted_category=classification_result["clothing_type"],
                confidence_score=classification_result["confidence"],
                detailed_predictions=classification_result["detailed_predictions"]
            )
            db.add(new_classification)
        
        # Detect dominant color and palette
        color_result = detect_dominant_color(image_data)
        if color_result.get("success"):
            item.dominant_color_rgb = color_result["dominant_color"]["rgb"]
            item.dominant_color_hex = color_result["dominant_color"]["hex"]
            item.dominant_color_name = color_result["dominant_color"]["name"]
            item.color_properties = color_result["properties"]
            
            palette_result = extract_color_palette(image_data)
            if palette_result.get("success"):
                item.color_palette = palette_result["palette"]
            
            # Store detailed color analysis
            new_color_analysis = ColorAnalysis(
                wardrobe_item_id=item.id,
                dominant_color_rgb=color_result["dominant_color"]["rgb"],
                dominant_color_hex=color_result["dominant_color"]["hex"],
                dominant_color_name=color_result["dominant_color"]["name"],
                color_palette=palette_result.get("palette"),
                color_harmony_analysis=palette_result.get("harmony_analysis"),
                color_suggestions=get_color_detector().get_color_suggestions(color_result["dominant_color"]["rgb"])
            )
            db.add(new_color_analysis)
        
        # Extract style features (can be done here or in recommendation engine)
        # item.style_features = get_recommendation_engine()._extract_style_features(item.description or "")
        
        db.commit()
        db.refresh(item)
        
    except Exception as e:
        logger.error(f"Error processing ML data for item {item.id}: {str(e)}", exc_info=True)
        db.rollback()
        # Do not raise error here, allow main operation to continue

# Example of integrating ML processing into an existing endpoint (e.g., add item)
# This would typically be in app/routers/wardrobe.py

# @router.post("/items/", response_model=WardrobeItemResponse)
# async def create_wardrobe_item_with_ml(
#     item_data: WardrobeItemCreate,
#     image_file: UploadFile = File(None),
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     db_item = WardrobeItem(**item_data.dict(), user_id=current_user.id)
#     if image_file:
#         image_data = await image_file.read()
#         # Store image_url (e.g., to S3 or local storage)
#         # db_item.image_url = ...
#         
#         # Process ML data
#         await process_and_update_item_ml_data(db_item, image_data, db)
#     
#     db.add(db_item)
#     db.commit()
#     db.refresh(db_item)
#     return db_item


