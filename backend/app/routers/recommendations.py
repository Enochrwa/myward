from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional # For List type hint & Optional query params

from .. import tables as schemas
from .. import model as models
from ..security import get_current_user
from ..db.database import get_db
from ..services.recommendation_services import get_wardrobe_recommendations_service, recommend_outfits_for_occasion_service
# EventDetailsInput is available via schemas.EventDetailsInput
# Outfit is available via schemas.Outfit

router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
    responses={404: {"description": "Not found"}},
)

@router.get("/wardrobe/", response_model=schemas.PersonalizedWardrobeSuggestions)
async def get_personalized_wardrobe_recommendations(
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user) # Ensure type is schemas.User
):
    suggestions = await get_wardrobe_recommendations_service(
        db=db,
        user=current_user,
        latitude=lat,
        longitude=lon
    )
    if not suggestions.newOutfitIdeas and not suggestions.itemsToAcquire:
        # Optional: return a specific message or 204 if no suggestions,
        # or just return the empty suggestion structure.
        # For now, returning empty structure is fine.
        pass
    return suggestions

@router.post("/event/", response_model=List[schemas.Outfit])
async def get_recommendations_for_event(
    event_details: schemas.EventDetailsInput,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # Ensure this is models.User for service compatibility
):
    """
    Provides outfit recommendations based on event details, user's wardrobe, and learned style preferences.

    The system uses AI to understand the occasion context and matches it with suitable outfits,
    prioritizing those that align with the user's personal style profile for that type of event.
    """

    # The recommend_outfits_for_occasion_service expects an object with 'name' and 'notes' attributes.
    # We'll create a simple ad-hoc object for this.
    class TempOccasionContext:
        def __init__(self, name: str, notes: Optional[str]):
            self.name = name
            self.notes = notes

    # Constructing a detailed note string from event_details
    notes_parts = []
    if event_details.location:
        notes_parts.append(f"Location: {event_details.location}")
    if event_details.weather:
        notes_parts.append(f"Weather: {event_details.weather}")
    if event_details.time_of_day:
        notes_parts.append(f"Time: {event_details.time_of_day}")
    if event_details.formality:
        notes_parts.append(f"Formality: {event_details.formality}")
    if event_details.notes:
        notes_parts.append(f"User notes: {event_details.notes}")

    full_notes = ", ".join(notes_parts)
    if not full_notes:
        full_notes = "General context for event type."


    occasion_context = TempOccasionContext(
        name=event_details.event_type,
        notes=full_notes
    )

    recommendations = await recommend_outfits_for_occasion_service(
        db=db,
        user=current_user, # Pass the models.User object
        occasion=occasion_context, # Pass the ad-hoc context object
        num_recommendations=3 # Or make this configurable
    )

    if not recommendations:
        # Handle case where no recommendations are found, could raise HTTPException or return empty list
        # For now, returning an empty list if service returns None/empty
        return []

    return recommendations
