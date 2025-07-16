# utils/recommender.py
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Any, Tuple
from .color_utils import colors_match, get_color_harmony, get_temperature, get_tone
import random

class OutfitRecommender:
    def __init__(self, wardrobe_db_path: str):
        self.wardrobe_db_path = wardrobe_db_path
        self.scaler = StandardScaler()
        
    def load_wardrobe(self) -> List[Dict]:
        """Load wardrobe data from JSON file"""
        try:
            with open(self.wardrobe_db_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def extract_features(self, item: Dict) -> np.ndarray:
        """Extract numerical features from wardrobe item"""
        features = []
        
        # Color features (RGB values)
        if 'features' in item:
            features.extend(item['features'])
        
        # Texture features
        if 'texture_features' in item:
            texture = item['texture_features']
            features.extend([
                texture.get('laplacian_variance', 0),
                texture.get('contrast', 0),
                texture.get('brightness', 0)
            ])
        
        # Color distribution features
        if 'color_distribution' in item:
            color_dist = item['color_distribution']
            features.extend([
                color_dist.get('hue_diversity', 0),
                color_dist.get('saturation_diversity', 0),
                color_dist.get('value_diversity', 0)
            ])
        
        # Categorical features (encoded)
        features.append(self._encode_category(item.get('category', '')))
        features.append(self._encode_occasion(item.get('occasion', '')))
        features.append(self._encode_temperature(item.get('temperature', '')))
        features.append(self._encode_tone(item.get('tone', '')))
        
        return np.array(features)
    
    def _encode_category(self, category: str) -> float:
        """Encode category as numerical value"""
        category_map = {
            'top': 1.0, 'shirt': 1.0, 'blouse': 1.0, 't-shirt': 1.0,
            'bottom': 2.0, 'pants': 2.0, 'jeans': 2.0, 'skirt': 2.0,
            'dress': 3.0, 'gown': 3.0,
            'outerwear': 4.0, 'jacket': 4.0, 'coat': 4.0, 'blazer': 4.0,
            'footwear': 5.0, 'shoes': 5.0, 'boots': 5.0, 'sneakers': 5.0,
            'accessory': 6.0, 'bag': 6.0, 'belt': 6.0, 'hat': 6.0
        }
        return category_map.get(category.lower(), 0.0)
    
    def _encode_occasion(self, occasion: str) -> float:
        """Encode occasion as numerical value"""
        occasion_map = {
            'casual': 1.0, 'everyday': 1.0,
            'work': 2.0, 'business': 2.0, 'professional': 2.0,
            'formal': 3.0, 'evening': 3.0, 'dressy': 3.0,
            'party': 4.0, 'celebration': 4.0,
            'sport': 5.0, 'gym': 5.0, 'athletic': 5.0
        }
        return occasion_map.get(occasion.lower(), 0.0)
    
    def _encode_temperature(self, temperature: str) -> float:
        """Encode color temperature as numerical value"""
        temp_map = {'cool': 1.0, 'neutral': 2.0, 'warm': 3.0}
        return temp_map.get(temperature.lower(), 0.0)
    
    def _encode_tone(self, tone: str) -> float:
        """Encode color tone as numerical value"""
        tone_map = {'dark': 1.0, 'medium': 2.0, 'light': 3.0}
        return tone_map.get(tone.lower(), 0.0)
    
    def recommend_outfits(self, occasion: str = "casual", limit: int = 5) -> List[Dict]:
        """Recommend complete outfits for a given occasion"""
        wardrobe = self.load_wardrobe()
        
        if not wardrobe:
            return []
        
        # Filter by occasion
        filtered_items = [item for item in wardrobe 
                         if item.get('occasion', '').lower() == occasion.lower()]
        
        if not filtered_items:
            return []
        
        # Group items by category
        grouped_items = self._group_by_category(filtered_items)
        
        # Generate outfit combinations
        outfits = self._generate_outfit_combinations(grouped_items, limit)
        
        return outfits
    
    def _group_by_category(self, items: List[Dict]) -> Dict[str, List[Dict]]:
        """Group items by category"""
        groups = {}
        for item in items:
            category = item.get('category', '').lower()
            if category not in groups:
                groups[category] = []
            groups[category].append(item)
        return groups
    
    def _generate_outfit_combinations(self, grouped_items: Dict[str, List[Dict]], 
                                    limit: int) -> List[Dict]:
        """Generate outfit combinations with color matching"""
        outfits = []
        
        # Define outfit templates
        outfit_templates = [
            ['top', 'bottom'],
            ['dress'],
            ['top', 'bottom', 'outerwear'],
            ['top', 'bottom', 'footwear'],
            ['dress', 'outerwear'],
            ['top', 'bottom', 'outerwear', 'footwear']
        ]
        
        for template in outfit_templates:
            if len(outfits) >= limit:
                break
                
            # Check if all required categories are available
            if all(cat in grouped_items for cat in template):
                combinations = self._get_combinations_for_template(
                    template, grouped_items, limit - len(outfits)
                )
                outfits.extend(combinations)
        
        return outfits[:limit]
    
    def _get_combinations_for_template(self, template: List[str], 
                                     grouped_items: Dict[str, List[Dict]], 
                                     limit: int) -> List[Dict]:
        """Get combinations for a specific template"""
        combinations = []
        attempts = 0
        max_attempts = 100
        
        while len(combinations) < limit and attempts < max_attempts:
            attempts += 1
            
            # Select random items for each category
            outfit_items = []
            for category in template:
                if category in grouped_items:
                    item = random.choice(grouped_items[category])
                    outfit_items.append(item)
            
            if len(outfit_items) == len(template):
                # Check color compatibility
                if self._check_color_compatibility(outfit_items):
                    outfit_score = self._calculate_outfit_score(outfit_items)
                    combinations.append({
                        'items': outfit_items,
                        'score': outfit_score,
                        'template': template,
                        'color_harmony': self._analyze_outfit_harmony(outfit_items)
                    })
        
        # Sort by score and return
        combinations.sort(key=lambda x: x['score'], reverse=True)
        return combinations
    
    def _check_color_compatibility(self, items: List[Dict]) -> bool:
        """Check if colors in the outfit are compatible"""
        if len(items) < 2:
            return True
        
        # Check pairwise compatibility
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                item1_features = items[i].get('features', [0, 0, 0])
                item2_features = items[j].get('features', [0, 0, 0])
                
                if not colors_match(item1_features, item2_features):
                    return False
        
        return True
    
    def _calculate_outfit_score(self, items: List[Dict]) -> float:
        """Calculate compatibility score for an outfit"""
        if not items:
            return 0.0
        
        scores = []
        
        # Color harmony score
        if len(items) >= 2:
            color_scores = []
            for i in range(len(items)):
                for j in range(i + 1, len(items)):
                    item1_features = items[i].get('features', [0, 0, 0])
                    item2_features = items[j].get('features', [0, 0, 0])
                    
                    harmony = get_color_harmony(item1_features, item2_features)
                    harmony_score = {
                        'Complementary': 1.0,
                        'Analogous': 0.9,
                        'Triadic': 0.8,
                        'Split-Complementary': 0.7
                    }.get(harmony, 0.5)
                    
                    color_scores.append(harmony_score)
            
            scores.append(np.mean(color_scores))
        
        # Temperature consistency score
        temperatures = [item.get('temperature', 'Neutral') for item in items]
        temp_consistency = len(set(temperatures)) / len(temperatures)
        scores.append(1.0 - temp_consistency + 0.5)  # Reward consistency
        
        # Tone balance score
        tones = [item.get('tone', 'Medium') for item in items]
        tone_variety = len(set(tones)) / len(tones)
        scores.append(tone_variety)  # Reward some variety in tones
        
        return np.mean(scores)
    
    def _analyze_outfit_harmony(self, items: List[Dict]) -> Dict[str, Any]:
        """Analyze color harmony of the outfit"""
        if len(items) < 2:
            return {'type': 'Single Item', 'compatibility': 1.0}
        
        harmonies = []
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                item1_features = items[i].get('features', [0, 0, 0])
                item2_features = items[j].get('features', [0, 0, 0])
                harmony = get_color_harmony(item1_features, item2_features)
                harmonies.append(harmony)
        
        # Find most common harmony type
        harmony_counts = {}
        for harmony in harmonies:
            harmony_counts[harmony] = harmony_counts.get(harmony, 0) + 1
        
        dominant_harmony = max(harmony_counts, key=harmony_counts.get)
        compatibility = harmony_counts[dominant_harmony] / len(harmonies)
        
        return {
            'type': dominant_harmony,
            'compatibility': compatibility,
            'all_harmonies': harmonies
        }
    
    def find_similar_items(self, target_item: Dict, limit: int = 5) -> List[Dict]:
        """Find items similar to the target item"""
        wardrobe = self.load_wardrobe()
        
        if not wardrobe:
            return []
        
        # Extract features for all items
        target_features = self.extract_features(target_item)
        item_features = [self.extract_features(item) for item in wardrobe]
        
        # Calculate similarities
        similarities = []
        for i, item in enumerate(wardrobe):
            if item != target_item:  # Exclude the target item itself
                try:
                    similarity = cosine_similarity([target_features], [item_features[i]])[0][0]
                    similarities.append((item, similarity))
                except:
                    continue
        
        # Sort by similarity and return top items
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [item for item, _ in similarities[:limit]]

# Factory function for easy use
def recommend_outfits(occasion: str = "casual", wardrobe_db_path: str = "database/wardrobe.json", 
                     limit: int = 5) -> List[Dict]:
    """Convenience function to get outfit recommendations"""
    recommender = OutfitRecommender(wardrobe_db_path)
    return recommender.recommend_outfits(occasion, limit)

def map_weather_to_occasion_and_needs(weather: Dict) -> Tuple[str, List[str]]:
    """
    Map OpenWeather data to an appropriate occasion and needed categories.
    Returns (occasion, required_categories)
    """
    temp = weather.get("main", {}).get("temp", 20)
    weather_main = weather.get("weather", [{}])[0].get("main", "").lower()

    if temp < 10:
        occasion = "casual"
        needed = ["outerwear", "top", "bottom"]
    elif "rain" in weather_main or "storm" in weather_main:
        occasion = "casual"
        needed = ["outerwear", "shoes", "top", "bottom"]
    elif 10 <= temp < 20:
        occasion = "work"
        needed = ["top", "bottom", "outerwear"]
    elif 20 <= temp < 28:
        occasion = "casual"
        needed = ["top", "bottom"]
    else:
        occasion = "sport"
        needed = ["t-shirt", "shorts"]

    return occasion, needed

def recommend_for_weather(weather_data: Dict, wardrobe_db_path: str = "database/wardrobe.json", limit: int = 5) -> List[Dict]:
    occasion, needed_categories = map_weather_to_occasion_and_needs(weather_data)
    recommender = OutfitRecommender(wardrobe_db_path)
    all_outfits = recommender.recommend_outfits(occasion, limit=limit * 2)  # generate more to filter later

    filtered = []
    for outfit in all_outfits:
        item_cats = [item.get("category", "").lower() for item in outfit["items"]]
        if all(any(need in cat for cat in item_cats) for need in needed_categories):
            filtered.append(outfit)
        if len(filtered) >= limit:
            break

    return filtered
