from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from .. import tables as schemas, model as models # Import models and schemas
from ..security import get_current_user # get_current_user returns schemas.User
from ..db.database import get_db
from ..services.recommendation_services import recommend_outfits_for_occasion_service # Import service

router = APIRouter(
    prefix="/occasions",
    tags=["Occasions"],
    responses={404: {"description": "Not found"}},
)

# Helper to convert model to schema and add suggestions
async def occasion_model_to_response(db_occasion_model: models.Occasion, db: Session, current_user: schemas.User) -> schemas.Occasion:
    # Convert base model to schema
    occasion_schema = schemas.Occasion.model_validate(db_occasion_model)

    # Fetch and add suggestions
    # Ensure current_user is passed as schemas.User, which it should be from get_current_user
    suggested_db_outfits = await recommend_outfits_for_occasion_service(
        db=db,
        user=current_user, # This should be schemas.User
        occasion=occasion_schema # Pass the schema version of occasion
    )
    occasion_schema.suggested_outfits = suggested_db_outfits # This list is already of schemas.Outfit
    return occasion_schema


@router.post("/", response_model=schemas.Occasion, status_code=status.HTTP_201_CREATED)
async def create_occasion(
    occasion: schemas.OccasionCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user) # Ensure type is schemas.User
):
    if occasion.outfit_id:
        outfit = db.query(models.Outfit).filter(models.Outfit.id == occasion.outfit_id, models.Outfit.user_id == current_user.id).first()
        if not outfit:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Outfit with ID {occasion.outfit_id} not found or does not belong to user.")

    db_occasion_model = models.Occasion(
        **occasion.model_dump(),
        user_id=current_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_occasion_model)
    db.commit()
    db.refresh(db_occasion_model)

    # Use the helper to include suggestions in the response
    return await occasion_model_to_response(db_occasion_model, db, current_user)


@router.get("/", response_model=List[schemas.Occasion])
async def read_occasions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    # Note: Suggestions are NOT added to the list view to keep it light.
    # Client can fetch individual occasion to get suggestions.
    occasions_models = db.query(models.Occasion).filter(models.Occasion.user_id == current_user.id).order_by(models.Occasion.date.desc()).offset(skip).limit(limit).all()
    # Basic conversion, no suggestions here.
    return [schemas.Occasion.model_validate(occ) for occ in occasions_models]


@router.get("/{occasion_id}", response_model=schemas.Occasion)
async def read_occasion(
    occasion_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user) # Ensure type is schemas.User
):
    db_occasion_model = db.query(models.Occasion).filter(models.Occasion.id == occasion_id, models.Occasion.user_id == current_user.id).first()
    if db_occasion_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Occasion not found")

    return await occasion_model_to_response(db_occasion_model, db, current_user)


@router.put("/{occasion_id}", response_model=schemas.Occasion)
async def update_occasion(
    occasion_id: int,
    occasion_update: schemas.OccasionUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user) # Ensure type is schemas.User
):
    db_occasion_model = db.query(models.Occasion).filter(models.Occasion.id == occasion_id, models.Occasion.user_id == current_user.id).first()

    if db_occasion_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Occasion not found")

    update_data = occasion_update.model_dump(exclude_unset=True)
    if "outfit_id" in update_data: # Check if outfit_id is part of the update
        new_outfit_id = update_data["outfit_id"]
        if new_outfit_id is not None: # If a new outfit_id is provided
            outfit = db.query(models.Outfit).filter(models.Outfit.id == new_outfit_id, models.Outfit.user_id == current_user.id).first()
            if not outfit:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Outfit with ID {new_outfit_id} not found or does not belong to user.")
        # If new_outfit_id is None, it will be set directly by setattr, unlinking the outfit.

    for key, value in update_data.items():
        setattr(db_occasion_model, key, value)

    db_occasion_model.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_occasion_model)

    return await occasion_model_to_response(db_occasion_model, db, current_user)

@router.delete("/{occasion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_occasion(
    occasion_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_occasion = db.query(models.Occasion).filter(models.Occasion.id == occasion_id, models.Occasion.user_id == current_user.id).first()

    if db_occasion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Occasion not found")

    db.delete(db_occasion)
    db.commit()
    return
