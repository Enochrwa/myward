import unittest
import sys
import os
from unittest.mock import MagicMock

# Add the backend directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.occasion_weather_outfits import SmartOutfitRecommender, ClothingItem, WeatherData

class TestSmartOutfitRecommender(unittest.TestCase):

    def setUp(self):
        self.weather_service_mock = MagicMock()
        self.recommender = SmartOutfitRecommender(self.weather_service_mock)
        self.sample_wardrobe = [
            # Tops
            {'id': '1', 'filename': 'a', 'original_name': 'a', 'category': 't-shirt', 'clothing_part': 'top', 'color_palette': '[]', 'dominant_color': '#ffffff', 'style': 'Casual', 'occasion': '"Everyday"', 'season': '"All Season"', 'temperature_range': '{"min": 10, "max": 30}', 'gender': 'Male', 'material': 'cotton', 'pattern': 'solid', 'resnet_features': f'[{",".join(["0.1"]*512)}]' },
            {'id': '2', 'filename': 'a', 'original_name': 'a', 'category': 'dress_shirt', 'clothing_part': 'top', 'color_palette': '[]', 'dominant_color': '#add8e6', 'style': 'Business', 'occasion': '"Work"', 'season': '"All Season"', 'temperature_range': '{"min": 10, "max": 25}', 'gender': 'Male', 'material': 'cotton', 'pattern': 'solid', 'resnet_features': f'[{",".join(["0.2"]*512)}]' },
            {'id': '10', 'filename': 'a', 'original_name': 'a', 'category': 'polo-shirt', 'clothing_part': 'top', 'color_palette': '[]', 'dominant_color': '#ff0000', 'style': 'Casual', 'occasion': '"Everyday"', 'season': '"All Season"', 'temperature_range': '{"min": 10, "max": 30}', 'gender': 'Male', 'material': 'cotton', 'pattern': 'solid', 'resnet_features': f'[{",".join(["0.9"]*512)}]' },
            # Bottoms
            {'id': '3', 'filename': 'a', 'original_name': 'a', 'category': 'jeans', 'clothing_part': 'bottom', 'color_palette': '[]', 'dominant_color': '#4b565e', 'style': 'Casual', 'occasion': '"Everyday"', 'season': '"All Season"', 'temperature_range': '{"min": 0, "max": 25}', 'gender': 'Male', 'material': 'denim', 'pattern': 'solid', 'resnet_features': f'[{",".join(["0.3"]*512)}]' },
            {'id': '4', 'filename': 'a', 'original_name': 'a', 'category': 'shorts', 'clothing_part': 'bottom', 'color_palette': '[]', 'dominant_color': '#0000ff', 'style': 'Casual', 'occasion': '"Everyday"', 'season': '"Summer"', 'temperature_range': '{"min": 20, "max": 35}', 'gender': 'Male', 'material': 'cotton', 'pattern': 'solid', 'resnet_features': f'[{",".join(["0.4"]*512)}]' },
            # Shoes
            {'id': '5', 'filename': 'a', 'original_name': 'a', 'category': 'sneakers', 'clothing_part': 'footwear', 'color_palette': '[]', 'dominant_color': '#000000', 'style': 'Casual', 'occasion': '"Everyday"', 'season': '"All Season"', 'temperature_range': '{"min": 0, "max": 30}', 'gender': 'Male', 'material': 'leather', 'pattern': 'solid', 'resnet_features': f'[{",".join(["0.5"]*512)}]' },
            {'id': '6', 'filename': 'a', 'original_name': 'a', 'category': 'sandals', 'clothing_part': 'footwear', 'color_palette': '[]', 'dominant_color': '#a52a2a', 'style': 'Casual', 'occasion': '"Everyday"', 'season': '"Summer"', 'temperature_range': '{"min": 25, "max": 40}', 'gender': 'Male', 'material': 'leather', 'pattern': 'solid', 'resnet_features': f'[{",".join(["0.6"]*512)}]' },
        ]
        self.recommender.load_wardrobe(self.sample_wardrobe)
        self.weather = WeatherData(temperature=20, feels_like=20, humidity=50, pressure=1012, visibility=10000, wind_speed=5, weather_condition='Clear', description='clear sky', cloud_coverage=0, sunrise=0, sunset=0)

    def test_generate_outfit_combinations_small_wardrobe(self):
        # Remove bottoms to simulate a small wardrobe
        small_wardrobe = [item for item in self.sample_wardrobe if item['clothing_part'] != 'bottom']
        self.recommender.load_wardrobe(small_wardrobe)

        recommendations = self.recommender.generate_outfit_combinations(self.weather, "casual")
        
        self.assertGreater(len(recommendations), 0, "Should suggest partial outfits for a small wardrobe.")
        for rec in recommendations:
            self.assertLess(len(rec.items), 3, "Partial outfits should have less than 3 items.")

    def test_plan_weekly_outfits_avoids_repetition(self):
        weekly_plan = {
            "2025-07-21": {"occasion": "casual"},
            "2025-07-22": {"occasion": "casual"},
        }
        
        self.weather_service_mock.get_current_weather.return_value = self.weather
        
        weekly_outfits = self.recommender.plan_weekly_outfits(weekly_plan, "Kigali")
        
        outfit1_items = {item.id for item in weekly_outfits["2025-07-21"][0].items}
        outfit2_items = {item.id for item in weekly_outfits["2025-07-22"][0].items}
        
        self.assertNotEqual(outfit1_items, outfit2_items, "Weekly plan should avoid repeating the exact same outfit.")

if __name__ == '__main__':
    unittest.main()
