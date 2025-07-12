"""
Enhanced Intelligent Matching Algorithm for Digital Wardrobe System

This module implements an advanced matching algorithm that suggests compatible clothing items
based on color theory, style compatibility, occasion appropriateness, and user preferences.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sklearn.metrics.pairwise import cosine_similarity
from itertools import combinations
import colorsys
import logging

logger = logging.getLogger(__name__)

class ColorTheory:
    """Advanced color theory implementation for clothing matching"""
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            return (128, 128, 128)
        try:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except ValueError:
            return (128, 128, 128)
    
    @staticmethod
    def rgb_to_hsv(r: int, g: int, b: int) -> Tuple[float, float, float]:
        """Convert RGB to HSV for better color analysis"""
        return colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
    
    @staticmethod
    def get_color_temperature(hex_color: str) -> str:
        """Determine if color is warm, cool, or neutral"""
        r, g, b = ColorTheory.hex_to_rgb(hex_color)
        h, s, v = ColorTheory.rgb_to_hsv(r, g, b)
        
        # Convert hue to degrees
        hue_degrees = h * 360
        
        if s < 0.2:  # Low saturation = neutral
            return "neutral"
        elif 0 <= hue_degrees <= 60 or 300 <= hue_degrees <= 360:  # Red-Yellow range
            return "warm"
        elif 180 <= hue_degrees <= 300:  # Blue-Green range
            return "cool"
        else:
            return "neutral"
    
    @staticmethod
    def calculate_color_harmony_score(colors: List[str]) -> float:
        """Calculate harmony score based on advanced color theory"""
        if len(colors) < 2:
            return 1.0
        
        # Remove duplicates
        unique_colors = list(set(colors))
        if len(unique_colors) == 1:
            return 1.0
        
        harmony_score = 0.0
        total_comparisons = 0
        
        for i, color1 in enumerate(unique_colors):
            for color2 in unique_colors[i+1:]:
                score = ColorTheory._calculate_pair_harmony(color1, color2)
                harmony_score += score
                total_comparisons += 1
        
        return harmony_score / total_comparisons if total_comparisons > 0 else 0.0
    
    @staticmethod
    def _calculate_pair_harmony(color1: str, color2: str) -> float:
        """Calculate harmony score between two colors"""
        r1, g1, b1 = ColorTheory.hex_to_rgb(color1)
        r2, g2, b2 = ColorTheory.hex_to_rgb(color2)
        
        h1, s1, v1 = ColorTheory.rgb_to_hsv(r1, g1, b1)
        h2, s2, v2 = ColorTheory.rgb_to_hsv(r2, g2, b2)
        
        # Convert to degrees
        h1_deg, h2_deg = h1 * 360, h2 * 360
        
        # Calculate hue difference
        hue_diff = min(abs(h1_deg - h2_deg), 360 - abs(h1_deg - h2_deg))
        
        # Neutral colors (low saturation) are always harmonious
        if s1 < 0.2 or s2 < 0.2:
            return 0.95
        
        # Monochromatic (same hue, different saturation/value)
        if hue_diff < 15:
            return 0.9
        
        # Analogous colors (adjacent on color wheel)
        if hue_diff < 60:
            return 0.85
        
        # Complementary colors (opposite on color wheel)
        if 150 <= hue_diff <= 210:
            # Complementary can work but need balance
            saturation_balance = 1 - abs(s1 - s2)
            return 0.7 * saturation_balance
        
        # Triadic colors (120 degrees apart)
        if 100 <= hue_diff <= 140:
            return 0.65
        
        # Split complementary
        if 120 <= hue_diff <= 180:
            return 0.6
        
        # Default for other combinations
        return 0.5

class StyleCompatibility:
    """Style compatibility analysis for clothing items"""
    
    # Define style compatibility matrix
    STYLE_COMPATIBILITY = {
        "casual": ["casual", "smart-casual", "sporty", "bohemian"],
        "formal": ["formal", "business", "elegant", "classic"],
        "business": ["business", "formal", "smart-casual", "classic"],
        "smart-casual": ["smart-casual", "casual", "business", "classic"],
        "sporty": ["sporty", "casual", "athleisure"],
        "bohemian": ["bohemian", "casual", "vintage", "artistic"],
        "vintage": ["vintage", "classic", "bohemian", "retro"],
        "elegant": ["elegant", "formal", "classic", "sophisticated"],
        "classic": ["classic", "formal", "business", "elegant", "smart-casual"],
        "trendy": ["trendy", "casual", "smart-casual", "modern"],
        "artistic": ["artistic", "bohemian", "creative", "unique"],
        "minimalist": ["minimalist", "classic", "modern", "clean"]
    }
    
    @staticmethod
    def calculate_style_compatibility(style1: str, style2: str) -> float:
        """Calculate compatibility score between two styles"""
        style1_lower = style1.lower()
        style2_lower = style2.lower()
        
        if style1_lower == style2_lower:
            return 1.0
        
        compatible_styles = StyleCompatibility.STYLE_COMPATIBILITY.get(style1_lower, [])
        if style2_lower in compatible_styles:
            return 0.8
        
        # Check reverse compatibility
        compatible_styles_reverse = StyleCompatibility.STYLE_COMPATIBILITY.get(style2_lower, [])
        if style1_lower in compatible_styles_reverse:
            return 0.8
        
        return 0.3  # Low compatibility for unrelated styles

class OccasionMatcher:
    """Occasion-based clothing matching"""
    
    OCCASION_STYLES = {
        "wedding": {
            "preferred_styles": ["formal", "elegant", "classic"],
            "avoid_styles": ["casual", "sporty"],
            "formality_level": 0.9
        },
        "church": {
            "preferred_styles": ["formal", "business", "classic", "elegant"],
            "avoid_styles": ["casual", "sporty", "revealing"],
            "formality_level": 0.8
        },
        "home": {
            "preferred_styles": ["casual", "comfortable", "relaxed"],
            "avoid_styles": ["formal", "business"],
            "formality_level": 0.2
        },
        "casual": {
            "preferred_styles": ["casual", "smart-casual", "trendy"],
            "avoid_styles": ["formal", "business"],
            "formality_level": 0.3
        },
        "work": {
            "preferred_styles": ["business", "formal", "smart-casual", "classic"],
            "avoid_styles": ["casual", "sporty"],
            "formality_level": 0.7
        },
        "date": {
            "preferred_styles": ["smart-casual", "elegant", "trendy", "classic"],
            "avoid_styles": ["sporty", "too-casual"],
            "formality_level": 0.6
        },
        "party": {
            "preferred_styles": ["trendy", "elegant", "fun", "stylish"],
            "avoid_styles": ["business", "too-formal"],
            "formality_level": 0.5
        }
    }
    
    @staticmethod
    def calculate_occasion_score(item_style: str, occasion: str) -> float:
        """Calculate how well an item fits an occasion"""
        occasion_lower = occasion.lower()
        item_style_lower = item_style.lower()
        
        if occasion_lower not in OccasionMatcher.OCCASION_STYLES:
            return 0.5  # Neutral score for unknown occasions
        
        occasion_info = OccasionMatcher.OCCASION_STYLES[occasion_lower]
        
        # Check if style is preferred for this occasion
        if item_style_lower in occasion_info["preferred_styles"]:
            return 0.9
        
        # Check if style should be avoided
        if item_style_lower in occasion_info["avoid_styles"]:
            return 0.2
        
        # Calculate based on formality level
        style_formality = StyleCompatibility._get_style_formality(item_style_lower)
        occasion_formality = occasion_info["formality_level"]
        
        formality_diff = abs(style_formality - occasion_formality)
        return max(0.3, 1.0 - formality_diff)
    
    @staticmethod
    def _get_style_formality(style: str) -> float:
        """Get formality level of a style (0.0 = very casual, 1.0 = very formal)"""
        formality_map = {
            "formal": 0.9,
            "business": 0.8,
            "elegant": 0.85,
            "classic": 0.7,
            "smart-casual": 0.5,
            "casual": 0.3,
            "sporty": 0.2,
            "bohemian": 0.4,
            "trendy": 0.5,
            "artistic": 0.4,
            "minimalist": 0.6
        }
        return formality_map.get(style, 0.5)

class IntelligentMatchingAlgorithm:
    """Main intelligent matching algorithm that combines all factors"""
    
    def __init__(self):
        self.color_theory = ColorTheory()
        self.style_compatibility = StyleCompatibility()
        self.occasion_matcher = OccasionMatcher()
    
    def find_matching_items(
        self,
        target_item: Dict[str, Any],
        wardrobe_items: List[Dict[str, Any]],
        occasion: Optional[str] = None,
        user_preferences: Optional[Dict[str, Any]] = None,
        max_suggestions: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find items that match well with the target item
        
        Args:
            target_item: The item to find matches for
            wardrobe_items: List of available wardrobe items
            occasion: Optional occasion context
            user_preferences: Optional user style preferences
            max_suggestions: Maximum number of suggestions to return
        
        Returns:
            List of matching items with compatibility scores
        """
        matches = []
        
        for item in wardrobe_items:
            if item["id"] == target_item["id"]:
                continue  # Skip the target item itself
            
            compatibility_score = self._calculate_item_compatibility(
                target_item, item, occasion, user_preferences
            )
            
            if compatibility_score > 0.4:  # Minimum threshold
                matches.append({
                    **item,
                    "compatibility_score": compatibility_score,
                    "match_reasons": self._get_match_reasons(target_item, item, compatibility_score)
                })
        
        # Sort by compatibility score and return top matches
        matches.sort(key=lambda x: x["compatibility_score"], reverse=True)
        return matches[:max_suggestions]
    
    def _calculate_item_compatibility(
        self,
        item1: Dict[str, Any],
        item2: Dict[str, Any],
        occasion: Optional[str] = None,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> float:
        """Calculate overall compatibility score between two items"""
        
        # 1. Color compatibility (30% weight)
        colors1 = item1.get("colors", [])
        colors2 = item2.get("colors", [])
        all_colors = colors1 + colors2
        color_score = self.color_theory.calculate_color_harmony_score(all_colors)
        
        # 2. Style compatibility (25% weight)
        style1 = item1.get("style", "casual")
        style2 = item2.get("style", "casual")
        style_score = self.style_compatibility.calculate_style_compatibility(style1, style2)
        
        # 3. Category compatibility (20% weight)
        category_score = self._calculate_category_compatibility(
            item1.get("category", ""), item2.get("category", "")
        )
        
        # 4. Occasion appropriateness (15% weight)
        occasion_score = 1.0  # Default if no occasion specified
        if occasion:
            occasion_score1 = self.occasion_matcher.calculate_occasion_score(style1, occasion)
            occasion_score2 = self.occasion_matcher.calculate_occasion_score(style2, occasion)
            occasion_score = (occasion_score1 + occasion_score2) / 2
        
        # 5. User preference alignment (10% weight)
        preference_score = self._calculate_preference_score(item1, item2, user_preferences)
        
        # Weighted combination
        total_score = (
            color_score * 0.30 +
            style_score * 0.25 +
            category_score * 0.20 +
            occasion_score * 0.15 +
            preference_score * 0.10
        )
        
        return min(1.0, max(0.0, total_score))
    
    def _calculate_category_compatibility(self, category1: str, category2: str) -> float:
        """Calculate compatibility between clothing categories"""
        
        # Define compatible category combinations
        compatible_combinations = {
            ("tops", "bottoms"): 0.9,
            ("tops", "outerwear"): 0.8,
            ("bottoms", "shoes"): 0.8,
            ("tops", "accessories"): 0.7,
            ("bottoms", "accessories"): 0.7,
            ("outerwear", "accessories"): 0.6,
            ("shoes", "accessories"): 0.6,
        }
        
        cat1_lower = category1.lower()
        cat2_lower = category2.lower()
        
        # Check direct compatibility
        combo_key = tuple(sorted([cat1_lower, cat2_lower]))
        if combo_key in compatible_combinations:
            return compatible_combinations[combo_key]
        
        # Same category items usually don't match well together
        if cat1_lower == cat2_lower:
            return 0.3
        
        return 0.5  # Default compatibility
    
    def _calculate_preference_score(
        self,
        item1: Dict[str, Any],
        item2: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate score based on user preferences"""
        if not user_preferences:
            return 0.5  # Neutral score
        
        score = 0.5
        
        # Check preferred colors
        preferred_colors = user_preferences.get("preferred_colors", [])
        if preferred_colors:
            item_colors = item1.get("colors", []) + item2.get("colors", [])
            color_matches = sum(1 for color in item_colors if color in preferred_colors)
            if color_matches > 0:
                score += 0.2
        
        # Check preferred styles
        preferred_styles = user_preferences.get("preferred_styles", [])
        if preferred_styles:
            item_styles = [item1.get("style", ""), item2.get("style", "")]
            style_matches = sum(1 for style in item_styles if style in preferred_styles)
            if style_matches > 0:
                score += 0.2
        
        # Check avoided items
        avoided_colors = user_preferences.get("avoided_colors", [])
        if avoided_colors:
            item_colors = item1.get("colors", []) + item2.get("colors", [])
            color_conflicts = sum(1 for color in item_colors if color in avoided_colors)
            if color_conflicts > 0:
                score -= 0.3
        
        return min(1.0, max(0.0, score))
    
    def _get_match_reasons(self, item1: Dict[str, Any], item2: Dict[str, Any], score: float) -> List[str]:
        """Generate human-readable reasons for the match"""
        reasons = []
        
        # Color harmony
        colors1 = item1.get("colors", [])
        colors2 = item2.get("colors", [])
        if colors1 and colors2:
            color_score = self.color_theory.calculate_color_harmony_score(colors1 + colors2)
            if color_score > 0.7:
                reasons.append("Excellent color harmony")
            elif color_score > 0.5:
                reasons.append("Good color compatibility")
        
        # Style compatibility
        style1 = item1.get("style", "")
        style2 = item2.get("style", "")
        if style1 and style2:
            style_score = self.style_compatibility.calculate_style_compatibility(style1, style2)
            if style_score > 0.8:
                reasons.append(f"Perfect style match ({style1} + {style2})")
            elif style_score > 0.6:
                reasons.append(f"Compatible styles ({style1} + {style2})")
        
        # Overall score
        if score > 0.8:
            reasons.append("Highly recommended combination")
        elif score > 0.6:
            reasons.append("Good pairing option")
        
        return reasons if reasons else ["Compatible items"]

# Usage example and testing
if __name__ == "__main__":
    # Example usage
    matcher = IntelligentMatchingAlgorithm()
    
    target_item = {
        "id": "item1",
        "name": "Blue Dress Shirt",
        "category": "tops",
        "style": "business",
        "colors": ["#4A90E2"]
    }
    
    wardrobe_items = [
        {
            "id": "item2",
            "name": "Black Trousers",
            "category": "bottoms",
            "style": "business",
            "colors": ["#000000"]
        },
        {
            "id": "item3",
            "name": "Red Sneakers",
            "category": "shoes",
            "style": "casual",
            "colors": ["#FF0000"]
        }
    ]
    
    matches = matcher.find_matching_items(
        target_item=target_item,
        wardrobe_items=wardrobe_items,
        occasion="work"
    )
    
    for match in matches:
        print(f"Match: {match['name']} - Score: {match['compatibility_score']:.2f}")
        print(f"Reasons: {', '.join(match['match_reasons'])}")

