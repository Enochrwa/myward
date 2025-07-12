from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List # Required for List type hint if not already imported

from ..import tables as schemas, model as models # Assuming models might be needed later
from ..security import get_current_user
from ..db.database import get_db
from ..services.ai_services import analyze_outfit_image_service # Import the service

router = APIRouter(
    prefix="/ai", # General prefix for AI related endpoints
    tags=["AI Analysis"],
    responses={404: {"description": "Not found"}},
)

@router.post("/analyze-outfit/", response_model=schemas.OutfitAnalysisResponse)
async def analyze_outfit_image_endpoint(
    file: UploadFile = File(...), # Use File(...) for required file upload
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

    # Max file size check (e.g., 10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    size = await file.read() # Read to check size
    await file.seek(0) # Reset pointer to beginning of file for service to read
    if len(size) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"Image file too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB.")


    analysis_result = await analyze_outfit_image_service(file=file, db=db, user=current_user)
    return analysis_result

# In backend/app/routers/ai_analyzer.py
# ... (other imports)
from ..services.ai_services import get_fashion_trends_service # Import the service
from typing import Optional # Ensure Optional is imported

# ... (existing analyze_outfit_image_endpoint) ...

@router.get("/fashion-trends/", response_model=schemas.TrendForecastResponse)
async def get_fashion_trends_endpoint(
    db: Session = Depends(get_db),
    # Making current_user optional for trends, as they might be general
    # or personalized if user is logged in. Service handles the Optional user.
    current_user: Optional[schemas.User] = Depends(get_current_user) # Allow optional user
):
    # The get_current_user dependency needs to be able to handle being optional.
    # A common way is to have a get_optional_current_user dependency,
    # or adjust get_current_user if it's designed to allow optional authentication.
    # For now, let's assume get_current_user can return None if token is not provided or invalid,
    # and the endpoint/service is designed for this.
    # However, OAuth2PasswordBearer(auto_error=True) by default raises an error if token is missing.
    # To make it truly optional, you might need a different dependency or set auto_error=False
    # and handle the None token case.

    # Simplification for this step: We'll make `get_current_user` non-optional for now.
    # Personalization based on user can be a future enhancement if user is present.
    # So, changing current_user back to non-optional for this endpoint for simplicity,
    # meaning trends are general unless service is adapted.
    # current_user: schemas.User = Depends(get_current_user)

    # Re-evaluating: The frontend AITrendForecasting doesn't seem to send auth for trends.
    # Let's make a new dependency for optional user or make get_current_user support auto_error=False.
    # For now, to keep it simple and focus on mock data, we'll pass the current_user if available.
    # The simplest approach is to require authentication for this endpoint for now.
    # If trends are to be public, security.py's oauth2_scheme and get_current_user would need adjustment.

    # Decision: Keep current_user mandatory for now. Service can ignore it if trends are general.
    user_dependency: schemas.User = Depends(get_current_user)

    trends_response = await get_fashion_trends_service(db=db, user=user_dependency)
    return trends_response
