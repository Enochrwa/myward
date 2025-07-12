# Model Cache Management API Endpoints
# This module provides API endpoints for managing AI model caching

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from ..security import get_current_user
from ..db.database import get_db
from .. import tables as schemas
from ..services.model_manager import get_model_manager

router = APIRouter(
    prefix="/model-cache",
    tags=["Model Cache Management"],
    responses={404: {"description": "Not found"}},
)

@router.get("/info", response_model=Dict[str, Any])
async def get_cache_info(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get information about cached AI models"""
    model_manager = get_model_manager()
    cache_info = model_manager.get_cache_info()
    return cache_info

@router.post("/preload")
async def preload_models(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Preload all AI models to cache"""
    model_manager = get_model_manager()
    
    results = {}
    for model_name in ["mobilenet_v2", "efficientdet_lite0"]:
        try:
            model = model_manager.get_model(model_name)
            if model is not None:
                results[model_name] = "loaded"
            else:
                results[model_name] = "failed"
        except Exception as e:
            results[model_name] = f"error: {str(e)}"
    
    return {"status": "completed", "results": results}

@router.delete("/clear")
async def clear_cache(
    model_name: str = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Clear model cache (specific model or all models)"""
    model_manager = get_model_manager()
    
    try:
        model_manager.clear_cache(model_name)
        if model_name:
            return {"status": "success", "message": f"Cache cleared for {model_name}"}
        else:
            return {"status": "success", "message": "All caches cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")

@router.get("/status")
async def get_model_status():
    """Get the status of all AI models (no authentication required)"""
    model_manager = get_model_manager()
    cache_info = model_manager.get_cache_info()
    
    status = {}
    for model_name, info in cache_info["models"].items():
        status[model_name] = {
            "cached": info["cached"],
            "in_memory": info["in_memory"],
            "ready": info["cached"] or info["in_memory"]
        }
    
    return {"models": status, "cache_dir": cache_info["cache_dir"]}

