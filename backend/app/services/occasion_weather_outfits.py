import numpy as np
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from sklearn.metrics.pairwise import cosine_similarity
import requests
from pydantic import BaseModel
import os
from dotenv import  load_dotenv

load_dotenv()

@dataclass
class ClothingItem:
    """Represents a single clothing item with all its attributes"""
    id: str
    filename: str
    original_name: str
    category: str
    clothing_part: str  # top, bottom, footwear, accessories
    color_palette: List[str]
    dominant_color: str
    style: str
    occasion: str
    season: str
    temperature_range: Dict[str, int]
    gender: str
    material: str
    pattern: str
    resnet_features: List[float]
    
    @classmethod
    def from_db_record(cls, record: Dict):
        """Create ClothingItem from database record"""
        return cls(
            id=record['id'],
            filename=record['filename'],
            original_name=record['original_name'],
            category=record['category'],
            clothing_part=record['clothing_part'],
            color_palette=json.loads(record['color_palette']),
            dominant_color=record['dominant_color'],
            style=record['style'],
            occasion=record['occasion'].strip('"'),
            season=record['season'].strip('"'),
            temperature_range=json.loads(record['temperature_range']),
            gender=record['gender'],
            material=record['material'],
            pattern=record['pattern'],
            resnet_features=json.loads(record['resnet_features'])
        )

@dataclass
class WeatherData:
    temperature: float
    feels_like: float
    humidity: int
    pressure: int
    visibility: int
    wind_speed: float
    weather_condition: str
    description: str
    cloud_coverage: int
    sunrise: int
    sunset: int

    
class WeatherService:
    """Service to fetch weather data from OpenWeatherAPI"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    def get_current_weather(self, city: str, country_code: str = None) -> WeatherData:
        """Fetch current weather data"""
        location = f"{city},{country_code}" if country_code else city
        params = {
            'q': location,
            'appid': self.api_key,
            'units': 'metric'  # use 'metric' not 'celsius'
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            return WeatherData(
                temperature=data['main']['temp'],
                feels_like=data['main']['feels_like'],
                humidity=data['main']['humidity'],
                pressure=data['main']['pressure'],
                visibility=data.get('visibility', 10000),  # default fallback
                wind_speed=data['wind']['speed'],
                weather_condition=data['weather'][0]['main'],
                description=data['weather'][0]['description'],
                cloud_coverage=data['clouds']['all'],
                sunrise=data['sys']['sunrise'],
                sunset=data['sys']['sunset']
            )
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch weather data: {e}")


@dataclass
class OutfitRecommendation:
    """Represents a complete outfit recommendation"""
    items: List[ClothingItem]
    compatibility_score: float
    weather_suitability: float
    occasion_match: float
    style_coherence: float
    color_harmony: float
    
    def overall_score(self) -> float:
        """Calculate overall outfit score"""
        return (
            self.compatibility_score * 0.25 +
            self.weather_suitability * 0.25 +
            self.occasion_match * 0.25 +
            self.style_coherence * 0.15 +
            self.color_harmony * 0.10
        )
# Put this after your existing SmartOutfitRequest
class WeatherOccasionRequest(BaseModel):
    city: str
    country_code: Optional[str] = None
    occasion: str
    wardrobe_items: List[Dict[str, Any]]

class SmartOutfitRecommender:
    """Main outfit recommendation engine"""
    
    def __init__(self, weather_service: WeatherService):
        self.weather_service = weather_service
        self.wardrobe: List[ClothingItem] = []
        
        # Enhanced hierarchical occasion mapping
        self.occasion_hierarchy = {
            'work': ['business', 'office', 'interview', 'professional', 'meeting'],
            'formal': ['wedding', 'formal', 'black tie', 'gala', 'ceremony'],
            'leisure': ['casual', 'weekend', 'home', 'everyday', 'shopping', 'brunch'],
            'party': ['party', 'nightout', 'celebration', 'date', 'dinner', 'cocktail'],
            'sport': ['gym', 'sports', 'exercise', 'running', 'fitness', 'yoga'],
            'outdoor': ['hiking', 'camping', 'outdoor', 'travel', 'vacation', 'beach'],
            'smart_casual': ['smart casual', 'semi-formal', 'dinner casual', 'theater']
        }
        
        # Season mappings for current season detection
        self.season_months = {
            'spring': [3, 4, 5],
            'summer': [6, 7, 8], 
            'autumn': [9, 10, 11],
            'winter': [12, 1, 2]
        }
        
        # Weather condition mappings
        self.weather_conditions = {
            'Clear': {'temp_adjust': 0, 'layers': False, 'waterproof': False},
            'Clouds': {'temp_adjust': -2, 'layers': True, 'waterproof': False},
            'Rain': {'temp_adjust': -5, 'layers': True, 'waterproof': True},
            'Snow': {'temp_adjust': -10, 'layers': True, 'waterproof': True},
            'Thunderstorm': {'temp_adjust': -5, 'layers': True, 'waterproof': True},
            'Mist': {'temp_adjust': -3, 'layers': True, 'waterproof': False}
        }
    
    def get_current_season(self) -> str:
        """Determine current season based on month"""
        current_month = datetime.now().month
        for season, months in self.season_months.items():
            if current_month in months:
                return season
        return 'spring'  # fallback
    
    def calculate_season_compatibility(self, item: ClothingItem) -> float:
        """Calculate seasonal compatibility bonus"""
        current_season = self.get_current_season()
        item_seasons = [s.strip().lower() for s in item.season.strip('"').split(',')]
        
        if 'all season' in item_seasons:
            return 1.0
        elif current_season in item_seasons:
            return 1.0
        else:
            # Adjacent seasons get partial credit
            season_adjacency = {
                'spring': ['winter', 'summer'],
                'summer': ['spring', 'autumn'], 
                'autumn': ['summer', 'winter'],
                'winter': ['autumn', 'spring']
            }
            adjacent_seasons = season_adjacency.get(current_season, [])
            if any(season in item_seasons for season in adjacent_seasons):
                return 0.8
            return 0.6
    
    def load_wardrobe(self, clothing_items: List[Dict]):
        """Load wardrobe items from database records"""
        self.wardrobe = [ClothingItem.from_db_record(item) for item in clothing_items]


    
    def filter_by_occasion(self, items: List[ClothingItem], occasion: str) -> List[ClothingItem]:
        """Enhanced occasion filtering with hierarchical matching"""
        occasion_lower = occasion.lower()
        suitable_items = []
        
        # Find which category the occasion belongs to
        occasion_category = None
        for category, occasions in self.occasion_hierarchy.items():
            if occasion_lower in occasions:
                occasion_category = category
                break
        
        for item in items:
            item_occasion = item.occasion.lower()
            match_score = 0
            
            # Direct match gets highest score
            if occasion_lower == item_occasion:
                match_score = 1.0
            # Category match gets good score
            elif occasion_category:
                for category, occasions in self.occasion_hierarchy.items():
                    if category == occasion_category and item_occasion in occasions:
                        match_score = 0.9
                        break
                    elif item_occasion in occasions and occasion_lower in occasions:
                        match_score = 0.8
                        break
            
            # Include items with reasonable match scores
            if match_score >= 0.7:
                suitable_items.append(item)
        
        return suitable_items
    
    def calculate_visual_compatibility(self, items: List[ClothingItem]) -> float:
        """Calculate visual compatibility using ResNet features"""
        if len(items) < 2:
            return 1.0
        
        features_matrix = np.array([item.resnet_features for item in items])
        similarities = cosine_similarity(features_matrix)
        
        # Calculate average pairwise similarity (excluding diagonal)
        mask = ~np.eye(similarities.shape[0], dtype=bool)
        avg_similarity = similarities[mask].mean()
        
        return max(0.0, min(1.0, avg_similarity))
    
    def calculate_color_harmony(self, items: List[ClothingItem]) -> float:
        """Calculate color harmony score"""
        if len(items) < 2:
            return 1.0
        
        colors = [item.dominant_color for item in items]
        
        # Convert hex colors to RGB for better analysis
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        rgb_colors = [hex_to_rgb(color) for color in colors]
        
        # Calculate color distance (simplified color theory)
        total_distance = 0
        pairs = 0
        
        for i in range(len(rgb_colors)):
            for j in range(i+1, len(rgb_colors)):
                r1, g1, b1 = rgb_colors[i]
                r2, g2, b2 = rgb_colors[j]
                distance = np.sqrt((r1-r2)**2 + (g1-g2)**2 + (b1-b2)**2)
                total_distance += distance
                pairs += 1
        
        avg_distance = total_distance / pairs if pairs > 0 else 0
        
        # Normalize and invert (closer colors = better harmony for most cases)
        harmony_score = 1.0 - min(avg_distance / 441.67, 1.0)  # 441.67 is max RGB distance
        
        return harmony_score
    
    def calculate_style_coherence(self, items: List[ClothingItem]) -> float:
        """Calculate style coherence across items"""
        if len(items) < 2:
            return 1.0
        
        styles = [item.style for item in items]
        unique_styles = set(styles)
        
        # Perfect coherence if all items have the same style
        if len(unique_styles) == 1:
            return 1.0
        
        # Define compatible style combinations
        compatible_styles = {
            'Formal': ['Formal', 'Business'],
            'Casual': ['Casual', 'Smart Casual'],
            'Business': ['Business', 'Formal'],
            'Smart Casual': ['Smart Casual', 'Casual']
        }
        
        # Check if all styles are compatible
        for style in styles:
            compatible = compatible_styles.get(style, [style])
            if not all(s in compatible for s in styles):
                return 0.5  # Partial compatibility
        
        return 0.8  # Good compatibility but not perfect
    
    def filter_by_weather(self, items: List[ClothingItem], weather: WeatherData) -> List[ClothingItem]:
        """Filter wardrobe items suitable for current weather conditions."""
        weather_adjust = self.weather_conditions.get(weather.weather_condition, {})
        adjusted_temp = weather.temperature + weather_adjust.get('temp_adjust', 0)

        suitable_items = []
        for item in items:
            temp_range = item.temperature_range
            if temp_range['min'] <= adjusted_temp <= temp_range['max']:
                # Additional weather-specific filtering
                if weather.weather_condition == 'Rain' and item.material in ['cotton', 'linen']:
                    continue  # Skip absorbent materials in rain
                if weather.weather_condition == 'Snow' and item.clothing_part == 'footwear':
                    if 'sandal' in item.category.lower() or 'flip' in item.category.lower():
                        continue  # Skip inappropriate footwear
                suitable_items.append(item)

        return suitable_items

    def generate_outfit_combinations(self, weather: WeatherData, occasion: str, 
                                   max_combinations: int = 10) -> List[OutfitRecommendation]:
        """Enhanced outfit generation with diversity and season weighting"""
        
        # Filter wardrobe by weather and occasion
        weather_suitable = self.filter_by_weather(self.wardrobe, weather)
        occasion_suitable = self.filter_by_occasion(weather_suitable, occasion)
        
        # Group by clothing parts
        clothing_groups = {}
        for item in occasion_suitable:
            part = item.clothing_part
            if part not in clothing_groups:
                clothing_groups[part] = []
            clothing_groups[part].append(item)
        
        # Generate combinations with diversity tracking
        combinations = []
        used_item_combinations = set()  # Track used combinations for diversity
        
        tops = clothing_groups.get('top', [])
        bottoms = clothing_groups.get('bottom', [])
        footwear = clothing_groups.get('footwear', [])
        
        # Sort items by seasonal compatibility for better selection
        tops.sort(key=lambda x: self.calculate_season_compatibility(x), reverse=True)
        bottoms.sort(key=lambda x: self.calculate_season_compatibility(x), reverse=True)
        footwear.sort(key=lambda x: self.calculate_season_compatibility(x), reverse=True)
        
        combination_attempts = 0
        max_attempts = min(len(tops) * len(bottoms) * len(footwear), 500)  # Limit for performance
        
        for top in tops:
            for bottom in bottoms:
                for shoe in footwear:
                    combination_attempts += 1
                    if combination_attempts > max_attempts:
                        break
                    
                    # Create unique combination signature for diversity
                    combo_signature = frozenset([top.id, bottom.id, shoe.id])
                    if combo_signature in used_item_combinations:
                        continue
                    
                    # Avoid too much similarity in consecutive recommendations
                    if len(combinations) > 0:
                        recent_items = set()
                        for recent_combo in combinations[-3:]:  # Check last 3 combinations
                            recent_items.update(item.id for item in recent_combo.items)
                        
                        current_items = {top.id, bottom.id, shoe.id}
                        overlap = len(current_items & recent_items)
                        if overlap > 1:  # Skip if too similar to recent combinations
                            continue
                    
                    outfit_items = [top, bottom, shoe]
                    used_item_combinations.add(combo_signature)
                    
                    # Calculate enhanced scores with season weighting
                    compatibility = self.calculate_visual_compatibility(outfit_items)
                    weather_suit = self.calculate_enhanced_weather_suitability(outfit_items, weather)
                    occasion_match = self.calculate_occasion_match(outfit_items, occasion)
                    style_coherence = self.calculate_style_coherence(outfit_items)
                    color_harmony = self.calculate_color_harmony(outfit_items)
                    
                    recommendation = OutfitRecommendation(
                        items=outfit_items,
                        compatibility_score=compatibility,
                        weather_suitability=weather_suit,
                        occasion_match=occasion_match,
                        style_coherence=style_coherence,
                        color_harmony=color_harmony
                    )
                    
                    combinations.append(recommendation)
                    
                    if len(combinations) >= max_combinations * 2:  # Generate more, filter later
                        break
                if len(combinations) >= max_combinations * 2:
                    break
            if len(combinations) >= max_combinations * 2:
                break
        
        # Sort by overall score and return diverse top combinations
        combinations.sort(key=lambda x: x.overall_score(), reverse=True)
        
        # Final diversity filter - ensure no item appears in more than 2 of top recommendations
        final_combinations = []
        item_usage_count = {}
        
        for combo in combinations:
            # Count item usage
            can_add = True
            for item in combo.items:
                if item_usage_count.get(item.id, 0) >= 2:
                    can_add = False
                    break
            
            if can_add and len(final_combinations) < max_combinations:
                final_combinations.append(combo)
                for item in combo.items:
                    item_usage_count[item.id] = item_usage_count.get(item.id, 0) + 1
        
        return final_combinations
    
    def calculate_enhanced_weather_suitability(self, items: List[ClothingItem], weather: WeatherData) -> float:
        """Enhanced weather suitability calculation with season weighting"""
        total_score = 0
        
        for item in items:
            temp_range = item.temperature_range
            temp_score = 1.0 if temp_range['min'] <= weather.temperature <= temp_range['max'] else 0.5
            
            # Weather condition specific scoring
            condition_score = 1.0
            if weather.weather_condition == 'Rain':
                if item.material in ['wool', 'polyester', 'nylon']:
                    condition_score = 1.0
                elif item.material in ['cotton', 'linen']:
                    condition_score = 0.3
                elif item.category in ['jacket', 'coat', 'raincoat']:
                    condition_score = 1.2  # Bonus for appropriate outerwear
            elif weather.weather_condition == 'Snow':
                if item.category in ['boots', 'coat', 'jacket']:
                    condition_score = 1.2
                elif item.category in ['sandals', 'shorts', 't-shirt']:
                    condition_score = 0.1
            
            # Season compatibility bonus
            season_bonus = self.calculate_season_compatibility(item)
            
            total_score += temp_score * condition_score * season_bonus
        
        return min(total_score / len(items), 1.0)  # Normalize to max 1.0
    
    def calculate_occasion_match(self, items: List[ClothingItem], occasion: str) -> float:
        """Enhanced occasion matching with hierarchical scoring"""
        occasion_lower = occasion.lower()
        total_score = 0
        
        # Find occasion category for better matching
        occasion_category = None
        for category, occasions in self.occasion_hierarchy.items():
            if occasion_lower in occasions:
                occasion_category = category
                break
        
        for item in items:
            item_occasion = item.occasion.lower()
            match_score = 0
            
            # Direct match - highest score
            if occasion_lower == item_occasion:
                match_score = 1.0
            # Category match - good score
            elif occasion_category:
                target_occasions = self.occasion_hierarchy.get(occasion_category, [])
                if item_occasion in target_occasions:
                    match_score = 0.9
                else:
                    # Cross-category compatibility (e.g., smart_casual works for work)
                    compatibility_map = {
                        'work': ['smart_casual', 'formal'],
                        'formal': ['work'],
                        'smart_casual': ['work', 'leisure'],
                        'leisure': ['smart_casual']
                    }
                    compatible_categories = compatibility_map.get(occasion_category, [])
                    for compat_cat in compatible_categories:
                        if item_occasion in self.occasion_hierarchy.get(compat_cat, []):
                            match_score = 0.7
                            break
            
            total_score += match_score
        
        return total_score / len(items)
    
    def plan_weekly_outfits(self, weekly_plan: Dict[str, Dict], location: str) -> Dict[str, List[OutfitRecommendation]]:
        """Generate outfit recommendations for a weekly plan
        
        Args:
            weekly_plan: Dict with date as key and {'occasion': str, 'weather_override': WeatherData (optional)}
            location: City name for weather data
        
        Returns:
            Dict with date as key and list of outfit recommendations
        """
        weekly_outfits = {}
        
        for date_str, plan_info in weekly_plan.items():
            try:
                # Use provided weather or fetch current weather
                if 'weather_override' in plan_info:
                    weather = plan_info['weather_override']
                else:
                    weather = self.weather_service.get_current_weather(location)
                
                occasion = plan_info['occasion']
                outfits = self.generate_outfit_combinations(weather, occasion, max_combinations=5)
                weekly_outfits[date_str] = outfits
                
            except Exception as e:
                print(f"Error generating outfits for {date_str}: {e}")
                weekly_outfits[date_str] = []
        
        return weekly_outfits

# Example usage and testing
def example_usage():
    """Example of how to use the Smart Outfit Recommender"""
    
    # Initialize weather service (you'll need an API key)
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    weather_service = WeatherService(api_key)
    recommender = SmartOutfitRecommender(weather_service)
    
    # Example wardrobe data (based on your provided structure)
    sample_wardrobe = [
        {
            'id': '0ae01b82-9285-4ed4-ae6f-98e49375e965',
            'filename': '3bebe41a645242d0b5fe5c46baed34e8.jpg',
            'original_name': 'blue_man_sport_jeans_4.jpg',
            'category': 'jeans',
            'clothing_part': 'bottom',
            'color_palette': '["#4b565e"]',
            'dominant_color': '#4b565e',
            'style': 'Casual',
            'occasion': '"Everyday"',
            'season': '"All Season"',
            'temperature_range': '{"min": 0, "max": 30}',
            'gender': 'Male',
            'material': 'cotton',
            'pattern': '',
            'resnet_features': '[0.00539401825517416, 0.01764697954058647, ...]'  # Truncated for example
        }
        
    ]
    
    # Load wardrobe
    recommender.load_wardrobe(sample_wardrobe)
    
    # Get current weather and generate outfits
    try:
        weather = weather_service.get_current_weather("New York", "US")
        outfits = recommender.generate_outfit_combinations(weather, "casual", max_combinations=5)
        
        print(f"Generated {len(outfits)} outfit recommendations for casual occasion")
        for i, outfit in enumerate(outfits[:3]):
            print(f"\nOutfit {i+1} (Score: {outfit.overall_score():.2f}):")
            for item in outfit.items:
                print(f"  - {item.category}: {item.original_name}")
    
    except Exception as e:
        print(f"Error: {e}")
    
    # Weekly planning example
    weekly_plan = {
        "2025-07-21": {"occasion": "business"},
        "2025-07-22": {"occasion": "casual"},
        "2025-07-23": {"occasion": "party"},
        "2025-07-24": {"occasion": "formal"},
        "2025-07-25": {"occasion": "casual"}
    }
    
    weekly_outfits = recommender.plan_weekly_outfits(weekly_plan, "New York")
    print(f"\nGenerated weekly outfit plan with {len(weekly_outfits)} days")

if __name__ == "__main__":
    example_usage()