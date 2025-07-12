from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import tables as schemas  # schemas are in tables.py
from .. import model as models    # SQLAlchemy models are in model.py
from ..security import get_current_user
from ..db.database import get_db
from datetime import datetime

router = APIRouter(
    prefix="/community",
    tags=["Community Features"],
    responses={404: {"description": "Not found"}},
)

@router.post("/outfits/{outfit_id}/feedback", response_model=schemas.Feedback)
async def create_feedback_for_outfit(
    outfit_id: int,
    feedback_data: schemas.FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check if outfit exists
    outfit = db.query(models.Outfit).filter(models.Outfit.id == outfit_id).first()
    if not outfit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outfit not found")

    new_feedback = models.Feedback(
        **feedback_data.model_dump(),
        outfit_id=outfit_id,
        user_id=current_user.id,
        created_at=datetime.utcnow()
    )
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)

    # For the response, populate commenter_username
    # This assumes schemas.Feedback has a 'commenter_username' field
    # and your User model (current_user) has a 'username' attribute.
    response_feedback = schemas.Feedback.model_validate(new_feedback)
    response_feedback.commenter_username = current_user.username
    return response_feedback

@router.get("/outfits/{outfit_id}/feedback", response_model=List[schemas.Feedback])
async def get_feedback_for_outfit(
    outfit_id: int,
    db: Session = Depends(get_db)
):
    # Check if outfit exists
    outfit = db.query(models.Outfit).filter(models.Outfit.id == outfit_id).first()
    if not outfit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outfit not found")

    feedbacks_db = db.query(models.Feedback).filter(models.Feedback.outfit_id == outfit_id).all()

    response_feedbacks = []
    for fb_db in feedbacks_db:
        # Assuming fb_db.commenter is the relationship to the User model
        # and User model has a 'username' attribute.
        commenter_username = fb_db.commenter.username if fb_db.commenter else "Unknown User"

        feedback_schema = schemas.Feedback.model_validate(fb_db)
        feedback_schema.commenter_username = commenter_username
        response_feedbacks.append(feedback_schema)

    return response_feedbacks

@router.delete("/feedback/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    feedback_to_delete = db.query(models.Feedback).filter(models.Feedback.id == feedback_id).first()

    if not feedback_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")

    # Check if the current user is the owner of the feedback
    # Add admin override here if needed in the future
    if feedback_to_delete.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this feedback")

    db.delete(feedback_to_delete)
    db.commit()
    return
