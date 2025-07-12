"""
Occasion-based recommendation service for Digital Wardrobe System
Provides intelligent outfit recommendations based on specific occasions and events
"""
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, time
from dataclasses import dataclass

from models.database_models import ClothingItemResponse, User
from services.database_service import db_service
from services.outfit_matching_service import outfit_matching_service
from services.weather_service import weather_service

logger = logging.getLogger(__name__)

@dataclass
class OccasionProfile:
    """Profile for a specific occasion with clothing requirements"""
    name: str
    formality_level: str
    dress_code: str
    required_items: List[str]
    recommended_items: List[str]
    avoid_items: List[str]
    preferred_colors: List[str]
    avoid_colors: List[str]
    preferred_fabrics: List[str]
    avoid_fabrics: List[str]
    style_preferences: List[str]
    special_considerations: List[str]
    time_of_day: Optional[str] = None
    season_considerations: Optional[str] = None

class OccasionRecommendationService:
    """Service for generating occasion-based outfit recommendations"""
    
    def __init__(self):
        # Define occasion profiles
        self.occasion_profiles = {
            "job_interview": OccasionProfile(
                name="Job Interview",
                formality_level="formal",
                dress_code="business_professional",
                required_items=["dress_shirt_or_blouse", "dress_pants_or_skirt", "blazer_or_suit_jacket", "dress_shoes"],
                recommended_items=["tie_or_scarf", "belt", "minimal_jewelry", "portfolio_bag"],
                avoid_items=["casual_shoes", "jeans", "t_shirts", "shorts", "flip_flops", "athletic_wear"],
                preferred_colors=["navy", "black", "gray", "white", "burgundy"],
                avoid_colors=["neon", "bright_pink", "orange", "lime_green"],
                preferred_fabrics=["wool", "cotton", "silk", "polyester_blend"],
                avoid_fabrics=["denim", "jersey", "fleece", "athletic_materials"],
                style_preferences=["conservative", "professional", "polished"],
                special_considerations=[
                    "Ensure clothes are well-fitted and pressed",
                    "Keep accessories minimal and professional",
                    "Choose closed-toe shoes",
                    "Avoid strong fragrances"
                ]
            ),
            
            "wedding_guest": OccasionProfile(
                name="Wedding Guest",
                formality_level="formal",
                dress_code="cocktail_to_formal",
                required_items=["dress_or_suit", "dress_shoes", "appropriate_undergarments"],
                recommended_items=["jewelry", "clutch_or_small_bag", "light_jacket_or_wrap"],
                avoid_items=["white_clothing", "black_clothing", "casual_shoes", "shorts", "flip_flops"],
                preferred_colors=["pastels", "jewel_tones", "navy", "burgundy", "forest_green"],
                avoid_colors=["white", "ivory", "cream", "black", "red"],
                preferred_fabrics=["silk", "chiffon", "crepe", "wool", "cotton_blend"],
                avoid_fabrics=["denim", "jersey", "athletic_materials"],
                style_preferences=["elegant", "sophisticated", "festive"],
                special_considerations=[
                    "Avoid white, ivory, or cream (bride's colors)",
                    "Avoid all black unless specified",
                    "Consider the venue and time of day",
                    "Dress appropriately for religious ceremonies"
                ]
            ),
            
            "business_meeting": OccasionProfile(
                name="Business Meeting",
                formality_level="business",
                dress_code="business_professional",
                required_items=["button_down_shirt", "dress_pants_or_skirt", "blazer", "dress_shoes"],
                recommended_items=["belt", "watch", "minimal_jewelry", "briefcase_or_bag"],
                avoid_items=["jeans", "sneakers", "t_shirts", "shorts", "flip_flops"],
                preferred_colors=["navy", "gray", "black", "white", "light_blue"],
                avoid_colors=["neon", "bright_colors", "overly_casual_patterns"],
                preferred_fabrics=["wool", "cotton", "silk", "polyester_blend"],
                avoid_fabrics=["denim", "jersey", "athletic_materials"],
                style_preferences=["professional", "conservative", "polished"],
                special_considerations=[
                    "Ensure professional appearance",
                    "Keep accessories minimal",
                    "Choose comfortable shoes for long meetings",
                    "Consider company culture"
                ]
            ),
            
            "casual_date": OccasionProfile(
                name="Casual Date",
                formality_level="smart_casual",
                dress_code="smart_casual",
                required_items=["nice_top", "jeans_or_casual_pants", "comfortable_shoes"],
                recommended_items=["light_jacket", "accessories", "nice_bag"],
                avoid_items=["overly_formal_wear", "athletic_wear", "flip_flops"],
                preferred_colors=["any_flattering_colors"],
                avoid_colors=["overly_bright_neon"],
                preferred_fabrics=["cotton", "denim", "silk", "knit"],
                avoid_fabrics=["athletic_materials", "overly_formal_fabrics"],
                style_preferences=["comfortable", "stylish", "approachable"],
                special_considerations=[
                    "Choose comfortable yet stylish clothing",
                    "Consider the date activity",
                    "Dress to feel confident",
                    "Avoid overdressing or underdressing"
                ]
            ),
            
            "gym_workout": OccasionProfile(
                name="Gym Workout",
                formality_level="very_casual",
                dress_code="athletic",
                required_items=["athletic_top", "athletic_bottoms", "athletic_shoes", "sports_bra"],
                recommended_items=["water_bottle", "towel", "gym_bag", "fitness_tracker"],
                avoid_items=["cotton_clothing", "jeans", "dress_shoes", "jewelry"],
                preferred_colors=["any_colors", "moisture_hiding_colors"],
                avoid_colors=["light_colors_that_show_sweat"],
                preferred_fabrics=["moisture_wicking", "polyester", "spandex", "athletic_blends"],
                avoid_fabrics=["cotton", "wool", "silk", "denim"],
                style_preferences=["functional", "comfortable", "breathable"],
                special_considerations=[
                    "Choose moisture-wicking fabrics",
                    "Ensure proper support for activities",
                    "Avoid cotton which retains moisture",
                    "Choose appropriate footwear for activity type"
                ]
            ),
            
            "dinner_party": OccasionProfile(
                name="Dinner Party",
                formality_level="smart_casual",
                dress_code="cocktail_casual",
                required_items=["nice_dress_or_outfit", "dress_shoes", "appropriate_undergarments"],
                recommended_items=["jewelry", "clutch", "light_jacket"],
                avoid_items=["overly_casual_wear", "athletic_wear", "flip_flops"],
                preferred_colors=["sophisticated_colors", "jewel_tones", "classic_colors"],
                avoid_colors=["overly_bright_neon", "white_if_not_appropriate"],
                preferred_fabrics=["silk", "wool", "cotton_blend", "crepe"],
                avoid_fabrics=["athletic_materials", "overly_casual_fabrics"],
                style_preferences=["elegant", "sophisticated", "social"],
                special_considerations=[
                    "Consider the host's style and venue",
                    "Dress appropriately for the time of day",
                    "Choose comfortable shoes for standing/socializing",
                    "Avoid overpowering the host"
                ]
            ),
            
            "beach_vacation": OccasionProfile(
                name="Beach Vacation",
                formality_level="very_casual",
                dress_code="resort_casual",
                required_items=["swimwear", "cover_up", "sandals", "sun_hat"],
                recommended_items=["sunglasses", "beach_bag", "flip_flops", "light_dress"],
                avoid_items=["heavy_fabrics", "dark_colors", "closed_shoes"],
                preferred_colors=["light_colors", "bright_colors", "tropical_prints"],
                avoid_colors=["dark_colors", "heavy_patterns"],
                preferred_fabrics=["cotton", "linen", "quick_dry", "UV_protective"],
                avoid_fabrics=["wool", "heavy_synthetics", "non_breathable"],
                style_preferences=["relaxed", "comfortable", "vacation_ready"],
                special_considerations=[
                    "Choose UV protective clothing",
                    "Pack light, breathable fabrics",
                    "Include swimwear and cover-ups",
                    "Don't forget sun protection accessories"
                ]
            ),
            
            "office_casual": OccasionProfile(
                name="Office Casual",
                formality_level="smart_casual",
                dress_code="business_casual",
                required_items=["collared_shirt_or_blouse", "chinos_or_dress_pants", "closed_toe_shoes"],
                recommended_items=["cardigan_or_blazer", "belt", "watch"],
                avoid_items=["jeans", "t_shirts", "sneakers", "flip_flops", "shorts"],
                preferred_colors=["neutral_colors", "muted_tones", "professional_colors"],
                avoid_colors=["neon", "overly_bright_colors"],
                preferred_fabrics=["cotton", "wool_blend", "polyester_blend"],
                avoid_fabrics=["denim", "athletic_materials", "overly_casual"],
                style_preferences=["professional", "comfortable", "polished_casual"],
                special_considerations=[
                    "Follow company dress code policy",
                    "Choose comfortable yet professional clothing",
                    "Keep it neat and well-fitted",
                    "Avoid overly casual items"
                ]
            ),
            
            "cocktail_party": OccasionProfile(
                name="Cocktail Party",
                formality_level="formal",
                dress_code="cocktail",
                required_items=["cocktail_dress_or_suit", "dress_shoes", "appropriate_undergarments"],
                recommended_items=["jewelry", "clutch", "wrap_or_jacket"],
                avoid_items=["casual_wear", "athletic_wear", "flip_flops", "overly_revealing_clothing"],
                preferred_colors=["sophisticated_colors", "jewel_tones", "black", "navy"],
                avoid_colors=["overly_casual_colors", "neon"],
                preferred_fabrics=["silk", "crepe", "wool", "chiffon"],
                avoid_fabrics=["denim", "jersey", "athletic_materials"],
                style_preferences=["elegant", "sophisticated", "party_appropriate"],
                special_considerations=[
                    "Dress for the venue and time",
                    "Choose comfortable shoes for standing",
                    "Keep accessories elegant but not overwhelming",
                    "Consider the party's theme if any"
                ]
            )
        }
    
    def get_occasion_recommendations(self, 
                                   user_id: str,
                                   occasion_name: str,
                                   weather_location: Optional[str] = None,
                                   specific_requirements: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get comprehensive outfit recommendations for a specific occasion"""
        try:
            # Get occasion profile
            occasion_profile = self.occasion_profiles.get(occasion_name.lower())
            if not occasion_profile:
                available_occasions = list(self.occasion_profiles.keys())
                return {
                    "error": f"Occasion '{occasion_name}' not found",
                    "available_occasions": available_occasions
                }
            
            # Get user's wardrobe
            user_items = db_service.get_clothing_items_by_user(user_id, limit=1000)
            if not user_items:
                return {
                    "error": "No clothing items found in wardrobe",
                    "occasion": occasion_profile.name
                }
            
            # Get weather data if location provided
            weather_data = None
            weather_recommendations = {}
            if weather_location:
                weather_data = weather_service.get_current_weather(weather_location)
                if weather_data:
                    weather_recommendations = weather_service.generate_weather_clothing_recommendations(weather_data)
            
            # Filter items based on occasion requirements
            suitable_items = self._filter_items_for_occasion(user_items, occasion_profile, weather_data)
            
            # Generate outfit combinations
            outfit_suggestions = self._generate_occasion_outfits(suitable_items, occasion_profile, weather_recommendations)
            
            # Prepare comprehensive recommendations
            recommendations = {
                "occasion": {
                    "name": occasion_profile.name,
                    "formality_level": occasion_profile.formality_level,
                    "dress_code": occasion_profile.dress_code
                },
                "outfit_suggestions": outfit_suggestions,
                "occasion_guidelines": {
                    "required_items": occasion_profile.required_items,
                    "recommended_items": occasion_profile.recommended_items,
                    "items_to_avoid": occasion_profile.avoid_items,
                    "preferred_colors": occasion_profile.preferred_colors,
                    "colors_to_avoid": occasion_profile.avoid_colors,
                    "preferred_fabrics": occasion_profile.preferred_fabrics,
                    "fabrics_to_avoid": occasion_profile.avoid_fabrics,
                    "style_preferences": occasion_profile.style_preferences,
                    "special_considerations": occasion_profile.special_considerations
                },
                "weather_considerations": weather_recommendations if weather_data else None,
                "missing_items": self._identify_missing_items(user_items, occasion_profile),
                "shopping_suggestions": self._generate_shopping_suggestions(user_items, occasion_profile)
            }
            
            # Apply specific requirements if provided
            if specific_requirements:
                recommendations = self._apply_specific_requirements(recommendations, specific_requirements)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating occasion recommendations: {e}")
            return {"error": str(e)}
    
    def _filter_items_for_occasion(self, 
                                  items: List[ClothingItemResponse], 
                                  occasion_profile: OccasionProfile,
                                  weather_data: Optional[Any] = None) -> Dict[str, List[ClothingItemResponse]]:
        """Filter clothing items suitable for the occasion"""
        try:
            suitable_items = {
                "highly_suitable": [],
                "suitable": [],
                "acceptable": [],
                "not_suitable": []
            }
            
            for item in items:
                if not item.is_available:
                    continue
                
                suitability_score = self._calculate_item_suitability(item, occasion_profile, weather_data)
                
                if suitability_score >= 0.8:
                    suitable_items["highly_suitable"].append(item)
                elif suitability_score >= 0.6:
                    suitable_items["suitable"].append(item)
                elif suitability_score >= 0.4:
                    suitable_items["acceptable"].append(item)
                else:
                    suitable_items["not_suitable"].append(item)
            
            return suitable_items
            
        except Exception as e:
            logger.error(f"Error filtering items for occasion: {e}")
            return {"highly_suitable": [], "suitable": [], "acceptable": [], "not_suitable": []}
    
    def _calculate_item_suitability(self, 
                                   item: ClothingItemResponse, 
                                   occasion_profile: OccasionProfile,
                                   weather_data: Optional[Any] = None) -> float:
        """Calculate how suitable an item is for the occasion"""
        try:
            score = 0.5  # Base score
            
            # Check formality level compatibility
            if hasattr(item, 'clothing_type') and item.clothing_type:
                item_formality = item.clothing_type.formality_level
                formality_compatibility = self._get_formality_compatibility(item_formality, occasion_profile.formality_level)
                score += formality_compatibility * 0.3
            
            # Check color preferences
            if hasattr(item, 'primary_color') and item.primary_color:
                color_name = item.primary_color.name.lower()
                if any(preferred.lower() in color_name for preferred in occasion_profile.preferred_colors):
                    score += 0.2
                elif any(avoid.lower() in color_name for avoid in occasion_profile.avoid_colors):
                    score -= 0.3
            
            # Check item type requirements
            if hasattr(item, 'clothing_type') and item.clothing_type:
                item_type = item.clothing_type.name.lower()
                
                # Check if item is required
                if any(req.lower() in item_type for req in occasion_profile.required_items):
                    score += 0.3
                
                # Check if item is recommended
                elif any(rec.lower() in item_type for rec in occasion_profile.recommended_items):
                    score += 0.2
                
                # Check if item should be avoided
                elif any(avoid.lower() in item_type for avoid in occasion_profile.avoid_items):
                    score -= 0.4
            
            # Weather considerations
            if weather_data:
                weather_score = self._calculate_weather_suitability(item, weather_data)
                score += weather_score * 0.2
            
            # Ensure score is between 0 and 1
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Error calculating item suitability: {e}")
            return 0.5
    
    def _get_formality_compatibility(self, item_formality: str, occasion_formality: str) -> float:
        """Calculate compatibility between item and occasion formality levels"""
        formality_order = ["very_casual", "casual", "smart_casual", "business", "formal", "black_tie"]
        
        try:
            item_index = formality_order.index(item_formality)
            occasion_index = formality_order.index(occasion_formality)
            
            # Perfect match
            if item_index == occasion_index:
                return 1.0
            
            # Close match (1 level difference)
            elif abs(item_index - occasion_index) == 1:
                return 0.8
            
            # Acceptable match (2 levels difference)
            elif abs(item_index - occasion_index) == 2:
                return 0.5
            
            # Poor match
            else:
                return 0.2
                
        except ValueError:
            return 0.5  # Default if formality levels not found
    
    def _calculate_weather_suitability(self, item: ClothingItemResponse, weather_data: Any) -> float:
        """Calculate how suitable an item is for current weather"""
        try:
            # This is a simplified weather suitability calculation
            # In a real implementation, you'd analyze fabric, thickness, etc.
            
            temp_category = weather_data.get_temperature_category()
            
            # Get item features for weather analysis
            features = db_service.get_clothing_features(item.id)
            if features and features.style_features:
                season_info = features.style_features.get('season', {})
                if isinstance(season_info, dict):
                    primary_season = season_info.get('primary_season', 'all_seasons')
                    
                    # Simple season-temperature mapping
                    if temp_category in ["extremely_cold", "very_cold"] and primary_season == "winter":
                        return 0.8
                    elif temp_category in ["hot", "extremely_hot"] and primary_season == "summer":
                        return 0.8
                    elif temp_category in ["cool", "mild"] and primary_season in ["spring", "fall"]:
                        return 0.8
                    elif primary_season == "all_seasons":
                        return 0.6
                    else:
                        return 0.3
            
            return 0.5  # Default score
            
        except Exception as e:
            logger.error(f"Error calculating weather suitability: {e}")
            return 0.5
    
    def _generate_occasion_outfits(self, 
                                  suitable_items: Dict[str, List[ClothingItemResponse]], 
                                  occasion_profile: OccasionProfile,
                                  weather_recommendations: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate complete outfit suggestions for the occasion"""
        try:
            outfit_suggestions = []
            
            # Combine highly suitable and suitable items for outfit generation
            available_items = suitable_items["highly_suitable"] + suitable_items["suitable"]
            
            if len(available_items) < 2:
                # Not enough suitable items, include acceptable items
                available_items.extend(suitable_items["acceptable"])
            
            if len(available_items) < 2:
                return [{
                    "message": "Not enough suitable items found for this occasion",
                    "suggestion": "Consider adding more formal/appropriate clothing to your wardrobe"
                }]
            
            # Use the outfit matching service to generate combinations
            # For now, we'll create a simplified version
            outfit_suggestions = self._create_simple_outfit_combinations(available_items, occasion_profile)
            
            return outfit_suggestions[:5]  # Return top 5 suggestions
            
        except Exception as e:
            logger.error(f"Error generating occasion outfits: {e}")
            return []
    
    def _create_simple_outfit_combinations(self, 
                                         items: List[ClothingItemResponse], 
                                         occasion_profile: OccasionProfile) -> List[Dict[str, Any]]:
        """Create simple outfit combinations from available items"""
        try:
            # Group items by category
            items_by_category = {}
            for item in items:
                if hasattr(item, 'clothing_type') and item.clothing_type:
                    category = self._get_item_category(item.clothing_type.name)
                    if category not in items_by_category:
                        items_by_category[category] = []
                    items_by_category[category].append(item)
            
            outfit_suggestions = []
            
            # Generate basic outfit combinations
            if "tops" in items_by_category and "bottoms" in items_by_category:
                for top in items_by_category["tops"][:3]:  # Limit to top 3
                    for bottom in items_by_category["bottoms"][:3]:
                        outfit = {
                            "items": [
                                self._format_item_for_response(top),
                                self._format_item_for_response(bottom)
                            ],
                            "occasion_score": 0.8,
                            "reasoning": f"Classic {occasion_profile.dress_code} combination"
                        }
                        
                        # Add shoes if available
                        if "footwear" in items_by_category:
                            outfit["items"].append(self._format_item_for_response(items_by_category["footwear"][0]))
                        
                        # Add outerwear if available and appropriate
                        if "outerwear" in items_by_category and occasion_profile.formality_level in ["formal", "business"]:
                            outfit["items"].append(self._format_item_for_response(items_by_category["outerwear"][0]))
                        
                        outfit_suggestions.append(outfit)
            
            # Generate dress-based outfits
            if "dresses" in items_by_category:
                for dress in items_by_category["dresses"][:2]:
                    outfit = {
                        "items": [self._format_item_for_response(dress)],
                        "occasion_score": 0.9,
                        "reasoning": f"Elegant dress perfect for {occasion_profile.name.lower()}"
                    }
                    
                    # Add shoes if available
                    if "footwear" in items_by_category:
                        outfit["items"].append(self._format_item_for_response(items_by_category["footwear"][0]))
                    
                    outfit_suggestions.append(outfit)
            
            return outfit_suggestions
            
        except Exception as e:
            logger.error(f"Error creating outfit combinations: {e}")
            return []
    
    def _get_item_category(self, clothing_type_name: str) -> str:
        """Categorize clothing item for outfit building"""
        type_name = clothing_type_name.lower()
        
        if any(word in type_name for word in ["shirt", "blouse", "top", "sweater", "polo"]):
            return "tops"
        elif any(word in type_name for word in ["pants", "jeans", "skirt", "shorts", "trousers"]):
            return "bottoms"
        elif any(word in type_name for word in ["dress", "gown"]):
            return "dresses"
        elif any(word in type_name for word in ["jacket", "blazer", "coat", "cardigan"]):
            return "outerwear"
        elif any(word in type_name for word in ["shoes", "boots", "sneakers", "heels", "sandals"]):
            return "footwear"
        else:
            return "accessories"
    
    def _format_item_for_response(self, item: ClothingItemResponse) -> Dict[str, Any]:
        """Format clothing item for API response"""
        return {
            "id": item.id,
            "name": item.original_filename,
            "type": item.clothing_type.name if hasattr(item, 'clothing_type') and item.clothing_type else 'Unknown',
            "color": item.primary_color.name if hasattr(item, 'primary_color') and item.primary_color else 'Unknown',
            "brand": item.brand.name if hasattr(item, 'brand') and item.brand else None,
            "image_url": item.images[0].image_url if item.images else None
        }
    
    def _identify_missing_items(self, 
                               user_items: List[ClothingItemResponse], 
                               occasion_profile: OccasionProfile) -> List[str]:
        """Identify items missing from wardrobe for the occasion"""
        try:
            user_item_types = set()
            for item in user_items:
                if hasattr(item, 'clothing_type') and item.clothing_type:
                    user_item_types.add(item.clothing_type.name.lower())
            
            missing_items = []
            for required_item in occasion_profile.required_items:
                if not any(req_type in item_type for item_type in user_item_types for req_type in required_item.split('_')):
                    missing_items.append(required_item)
            
            return missing_items
            
        except Exception as e:
            logger.error(f"Error identifying missing items: {e}")
            return []
    
    def _generate_shopping_suggestions(self, 
                                     user_items: List[ClothingItemResponse], 
                                     occasion_profile: OccasionProfile) -> List[str]:
        """Generate shopping suggestions to complete the wardrobe for the occasion"""
        try:
            missing_items = self._identify_missing_items(user_items, occasion_profile)
            
            shopping_suggestions = []
            for missing_item in missing_items:
                suggestion = f"Consider adding a {missing_item.replace('_', ' ')} in {', '.join(occasion_profile.preferred_colors[:3])}"
                shopping_suggestions.append(suggestion)
            
            return shopping_suggestions
            
        except Exception as e:
            logger.error(f"Error generating shopping suggestions: {e}")
            return []
    
    def _apply_specific_requirements(self, 
                                   recommendations: Dict[str, Any], 
                                   specific_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Apply user-specific requirements to recommendations"""
        try:
            # This could include color preferences, budget constraints, etc.
            # For now, it's a placeholder for future enhancements
            
            if "preferred_colors" in specific_requirements:
                recommendations["occasion_guidelines"]["preferred_colors"] = specific_requirements["preferred_colors"]
            
            if "avoid_colors" in specific_requirements:
                recommendations["occasion_guidelines"]["colors_to_avoid"].extend(specific_requirements["avoid_colors"])
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error applying specific requirements: {e}")
            return recommendations
    
    def get_available_occasions(self) -> List[Dict[str, str]]:
        """Get list of available occasions with descriptions"""
        return [
            {
                "name": name,
                "display_name": profile.name,
                "formality_level": profile.formality_level,
                "dress_code": profile.dress_code,
                "description": f"{profile.name} - {profile.dress_code} dress code"
            }
            for name, profile in self.occasion_profiles.items()
        ]

# Global occasion recommendation service instance
occasion_recommendation_service = OccasionRecommendationService()

