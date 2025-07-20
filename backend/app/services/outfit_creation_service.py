import numpy as np
import json
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Any
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import colorsys
from collections import defaultdict

class SmartOutfitCreator:
    def __init__(self):
        # Color compatibility rules
        self.color_harmonies = {
            'complementary': 180,
            'analogous': 30,
            'triadic': 120,
            'split_complementary': 150,
            'tetradic': 90
        }
        
        # Style compatibility matrix
        self.style_compatibility = {
            'Casual': ['Casual', 'Smart Casual', 'Sporty'],
            'Formal': ['Formal', 'Business', 'Smart Casual'],
            'Smart Casual': ['Smart Casual', 'Casual', 'Business'],
            'Sporty': ['Sporty', 'Casual'],
            'Business': ['Business', 'Formal', 'Smart Casual'],
            'Party': ['Party', 'Formal', 'Smart Casual']
        }
        
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

        self.pattern_compatibility = {
            "solid": ["striped", "plaid", "floral", "polka_dot", "geometric", "solid"],
            "striped": ["solid", "polka_dot", "denim"],
            "plaid": ["solid", "denim"],
            "floral": ["solid", "denim", "striped"],
            "polka_dot": ["solid", "striped"],
            "geometric": ["solid"],
            "animal_print": ["solid", "black", "brown"],
        }

        self.material_compatibility = {
            "denim": ["cotton", "leather", "wool", "flannel"],
            "leather": ["denim", "cotton", "silk", "wool"],
            "silk": ["wool", "cotton", "leather"],
            "wool": ["denim", "leather", "cotton", "silk"],
            "cotton": ["denim", "leather", "wool", "silk", "polyester"],
            "polyester": ["cotton", "wool"],
        }

    def hex_to_hsv(self, hex_color: str) -> Tuple[float, float, float]:
        """Convert hex color to HSV for better color matching"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r, g, b = r/255.0, g/255.0, b/255.0
        return colorsys.rgb_to_hsv(r, g, b)

    def calculate_color_compatibility(self, color1: str, color2: str) -> float:
        """Calculate color compatibility score based on color theory"""
        try:
            h1, s1, v1 = self.hex_to_hsv(color1)
            h2, s2, v2 = self.hex_to_hsv(color2)
            
            # Convert hue to degrees
            h1_deg, h2_deg = h1 * 360, h2 * 360
            hue_diff = abs(h1_deg - h2_deg)
            if hue_diff > 180:
                hue_diff = 360 - hue_diff
            
            # Check for color harmonies
            compatibility_score = 0.0
            for harmony_type, angle in self.color_harmonies.items():
                if abs(hue_diff - angle) <= 15:  # 15-degree tolerance
                    compatibility_score = max(compatibility_score, 0.9)
                elif abs(hue_diff - angle) <= 30:  # 30-degree tolerance
                    compatibility_score = max(compatibility_score, 0.7)
            
            # Neutral colors (low saturation) work with everything
            if s1 < 0.3 or s2 < 0.3:
                compatibility_score = max(compatibility_score, 0.8)
            
            # Similar brightness levels work well together
            brightness_compatibility = 1 - abs(v1 - v2)
            
            # Monochromatic (same hue, different saturation/value)
            if hue_diff <= 15:
                compatibility_score = max(compatibility_score, 0.8)
            
            return (compatibility_score + brightness_compatibility) / 2
        except:
            return 0.5  # Default compatibility if color parsing fails

    def calculate_feature_similarity(self, features1: List[float], features2: List[float]) -> float:
        """Calculate similarity between ResNet features"""
        try:
            feat1 = np.array(features1).reshape(1, -1)
            feat2 = np.array(features2).reshape(1, -1)
            return cosine_similarity(feat1, feat2)[0][0]
        except:
            return 0.0

    def calculate_style_compatibility(self, style1: str, style2: str) -> float:
        """Calculate style compatibility score"""
        if style1 in self.style_compatibility:
            if style2 in self.style_compatibility[style1]:
                return 1.0 if style1 == style2 else 0.8
        return 0.3  # Low compatibility for mismatched styles

    def calculate_occasion_fit(self, item: Dict, target_occasion: str) -> float:
        """Calculate how well an item fits the target occasion"""
        item_occasion = item.get('occasion', '').strip('"')
        if item_occasion == target_occasion:
            return 1.0
        
        # Cross-occasion compatibility
        occasion_map = {
            'Everyday': ['Casual', 'Smart Casual'],
            'Work': ['Business', 'Formal', 'Smart Casual'],
            'Party': ['Party', 'Formal'],
            'Casual': ['Everyday', 'Smart Casual'],
            'Formal': ['Work', 'Business']
        }
        
        if target_occasion in occasion_map and item_occasion in occasion_map[target_occasion]:
            return 0.8
        return 0.4

    def calculate_seasonal_compatibility(self, item: Dict, target_season: str) -> float:
        """Calculate seasonal compatibility"""
        item_season = item.get('season', '').strip('"')
        if item_season == 'All Season':
            return 1.0
        if item_season == target_season:
            return 1.0
        
        # Seasonal transitions
        season_compatibility = {
            'Spring': ['Summer', 'All Season'],
            'Summer': ['Spring', 'All Season'],
            'Fall': ['Winter', 'All Season'],
            'Winter': ['Fall', 'All Season']
        }
        
        if target_season in season_compatibility and item_season in season_compatibility[target_season]:
            return 0.7
        return 0.3

    def get_outfit_combinations(self, wardrobe_items: List[Dict]) -> List[List[Dict]]:
        """Generate valid outfit combinations based on clothing parts"""
        # Group items by clothing part
        items_by_part = defaultdict(list)
        for item in wardrobe_items:
            part = item.get('clothing_part', 'unknown')
            items_by_part[part].append(item)
        
        # Basic outfit structures
        outfit_structures = [
            ['top', 'bottom'],  # Basic outfit
            ['top', 'bottom', 'shoes'],  # Complete outfit
            ['dress'],  # Dress only
            ['dress', 'shoes'],  # Dress with shoes
        ]
        
        valid_combinations = []
        
        for structure in outfit_structures:
            if all(part in items_by_part for part in structure):
                # Generate combinations for this structure
                self._generate_combinations_recursive(
                    structure, items_by_part, [], valid_combinations, 0
                )
        
        return valid_combinations

    def _generate_combinations_recursive(self, structure: List[str], items_by_part: Dict, 
                                       current_combo: List[Dict], all_combos: List[List[Dict]], 
                                       index: int):
        """Recursively generate outfit combinations"""
        if index >= len(structure):
            if len(current_combo) > 0:
                all_combos.append(current_combo.copy())
            return
        
        part = structure[index]
        for item in items_by_part[part]:
            current_combo.append(item)
            self._generate_combinations_recursive(
                structure, items_by_part, current_combo, all_combos, index + 1
            )
            current_combo.pop()

    def score_outfit(self, outfit: List[Dict], preferences: Dict) -> Dict:
        """Score an outfit based on various criteria"""
        if len(outfit) == 0:
            return {'total_score': 0, 'details': {}}

        scores = {
            'color_harmony': 0,
            'style_consistency': 0,
            'occasion_fit': 0,
            'seasonal_fit': 0,
            'pattern_compatibility': 0,
            'material_compatibility': 0,
            'pattern_clash': 1.0,
            'formality_score': 0,
        }

        target_occasion = preferences.get('occasion', 'Everyday')
        target_style = preferences.get('style', 'Casual')
        target_season = preferences.get('season', 'All Season')
        
        # Color harmony score
        if len(outfit) > 1:
            color_scores = []
            for i in range(len(outfit)):
                for j in range(i + 1, len(outfit)):
                    color1 = outfit[i].get('dominant_color', '#000000')
                    color2 = outfit[j].get('dominant_color', '#000000')
                    color_scores.append(self.calculate_color_compatibility(color1, color2))
            scores['color_harmony'] = np.mean(color_scores) if color_scores else 0.5
        else:
            scores['color_harmony'] = 0.8

        # Style consistency and coherence
        styles = [item.get('style', 'Casual') for item in outfit]
        style_consistency_score = self.calculate_style_coherence(outfit, target_style)
        scores['style_consistency'] = style_consistency_score
        
        # Occasion fit
        occasion_validation = self.validate_occasion_rules(outfit, target_occasion)
        scores['occasion_fit'] = occasion_validation['score']

        # Seasonal fit
        seasonal_scores = [self.calculate_seasonal_compatibility(item, target_season) for item in outfit]
        scores['seasonal_fit'] = np.mean(seasonal_scores) if seasonal_scores else 0.5

        # Pattern and Material Compatibility
        scores['pattern_compatibility'] = self.calculate_pattern_compatibility(outfit)
        scores['material_compatibility'] = self.calculate_material_compatibility(outfit)
        scores['pattern_clash'] = self.check_pattern_clash(outfit)
        
        # Formality Score
        scores['formality_score'] = self.get_outfit_formality_score(outfit)

        # Weighted total score
        weights = {
            'color_harmony': 0.20,
            'style_consistency': 0.20,
            'occasion_fit': 0.25,
            'seasonal_fit': 0.10,
            'pattern_compatibility': 0.10,
            'material_compatibility': 0.10,
            'pattern_clash': 0.05, # This is a penalty, so lower is better
        }

        total_score = sum(scores[key] * weights[key] for key in weights.keys())
        
        # Apply penalty for pattern clash
        total_score *= scores['pattern_clash']

        return {
            'total_score': total_score,
            'details': scores
        }

    def create_smart_outfits(self, wardrobe_items: List[Dict], preferences: Dict, 
                           top_n: int = 10) -> List[Dict]:
        """Create smart outfit recommendations"""
        print(f"Creating outfits from {len(wardrobe_items)} wardrobe items...")
        
        # Generate all possible outfit combinations
        combinations = self.get_outfit_combinations(wardrobe_items)
        print(f"Generated {len(combinations)} outfit combinations")
        
        # Score each outfit
        scored_outfits = []
        for outfit in combinations:
            score_data = self.score_outfit(outfit, preferences)
            
            outfit_info = {
                'items': outfit,
                'score': score_data['total_score'],
                'score_breakdown': score_data['details'],
                'description': self.generate_outfit_description(outfit),
                'dominant_colors': [item.get('dominant_color') for item in outfit],
                'styles': list(set(item.get('style') for item in outfit)),
                'occasions': list(set(item.get('occasion', '').strip('"') for item in outfit))
            }
            scored_outfits.append(outfit_info)
        
        # Sort by score and return top N
        scored_outfits.sort(key=lambda x: x['score'], reverse=True)
        return scored_outfits[:top_n]

    def generate_outfit_description(self, outfit: List[Dict]) -> str:
        """Generate a human-readable description of the outfit"""
        if not outfit:
            return "Empty outfit"
        
        descriptions = []
        for item in outfit:
            part = item.get('clothing_part', 'item')
            color = item.get('dominant_color', '#000000')
            style = item.get('style', 'casual')
            category = item.get('category', 'clothing')
            
            desc = f"{style.lower()} {category}"
            descriptions.append(desc)
        
        if len(descriptions) == 1:
            return descriptions[0]
        elif len(descriptions) == 2:
            return f"{descriptions[0]} with {descriptions[1]}"
        else:
            return f"{', '.join(descriptions[:-1])} and {descriptions[-1]}"

    def get_outfit_recommendations_by_occasion(self, wardrobe_items: List[Dict], 
                                             occasion: str, season: str = "All Season") -> List[Dict]:
        """Get outfit recommendations for a specific occasion"""
        preferences = {
            'occasion': occasion,
            'season': season
        }
        
        return self.create_smart_outfits(wardrobe_items, preferences, top_n=5)

    def find_missing_items(self, wardrobe_items: List[Dict], target_occasion: str) -> List[str]:
        """Identify missing clothing items for better outfit creation"""
        items_by_part = defaultdict(list)
        for item in wardrobe_items:
            part = item.get('clothing_part')
            items_by_part[part].append(item)
        
        missing_items = []
        essential_parts = ['top', 'bottom', 'shoes']
        
        for part in essential_parts:
            if not items_by_part[part]:
                missing_items.append(f"Missing {part} items")
            else:
                # Check if we have occasion-appropriate items
                suitable_items = [
                    item for item in items_by_part[part] 
                    if self.calculate_occasion_fit(item, target_occasion) > 0.6
                ]
                if not suitable_items:
                    missing_items.append(f"Missing {target_occasion.lower()} {part}")
        
        return missing_items

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

    def calculate_pattern_compatibility(self, outfit_items: List[Dict]) -> float:
        """Calculate pattern compatibility score for an outfit"""
        patterns = [item.get("pattern", "solid").lower() for item in outfit_items]
        if len(patterns) <= 1:
            return 1.0

        score = 0
        pairs = 0
        for i in range(len(patterns)):
            for j in range(i + 1, len(patterns)):
                pattern1 = patterns[i]
                pattern2 = patterns[j]
                
                if pattern1 in self.pattern_compatibility and pattern2 in self.pattern_compatibility[pattern1]:
                    score += 1
                elif pattern2 in self.pattern_compatibility and pattern1 in self.pattern_compatibility[pattern2]:
                    score += 1
                # Allow one pattern with solids
                elif pattern1 == "solid" or pattern2 == "solid":
                    score += 1
                
                pairs += 1
        
        return score / pairs if pairs > 0 else 1.0

    def calculate_material_compatibility(self, outfit_items: List[Dict]) -> float:
        """Calculate material compatibility score for an outfit"""
        materials = [item.get("material", "cotton").lower() for item in outfit_items]
        if len(materials) <= 1:
            return 1.0

        score = 0
        pairs = 0
        for i in range(len(materials)):
            for j in range(i + 1, len(materials)):
                material1 = materials[i]
                material2 = materials[j]

                if material1 in self.material_compatibility and material2 in self.material_compatibility[material1]:
                    score += 1
                elif material2 in self.material_compatibility and material1 in self.material_compatibility[material2]:
                    score += 1
                
                pairs += 1
        
        return score / pairs if pairs > 0 else 1.0

    def check_pattern_clash(self, outfit_items: List[Dict]) -> float:
        """Check for pattern clashes, e.g., multiple complex patterns"""
        patterns = [item.get("pattern", "solid").lower() for item in outfit_items if item.get("pattern", "solid").lower() != "solid"]
        
        # No clash if there's one or zero non-solid patterns
        if len(patterns) <= 1:
            return 1.0
        
        # More than two complex patterns is a potential clash
        if len(patterns) > 2:
            return 0.2

        # Check compatibility between the two patterns
        pattern1, pattern2 = patterns[0], patterns[1]
        if pattern1 in self.pattern_compatibility and pattern2 in self.pattern_compatibility[pattern1]:
            return 0.8  # Compatible but proceed with caution
        
        return 0.4 # Likely a clash

# Example usage and testing
def example_usage():
    # Sample wardrobe these come from database and will be taken to frontend for real life use
    sample_wardrobe = [
        {
            'id': '1', 'category': 't-shirt', 'clothing_part': 'top', 'dominant_color': '#ffffff', 
            'style': 'Casual', 'occasion': '"Everyday"', 'season': '"All Season"', 'pattern': 'solid', 'material': 'cotton'
        },
        {
            'id': '2', 'category': 'jeans', 'clothing_part': 'bottom', 'dominant_color': '#4b565e', 
            'style': 'Casual', 'occasion': '"Everyday"', 'season': '"All Season"', 'pattern': 'solid', 'material': 'denim'
        },
        {
            'id': '3', 'category': 'sneakers', 'clothing_part': 'shoes', 'dominant_color': '#000000', 
            'style': 'Casual', 'occasion': '"Everyday"', 'season': '"All Season"', 'pattern': 'solid', 'material': 'leather'
        },
        {
            'id': '4', 'category': 'dress_shirt', 'clothing_part': 'top', 'dominant_color': '#add8e6', 
            'style': 'Business', 'occasion': '"Work"', 'season': '"All Season"', 'pattern': 'striped', 'material': 'cotton'
        },
        {
            'id': '5', 'category': 'dress_pants', 'clothing_part': 'bottom', 'dominant_color': '#36454f', 
            'style': 'Business', 'occasion': '"Work"', 'season': '"All Season"', 'pattern': 'solid', 'material': 'wool'
        },
        {
            'id': '6', 'category': 'oxfords', 'clothing_part': 'shoes', 'dominant_color': '#a52a2a', 
            'style': 'Business', 'occasion': '"Work"', 'season': '"All Season"', 'pattern': 'solid', 'material': 'leather'
        },
        {
            'id': '7', 'category': 'floral_dress', 'clothing_part': 'dress', 'dominant_color': '#ffc0cb', 
            'style': 'Bohemian', 'occasion': '"Party"', 'season': '"Summer"', 'pattern': 'floral', 'material': 'silk'
        },
    ]
    
    # Create outfit creator instance
    outfit_creator = SmartOutfitCreator()
    
    # Get recommendations for work occasion
    print("--- Work Outfit Recommendations ---")
    work_outfits = outfit_creator.get_outfit_recommendations_by_occasion(
        sample_wardrobe, 'Work', 'All Season'
    )
    
    for i, outfit in enumerate(work_outfits, 1):
        print(f"\nOutfit {i} (Score: {outfit['score']:.2f}):")
        print(f"Description: {outfit['description']}")
        for item in outfit['items']:
            print(f"  - {item['category']} ({item['style']}, {item['pattern']})")
        print("Score breakdown:", outfit['score_breakdown'])

    # Get recommendations for a casual occasion
    print("\n--- Casual Outfit Recommendations ---")
    casual_outfits = outfit_creator.get_outfit_recommendations_by_occasion(
        sample_wardrobe, 'Casual', 'Summer'
    )

    for i, outfit in enumerate(casual_outfits, 1):
        print(f"\nOutfit {i} (Score: {outfit['score']:.2f}):")
        print(f"Description: {outfit['description']}")
        for item in outfit['items']:
            print(f"  - {item['category']} ({item['style']}, {item['pattern']})")
        print("Score breakdown:", outfit['score_breakdown'])

    # Find missing items
    missing = outfit_creator.find_missing_items(sample_wardrobe, 'Formal')
    if missing:
        print(f"\nMissing items for Formal outfits: {', '.join(missing)}")

if __name__ == "__main__":
    example_usage()