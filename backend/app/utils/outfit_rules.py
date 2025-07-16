# utils/outfit_rules.py
from typing import List, Dict, Any, Tuple
from .color_utils import get_temperature, get_tone, get_saturation

class OutfitRules:
    """Advanced outfit matching rules and style guidelines"""
    
    def __init__(self):
        self.season_colors = {
            "spring": ["coral", "peach", "yellow", "light_green", "turquoise"],
            "summer": ["soft_blue", "pink", "lavender", "mint", "rose"],
            "autumn": ["orange", "rust", "brown", "olive", "burgundy"],
            "winter": ["black", "white", "navy", "red", "jewel_tones"]
        }
        
        self.occasion_rules = {
            "formal": {
                "required_categories": ["dress", "suit", "formal_shoes"],
                "color_restrictions": ["black", "navy", "gray", "burgundy"],
                "avoid_patterns": ["casual_stripes", "loud_prints"],
                "fabric_preferences": ["silk", "wool", "cotton_blend"]
            },
            "business": {
                "required_categories": ["blazer", "dress_shirt", "dress_pants"],
                "color_restrictions": ["navy", "gray", "black", "white", "light_blue"],
                "avoid_patterns": ["casual_graphics", "bright_colors"],
                "fabric_preferences": ["cotton", "wool", "polyester_blend"]
            },
            "casual": {
                "allowed_categories": ["jeans", "t-shirt", "sneakers", "casual_top"],
                "color_freedom": True,
                "pattern_freedom": True,
                "comfort_priority": True
            },
            "date": {
                "style_focus": "attractive",
                "color_preferences": ["red", "black", "jewel_tones"],
                "avoid_categories": ["gym_wear", "work_clothes"],
                "fit_importance": "high"
            },
            "gym": {
                "required_features": ["moisture_wicking", "flexible"],
                "color_preferences": ["dark_colors", "athletic_colors"],
                "required_categories": ["athletic_wear", "sneakers"],
                "comfort_priority": True
            }
        }
        
        self.style_rules = {
            "minimalist": {
                "color_palette": ["black", "white", "gray", "beige"],
                "pattern_preference": "solid",
                "silhouette": "clean_lines",
                "accessories": "minimal"
            },
            "bohemian": {
                "color_palette": ["earth_tones", "warm_colors"],
                "pattern_preference": ["floral", "paisley", "ethnic"],
                "silhouette": "flowy",
                "accessories": "layered"
            },
            "classic": {
                "color_palette": ["navy", "black", "white", "camel"],
                "pattern_preference": ["stripes", "solid", "subtle_patterns"],
                "silhouette": "tailored",
                "accessories": "timeless"
            },
            "edgy": {
                "color_palette": ["black", "leather_tones", "metallics"],
                "pattern_preference": ["geometric", "bold"],
                "silhouette": "structured",
                "accessories": "statement"
            }
        }
    
    def check_color_season_compatibility(self, colors: List[str], season: str) -> float:
        """Check how well colors match the season"""
        if season not in self.season_colors:
            return 0.5  # Neutral score for unknown season
        
        season_palette = self.season_colors[season]
        compatible_count = 0
        
        for color in colors:
            if any(season_color in color.lower() for season_color in season_palette):
                compatible_count += 1
        
        return compatible_count / len(colors) if colors else 0

    def validate_occasion_rules(self, outfit_items: List[Dict], occasion: str) -> Dict[str, Any]:
        """Validate outfit against occasion rules"""
        if occasion not in self.occasion_rules:
            return {"valid": True, "score": 0.5, "notes": ["Unknown occasion"]}
        
        rules = self.occasion_rules[occasion]
        validation_results = {
            "valid": True,
            "score": 1.0,
            "notes": [],
            "violations": []
        }
        
        # Check required categories
        if "required_categories" in rules:
            outfit_categories = [item.get("category", "").lower() for item in outfit_items]
            missing_categories = []
            
            for required_cat in rules["required_categories"]:
                if not any(required_cat in cat for cat in outfit_categories):
                    missing_categories.append(required_cat)
            
            if missing_categories:
                validation_results["violations"].append(f"Missing: {', '.join(missing_categories)}")
                validation_results["score"] -= 0.3
        
        # Check color restrictions
        if "color_restrictions" in rules:
            outfit_colors = [item.get("color_name", "").lower() for item in outfit_items]
            restricted_colors = rules["color_restrictions"]
            
            non_compliant_colors = []
            for color in outfit_colors:
                if not any(restricted in color for restricted in restricted_colors):
                    non_compliant_colors.append(color)
            
            if non_compliant_colors:
                validation_results["violations"].append(f"Non-compliant colors: {', '.join(non_compliant_colors)}")
                validation_results["score"] -= 0.2
        
        # Update validity
        validation_results["valid"] = validation_results["score"] > 0.5
        
        return validation_results
    
    def calculate_style_coherence(self, outfit_items: List[Dict], target_style: str) -> float:
        """Calculate how well the outfit matches a target style"""
        if target_style not in self.style_rules:
            return 0.5
        
        style_rules = self.style_rules[target_style]
        coherence_scores = []
        
        # Check color palette compatibility
        if "color_palette" in style_rules:
            outfit_colors = [item.get("color_name", "").lower() for item in outfit_items]
            style_colors = style_rules["color_palette"]
            
            color_matches = sum(1 for color in outfit_colors 
                              if any(style_color in color for style_color in style_colors))
            color_score = color_matches / len(outfit_colors) if outfit_colors else 0
            coherence_scores.append(color_score)
        
        # Check pattern preferences
        if "pattern_preference" in style_rules:
            # This would require pattern detection in images - simplified for now
            coherence_scores.append(0.7)  # Default moderate score
        
        return sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0.5
    
    def get_outfit_formality_score(self, outfit_items: List[Dict]) -> float:
        """Calculate the formality level of an outfit (0 = very casual, 1 = very formal)"""
        formality_map = {
            "dress": 0.8, "suit": 0.9, "blazer": 0.7, "dress_shirt": 0.6,
            "dress_pants": 0.6, "formal_shoes": 0.7, "tie": 0.8,
            "jeans": 0.2, "t-shirt": 0.1, "sneakers": 0.1, "shorts": 0.1,
            "hoodie": 0.1, "flip-flops": 0.0
        }
        
        total_formality = 0
        item_count = 0
        
        for item in outfit_items:
            category = item.get("category", "").lower()
            for formal_item, score in formality_map.items():
                if formal_item in category:
                    total_formality += score
                    item_count += 1
                    break
            else:
                # Default formality for unknown items
                total_formality += 0.3
                item_count += 1
        
        return total_formality / item_count if item_count > 0 else 0.3
    
    def suggest_missing_pieces(self, outfit_items: List[Dict], occasion: str) -> List[str]:
        """Suggest missing pieces to complete an outfit"""
        suggestions = []
        
        if occasion not in self.occasion_rules:
            return suggestions
        
        rules = self.occasion_rules[occasion]
        current_categories = [item.get("category", "").lower() for item in outfit_items]
        
        # Check for missing required categories
        if "required_categories" in rules:
            for required_cat in rules["required_categories"]:
                if not any(required_cat in cat for cat in current_categories):
                    suggestions.append(f"Add {required_cat.replace('_', ' ')}")
        
        # Suggest complementary pieces
        if "business" in occasion or "formal" in occasion:
            if not any("accessory" in cat for cat in current_categories):
                suggestions.append("Consider adding a watch or belt")
        
        if "casual" in occasion:
            if len(outfit_items) < 3:
                suggestions.append("Consider adding a jacket or accessory for layering")
        
        return suggestions
    
    def calculate_weather_appropriateness(self, outfit_items: List[Dict], 
                                        weather_condition: str, temperature: float) -> float:
        """Calculate how appropriate the outfit is for given weather conditions"""
        weather_scores = []
        
        # Temperature appropriateness
        if temperature < 10:  # Cold
            cold_appropriate = ["coat", "jacket", "sweater", "boots", "long_pants"]
            cold_score = sum(1 for item in outfit_items 
                           if any(cold_item in item.get("category", "").lower() 
                                 for cold_item in cold_appropriate))
            weather_scores.append(min(cold_score / 2, 1.0))  # Need at least 2 warm items
        
        elif temperature > 25:  # Hot
            hot_appropriate = ["shorts", "t-shirt", "sandals", "light_dress", "tank_top"]
            hot_score = sum(1 for item in outfit_items 
                          if any(hot_item in item.get("category", "").lower() 
                                for hot_item in hot_appropriate))
            weather_scores.append(min(hot_score / 2, 1.0))
        
        else:  # Moderate temperature
            weather_scores.append(0.8)  # Most outfits work in moderate weather
        
        # Weather condition appropriateness
        if "rain" in weather_condition.lower():
            rain_appropriate = ["waterproof", "jacket", "boots"]
            rain_score = sum(1 for item in outfit_items 
                           if any(rain_item in item.get("category", "").lower() 
                                 for rain_item in rain_appropriate))
            weather_scores.append(min(rain_score, 1.0))
        
        return sum(weather_scores) / len(weather_scores) if weather_scores else 0.7