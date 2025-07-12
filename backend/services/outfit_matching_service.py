"""
Intelligent outfit matching and recommendation service for Digital Wardrobe System
Implements AI-powered outfit combinations, color matching, and style compatibility
"""
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from typing import List, Dict, Tuple, Optional, Any
import logging
import json
import colorsys
from datetime import datetime, date

from models.database_models import (
    ClothingItemResponse, OutfitResponse, OutfitCreate, OutfitItemCreate,
    User, FormalityLevel, Season
)
from services.database_service import db_service
from utils.color_utils import colors_match, get_color_harmony

logger = logging.getLogger(__name__)

class ColorMatcher:
    """Advanced color matching and harmony analysis"""
    
    def __init__(self):
        self.color_weights = {
            'complementary': 0.9,
            'analogous': 0.8,
            'triadic': 0.7,
            'monochromatic': 0.6,
            'neutral': 0.95
        }
    
    def calculate_color_compatibility(self, color1_hex: str, color2_hex: str) -> float:
        """Calculate compatibility score between two colors"""
        try:
            # Convert hex to RGB
            color1_rgb = [int(color1_hex[i:i+2], 16) for i in (1, 3, 5)]
            color2_rgb = [int(color2_hex[i:i+2], 16) for i in (1, 3, 5)]
            
            # Check if colors match using existing utility
            if colors_match(color1_rgb, color2_rgb):
                base_score = 0.8
            else:
                base_score = 0.4
            
            # Get color harmony type
            harmony = get_color_harmony(color1_rgb, color2_rgb)
            harmony_bonus = self.color_weights.get(harmony, 0.5)
            
            # Calculate final score
            final_score = min(base_score + harmony_bonus * 0.2, 1.0)
            
            return final_score
            
        except Exception as e:
            logger.error(f"Error calculating color compatibility: {e}")
            return 0.5
    
    def get_color_temperature_compatibility(self, temp1: str, temp2: str) -> float:
        """Calculate compatibility based on color temperature"""
        temp_compatibility = {
            ('warm', 'warm'): 0.9,
            ('cool', 'cool'): 0.9,
            ('neutral', 'warm'): 0.8,
            ('neutral', 'cool'): 0.8,
            ('warm', 'neutral'): 0.8,
            ('cool', 'neutral'): 0.8,
            ('warm', 'cool'): 0.3
        }
        
        return temp_compatibility.get((temp1.lower(), temp2.lower()), 0.5)
    
    def analyze_outfit_color_harmony(self, clothing_items: List[ClothingItemResponse]) -> Dict[str, Any]:
        """Analyze color harmony across multiple clothing items"""
        try:
            if len(clothing_items) < 2:
                return {"score": 1.0, "harmony_type": "single_item"}
            
            # Get all colors from items
            colors = []
            for item in clothing_items:
                if hasattr(item, 'primary_color') and item.primary_color:
                    colors.append(item.primary_color.hex_code)
                if hasattr(item, 'secondary_color') and item.secondary_color:
                    colors.append(item.secondary_color.hex_code)
            
            if len(colors) < 2:
                return {"score": 0.7, "harmony_type": "insufficient_data"}
            
            # Calculate pairwise compatibility scores
            compatibility_scores = []
            for i in range(len(colors)):
                for j in range(i + 1, len(colors)):
                    score = self.calculate_color_compatibility(colors[i], colors[j])
                    compatibility_scores.append(score)
            
            # Calculate overall harmony score
            avg_score = np.mean(compatibility_scores)
            min_score = np.min(compatibility_scores)
            
            # Penalize if any pair has very low compatibility
            if min_score < 0.3:
                final_score = min_score * 0.5 + avg_score * 0.5
            else:
                final_score = avg_score
            
            # Determine harmony type
            if avg_score > 0.8:
                harmony_type = "excellent"
            elif avg_score > 0.6:
                harmony_type = "good"
            elif avg_score > 0.4:
                harmony_type = "acceptable"
            else:
                harmony_type = "poor"
            
            return {
                "score": final_score,
                "harmony_type": harmony_type,
                "individual_scores": compatibility_scores,
                "average_score": avg_score,
                "min_score": min_score
            }
            
        except Exception as e:
            logger.error(f"Error analyzing outfit color harmony: {e}")
            return {"score": 0.5, "harmony_type": "error"}

class StyleMatcher:
    """Style compatibility and matching logic"""
    
    def __init__(self):
        # Style compatibility matrix (0-1 scale)
        self.style_compatibility = {
            'formal': {'formal': 1.0, 'business': 0.9, 'elegant': 0.8, 'classic': 0.7, 'casual': 0.2, 'sporty': 0.1},
            'business': {'business': 1.0, 'formal': 0.9, 'smart_casual': 0.8, 'classic': 0.7, 'casual': 0.3, 'sporty': 0.1},
            'casual': {'casual': 1.0, 'smart_casual': 0.8, 'trendy': 0.7, 'sporty': 0.6, 'business': 0.3, 'formal': 0.2},
            'sporty': {'sporty': 1.0, 'casual': 0.6, 'trendy': 0.5, 'smart_casual': 0.3, 'business': 0.1, 'formal': 0.1},
            'elegant': {'elegant': 1.0, 'formal': 0.8, 'classic': 0.7, 'business': 0.6, 'casual': 0.3, 'sporty': 0.1},
            'trendy': {'trendy': 1.0, 'casual': 0.7, 'smart_casual': 0.6, 'sporty': 0.5, 'business': 0.4, 'formal': 0.3},
            'classic': {'classic': 1.0, 'business': 0.7, 'elegant': 0.7, 'formal': 0.7, 'casual': 0.5, 'sporty': 0.2},
            'smart_casual': {'smart_casual': 1.0, 'casual': 0.8, 'business': 0.8, 'trendy': 0.6, 'formal': 0.4, 'sporty': 0.3}
        }
        
        # Formality level compatibility
        self.formality_compatibility = {
            'black_tie': {'black_tie': 1.0, 'formal': 0.3},
            'formal': {'formal': 1.0, 'black_tie': 0.3, 'business': 0.7},
            'business': {'business': 1.0, 'formal': 0.7, 'smart_casual': 0.6},
            'smart_casual': {'smart_casual': 1.0, 'business': 0.6, 'casual': 0.7},
            'casual': {'casual': 1.0, 'smart_casual': 0.7, 'very_casual': 0.8},
            'very_casual': {'very_casual': 1.0, 'casual': 0.8}
        }
    
    def calculate_style_compatibility(self, style1: str, style2: str) -> float:
        """Calculate compatibility between two styles"""
        style1_lower = style1.lower()
        style2_lower = style2.lower()
        
        if style1_lower in self.style_compatibility:
            return self.style_compatibility[style1_lower].get(style2_lower, 0.5)
        
        return 0.5  # Default compatibility
    
    def calculate_formality_compatibility(self, formality1: str, formality2: str) -> float:
        """Calculate compatibility between formality levels"""
        if formality1 in self.formality_compatibility:
            return self.formality_compatibility[formality1].get(formality2, 0.3)
        
        return 0.5  # Default compatibility
    
    def analyze_outfit_style_coherence(self, clothing_items: List[ClothingItemResponse]) -> Dict[str, Any]:
        """Analyze style coherence across outfit items"""
        try:
            if len(clothing_items) < 2:
                return {"score": 1.0, "coherence_type": "single_item"}
            
            # Extract style information from items
            styles = []
            formality_levels = []
            
            for item in clothing_items:
                # Get style from features if available
                features = db_service.get_clothing_features(item.id)
                if features and features.style_features:
                    style_data = features.style_features.get('style', {})
                    if isinstance(style_data, dict) and 'style' in style_data:
                        styles.append(style_data['style'])
                
                # Get formality from clothing type
                if hasattr(item, 'clothing_type') and item.clothing_type:
                    formality_levels.append(item.clothing_type.formality_level)
            
            # Calculate style compatibility scores
            style_scores = []
            if len(styles) >= 2:
                for i in range(len(styles)):
                    for j in range(i + 1, len(styles)):
                        score = self.calculate_style_compatibility(styles[i], styles[j])
                        style_scores.append(score)
            
            # Calculate formality compatibility scores
            formality_scores = []
            if len(formality_levels) >= 2:
                for i in range(len(formality_levels)):
                    for j in range(i + 1, len(formality_levels)):
                        score = self.calculate_formality_compatibility(formality_levels[i], formality_levels[j])
                        formality_scores.append(score)
            
            # Combine scores
            all_scores = style_scores + formality_scores
            if all_scores:
                avg_score = np.mean(all_scores)
                min_score = np.min(all_scores)
                
                # Penalize if any pair has very low compatibility
                if min_score < 0.3:
                    final_score = min_score * 0.4 + avg_score * 0.6
                else:
                    final_score = avg_score
            else:
                final_score = 0.7  # Default when insufficient data
            
            # Determine coherence type
            if final_score > 0.8:
                coherence_type = "excellent"
            elif final_score > 0.6:
                coherence_type = "good"
            elif final_score > 0.4:
                coherence_type = "acceptable"
            else:
                coherence_type = "poor"
            
            return {
                "score": final_score,
                "coherence_type": coherence_type,
                "style_scores": style_scores,
                "formality_scores": formality_scores,
                "styles_detected": styles,
                "formality_levels": formality_levels
            }
            
        except Exception as e:
            logger.error(f"Error analyzing style coherence: {e}")
            return {"score": 0.5, "coherence_type": "error"}

class OutfitGenerator:
    """Generate outfit combinations and recommendations"""
    
    def __init__(self):
        self.color_matcher = ColorMatcher()
        self.style_matcher = StyleMatcher()
        
        # Clothing category hierarchy for outfit building
        self.outfit_categories = {
            'tops': ['shirt', 'blouse', 'sweater', 'tank', 'polo'],
            'bottoms': ['pants', 'jeans', 'skirt', 'shorts', 'leggings'],
            'outerwear': ['jacket', 'blazer', 'coat', 'cardigan'],
            'footwear': ['shoes', 'boots', 'sneakers', 'heels', 'sandals'],
            'dresses': ['dress', 'gown'],
            'suits': ['suit', 'tuxedo']
        }
        
        # Essential outfit combinations
        self.outfit_templates = [
            {'required': ['tops', 'bottoms'], 'optional': ['outerwear', 'footwear']},
            {'required': ['dresses'], 'optional': ['outerwear', 'footwear']},
            {'required': ['suits'], 'optional': ['footwear']},
            {'required': ['tops', 'bottoms', 'footwear'], 'optional': ['outerwear']}
        ]
    
    def categorize_clothing_item(self, item: ClothingItemResponse) -> str:
        """Categorize clothing item into outfit category"""
        if hasattr(item, 'clothing_type') and item.clothing_type:
            type_name = item.clothing_type.name.lower()
            
            for category, types in self.outfit_categories.items():
                if any(t in type_name for t in types):
                    return category
        
        return 'other'
    
    def calculate_outfit_score(self, clothing_items: List[ClothingItemResponse]) -> Dict[str, Any]:
        """Calculate comprehensive outfit score"""
        try:
            # Color harmony analysis
            color_analysis = self.color_matcher.analyze_outfit_color_harmony(clothing_items)
            color_score = color_analysis['score']
            
            # Style coherence analysis
            style_analysis = self.style_matcher.analyze_outfit_style_coherence(clothing_items)
            style_score = style_analysis['score']
            
            # Category completeness check
            categories = [self.categorize_clothing_item(item) for item in clothing_items]
            completeness_score = self.calculate_completeness_score(categories)
            
            # Feature similarity (using ResNet features if available)
            feature_score = self.calculate_feature_similarity(clothing_items)
            
            # Weighted final score
            weights = {
                'color': 0.3,
                'style': 0.3,
                'completeness': 0.25,
                'features': 0.15
            }
            
            final_score = (
                color_score * weights['color'] +
                style_score * weights['style'] +
                completeness_score * weights['completeness'] +
                feature_score * weights['features']
            )
            
            return {
                'overall_score': final_score,
                'color_score': color_score,
                'style_score': style_score,
                'completeness_score': completeness_score,
                'feature_score': feature_score,
                'color_analysis': color_analysis,
                'style_analysis': style_analysis,
                'categories': categories
            }
            
        except Exception as e:
            logger.error(f"Error calculating outfit score: {e}")
            return {'overall_score': 0.5}
    
    def calculate_completeness_score(self, categories: List[str]) -> float:
        """Calculate how complete an outfit is based on categories"""
        try:
            category_set = set(categories)
            
            # Check against outfit templates
            best_score = 0.0
            
            for template in self.outfit_templates:
                required = set(template['required'])
                optional = set(template['optional'])
                
                # Check if all required categories are present
                if required.issubset(category_set):
                    base_score = 0.8
                    
                    # Bonus for optional categories
                    optional_present = len(optional.intersection(category_set))
                    optional_bonus = (optional_present / len(optional)) * 0.2 if optional else 0
                    
                    template_score = base_score + optional_bonus
                    best_score = max(best_score, template_score)
            
            return min(best_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating completeness score: {e}")
            return 0.5
    
    def calculate_feature_similarity(self, clothing_items: List[ClothingItemResponse]) -> float:
        """Calculate feature-based similarity for outfit coherence"""
        try:
            if len(clothing_items) < 2:
                return 1.0
            
            # Get ResNet features for all items
            features_list = []
            for item in clothing_items:
                features = db_service.get_clothing_features(item.id)
                if features and features.resnet_features:
                    features_list.append(features.resnet_features)
            
            if len(features_list) < 2:
                return 0.7  # Default when insufficient feature data
            
            # Calculate pairwise cosine similarities
            features_array = np.array(features_list)
            similarity_matrix = cosine_similarity(features_array)
            
            # Get upper triangle (excluding diagonal)
            upper_triangle = similarity_matrix[np.triu_indices_from(similarity_matrix, k=1)]
            
            if len(upper_triangle) > 0:
                avg_similarity = np.mean(upper_triangle)
                # Convert similarity to score (higher similarity = better outfit coherence)
                return min(avg_similarity * 1.2, 1.0)
            
            return 0.7
            
        except Exception as e:
            logger.error(f"Error calculating feature similarity: {e}")
            return 0.7
    
    def generate_outfit_suggestions(self, 
                                  base_item: ClothingItemResponse,
                                  user_items: List[ClothingItemResponse],
                                  occasion_id: Optional[int] = None,
                                  max_suggestions: int = 5) -> List[Dict[str, Any]]:
        """Generate outfit suggestions based on a base item"""
        try:
            suggestions = []
            base_category = self.categorize_clothing_item(base_item)
            
            # Filter items by availability
            available_items = [item for item in user_items if item.is_available and item.id != base_item.id]
            
            # Group items by category
            items_by_category = {}
            for item in available_items:
                category = self.categorize_clothing_item(item)
                if category not in items_by_category:
                    items_by_category[category] = []
                items_by_category[category].append(item)
            
            # Find suitable outfit templates
            suitable_templates = []
            for template in self.outfit_templates:
                if base_category in template['required'] or base_category in template.get('optional', []):
                    suitable_templates.append(template)
            
            # Generate combinations for each template
            for template in suitable_templates:
                required_categories = [cat for cat in template['required'] if cat != base_category]
                optional_categories = template.get('optional', [])
                
                # Generate combinations
                combinations = self.generate_category_combinations(
                    base_item, base_category, required_categories, optional_categories, items_by_category
                )
                
                # Score and rank combinations
                for combination in combinations:
                    outfit_score = self.calculate_outfit_score(combination)
                    
                    # Filter by occasion if specified
                    if occasion_id:
                        occasion_compatibility = self.check_occasion_compatibility(combination, occasion_id)
                        if occasion_compatibility < 0.5:
                            continue
                        outfit_score['occasion_compatibility'] = occasion_compatibility
                    
                    suggestions.append({
                        'items': combination,
                        'score': outfit_score,
                        'template': template
                    })
            
            # Sort by score and return top suggestions
            suggestions.sort(key=lambda x: x['score']['overall_score'], reverse=True)
            return suggestions[:max_suggestions]
            
        except Exception as e:
            logger.error(f"Error generating outfit suggestions: {e}")
            return []
    
    def generate_category_combinations(self, 
                                     base_item: ClothingItemResponse,
                                     base_category: str,
                                     required_categories: List[str],
                                     optional_categories: List[str],
                                     items_by_category: Dict[str, List[ClothingItemResponse]]) -> List[List[ClothingItemResponse]]:
        """Generate clothing combinations for outfit templates"""
        try:
            combinations = []
            
            # Start with base item
            base_combination = [base_item]
            
            # Add required items
            if self.add_required_items(base_combination, required_categories, items_by_category, combinations):
                # Add optional items
                self.add_optional_items(combinations, optional_categories, items_by_category)
            
            return combinations
            
        except Exception as e:
            logger.error(f"Error generating category combinations: {e}")
            return []
    
    def add_required_items(self, 
                          base_combination: List[ClothingItemResponse],
                          required_categories: List[str],
                          items_by_category: Dict[str, List[ClothingItemResponse]],
                          combinations: List[List[ClothingItemResponse]]) -> bool:
        """Recursively add required items to combinations"""
        if not required_categories:
            combinations.append(base_combination.copy())
            return True
        
        category = required_categories[0]
        remaining_categories = required_categories[1:]
        
        if category not in items_by_category:
            return False
        
        success = False
        for item in items_by_category[category][:3]:  # Limit to top 3 items per category
            new_combination = base_combination + [item]
            if self.add_required_items(new_combination, remaining_categories, items_by_category, combinations):
                success = True
        
        return success
    
    def add_optional_items(self, 
                          combinations: List[List[ClothingItemResponse]],
                          optional_categories: List[str],
                          items_by_category: Dict[str, List[ClothingItemResponse]]):
        """Add optional items to existing combinations"""
        new_combinations = []
        
        for combination in combinations:
            # Add combination without optional items
            new_combinations.append(combination)
            
            # Add combinations with one optional item
            for category in optional_categories:
                if category in items_by_category:
                    for item in items_by_category[category][:2]:  # Limit to top 2 optional items
                        new_combination = combination + [item]
                        new_combinations.append(new_combination)
        
        combinations.clear()
        combinations.extend(new_combinations)
    
    def check_occasion_compatibility(self, clothing_items: List[ClothingItemResponse], occasion_id: int) -> float:
        """Check how well an outfit matches a specific occasion"""
        try:
            # Get occasion details
            occasions = db_service.get_occasions()
            target_occasion = next((occ for occ in occasions if occ.id == occasion_id), None)
            
            if not target_occasion:
                return 0.5
            
            # Check formality level compatibility
            target_formality = target_occasion.formality_level
            formality_scores = []
            
            for item in clothing_items:
                if hasattr(item, 'clothing_type') and item.clothing_type:
                    item_formality = item.clothing_type.formality_level
                    score = self.style_matcher.calculate_formality_compatibility(target_formality, item_formality)
                    formality_scores.append(score)
            
            if formality_scores:
                return np.mean(formality_scores)
            
            return 0.5
            
        except Exception as e:
            logger.error(f"Error checking occasion compatibility: {e}")
            return 0.5

class OutfitMatchingService:
    """Main service for outfit matching and recommendations"""
    
    def __init__(self):
        self.outfit_generator = OutfitGenerator()
    
    def get_outfit_suggestions(self, 
                             user_id: str,
                             base_item_id: str,
                             occasion_id: Optional[int] = None,
                             max_suggestions: int = 5) -> Dict[str, Any]:
        """Get outfit suggestions for a base clothing item"""
        try:
            # Get base item
            base_item = db_service.get_clothing_item_by_id(base_item_id)
            if not base_item or base_item.user_id != user_id:
                raise ValueError("Base item not found or access denied")
            
            # Get user's wardrobe
            user_items = db_service.get_clothing_items_by_user(user_id, limit=1000)
            
            # Generate suggestions
            suggestions = self.outfit_generator.generate_outfit_suggestions(
                base_item=base_item,
                user_items=user_items,
                occasion_id=occasion_id,
                max_suggestions=max_suggestions
            )
            
            # Format response
            formatted_suggestions = []
            for suggestion in suggestions:
                formatted_suggestions.append({
                    'items': [self.format_item_for_response(item) for item in suggestion['items']],
                    'score': suggestion['score'],
                    'confidence': suggestion['score']['overall_score'],
                    'reasoning': self.generate_reasoning(suggestion)
                })
            
            return {
                'base_item': self.format_item_for_response(base_item),
                'suggestions': formatted_suggestions,
                'total_suggestions': len(formatted_suggestions)
            }
            
        except Exception as e:
            logger.error(f"Error getting outfit suggestions: {e}")
            raise
    
    def format_item_for_response(self, item: ClothingItemResponse) -> Dict[str, Any]:
        """Format clothing item for API response"""
        return {
            'id': item.id,
            'name': item.original_filename,
            'type': item.clothing_type.name if hasattr(item, 'clothing_type') and item.clothing_type else 'Unknown',
            'color': item.primary_color.name if hasattr(item, 'primary_color') and item.primary_color else 'Unknown',
            'brand': item.brand.name if hasattr(item, 'brand') and item.brand else None,
            'image_url': item.images[0].image_url if item.images else None
        }
    
    def generate_reasoning(self, suggestion: Dict[str, Any]) -> str:
        """Generate human-readable reasoning for outfit suggestion"""
        try:
            score = suggestion['score']
            
            reasons = []
            
            # Color harmony
            if score['color_score'] > 0.8:
                reasons.append("excellent color harmony")
            elif score['color_score'] > 0.6:
                reasons.append("good color coordination")
            
            # Style coherence
            if score['style_score'] > 0.8:
                reasons.append("perfect style match")
            elif score['style_score'] > 0.6:
                reasons.append("compatible styles")
            
            # Completeness
            if score['completeness_score'] > 0.8:
                reasons.append("complete outfit")
            
            if not reasons:
                reasons.append("balanced combination")
            
            return f"This outfit works well because of {', '.join(reasons)}."
            
        except Exception as e:
            logger.error(f"Error generating reasoning: {e}")
            return "This outfit combination has good overall compatibility."
    
    def create_outfit_from_suggestion(self, 
                                    user_id: str,
                                    item_ids: List[str],
                                    outfit_name: str,
                                    occasion_id: Optional[int] = None) -> Optional[str]:
        """Create a saved outfit from a suggestion"""
        try:
            # Validate items belong to user
            items = []
            for item_id in item_ids:
                item = db_service.get_clothing_item_by_id(item_id)
                if not item or item.user_id != user_id:
                    raise ValueError(f"Item {item_id} not found or access denied")
                items.append(item)
            
            # Calculate outfit score
            outfit_score = self.outfit_generator.calculate_outfit_score(items)
            
            # Determine formality level and season
            formality_levels = [item.clothing_type.formality_level for item in items if hasattr(item, 'clothing_type') and item.clothing_type]
            if formality_levels:
                # Use most formal level
                formality_order = ['very_casual', 'casual', 'smart_casual', 'business', 'formal', 'black_tie']
                formality_indices = [formality_order.index(level) for level in formality_levels if level in formality_order]
                if formality_indices:
                    outfit_formality = formality_order[max(formality_indices)]
                else:
                    outfit_formality = 'casual'
            else:
                outfit_formality = 'casual'
            
            # Create outfit
            outfit_data = OutfitCreate(
                name=outfit_name,
                description=f"AI-generated outfit with {len(items)} items",
                occasion_id=occasion_id,
                season='all_seasons',
                formality_level=outfit_formality,
                is_favorite=False,
                rating=None,
                clothing_item_ids=item_ids
            )
            
            # This would be implemented when outfit creation is added to database service
            # For now, return a placeholder
            logger.info(f"Would create outfit '{outfit_name}' for user {user_id} with items {item_ids}")
            return "placeholder_outfit_id"
            
        except Exception as e:
            logger.error(f"Error creating outfit from suggestion: {e}")
            return None

# Global outfit matching service instance
outfit_matching_service = OutfitMatchingService()

