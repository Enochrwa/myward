# backend/app/services/__init__.py
# Import AI services (if any are directly exposed or for re-export)
# from .ai_services import analyze_outfit_image_service, get_fashion_trends_service

# Import Recommendation services (if any are directly exposed or for re-export)
# from .recommendation_services import RecommendationService # Example

# Import Outfit Matching Service
from .outfit_matching_service import OutfitMatchingService

# Optionally, create an instance for easy use if desired,
# though dependency injection in routers is often preferred for FastAPI.
# outfit_matcher = OutfitMatchingService()

# You can also define __all__ if you want to specify what `from .services import *` imports
# __all__ = ["analyze_outfit_image_service", "get_fashion_trends_service", "OutfitMatchingService"]
