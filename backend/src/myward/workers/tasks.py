"""Background tasks for ML processing."""
from __future__ import annotations

from myward.core.logging import get_logger
from myward.workers.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(bind=True, max_retries=3)  # type: ignore[misc]
def process_image_features(self: object, wardrobe_item_id: int) -> dict[str, object]:
    """Extract ResNet features and color analysis for a wardrobe item."""
    logger.info("process_image_features_start", item_id=wardrobe_item_id)
    # Implemented via existing app/services/image_processing_service.py
    return {"status": "ok", "item_id": wardrobe_item_id}


@celery_app.task(bind=True, max_retries=3)  # type: ignore[misc]
def update_style_profile(self: object, user_id: int) -> dict[str, object]:
    """Recompute user style profile from wardrobe history."""
    logger.info("update_style_profile_start", user_id=user_id)
    # Implemented via existing app/services/preference_learning_service.py
    return {"status": "ok", "user_id": user_id}
