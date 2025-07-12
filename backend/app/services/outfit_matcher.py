# Enhanced Outfit Matching and Recommendation System
# This module provides advanced outfit matching algorithms and personalized recommendations

import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import colorsys
import re

logger = logging.getLogger(__name__)

class OccasionType(Enum):
    CASUAL = "casual"
    FORMAL = "formal"
    BUSINESS = "business"
    PARTY = "party"
    WEDDING = "wedding"
    CHURCH = "church"
    OUTDOOR = "outdoor"
    DATE = "date"
    WORKOUT = "workout"
    HOME = "home"

class SeasonType(Enum):
    SPRING = "spring"
    SUMMER = "summer"
    FALL = "fall"
    WINTER = "winter"

class WeatherType(Enum):
    SUNNY = "sunny"
    RAINY = "rainy"
    CLOUDY = "cloudy"
    SNOWY = "snowy"
    WINDY = "windy"

@dataclass
class ClothingItem:
    id: str
    name: str
    category: str  # top, bottom, shoes, accessory, outerwear
    color: str
    style: str
    occasion_suitability: List[OccasionType]
    season_suitability: List[SeasonType]
    weather_suitability: List[WeatherType]
    formality_level: int  # 1-10 scale
    comfort_level: int  # 1-10 scale
    tags: List[str]

@dataclass
class OutfitRecommendation:
    items: List[ClothingItem]
    occasion: OccasionType
    season: SeasonType
    weather: WeatherType
    confidence_score: float
    style_description: str
    matching_explanation: str
    tips: List[str]

class ColorMatcher:
    """Advanced color matching and harmony detection"""
    
    @staticmethod
    def hex_to_hsv(hex_color: str) -> Tuple[float, float, float]:
        """Convert hex color to HSV"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
    
    @staticmethod
    def hsv_to_hex(h: float, s: float, v: float) -> str:
        """Convert HSV to hex color"""
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
    
    @staticmethod
    def get_complementary_colors(hex_color: str) -> List[str]:
        """Get complementary colors for a given color"""
        h, s, v = ColorMatcher.hex_to_hsv(hex_color)
        
        # Complementary (opposite on color wheel)
        comp_h = (h + 0.5) % 1.0
        complementary = ColorMatcher.hsv_to_hex(comp_h, s, v)
        
        # Analogous colors (adjacent on color wheel)
        analog1_h = (h + 0.083) % 1.0  # +30 degrees
        analog2_h = (h - 0.083) % 1.0  # -30 degrees
        analogous1 = ColorMatcher.hsv_to_hex(analog1_h, s, v)
        analogous2 = ColorMatcher.hsv_to_hex(analog2_h, s, v)
        
        # Triadic colors
        triad1_h = (h + 0.333) % 1.0  # +120 degrees
        triad2_h = (h + 0.667) % 1.0  # +240 degrees
        triadic1 = ColorMatcher.hsv_to_hex(triad1_h, s, v)
        triadic2 = ColorMatcher.hsv_to_hex(triad2_h, s, v)
        
        return [complementary, analogous1, analogous2, triadic1, triadic2]
    
    @staticmethod
    def calculate_color_harmony(color1: str, color2: str) -> float:
        """Calculate harmony score between two colors (0-1)"""
        h1, s1, v1 = ColorMatcher.hex_to_hsv(color1)
        h2, s2, v2 = ColorMatcher.hex_to_hsv(color2)
        
        # Hue difference
        hue_diff = min(abs(h1 - h2), 1 - abs(h1 - h2))
        
        # Saturation and value similarity
        sat_diff = abs(s1 - s2)
        val_diff = abs(v1 - v2)
        
        # Calculate harmony based on color theory
        if hue_diff < 0.05:  # Very similar hues (monochromatic)
            harmony = 0.9 - (sat_diff + val_diff) * 0.5
        elif 0.45 < hue_diff < 0.55:  # Complementary
            harmony = 0.8 - (sat_diff + val_diff) * 0.3
        elif 0.08 < hue_diff < 0.12:  # Analogous
            harmony = 0.85 - (sat_diff + val_diff) * 0.4
        elif 0.3 < hue_diff < 0.37 or 0.63 < hue_diff < 0.7:  # Triadic
            harmony = 0.75 - (sat_diff + val_diff) * 0.3
        else:
            harmony = 0.5 - (sat_diff + val_diff) * 0.5
        
        return max(0, min(1, harmony))

class StyleMatcher:
    """Advanced style matching and compatibility detection"""
    
    STYLE_COMPATIBILITY = {
        "casual": ["casual", "bohemian", "sporty", "streetwear"],
        "formal": ["formal", "business", "classic", "elegant"],
        "business": ["business", "formal", "professional", "classic"],
        "bohemian": ["bohemian", "casual", "vintage", "artistic"],
        "vintage": ["vintage", "classic", "retro", "bohemian"],
        "modern": ["modern", "minimalist", "contemporary", "sleek"],
        "minimalist": ["minimalist", "modern", "clean", "simple"],
        "edgy": ["edgy", "punk", "gothic", "alternative"],
        "romantic": ["romantic", "feminine", "soft", "elegant"],
        "sporty": ["sporty", "athletic", "casual", "active"]
    }
    
    @staticmethod
    def calculate_style_compatibility(style1: str, style2: str) -> float:
        """Calculate compatibility score between two styles (0-1)"""
        style1_lower = style1.lower()
        style2_lower = style2.lower()
        
        if style1_lower == style2_lower:
            return 1.0
        
        compatible_styles = StyleMatcher.STYLE_COMPATIBILITY.get(style1_lower, [])
        if style2_lower in compatible_styles:
            return 0.8
        
        # Check reverse compatibility
        compatible_styles_reverse = StyleMatcher.STYLE_COMPATIBILITY.get(style2_lower, [])
        if style1_lower in compatible_styles_reverse:
            return 0.8
        
        # Check for partial matches
        for style in compatible_styles:
            if style in style2_lower or style2_lower in style:
                return 0.6
        
        return 0.3  # Default low compatibility

class OutfitMatcher:
    """Main outfit matching and recommendation engine"""
    
    def __init__(self):
        self.color_matcher = ColorMatcher()
        self.style_matcher = StyleMatcher()
    
    def find_matching_items(self, base_item: ClothingItem, wardrobe: List[ClothingItem], 
                          occasion: OccasionType, season: SeasonType, 
                          weather: WeatherType) -> List[ClothingItem]:
        """Find items that match well with a base item"""
        matching_items = []
        
        for item in wardrobe:
            if item.id == base_item.id:
                continue
            
            # Check if item is suitable for the occasion, season, and weather
            if (occasion not in item.occasion_suitability or 
                season not in item.season_suitability or 
                weather not in item.weather_suitability):
                continue
            
            # Calculate matching score
            score = self._calculate_item_compatibility(base_item, item)
            
            if score > 0.6:  # Threshold for good matches
                matching_items.append((item, score))
        
        # Sort by score and return items
        matching_items.sort(key=lambda x: x[1], reverse=True)
        return [item for item, score in matching_items]
    
    def _calculate_item_compatibility(self, item1: ClothingItem, item2: ClothingItem) -> float:
        """Calculate compatibility score between two items"""
        # Color harmony
        color_score = self.color_matcher.calculate_color_harmony(item1.color, item2.color)
        
        # Style compatibility
        style_score = self.style_matcher.calculate_style_compatibility(item1.style, item2.style)
        
        # Formality level compatibility
        formality_diff = abs(item1.formality_level - item2.formality_level)
        formality_score = max(0, 1 - formality_diff / 10)
        
        # Category compatibility (avoid conflicts)
        category_score = 1.0
        if item1.category == item2.category and item1.category not in ["accessory"]:
            category_score = 0.0  # Can't wear two tops, bottoms, etc.
        
        # Weighted average
        total_score = (
            color_score * 0.3 +
            style_score * 0.3 +
            formality_score * 0.2 +
            category_score * 0.2
        )
        
        return total_score
    
    def create_complete_outfit(self, wardrobe: List[ClothingItem], 
                             occasion: OccasionType, season: SeasonType, 
                             weather: WeatherType, 
                             preferred_style: Optional[str] = None) -> OutfitRecommendation:
        """Create a complete outfit recommendation"""
        
        # Filter items suitable for the context
        suitable_items = [
            item for item in wardrobe
            if (occasion in item.occasion_suitability and
                season in item.season_suitability and
                weather in item.weather_suitability)
        ]
        
        if not suitable_items:
            return self._create_fallback_recommendation(occasion, season, weather)
        
        # Group items by category
        categories = {}
        for item in suitable_items:
            if item.category not in categories:
                categories[item.category] = []
            categories[item.category].append(item)
        
        # Try to build outfit with required categories
        required_categories = ["top", "bottom", "shoes"]
        optional_categories = ["outerwear", "accessory"]
        
        best_outfit = None
        best_score = 0
        
        # Generate outfit combinations
        for top in categories.get("top", []):
            for bottom in categories.get("bottom", []):
                for shoes in categories.get("shoes", []):
                    outfit_items = [top, bottom, shoes]
                    
                    # Add outerwear if weather requires it
                    if weather in [WeatherType.RAINY, WeatherType.SNOWY, WeatherType.WINDY]:
                        outerwear_options = categories.get("outerwear", [])
                        if outerwear_options:
                            best_outerwear = max(outerwear_options, 
                                               key=lambda x: self._calculate_outfit_score(outfit_items + [x]))
                            outfit_items.append(best_outerwear)
                    
                    # Add accessories
                    accessory_options = categories.get("accessory", [])
                    if accessory_options:
                        best_accessory = max(accessory_options[:2],  # Limit to 2 accessories
                                           key=lambda x: self._calculate_outfit_score(outfit_items + [x]))
                        outfit_items.append(best_accessory)
                    
                    # Calculate outfit score
                    score = self._calculate_outfit_score(outfit_items)
                    
                    if score > best_score:
                        best_score = score
                        best_outfit = outfit_items
        
        if best_outfit:
            return self._create_outfit_recommendation(best_outfit, occasion, season, weather, best_score)
        else:
            return self._create_fallback_recommendation(occasion, season, weather)
    
    def _calculate_outfit_score(self, items: List[ClothingItem]) -> float:
        """Calculate overall score for an outfit"""
        if len(items) < 2:
            return 0
        
        total_score = 0
        comparisons = 0
        
        # Calculate pairwise compatibility
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                score = self._calculate_item_compatibility(items[i], items[j])
                total_score += score
                comparisons += 1
        
        if comparisons == 0:
            return 0
        
        return total_score / comparisons
    
    def _create_outfit_recommendation(self, items: List[ClothingItem], 
                                    occasion: OccasionType, season: SeasonType, 
                                    weather: WeatherType, score: float) -> OutfitRecommendation:
        """Create an outfit recommendation object"""
        
        # Generate style description
        styles = [item.style for item in items]
        dominant_style = max(set(styles), key=styles.count)
        
        # Generate matching explanation
        colors = [item.color for item in items]
        color_harmony = "harmonious" if score > 0.7 else "complementary"
        
        explanation = f"This outfit combines {dominant_style} style with {color_harmony} colors."
        
        # Generate tips
        tips = []
        if weather == WeatherType.RAINY:
            tips.append("Consider bringing an umbrella or waterproof jacket.")
        if occasion == OccasionType.FORMAL:
            tips.append("Ensure all items are well-pressed and clean.")
        if season == SeasonType.SUMMER:
            tips.append("Choose breathable fabrics and lighter colors.")
        
        return OutfitRecommendation(
            items=items,
            occasion=occasion,
            season=season,
            weather=weather,
            confidence_score=score,
            style_description=f"{dominant_style.title()} {occasion.value.title()}",
            matching_explanation=explanation,
            tips=tips
        )
    
    def _create_fallback_recommendation(self, occasion: OccasionType, 
                                      season: SeasonType, 
                                      weather: WeatherType) -> OutfitRecommendation:
        """Create a fallback recommendation when no suitable items are found"""
        return OutfitRecommendation(
            items=[],
            occasion=occasion,
            season=season,
            weather=weather,
            confidence_score=0.0,
            style_description="No suitable outfit found",
            matching_explanation="No items in wardrobe match the specified criteria.",
            tips=["Consider adding more versatile pieces to your wardrobe."]
        )

# Weather-based recommendations
class WeatherRecommendationEngine:
    """Provides weather-specific outfit recommendations"""
    
    WEATHER_GUIDELINES = {
        WeatherType.SUNNY: {
            "colors": ["light", "bright", "pastel"],
            "fabrics": ["cotton", "linen", "breathable"],
            "accessories": ["sunglasses", "hat", "light scarf"],
            "tips": ["Protect from UV rays", "Choose breathable fabrics"]
        },
        WeatherType.RAINY: {
            "colors": ["dark", "waterproof"],
            "fabrics": ["waterproof", "quick-dry", "synthetic"],
            "accessories": ["umbrella", "waterproof shoes", "rain jacket"],
            "tips": ["Avoid light colors", "Choose waterproof materials"]
        },
        WeatherType.SNOWY: {
            "colors": ["dark", "warm"],
            "fabrics": ["wool", "fleece", "insulated"],
            "accessories": ["warm hat", "gloves", "scarf", "boots"],
            "tips": ["Layer for warmth", "Choose insulated footwear"]
        },
        WeatherType.WINDY: {
            "colors": ["any"],
            "fabrics": ["structured", "heavier"],
            "accessories": ["secure hat", "closed shoes"],
            "tips": ["Avoid loose items", "Choose structured pieces"]
        }
    }
    
    @staticmethod
    def get_weather_recommendations(weather: WeatherType, temperature: Optional[int] = None) -> Dict[str, Any]:
        """Get weather-specific recommendations"""
        base_recommendations = WeatherRecommendationEngine.WEATHER_GUIDELINES.get(weather, {})
        
        # Add temperature-specific recommendations
        if temperature is not None:
            if temperature < 32:  # Freezing
                base_recommendations["additional_tips"] = ["Layer heavily", "Protect extremities"]
            elif temperature < 50:  # Cold
                base_recommendations["additional_tips"] = ["Add warm layers", "Consider outerwear"]
            elif temperature > 80:  # Hot
                base_recommendations["additional_tips"] = ["Choose minimal layers", "Prioritize cooling"]
        
        return base_recommendations

# Usage example
def create_sample_wardrobe() -> List[ClothingItem]:
    """Create a sample wardrobe for testing"""
    return [
        ClothingItem(
            id="1", name="White Button Shirt", category="top", color="#FFFFFF",
            style="classic", occasion_suitability=[OccasionType.BUSINESS, OccasionType.FORMAL],
            season_suitability=[SeasonType.SPRING, SeasonType.SUMMER, SeasonType.FALL],
            weather_suitability=[WeatherType.SUNNY, WeatherType.CLOUDY],
            formality_level=8, comfort_level=7, tags=["versatile", "professional"]
        ),
        ClothingItem(
            id="2", name="Dark Jeans", category="bottom", color="#2F4F4F",
            style="casual", occasion_suitability=[OccasionType.CASUAL, OccasionType.DATE],
            season_suitability=[SeasonType.SPRING, SeasonType.FALL, SeasonType.WINTER],
            weather_suitability=[WeatherType.SUNNY, WeatherType.CLOUDY, WeatherType.WINDY],
            formality_level=4, comfort_level=9, tags=["versatile", "comfortable"]
        ),
        ClothingItem(
            id="3", name="Black Dress Shoes", category="shoes", color="#000000",
            style="formal", occasion_suitability=[OccasionType.BUSINESS, OccasionType.FORMAL],
            season_suitability=[SeasonType.SPRING, SeasonType.SUMMER, SeasonType.FALL],
            weather_suitability=[WeatherType.SUNNY, WeatherType.CLOUDY],
            formality_level=9, comfort_level=6, tags=["professional", "elegant"]
        )
    ]

if __name__ == "__main__":
    # Test the outfit matching system
    matcher = OutfitMatcher()
    sample_wardrobe = create_sample_wardrobe()
    
    recommendation = matcher.create_complete_outfit(
        wardrobe=sample_wardrobe,
        occasion=OccasionType.BUSINESS,
        season=SeasonType.SPRING,
        weather=WeatherType.SUNNY
    )
    
    logger.info(f"Outfit recommendation: {recommendation.style_description}")
    logger.info(f"Confidence: {recommendation.confidence_score:.2f}")
    logger.info(f"Items: {[item.name for item in recommendation.items]}")

