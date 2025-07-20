import unittest
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.outfit_creation_service import SmartOutfitCreator

class TestSmartOutfitCreator(unittest.TestCase):

    def setUp(self):
        self.outfit_creator = SmartOutfitCreator()
        self.sample_wardrobe = [
            # Tops
            {'id': '1', 'category': 't-shirt', 'clothing_part': 'top', 'dominant_color': '#ffffff', 'style': 'Casual', 'occasion': 'Everyday', 'season': 'All Season', 'pattern': 'solid', 'material': 'cotton'},
            {'id': '2', 'category': 'dress_shirt', 'clothing_part': 'top', 'dominant_color': '#add8e6', 'style': 'Business', 'occasion': 'Work', 'season': 'All Season', 'pattern': 'solid', 'material': 'cotton'},
            # Bottoms
            {'id': '3', 'category': 'jeans', 'clothing_part': 'bottom', 'dominant_color': '#4b565e', 'style': 'Casual', 'occasion': 'Everyday', 'season': 'All Season', 'pattern': 'solid', 'material': 'denim'},
            {'id': '4', 'category': 'dress_pants', 'clothing_part': 'bottom', 'dominant_color': '#36454f', 'style': 'Business', 'occasion': 'Work', 'season': 'All Season', 'pattern': 'solid', 'material': 'wool'},
            # Shoes
            {'id': '5', 'category': 'sneakers', 'clothing_part': 'shoes', 'dominant_color': '#000000', 'style': 'Casual', 'occasion': 'Everyday', 'season': 'All Season', 'pattern': 'solid', 'material': 'leather'},
            {'id': '6', 'category': 'oxfords', 'clothing_part': 'shoes', 'dominant_color': '#a52a2a', 'style': 'Business', 'occasion': 'Work', 'season': 'All Season', 'pattern': 'solid', 'material': 'leather'},
            # Dresses
            {'id': '7', 'category': 'floral_dress', 'clothing_part': 'dress', 'dominant_color': '#ffc0cb', 'style': 'Bohemian', 'occasion': 'Party', 'season': 'Summer', 'pattern': 'floral', 'material': 'silk'},
            # Accessories
            {'id': '8', 'category': 'belt', 'clothing_part': 'accessory', 'dominant_color': '#a52a2a', 'style': 'Business', 'occasion': 'Work', 'season': 'All Season', 'pattern': 'solid', 'material': 'leather'},
            {'id': '9', 'category': 'watch', 'clothing_part': 'accessory', 'dominant_color': '#c0c0c0', 'style': 'Classic', 'occasion': 'Everyday', 'season': 'All Season', 'pattern': 'solid', 'material': 'metal', 'color_name': 'silver'},
            {'id': '10', 'category': 'sunglasses', 'clothing_part': 'accessory', 'dominant_color': '#000000', 'style': 'Casual', 'occasion': 'Everyday', 'season': 'Summer', 'pattern': 'solid', 'material': 'plastic'},
        ]

    def test_outfit_generation_with_accessories(self):
        preferences = {'occasion': 'Business'}
        outfits = self.outfit_creator.create_smart_outfits(self.sample_wardrobe, preferences)
        
        # Check if any outfit includes an accessory
        has_accessory = any(
            any(item.get('clothing_part') == 'accessory' for item in outfit['items'])
            for outfit in outfits
        )
        self.assertTrue(has_accessory, "Outfit generation should include accessories.")

    def test_accessory_compatibility_score(self):
        # Outfit with matching accessories
        outfit1 = [
            {'id': '2', 'category': 'dress_shirt', 'clothing_part': 'top', 'style': 'Business'},
            {'id': '4', 'category': 'dress_pants', 'clothing_part': 'bottom', 'style': 'Business'},
            {'id': '6', 'category': 'oxfords', 'clothing_part': 'shoes', 'style': 'Business'},
            {'id': '8', 'category': 'belt', 'clothing_part': 'accessory', 'style': 'Business'},
        ]
        score1 = self.outfit_creator.calculate_accessory_compatibility(outfit1)
        self.assertGreater(score1, 0.6, "Matching accessories should have a high score.")

        # Outfit with clashing accessories
        outfit2 = [
            {'id': '2', 'category': 'dress_shirt', 'clothing_part': 'top', 'style': 'Business'},
            {'id': '4', 'category': 'dress_pants', 'clothing_part': 'bottom', 'style': 'Business'},
            {'id': '9', 'category': 'watch', 'clothing_part': 'accessory', 'style': 'Classic', 'color_name': 'silver'},
            {'id': '8', 'category': 'belt', 'clothing_part': 'accessory', 'style': 'Business', 'color_name': 'gold'},
        ]
        score2 = self.outfit_creator.calculate_accessory_compatibility(outfit2)
        self.assertLess(score2, 0.6, "Clashing accessories should have a low score.")

    def test_suggest_accessories(self):
        outfit = [
            {'id': '2', 'category': 'dress_shirt', 'clothing_part': 'top'},
            {'id': '4', 'category': 'dress_pants', 'clothing_part': 'bottom'},
        ]
        suggestions = self.outfit_creator.suggest_accessories(outfit, self.sample_wardrobe, 'Business')
        
        self.assertGreater(len(suggestions), 0, "Should suggest accessories for the outfit.")
        
        # Verify that the suggested accessory is of a suitable type
        suggested_categories = [item['category'] for item in suggestions]
        self.assertIn('belt', suggested_categories, "Should suggest a belt for a business outfit.")

if __name__ == '__main__':
    unittest.main()
