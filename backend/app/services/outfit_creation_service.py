import numpy as np
import json
from datetime import datetime
from typing import List, Dict, Tuple, Optional
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
        
        # Occasion-based outfit rules
        self.occasion_rules = {
            'Everyday': {'formality': 0.3, 'color_boldness': 0.5},
            'Work': {'formality': 0.8, 'color_boldness': 0.3},
            'Party': {'formality': 0.6, 'color_boldness': 0.8},
            'Date': {'formality': 0.7, 'color_boldness': 0.6},
            'Casual': {'formality': 0.2, 'color_boldness': 0.7},
            'Formal': {'formality': 1.0, 'color_boldness': 0.2}
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
            'feature_similarity': 0
        }
        
        target_occasion = preferences.get('occasion', 'Everyday')
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
            scores['color_harmony'] = 0.8  # Single item gets neutral score
        
        # Style consistency
        styles = [item.get('style', 'Casual') for item in outfit]
        if len(set(styles)) == 1:
            scores['style_consistency'] = 1.0
        else:
            style_scores = []
            for i in range(len(styles)):
                for j in range(i + 1, len(styles)):
                    style_scores.append(self.calculate_style_compatibility(styles[i], styles[j]))
            scores['style_consistency'] = np.mean(style_scores) if style_scores else 0.5
        
        # Occasion fit
        occasion_scores = [self.calculate_occasion_fit(item, target_occasion) for item in outfit]
        scores['occasion_fit'] = np.mean(occasion_scores)
        
        # Seasonal fit
        seasonal_scores = [self.calculate_seasonal_compatibility(item, target_season) for item in outfit]
        scores['seasonal_fit'] = np.mean(seasonal_scores)
        
        # Feature similarity (for cohesion)
        if len(outfit) > 1:
            feature_scores = []
            for i in range(len(outfit)):
                for j in range(i + 1, len(outfit)):
                    try:
                        feat1 = json.loads(outfit[i].get('resnet_features', '[]'))
                        feat2 = json.loads(outfit[j].get('resnet_features', '[]'))
                        if feat1 and feat2:
                            similarity = self.calculate_feature_similarity(feat1, feat2)
                            # Convert similarity to compatibility (moderate similarity is good)
                            feature_scores.append(min(1.0, similarity + 0.3))
                    except:
                        feature_scores.append(0.5)
            scores['feature_similarity'] = np.mean(feature_scores) if feature_scores else 0.5
        else:
            scores['feature_similarity'] = 0.7
        
        # Weighted total score
        weights = {
            'color_harmony': 0.3,
            'style_consistency': 0.25,
            'occasion_fit': 0.25,
            'seasonal_fit': 0.1,
            'feature_similarity': 0.1
        }
        
        total_score = sum(scores[key] * weights[key] for key in scores.keys())
        
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

# Example usage and testing
def example_usage():
    # Sample wardrobe these come from database and will be taken to frontend for real life use
    sample_wardrobe = [
        {
            'id': '0ae01b82-9285-4ed4-ae6f-98e49375e965',
            'filename': '3bebe41a645242d0b5fe5c46baed34e8.jpg',
            'category': 'jeans',
            'clothing_part': 'bottom',
            'dominant_color': '#4b565e',
            'style': 'Formal',
            'occasion': '"Everyday"',
            'season': '"All Season"',
            'gender': 'Male',
            'resnet_features': '[0.005394, 0.017647, 0.0, 0.329253]'  # Truncated for example
        },
        # Add more sample items here for testing
    ]
    
    # Create outfit creator instance
    outfit_creator = SmartOutfitCreator()
    
    # Get recommendations for work occasion
    work_outfits = outfit_creator.get_outfit_recommendations_by_occasion(
        sample_wardrobe, 'Work', 'All Season'
    )
    
    print("Work Outfit Recommendations:")
    for i, outfit in enumerate(work_outfits, 1):
        print(f"\nOutfit {i} (Score: {outfit['score']:.2f}):")
        print(f"Description: {outfit['description']}")
        print(f"Items: {len(outfit['items'])}")
        print("Score breakdown:", outfit['score_breakdown'])
    
    # Find missing items
    missing = outfit_creator.find_missing_items(sample_wardrobe, 'Work')
    if missing:
        print(f"\nMissing items for Work outfits: {', '.join(missing)}")

if __name__ == "__main__":
    example_usage()