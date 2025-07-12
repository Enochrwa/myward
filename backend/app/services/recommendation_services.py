from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from .. import model as models, tables as schemas
from sqlalchemy import func, or_

# Added imports for AI-powered recommendations
import numpy as np # For random embeddings if needed
import random
from itertools import combinations
from sqlalchemy.orm import joinedload # For eager loading of outfit items

from ..services.outfit_matching_service import OutfitMatchingService
# from ..services.ai_services import get_fashion_trends_service # Keep commented if not fully implementing trend integration yet
# from ..services.ai_services import analyze_outfit_image_service # Not directly used if AI features are mocked/pre-stored

# For sentence embeddings for occasion matching
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    sentence_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
except ImportError:
    import logging 
    logger = logging.getLogger(__name__)
    logger.warning("sentence_transformers not available. Occasion matching will use fallback logic.")
    sentence_model = None
    cosine_similarity = None

import json # For parsing UserStyleProfile JSON fields
from .user_style_profile_service import get_or_create_user_style_profile # Import for UserStyleProfile

# --- Load Models ---
# Models are loaded in the import section above

# Instantiate services needed
outfit_matcher = OutfitMatchingService()

from .weather_service import get_weather_data 
import asyncio 

# New AI-driven helper function for occasion matching
def find_ai_matched_outfits_for_occasion(
    db: Session,
    user_id: int,
    occasion_name_from_input: str, # Specifically the name/type of occasion from user input
    occasion_notes_from_input: str, # Additional notes for context
    num_recommendations: int = 3,
    min_coherence_score: float = 0.4 
) -> List[models.Outfit]:
    logger = logging.getLogger(__name__) 

    occasion_text_for_embedding = f"{occasion_name_from_input} {occasion_notes_from_input}".strip()

    if not sentence_model or not occasion_text_for_embedding:
        logger.warning("Sentence transformer model not loaded or occasion text is empty. Cannot perform AI matching.")
        return []

    try:
        occasion_embedding = sentence_model.encode(occasion_text)
    except Exception as e:
        logger.error(f"Error encoding occasion text: {e}")
        return []

    # Fetch user's outfits with their items eagerly loaded
    # Assuming 'items_association' is the relationship from Outfit to OutfitItem (association object)
    # and 'item' is the relationship from OutfitItem to WardrobeItem.
    user_outfits = db.query(models.Outfit)\
        .filter(models.Outfit.user_id == user_id)\
        .options(joinedload(models.Outfit.items))\
        .all() # Changed from items_association to items directly

    if not user_outfits:
        return []

    # Fetch UserStyleProfile
    user_style_profile = get_or_create_user_style_profile(db, user_id)
    profile_preferred_colors = json.loads(user_style_profile.preferred_colors) if user_style_profile.preferred_colors else []
    profile_style_keywords = json.loads(user_style_profile.style_keywords) if user_style_profile.style_keywords else []
    profile_occasion_prefs = json.loads(user_style_profile.occasion_preferences) if user_style_profile.occasion_preferences else {}
    
    # Get occasion-specific preferences from UserStyleProfile
    current_occasion_specific_prefs = profile_occasion_prefs.get(occasion_name_from_input.lower(), {})
    occasion_preferred_colors = current_occasion_specific_prefs.get("colors", [])
    occasion_preferred_styles = current_occasion_specific_prefs.get("styles", [])


    scored_outfits = []

    for outfit in user_outfits:
        if not outfit.items: # Skip outfits with no items
            continue

        outfit_item_features_for_matcher: List[Dict[str, Any]] = []
        item_embeddings_for_outfit_avg: List[np.ndarray] = []
        
        outfit_aggregated_colors: set[str] = set()
        outfit_aggregated_styles: set[str] = set() # From item.style_features.identified_styles

        for item in outfit.items: # Iterate through WardrobeItem directly
            if not item: continue

            item_emb_list = item.ai_embedding if item.ai_embedding else np.random.rand(384).tolist()
            item_colors_hex = item.color_palette[0]["hex"] if item.color_palette and isinstance(item.color_palette, list) and item.color_palette[0].get("hex") else (item.dominant_color_hex if item.dominant_color_hex else "#808080")
            
            # For OutfitMatchingService, it expects a list of hex colors per item.
            # For simplicity, let's use the dominant hex or first from palette.
            # The OutfitMatchingService's check_color_harmony takes a flat list of all colors in the outfit.
            # So, we'll collect all dominant_color_name for preference check, and all hex for harmony.
            
            if item.dominant_color_name:
                outfit_aggregated_colors.add(item.dominant_color_name.lower())

            if item.style_features and isinstance(item.style_features.get("identified_styles"), list):
                for style in item.style_features["identified_styles"]:
                    outfit_aggregated_styles.add(style.lower())

            outfit_item_features_for_matcher.append({
                "id": item.id,
                "name": item.name,
                "embedding": item_emb_list,
                "colors": [item_colors_hex], # Pass as list of hex strings
                "category": item.category or "unknown"
            })
            item_embeddings_for_outfit_avg.append(np.array(item_emb_list))

        if not outfit_item_features_for_matcher or not item_embeddings_for_outfit_avg:
            continue

        coherence_details = outfit_matcher.calculate_compatibility_score(outfit_item_features_for_matcher)
        internal_coherence_score = coherence_details["score"]

        if internal_coherence_score < min_coherence_score:
            continue

        outfit_embedding_avg = np.mean(item_embeddings_for_outfit_avg, axis=0)
        similarity_to_occasion = cosine_similarity(occasion_embedding.reshape(1, -1), outfit_embedding_avg.reshape(1, -1))[0][0]
        similarity_to_occasion_normalized = (similarity_to_occasion + 1) / 2

        # Calculate preference boost
        preference_boost = 0.0
        # General color preference
        if any(color in profile_preferred_colors for color in outfit_aggregated_colors):
            preference_boost += 0.05
        # General style preference
        if any(style in profile_style_keywords for style in outfit_aggregated_styles):
            preference_boost += 0.05
        
        # Occasion-specific color preference
        if occasion_preferred_colors and any(color in occasion_preferred_colors for color in outfit_aggregated_colors):
            preference_boost += 0.10 # Higher boost for occasion-specific match
        # Occasion-specific style preference
        if occasion_preferred_styles and any(style in occasion_preferred_styles for style in outfit_aggregated_styles):
            preference_boost += 0.10

        # Weights for combining scores
        occasion_similarity_weight = 0.6
        coherence_weight = 0.25
        preference_weight = 0.15 # Weight for user preference boost
        
        final_match_score = (occasion_similarity_weight * similarity_to_occasion_normalized) + \
                            (coherence_weight * internal_coherence_score) + \
                            (preference_weight * min(preference_boost, 1.0)) # Cap boost

        scored_outfits.append({
            "outfit_model": outfit,
            "score": final_match_score,
            "debug_occasion_sim": similarity_to_occasion_normalized,
            "debug_coherence": internal_coherence_score,
            "debug_pref_boost": preference_boost
        })

    sorted_outfits = sorted(scored_outfits, key=lambda x: x["score"], reverse=True)
    # logger.info(f"Top sorted outfits for occasion '{occasion_name_from_input}': " + ", ".join([f"{s['outfit_model'].name} (Score: {s['score']:.2f}, PrefBoost: {s['debug_pref_boost']:.2f})" for s in sorted_outfits[:5]]))

    return [s["outfit_model"] for s in sorted_outfits[:num_recommendations]]


async def recommend_outfits_for_occasion_service(
    db: Session,
    user: schemas.User, 
    occasion: schemas.Occasion, # This is the TempOccasionContext from the router
    num_recommendations: int = 3
) -> List[schemas.Outfit]: 

    # Use occasion.name (event_type from input) and occasion.notes (combined details)
    # find_ai_matched_outfits_for_occasion expects occasion_name and occasion_notes separately
    db_outfits = find_ai_matched_outfits_for_occasion(
        db=db,
        user_id=user.id,
        occasion_name_from_input=occasion.name, 
        occasion_notes_from_input=occasion.notes if occasion.notes else "",
        num_recommendations=num_recommendations
    )

    recommendations = []
    for outfit_model in db_outfits:
        # The Outfit schema should be able to serialize from the SQLAlchemy model
        # Ensure that `schemas.Outfit.from_orm` or `model_validate` is configured correctly,
        # especially for nested items. The `joinedload` in the helper should make items available.
        try:
            recommendations.append(schemas.Outfit.model_validate(outfit_model))
        except Exception as e:
            logger.error(f"Error validating outfit model {outfit_model.id} for schema: {e}")
            # Optionally, skip this outfit or handle error
            continue

    return recommendations


async def get_wardrobe_recommendations_service(
    db: Session,
    user: schemas.User,
    num_recommendations: int = 5, # Max number of new outfit ideas
    latitude: Optional[float] = None,
    longitude: Optional[float] = None
) -> schemas.PersonalizedWardrobeSuggestions:

    weather_conditions: Optional[Dict[str, Any]] = None
    if latitude is not None and longitude is not None:
        # Assuming get_weather_data is async
        weather_conditions = await get_weather_data(latitude=latitude, longitude=longitude)
        # If get_weather_data is not async, call it directly:
        # weather_conditions = get_weather_data(latitude=latitude, longitude=longitude)

    user_items_query = db.query(models.WardrobeItem).filter(models.WardrobeItem.user_id == user.id)

    # Initial filtering based on very basic weather conditions if available
    # This is a simple approach. More advanced would involve scoring items.
    if weather_conditions:
        temp = weather_conditions.get("temperature_celsius")
        condition = weather_conditions.get("condition", "").lower()

        if temp is not None:
            if temp < 10: # Cold
                # Prioritize warmer clothes, allow layers
                # This example prioritizes by category or season, could also use tags
                user_items_query = user_items_query.filter(
                    or_(
                        models.WardrobeItem.category.in_(["Sweater", "Coat", "Jacket", "Outerwear", "Knitwear", "Hoodie", "Long-Sleeve"]),
                        models.WardrobeItem.season.in_(["Winter", "Autumn"]),
                        # Add tag-based filtering here if tags are well-defined for warmth
                    )
                )
            elif temp > 25: # Hot
                user_items_query = user_items_query.filter(
                    or_(
                        models.WardrobeItem.category.in_(["T-Shirt", "Shorts", "Tank Top", "Dress", "Skirt"]),
                        models.WardrobeItem.season.in_(["Summer", "Spring"]),
                    )
                )

        if "rain" in condition:
            # Further prioritize or filter for rain-proof items
            # This assumes 'Raincoat' category or a 'waterproof' tag exists
            # For simplicity, this example doesn't add a separate mandatory filter for rain anorak
            # but one could add an additional filter or boost scores of rain-appropriate items.
            pass # Placeholder for more specific rain logic, e.g. boosting raincoats

        if "snow" in condition:
            # Similar to cold, but could be more specific for snow gear
            user_items_query = user_items_query.filter(
                models.WardrobeItem.category.in_(["Winter Coat", "Insulated Jacket", "Boots", "Snow Pants"])
            )


    user_items = user_items_query.all()

    # Process items to ensure they have AI features (mocked if not present)
    processed_user_items: List[Dict[str, Any]] = []
    for item in user_items: # Corrected variable name from user_items_from_db
        # Use actual AI embedding if available, otherwise mock
        embedding = item.ai_embedding
        if embedding is None: # Check covers both missing attr and attr is None
            embedding = np.random.rand(512).tolist() # Example ViT-base embedding

        # Use actual AI dominant colors if available, otherwise mock
        ai_colors = item.ai_dominant_colors
        if ai_colors is None:
            ai_colors = random.sample(["#1A1A1A", "#FFFFFF", "#FF0000", "#00FF00", "#0000FF", "#F0F0F0"], k=2)

        # Ensure category is present, mock if not
        category = getattr(item, "category", None)
        if category is None:
            category = random.choice(["Tops", "Bottoms", "Shoes", "Accessories", "Outerwear"])

        processed_user_items.append({
            "id": item.id,
            "name": item.name,
            "image_url": item.image_url, # Keep other useful fields
            "category": category,
            "embedding": embedding,
            "colors": ai_colors,
            # Add other fields like item.ai_style if it were available and needed
        })

    new_outfit_ideas: List[str] = []

    # --- "New Outfit Ideas" Generation ---
    # Filter items that have necessary features for matching
    matchable_items = [item for item in processed_user_items if item.get("embedding") and item.get("colors") and item.get("category")]

    # Group items by category for easier selection
    items_by_category: Dict[str, List[Dict[str, Any]]] = {}
    for item in matchable_items:
        items_by_category.setdefault(item["category"], []).append(item)

    # Define typical outfit structures (e.g., top + bottom, top + bottom + shoes)
    # This is a simplified approach. More complex logic could handle more variations.
    outfit_structures = [
        ["Tops", "Bottoms"],
        ["Tops", "Bottoms", "Shoes"],
        ["Tops", "Bottoms", "Outerwear"],
    ]

    attempts_to_find_outfits = 15 # Try a number of times to generate diverse outfits
    generated_outfit_count = 0

    if len(matchable_items) >= 2: # Need at least 2 items to form an outfit
        for _ in range(attempts_to_find_outfits):
            if generated_outfit_count >= num_recommendations:
                break

            chosen_structure = random.choice(outfit_structures)
            current_outfit_items_features: List[Dict[str, Any]] = []
            current_outfit_item_names: List[str] = []

            possible_to_form = True
            for cat in chosen_structure:
                if items_by_category.get(cat):
                    chosen_item = random.choice(items_by_category[cat])
                    # Avoid choosing the same item twice if a category is listed multiple times (not in current structures)
                    if chosen_item["id"] not in [ci["id"] for ci in current_outfit_items_features]:
                        current_outfit_items_features.append(chosen_item)
                        current_outfit_item_names.append(chosen_item["name"])
                    else: # Could not find a unique item for this part of the structure
                        possible_to_form = False; break
                else: # Not enough items in a required category
                    possible_to_form = False; break

            if possible_to_form and len(current_outfit_items_features) >= 2:
                # Check if this specific combination of item names has been suggested already
                # Sort names to ensure order doesn't matter for uniqueness
                sorted_item_names = ", ".join(sorted(current_outfit_item_names))
                if any(sorted_item_names in idea for idea in new_outfit_ideas): # Basic check to avoid exact duplicates by name
                    continue

                score_details = outfit_matcher.calculate_compatibility_score(current_outfit_items_features)
                if score_details["score"] > 0.55: # Compatibility threshold
                    idea = (f"Try combining: {', '.join(current_outfit_item_names)} "
                            f"(Style: {score_details['style_cohesion_score']:.2f}, "
                            f"Color: {score_details['color_harmony_score']:.2f}, "
                            f"Overall: {score_details['score']:.2f})")
                    new_outfit_ideas.append(idea)
                    generated_outfit_count += 1

    if not new_outfit_ideas and matchable_items: # Fallback if no high-scoring outfits found
        new_outfit_ideas.append("Try experimenting with different combinations from your wardrobe! Use items from different categories like Tops, Bottoms, and Shoes.")


    # --- "Items to Acquire" Enhancement ---
    items_to_acquire_suggestions: List[str] = []
    user_categories_owned = {item["category"] for item in processed_user_items if item.get("category")}
    essential_categories = {"Tops", "Bottoms", "Shoes", "Outerwear"}
    missing_essentials = essential_categories - user_categories_owned

    for cat in missing_essentials:
        items_to_acquire_suggestions.append(f"Consider adding a versatile item to your '{cat}' collection (e.g., a neutral-colored {cat.lower()[:-1] if cat.endswith('s') else cat.lower()}).")

    # Basic trend integration placeholder (can be expanded if get_fashion_trends_service is ready)
    # try:
    #     trends_response = await get_fashion_trends_service(db, user) # Assuming it's async
    #     if trends_response and trends_response.trends:
    #         # Example: Suggest a trending item if user is missing its category
    #         for trend_item in trends_response.trends[:2]: # Check top 2 trends
    #             if trend_item.category in missing_essentials and len(items_to_acquire_suggestions) < 3:
    #                 items_to_acquire_suggestions.append(f"Fashion Highlight: '{trend_item.name}' ({trend_item.category}) is currently trending. This could be a great addition!")
    # except Exception as e:
    #     logger.error(f"Could not fetch fashion trends for recommendations: {e}")

    if not items_to_acquire_suggestions:
        items_to_acquire_suggestions.append("Your wardrobe essentials seem covered! Explore accessories to diversify your looks.")


    return schemas.PersonalizedWardrobeSuggestions(
        newOutfitIdeas=new_outfit_ideas[:num_recommendations],
        itemsToAcquire=items_to_acquire_suggestions[:3] # Limit acquisition suggestions
    )
