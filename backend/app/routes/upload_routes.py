"""
Image upload routes for Digital Wardrobe System
Handles intelligent image processing and clothing item creation
"""
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from typing import List, Optional
from pydantic import BaseModel
import logging

from models.database_models import (
    User, ClothingItemResponse, ClothingItemCreate, 
    ClothingImageCreate, ClothingFeaturesCreate
)
from services.auth_service import get_current_active_user
from services.database_service import db_service
from services.image_processing_service import image_processing_service
from config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Response models
class UploadResponse(BaseModel):
    message: str
    clothing_item_id: str
    image_url: str
    analysis: dict
    intelligent_filename: str

class BatchUploadResponse(BaseModel):
    message: str
    total_images: int
    successful_uploads: int
    failed_uploads: int
    results: List[dict]
    processing_time: float

@router.post("/upload-clothing-image", response_model=UploadResponse)
async def upload_clothing_image(
    file: UploadFile = File(...),
    clothing_type_id: Optional[int] = Form(None),
    brand_id: Optional[int] = Form(None),
    primary_color_id: Optional[int] = Form(None),
    notes: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user)
):
    """Upload and process a single clothing image with AI analysis"""
    try:
        # Validate file
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Check file size
        contents = await file.read()
        if len(contents) > settings.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size is {settings.max_file_size / (1024*1024):.1f}MB"
            )
        
        # Check file extension
        file_ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        if f".{file_ext}" not in settings.allowed_image_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {', '.join(settings.allowed_image_extensions)}"
            )
        
        # Process image with AI analysis
        analysis_results = image_processing_service.process_clothing_image(
            image_data=contents,
            original_filename=file.filename,
            user_id=current_user.id
        )
        
        if not analysis_results:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process image"
            )
        
        # Extract analysis data
        file_info = analysis_results["file_info"]
        clothing_analysis = analysis_results["clothing_analysis"]
        features = analysis_results["features"]
        
        # Map AI classifications to database IDs
        # If user provided explicit values, use those; otherwise use AI suggestions
        final_clothing_type_id = clothing_type_id
        final_primary_color_id = primary_color_id
        
        # If not provided by user, try to map AI classifications to database
        if not final_clothing_type_id:
            # Get clothing type from AI classification
            ai_clothing_type = clothing_analysis["type"]["clothing_type"]
            clothing_types = db_service.get_clothing_types()
            for ct in clothing_types:
                if ai_clothing_type.lower() in ct.name.lower():
                    final_clothing_type_id = ct.id
                    break
            
            # Default to first clothing type if no match found
            if not final_clothing_type_id and clothing_types:
                final_clothing_type_id = clothing_types[0].id
        
        if not final_primary_color_id:
            # Get color from AI analysis
            ai_color_name = features["color"]["dominant_color"]["name"]
            colors = db_service.get_colors()
            for color in colors:
                if ai_color_name.lower() in color.name.lower():
                    final_primary_color_id = color.id
                    break
            
            # Default to first color if no match found
            if not final_primary_color_id and colors:
                final_primary_color_id = colors[0].id
        
        # Create clothing item record
        clothing_item_data = ClothingItemCreate(
            original_filename=file_info["original_filename"],
            stored_filename=file_info["stored_filename"],
            clothing_type_id=final_clothing_type_id,
            brand_id=brand_id,
            primary_color_id=final_primary_color_id,
            secondary_color_id=None,
            pattern_id=None,
            notes=notes,
            is_favorite=False,
            is_available=True,
            condition_rating="excellent"
        )
        
        clothing_item_id = db_service.create_clothing_item(current_user.id, clothing_item_data)
        
        if not clothing_item_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create clothing item record"
            )
        
        # Create image record
        image_data = ClothingImageCreate(
            clothing_item_id=clothing_item_id,
            image_path=f"{settings.upload_dir}/{file_info['stored_filename']}",
            image_url=analysis_results["image_url"],
            file_size=file_info["file_size"],
            image_width=file_info["dimensions"]["width"],
            image_height=file_info["dimensions"]["height"],
            is_primary=True
        )
        
        image_id = db_service.create_clothing_image(image_data)
        
        if not image_id:
            logger.warning(f"Failed to create image record for clothing item {clothing_item_id}")
        
        # Create features record
        features_data = ClothingFeaturesCreate(
            clothing_item_id=clothing_item_id,
            resnet_features=features["resnet"],
            opencv_features=features["opencv"],
            color_palette=features["color"]["palette"]["hex_codes"],
            texture_features=features["opencv"].get("texture", {}),
            style_features={
                "clothing_type": clothing_analysis["type"],
                "style": clothing_analysis["style"],
                "occasion": clothing_analysis["occasion"],
                "season": clothing_analysis["season"]
            }
        )
        
        features_id = db_service.create_clothing_features(features_data)
        
        if not features_id:
            logger.warning(f"Failed to create features record for clothing item {clothing_item_id}")
        
        # Prepare response
        response = UploadResponse(
            message="Clothing image uploaded and analyzed successfully",
            clothing_item_id=clothing_item_id,
            image_url=analysis_results["image_url"],
            analysis=clothing_analysis,
            intelligent_filename=file_info["stored_filename"]
        )
        
        logger.info(f"Successfully uploaded clothing image for user {current_user.id}: {clothing_item_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading clothing image: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during image upload"
        )

@router.post("/upload-multiple-images", response_model=BatchUploadResponse)
async def upload_multiple_clothing_images(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """Upload and process multiple clothing images"""
    import time
    start_time = time.time()
    
    try:
        # Validate number of files
        if len(files) > settings.max_files_per_request:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Too many files. Maximum {settings.max_files_per_request} files allowed"
            )
        
        results = []
        successful_uploads = 0
        failed_uploads = 0
        
        for file in files:
            try:
                # Validate file
                if not file.content_type or not file.content_type.startswith('image/'):
                    results.append({
                        "filename": file.filename,
                        "success": False,
                        "error": "File must be an image"
                    })
                    failed_uploads += 1
                    continue
                
                # Check file size
                contents = await file.read()
                if len(contents) > settings.max_file_size:
                    results.append({
                        "filename": file.filename,
                        "success": False,
                        "error": "File too large"
                    })
                    failed_uploads += 1
                    continue
                
                # Process image
                analysis_results = image_processing_service.process_clothing_image(
                    image_data=contents,
                    original_filename=file.filename,
                    user_id=current_user.id
                )
                
                if not analysis_results:
                    results.append({
                        "filename": file.filename,
                        "success": False,
                        "error": "Failed to process image"
                    })
                    failed_uploads += 1
                    continue
                
                # Create database records (simplified for batch processing)
                file_info = analysis_results["file_info"]
                clothing_analysis = analysis_results["clothing_analysis"]
                features = analysis_results["features"]
                
                # Use AI suggestions for batch processing
                clothing_types = db_service.get_clothing_types()
                colors = db_service.get_colors()
                
                # Find matching clothing type
                ai_clothing_type = clothing_analysis["type"]["clothing_type"]
                clothing_type_id = None
                for ct in clothing_types:
                    if ai_clothing_type.lower() in ct.name.lower():
                        clothing_type_id = ct.id
                        break
                if not clothing_type_id and clothing_types:
                    clothing_type_id = clothing_types[0].id
                
                # Find matching color
                ai_color_name = features["color"]["dominant_color"]["name"]
                primary_color_id = None
                for color in colors:
                    if ai_color_name.lower() in color.name.lower():
                        primary_color_id = color.id
                        break
                if not primary_color_id and colors:
                    primary_color_id = colors[0].id
                
                # Create clothing item
                clothing_item_data = ClothingItemCreate(
                    original_filename=file_info["original_filename"],
                    stored_filename=file_info["stored_filename"],
                    clothing_type_id=clothing_type_id,
                    brand_id=None,
                    primary_color_id=primary_color_id,
                    secondary_color_id=None,
                    pattern_id=None,
                    notes=f"Auto-processed: {clothing_analysis['type']['clothing_type']} - {clothing_analysis['style']['style']}",
                    is_favorite=False,
                    is_available=True,
                    condition_rating="excellent"
                )
                
                clothing_item_id = db_service.create_clothing_item(current_user.id, clothing_item_data)
                
                if clothing_item_id:
                    # Create image and features records
                    image_data = ClothingImageCreate(
                        clothing_item_id=clothing_item_id,
                        image_path=f"{settings.upload_dir}/{file_info['stored_filename']}",
                        image_url=analysis_results["image_url"],
                        file_size=file_info["file_size"],
                        image_width=file_info["dimensions"]["width"],
                        image_height=file_info["dimensions"]["height"],
                        is_primary=True
                    )
                    db_service.create_clothing_image(image_data)
                    
                    features_data = ClothingFeaturesCreate(
                        clothing_item_id=clothing_item_id,
                        resnet_features=features["resnet"],
                        opencv_features=features["opencv"],
                        color_palette=features["color"]["palette"]["hex_codes"],
                        texture_features=features["opencv"].get("texture", {}),
                        style_features={
                            "clothing_type": clothing_analysis["type"],
                            "style": clothing_analysis["style"],
                            "occasion": clothing_analysis["occasion"],
                            "season": clothing_analysis["season"]
                        }
                    )
                    db_service.create_clothing_features(features_data)
                    
                    results.append({
                        "filename": file.filename,
                        "success": True,
                        "clothing_item_id": clothing_item_id,
                        "intelligent_filename": file_info["stored_filename"],
                        "analysis": clothing_analysis
                    })
                    successful_uploads += 1
                else:
                    results.append({
                        "filename": file.filename,
                        "success": False,
                        "error": "Failed to create clothing item record"
                    })
                    failed_uploads += 1
                
            except Exception as e:
                logger.error(f"Error processing file {file.filename}: {e}")
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": str(e)
                })
                failed_uploads += 1
        
        processing_time = time.time() - start_time
        
        response = BatchUploadResponse(
            message=f"Batch upload completed. {successful_uploads} successful, {failed_uploads} failed.",
            total_images=len(files),
            successful_uploads=successful_uploads,
            failed_uploads=failed_uploads,
            results=results,
            processing_time=processing_time
        )
        
        logger.info(f"Batch upload completed for user {current_user.id}: {successful_uploads}/{len(files)} successful")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during batch upload"
        )

