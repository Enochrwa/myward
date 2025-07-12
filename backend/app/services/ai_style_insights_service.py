import logging
from sqlalchemy.orm import Session
from typing import List, Optional, Dict

from .. import model as models
from .. import tables as schemas

logger = logging.getLogger(__name__)

def get_user_style_profile(db: Session, user: models.User) -> schemas.UserStyleProfileResponse:
    """
    Generates a style profile response for a given user, combining stored preferences
    with basic generated insights.
    """
    logger.info(f"Generating style profile for user_id: {user.id}")

    profile_data = schemas.StyleProfileData()
    generated_insights = schemas.StyleProfileInsights()

    user_db_profile = user.profile  # This is of type models.UserProfile

    if user_db_profile:
        logger.debug(f"User profile found for user_id: {user.id}")
        # Populate StyleProfileData
        if user_db_profile.preferred_styles:
            profile_data.primary_style = user_db_profile.preferred_styles[0] if user_db_profile.preferred_styles else None
            if len(user_db_profile.preferred_styles) > 1:
                profile_data.secondary_styles = user_db_profile.preferred_styles[1:]
            else:
                profile_data.secondary_styles = []
        else:
            profile_data.primary_style = None
            profile_data.secondary_styles = []

        profile_data.color_preferences = user_db_profile.preferred_colors if user_db_profile.preferred_colors else []

        # Placeholder logic for body_type from sizes
        if user_db_profile.sizes:
            sizes_str = ", ".join([f"{k.capitalize()}: {v}" for k, v in user_db_profile.sizes.items() if v])
            profile_data.body_type = f"Sizes: {sizes_str}" if sizes_str else "Not specified"
        else:
            profile_data.body_type = "Not specified"

        # Fields not directly in models.UserProfile, set to defaults
        profile_data.lifestyle = "Not specified" # Or None / [] as appropriate per schema
        profile_data.brand_alignment = []
        profile_data.fashion_goals = []

    else:
        logger.debug(f"No user profile found for user_id: {user.id}. Using default StyleProfileData.")
        # Set defaults for profile_data if no user_db_profile
        profile_data.primary_style = None
        profile_data.secondary_styles = []
        profile_data.color_preferences = []
        profile_data.body_type = "Not specified"
        profile_data.lifestyle = "Not specified"
        profile_data.brand_alignment = []
        profile_data.fashion_goals = []

    # Populate StyleProfileInsights with placeholder/basic data
    generated_insights.style_confidence_score = 0.75 # Placeholder
    generated_insights.wardrobe_versatility_score = 0.60 # Placeholder

    summary_parts = []
    if profile_data.primary_style:
        summary_parts.append(f"Prefers {profile_data.primary_style} style")
    if profile_data.color_preferences:
        summary_parts.append(f"likes colors such as {profile_data.color_preferences[0]}")

    if summary_parts:
        generated_insights.style_summary = ", and ".join(summary_parts) + "."
    else:
        generated_insights.style_summary = "User has not specified style preferences."

    logger.info(f"Successfully generated style profile for user_id: {user.id}")

    return schemas.UserStyleProfileResponse(
        profile_data=profile_data,
        generated_insights=generated_insights
    )

def get_wardrobe_analysis_details(db: Session, user: models.User) -> schemas.WardrobeAnalysisDetails:
    """
    Analyzes a user's wardrobe items to provide detailed statistics and insights.
    """
    logger.info(f"Starting wardrobe analysis for user_id: {user.id}")

    user_items = db.query(models.WardrobeItem).filter(models.WardrobeItem.user_id == user.id).all()

    total_items = len(user_items)
    logger.debug(f"Total items found: {total_items} for user_id: {user.id}")

    category_breakdown: Dict[str, int] = {}
    color_distribution: Dict[str, int] = {}
    total_price_sum = 0
    items_with_price_count = 0
    brands = set()

    for item in user_items:
        # Category breakdown
        category_breakdown[item.category] = category_breakdown.get(item.category, 0) + 1

        # Color distribution
        if item.ai_dominant_colors: # Check if list is not None and not empty
            for color in item.ai_dominant_colors:
                color_distribution[color] = color_distribution.get(color, 0) + 1

        # Average item price
        if item.price is not None:
            total_price_sum += item.price
            items_with_price_count += 1

        # Brand diversity
        if item.brand:
            brands.add(item.brand.lower()) # Normalize brand names for counting

    average_item_price = None
    if items_with_price_count > 0:
        average_item_price = total_price_sum / items_with_price_count
    else:
        logger.debug(f"No items with price found for user_id: {user.id}, average_item_price is None.")

    brand_diversity_score = 0.0
    if total_items > 0:
        unique_brands_count = len(brands)
        brand_diversity_score = round(unique_brands_count / total_items, 2) if total_items > 0 else 0.5 # Placeholder if no items
        # Simple ratio, could be more complex e.g. normalized score
    else: # No items, so score is somewhat arbitrary, let's say 0.0 or 0.5 if that implies potential
        brand_diversity_score = 0.0


    style_consistency_score = 0.65  # Placeholder

    wardrobe_gaps = []
    essential_categories = {
        "Tops": 5, "Bottoms": 4, "Outerwear": 2, "Shoes": 3,
        "Formal Wear": 1, "Casual Dress": 2, "Accessories": 5
    } # Category: minimum desired count

    for cat, min_count in essential_categories.items():
        if category_breakdown.get(cat, 0) < min_count:
            wardrobe_gaps.append(f"Consider adding more '{cat}'. You have {category_breakdown.get(cat, 0)}, ideally {min_count}+.")

    if not user_items and not wardrobe_gaps: # If no items at all
        wardrobe_gaps.append("Your wardrobe is empty! Start by adding some essential items.")


    improvement_suggestions = [
        "Explore items in your preferred colors but new categories to diversify your options.",
        "Consider items that can bridge your primary and secondary styles if you have defined them.",
        "Regularly review items you haven't worn in a while."
    ]
    if average_item_price is not None and average_item_price > 200: # Example condition
        improvement_suggestions.append("You have some high-value items. Ensure they are versatile.")
    if brand_diversity_score < 0.3 and total_items > 10: # Example condition
        improvement_suggestions.append("Consider exploring new brands to diversify your style sources.")


    logger.info(f"Completed wardrobe analysis for user_id: {user.id}")

    return schemas.WardrobeAnalysisDetails(
        total_items=total_items,
        category_breakdown=category_breakdown,
        color_distribution=color_distribution,
        average_item_price=average_item_price,
        brand_diversity_score=brand_diversity_score, # Placeholder
        style_consistency_score=style_consistency_score, # Placeholder
        wardrobe_gaps=wardrobe_gaps, # Placeholder
        improvement_suggestions=improvement_suggestions # Placeholder
    )

def generate_personalized_general_insights(
    user_style_profile: schemas.UserStyleProfileResponse,
    wardrobe_analysis: schemas.WardrobeAnalysisDetails
) -> List[schemas.PersonalizedGeneralInsight]:
    """
    Generates a list of personalized general insights based on user profile and wardrobe analysis.
    (Placeholder implementation)
    """
    logger.info(f"Generating personalized general insights for primary style: {user_style_profile.profile_data.primary_style}")
    insights = []

    # Example 1: Style Focus
    if user_style_profile.profile_data.primary_style:
        insights.append(schemas.PersonalizedGeneralInsight(
            id="style_tip_1",
            insight_type="style",
            title="Embrace Your Primary Style",
            description=f"Your primary style is {user_style_profile.profile_data.primary_style}. Focus on finding key pieces that exemplify this.",
            actionable_advice=f"Look for items tagged or described as '{user_style_profile.profile_data.primary_style}' when shopping.",
            confidence_score=0.8,
            impact_level="high"
        ))

    # Example 2: Color Focus
    if user_style_profile.profile_data.color_preferences:
        preferred_colors_str = ', '.join(user_style_profile.profile_data.color_preferences[:2])
        insights.append(schemas.PersonalizedGeneralInsight(
            id="color_tip_1",
            insight_type="color",
            title="Leverage Preferred Colors",
            description=f"You prefer colors like {preferred_colors_str}. These can form the base of many versatile outfits.",
            actionable_advice="Build a core wardrobe around these colors and use accent colors for variety.",
            confidence_score=0.75,
            impact_level="medium"
        ))
    else: # Fallback if no color preferences
        insights.append(schemas.PersonalizedGeneralInsight(
            id="color_tip_generic_1",
            insight_type="color",
            title="Discover Your Color Palette",
            description="Understanding which colors complement your skin tone and personal taste can elevate your style.",
            actionable_advice="Experiment with different color groups or consider a professional color analysis.",
            confidence_score=0.70,
            impact_level="medium"
        ))


    # Example 3: Wardrobe Gap Focus
    if wardrobe_analysis.wardrobe_gaps:
        first_gap = wardrobe_analysis.wardrobe_gaps[0]
        # Extract the category name from the gap message for cleaner advice
        gap_category_name = first_gap.split("'")[1] if "'" in first_gap else "an identified area"

        insights.append(schemas.PersonalizedGeneralInsight(
            id="gap_tip_1",
            insight_type="wardrobe_balance",
            title="Address Wardrobe Gaps",
            description=f"Your wardrobe analysis shows a potential gap: {first_gap}.",
            actionable_advice=f"Consider looking for items to fill your '{gap_category_name}' category to increase versatility.",
            confidence_score=0.7,
            impact_level="medium"
        ))

    logger.info(f"Generated {len(insights)} personalized general insights.")
    return insights

def generate_ai_style_outfit_recommendations(
    db: Session,
    user: models.User,
    user_style_profile: schemas.UserStyleProfileResponse,
    wardrobe_analysis: schemas.WardrobeAnalysisDetails,
    num_outfits: int = 3
) -> List[schemas.AIStyleInsightOutfitRecommendation]:
    """
    Generates a list of AI-powered outfit recommendations.
    (Placeholder implementation - uses recent items to form simple outfits)
    """
    logger.info(f"Generating {num_outfits} AI style outfit recommendations for user_id: {user.id}")

    # Fetch some items to form recommendations (e.g., most recent or favorites)
    # For this placeholder, let's take up to num_outfits * 2 most recently added items
    # In a real scenario, this would involve more complex selection logic (e.g., based on embeddings, style, etc.)
    candidate_items_db = db.query(models.WardrobeItem)\
        .filter(models.WardrobeItem.user_id == user.id)\
        .order_by(models.WardrobeItem.date_added.desc())\
        .limit(num_outfits * 3) \
        .all()

    # Convert model instances to schema instances
    candidate_items_schema = [schemas.WardrobeItem.model_validate(item) for item in candidate_items_db]

    recommendations = []

    if not candidate_items_schema or len(candidate_items_schema) < 2:
        logger.warning(f"Not enough items ({len(candidate_items_schema)}) to generate diverse outfit recommendations for user_id: {user.id}.")
        if not candidate_items_schema:
             # Optionally, return a default message within a recommendation if no items at all
            recommendations.append(schemas.AIStyleInsightOutfitRecommendation(
                outfit_id=None,
                outfit_name="Add Items to Get Recommendations",
                description="Your wardrobe is currently empty. Add some items, and we'll start generating outfit ideas for you!",
                image_url=None,
                items=[],
                confidence_score=0.5,
                style_match_notes="N/A",
                occasion_suitability="Any"
            ))
            return recommendations
        # If only one item, could suggest finding a match for it, but for now, let's return empty if < 2
        return []


    for i in range(num_outfits):
        # Placeholder: try to pick 2-3 distinct items for an outfit
        # This is very basic and will likely pick the same items if not enough variety
        start_index = i % len(candidate_items_schema)
        item1 = candidate_items_schema[start_index]

        # Try to get a second distinct item from a different category if possible
        item2 = None
        for j in range(1, len(candidate_items_schema)):
            potential_item2 = candidate_items_schema[(start_index + j) % len(candidate_items_schema)]
            if potential_item2.id != item1.id and potential_item2.category != item1.category :
                item2 = potential_item2
                break
        if item2 is None and len(candidate_items_schema) > 1: # Fallback if no different category found but >1 items exist
             item2 = candidate_items_schema[(start_index + 1) % len(candidate_items_schema)] if candidate_items_schema[(start_index + 1) % len(candidate_items_schema)].id != item1.id else None


        current_outfit_items = [item1]
        if item2:
            current_outfit_items.append(item2)

        # Try to get a third distinct item if available and different category from item1 and item2
        item3 = None
        if len(candidate_items_schema) > 2 and item2:
            for k in range(1, len(candidate_items_schema)):
                potential_item3 = candidate_items_schema[(start_index + k + 1) % len(candidate_items_schema)] # Ensure different starting point
                if potential_item3.id != item1.id and potential_item3.id != item2.id and \
                   potential_item3.category != item1.category and potential_item3.category != item2.category:
                    item3 = potential_item3
                    break
            if item3:
                 current_outfit_items.append(item3)


        primary_style_text = user_style_profile.profile_data.primary_style if user_style_profile.profile_data.primary_style else "your unique"

        recommendations.append(schemas.AIStyleInsightOutfitRecommendation(
            outfit_id=None, # Not linking to an existing persisted Outfit
            outfit_name=f"AI Curated Look #{i+1}",
            description=f"A versatile look combining items that could align well with your {primary_style_text} style preferences.",
            image_url=current_outfit_items[0].image_url if current_outfit_items and current_outfit_items[0].image_url else None,
            items=current_outfit_items, # List of schemas.WardrobeItem
            confidence_score=round(0.7 + (i * 0.03), 2), # Slight variation
            style_match_notes=f"This outfit is suggested to complement your {primary_style_text} style.",
            occasion_suitability="Smart Casual" # Placeholder
        ))

    logger.info(f"Generated {len(recommendations)} AI style outfit recommendations for user_id: {user.id}.")
    return recommendations

# Example of how this might be expanded or used (for testing or further dev):
# def get_full_ai_style_insights(db: Session, user: models.User) -> schemas.FullAIStyleInsightsResponse:
#     user_style_profile = get_user_style_profile(db, user)
#
#     # Placeholder for WardrobeAnalysisDetails
#     wardrobe_analysis = schemas.WardrobeAnalysisDetails(
#         total_items=0, # Calculate this
#         category_breakdown={}, # Populate this
#         color_distribution={}, # Populate this
#         brand_diversity_score=0.5,
#         average_item_price=None,
#         style_consistency_score=0.6,
#         wardrobe_gaps=[],
#         improvement_suggestions=[]
#     )
#
#     # Placeholder for PersonalizedGeneralInsight
#     personalized_insights = [
#         schemas.PersonalizedGeneralInsight(
#             id="psi_001",
#             insight_type="style",
#             title="Embrace Your Primary Style",
#             description=f"Your primary style seems to be {user_style_profile.profile_data.primary_style}. Focus on pieces that align with this.",
#             actionable_advice="Look for key items that define this style.",
#             confidence_score=0.8,
#             impact_level="high"
#         )
#     ]
#
#     # Placeholder for AIStyleInsightOutfitRecommendation
#     suggested_outfits = [] # Populate with actual recommendations
#
#     return schemas.FullAIStyleInsightsResponse(
#         user_profile=user_style_profile,
#         wardrobe_analysis=wardrobe_analysis,
#         personalized_insights=personalized_insights,
#         suggested_outfits=suggested_outfits
#     )
