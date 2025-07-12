"""
Content-Based Outfit Recommendation Service using scikit-learn

This module provides functionality to recommend similar outfits and clothing items
based on attributes like color, type, occasion, and style using machine learning
algorithms such as cosine similarity and KNN.
"""

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA
import logging
from typing import Dict, List, Tuple, Optional, Any
import json
from datetime import datetime
import pickle
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OutfitRecommendationEngine:
    """
    Content-based outfit recommendation engine using scikit-learn.
    
    This class provides methods to recommend outfits and clothing items based on
    user preferences, item attributes, and similarity metrics.
    """
    
    def __init__(self, model_cache_dir: str = "models"):
        """
        Initialize the recommendation engine.
        
        Args:
            model_cache_dir: Directory to cache trained models
        """
        self.model_cache_dir = model_cache_dir
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.scaler = StandardScaler()
        self.knn_model = NearestNeighbors(n_neighbors=10, metric='cosine')
        self.label_encoders = {}
        self.pca = PCA(n_components=50)
        
        # Ensure model cache directory exists
        os.makedirs(model_cache_dir, exist_ok=True)
        
        # Initialize feature weights for different recommendation types
        self.feature_weights = {
            'color_similarity': 0.3,
            'type_similarity': 0.25,
            'occasion_similarity': 0.2,
            'style_similarity': 0.15,
            'brand_similarity': 0.1
        }
        
        # Outfit compatibility rules
        self.compatibility_rules = self._load_compatibility_rules()
        
        # Seasonal and occasion mappings
        self.seasonal_colors = self._load_seasonal_colors()
        self.occasion_styles = self._load_occasion_styles()
    
    def _load_compatibility_rules(self) -> Dict[str, Dict]:
        """
        Load clothing compatibility rules for outfit recommendations.
        
        Returns:
            Dictionary of compatibility rules
        """
        return {
            "color_combinations": {
                "excellent": [
                    ("black", "white"), ("navy", "white"), ("gray", "white"),
                    ("black", "red"), ("navy", "beige"), ("brown", "cream"),
                    ("denim", "white"), ("khaki", "white"), ("burgundy", "gray")
                ],
                "good": [
                    ("black", "gray"), ("navy", "gray"), ("brown", "beige"),
                    ("green", "brown"), ("blue", "white"), ("red", "white"),
                    ("purple", "gray"), ("pink", "white"), ("orange", "brown")
                ],
                "avoid": [
                    ("black", "brown"), ("navy", "black"), ("red", "pink"),
                    ("orange", "red"), ("purple", "brown"), ("green", "red")
                ]
            },
            "type_combinations": {
                "formal": {
                    "tops": ["dress_shirt", "blouse", "blazer", "suit_jacket"],
                    "bottoms": ["dress_pants", "pencil_skirt", "suit_pants"],
                    "shoes": ["dress_shoes", "heels", "oxfords", "loafers"],
                    "accessories": ["tie", "watch", "belt", "briefcase"]
                },
                "casual": {
                    "tops": ["t_shirt", "polo", "sweater", "hoodie", "tank_top"],
                    "bottoms": ["jeans", "shorts", "casual_pants", "skirt"],
                    "shoes": ["sneakers", "sandals", "boots", "flats"],
                    "accessories": ["cap", "backpack", "casual_watch"]
                },
                "business_casual": {
                    "tops": ["button_down", "blouse", "cardigan", "polo"],
                    "bottoms": ["chinos", "dress_pants", "skirt", "dark_jeans"],
                    "shoes": ["loafers", "flats", "low_heels", "dress_boots"],
                    "accessories": ["belt", "watch", "blazer"]
                },
                "athletic": {
                    "tops": ["athletic_shirt", "tank_top", "sports_bra"],
                    "bottoms": ["athletic_shorts", "leggings", "sweatpants"],
                    "shoes": ["athletic_shoes", "running_shoes", "cross_trainers"],
                    "accessories": ["gym_bag", "water_bottle", "fitness_tracker"]
                }
            },
            "seasonal_appropriateness": {
                "spring": ["light_colors", "pastels", "light_fabrics"],
                "summer": ["bright_colors", "whites", "breathable_fabrics"],
                "fall": ["earth_tones", "warm_colors", "layering_pieces"],
                "winter": ["dark_colors", "warm_fabrics", "heavy_coats"]
            }
        }
    
    def _load_seasonal_colors(self) -> Dict[str, List[str]]:
        """
        Load seasonal color recommendations.
        
        Returns:
            Dictionary mapping seasons to recommended colors
        """
        return {
            "spring": [
                "pastel_pink", "light_blue", "mint_green", "lavender",
                "coral", "peach", "light_yellow", "soft_purple"
            ],
            "summer": [
                "white", "bright_blue", "coral", "turquoise",
                "lime_green", "hot_pink", "orange", "yellow"
            ],
            "fall": [
                "burgundy", "rust", "olive_green", "mustard",
                "brown", "orange", "deep_red", "forest_green"
            ],
            "winter": [
                "black", "navy", "deep_purple", "emerald",
                "burgundy", "charcoal", "royal_blue", "crimson"
            ]
        }
    
    def _load_occasion_styles(self) -> Dict[str, Dict]:
        """
        Load style recommendations for different occasions.
        
        Returns:
            Dictionary mapping occasions to style recommendations
        """
        return {
            "wedding": {
                "guest": {
                    "colors": ["pastels", "jewel_tones", "navy", "burgundy"],
                    "avoid_colors": ["white", "ivory", "black"],
                    "style": ["elegant", "formal", "sophisticated"],
                    "dress_code": ["cocktail", "formal", "semi_formal"]
                },
                "bridal_party": {
                    "colors": ["coordinated_palette", "bride_chosen"],
                    "style": ["elegant", "coordinated", "formal"],
                    "dress_code": ["formal", "black_tie"]
                }
            },
            "church": {
                "colors": ["conservative", "modest_tones", "pastels"],
                "style": ["modest", "conservative", "respectful"],
                "coverage": ["shoulders_covered", "knee_length_minimum"],
                "avoid": ["revealing", "too_casual", "bright_patterns"]
            },
            "casual": {
                "everyday": {
                    "colors": ["any", "personal_preference"],
                    "style": ["comfortable", "relaxed", "personal"],
                    "versatility": ["mix_and_match", "layering"]
                },
                "weekend": {
                    "colors": ["fun", "bright", "personal"],
                    "style": ["relaxed", "comfortable", "expressive"],
                    "activities": ["outdoor_friendly", "comfortable"]
                }
            },
            "home": {
                "loungewear": {
                    "colors": ["soft", "comfortable", "calming"],
                    "style": ["comfortable", "relaxed", "cozy"],
                    "fabrics": ["soft", "breathable", "comfortable"]
                },
                "work_from_home": {
                    "colors": ["professional_on_top", "comfortable_below"],
                    "style": ["business_casual_top", "comfortable_bottom"],
                    "video_call_ready": ["professional_appearance"]
                }
            },
            "work": {
                "office": {
                    "colors": ["professional", "neutral", "conservative"],
                    "style": ["business_professional", "polished"],
                    "dress_code": ["business_formal", "business_casual"]
                },
                "creative": {
                    "colors": ["expressive", "trendy", "personal"],
                    "style": ["creative", "individual", "trendy"],
                    "flexibility": ["personal_expression", "comfort"]
                }
            },
            "date": {
                "dinner": {
                    "colors": ["flattering", "sophisticated", "elegant"],
                    "style": ["attractive", "confident", "appropriate"],
                    "venue_appropriate": ["restaurant_suitable"]
                },
                "casual": {
                    "colors": ["approachable", "flattering", "personal"],
                    "style": ["comfortable", "attractive", "authentic"],
                    "activity_appropriate": ["versatile", "comfortable"]
                }
            }
        }
    
    def prepare_item_features(self, items: List[Dict]) -> np.ndarray:
        """
        Prepare feature vectors for clothing items.
        
        Args:
            items: List of clothing item dictionaries
            
        Returns:
            Feature matrix for the items
        """
        try:
            if not items:
                return np.array([])
            
            # Create DataFrame from items
            df = pd.DataFrame(items)
            
            # Initialize feature lists
            features = []
            
            for item in items:
                item_features = []
                
                # Color features (RGB values normalized)
                if 'dominant_color' in item and 'rgb' in item['dominant_color']:
                    rgb = item['dominant_color']['rgb']
                    item_features.extend([rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0])
                else:
                    item_features.extend([0.5, 0.5, 0.5])  # Default gray
                
                # Category/type features (one-hot encoded)
                category = item.get('category', 'unknown').lower()
                categories = ['shirts', 'pants', 'dresses', 'shoes', 'outerwear', 'accessories', 'skirts', 'underwear']
                category_features = [1.0 if cat == category else 0.0 for cat in categories]
                item_features.extend(category_features)
                
                # Brand features (encoded)
                brand = item.get('brand', 'unknown').lower()
                brand_hash = hash(brand) % 100  # Simple hash encoding
                item_features.append(brand_hash / 100.0)
                
                # Price features (normalized)
                price = float(item.get('price', 0))
                item_features.append(min(price / 1000.0, 1.0))  # Normalize to 0-1
                
                # Style features (from tags or description)
                style_text = f"{item.get('style', '')} {item.get('description', '')} {item.get('tags', '')}"
                style_features = self._extract_style_features(style_text)
                item_features.extend(style_features)
                
                # Seasonal appropriateness
                seasonal_features = self._extract_seasonal_features(item)
                item_features.extend(seasonal_features)
                
                # Occasion appropriateness
                occasion_features = self._extract_occasion_features(item)
                item_features.extend(occasion_features)
                
                features.append(item_features)
            
            # Convert to numpy array and handle any missing values
            feature_matrix = np.array(features, dtype=float)
            feature_matrix = np.nan_to_num(feature_matrix, nan=0.0)
            
            return feature_matrix
            
        except Exception as e:
            logger.error(f"Error preparing item features: {str(e)}")
            return np.array([])
    
    def _extract_style_features(self, style_text: str) -> List[float]:
        """
        Extract style features from text description.
        
        Args:
            style_text: Text description of style
            
        Returns:
            List of style feature values
        """
        style_keywords = {
            'casual': ['casual', 'relaxed', 'comfortable', 'everyday'],
            'formal': ['formal', 'elegant', 'sophisticated', 'dressy'],
            'business': ['business', 'professional', 'office', 'work'],
            'athletic': ['athletic', 'sport', 'gym', 'workout', 'active'],
            'trendy': ['trendy', 'fashionable', 'modern', 'contemporary'],
            'classic': ['classic', 'timeless', 'traditional', 'vintage'],
            'bohemian': ['boho', 'bohemian', 'free-spirited', 'artistic'],
            'minimalist': ['minimal', 'simple', 'clean', 'basic']
        }
        
        style_text_lower = style_text.lower()
        style_features = []
        
        for style, keywords in style_keywords.items():
            score = sum(1 for keyword in keywords if keyword in style_text_lower)
            style_features.append(min(score / len(keywords), 1.0))
        
        return style_features
    
    def _extract_seasonal_features(self, item: Dict) -> List[float]:
        """
        Extract seasonal appropriateness features.
        
        Args:
            item: Clothing item dictionary
            
        Returns:
            List of seasonal feature values
        """
        seasonal_features = [0.0, 0.0, 0.0, 0.0]  # spring, summer, fall, winter
        
        # Analyze color for seasonal appropriateness
        if 'dominant_color' in item and 'name' in item['dominant_color']:
            color_name = item['dominant_color']['name'].lower()
            
            for i, (season, colors) in enumerate(self.seasonal_colors.items()):
                if any(color in color_name for color in colors):
                    seasonal_features[i] = 1.0
        
        # Analyze fabric/material for seasonal appropriateness
        description = item.get('description', '').lower()
        material = item.get('material', '').lower()
        
        # Summer materials
        if any(material in f"{description} {material}" for material in ['cotton', 'linen', 'silk', 'chiffon']):
            seasonal_features[1] += 0.5  # summer
        
        # Winter materials
        if any(material in f"{description} {material}" for material in ['wool', 'cashmere', 'fleece', 'down']):
            seasonal_features[3] += 0.5  # winter
        
        return seasonal_features
    
    def _extract_occasion_features(self, item: Dict) -> List[float]:
        """
        Extract occasion appropriateness features.
        
        Args:
            item: Clothing item dictionary
            
        Returns:
            List of occasion feature values
        """
        occasions = ['casual', 'formal', 'business', 'athletic', 'party', 'wedding']
        occasion_features = [0.0] * len(occasions)
        
        category = item.get('category', '').lower()
        description = item.get('description', '').lower()
        style = item.get('style', '').lower()
        
        text_content = f"{category} {description} {style}"
        
        # Casual
        if any(word in text_content for word in ['casual', 't-shirt', 'jeans', 'sneakers']):
            occasion_features[0] = 1.0
        
        # Formal
        if any(word in text_content for word in ['formal', 'dress', 'suit', 'blazer', 'heels']):
            occasion_features[1] = 1.0
        
        # Business
        if any(word in text_content for word in ['business', 'professional', 'office', 'work']):
            occasion_features[2] = 1.0
        
        # Athletic
        if any(word in text_content for word in ['athletic', 'sport', 'gym', 'workout']):
            occasion_features[3] = 1.0
        
        # Party
        if any(word in text_content for word in ['party', 'cocktail', 'evening', 'glamorous']):
            occasion_features[4] = 1.0
        
        # Wedding
        if any(word in text_content for word in ['wedding', 'bridal', 'elegant', 'sophisticated']):
            occasion_features[5] = 1.0
        
        return occasion_features
    
    def train_recommendation_model(self, items: List[Dict]) -> bool:
        """
        Train the recommendation model with clothing items data.
        
        Args:
            items: List of clothing item dictionaries
            
        Returns:
            True if training successful, False otherwise
        """
        try:
            if len(items) < 5:
                logger.warning("Not enough items to train recommendation model")
                return False
            
            # Prepare features
            feature_matrix = self.prepare_item_features(items)
            
            if feature_matrix.size == 0:
                logger.error("Failed to prepare feature matrix")
                return False
            
            # Scale features
            scaled_features = self.scaler.fit_transform(feature_matrix)
            
            # Apply PCA for dimensionality reduction if needed
            if scaled_features.shape[1] > 50:
                scaled_features = self.pca.fit_transform(scaled_features)
            
            # Train KNN model
            self.knn_model.fit(scaled_features)
            
            # Save trained models
            self._save_models()
            
            logger.info(f"Recommendation model trained successfully with {len(items)} items")
            return True
            
        except Exception as e:
            logger.error(f"Error training recommendation model: {str(e)}")
            return False
    
    def get_outfit_recommendations(self, user_preferences: Dict, items: List[Dict], 
                                 occasion: str = "casual", num_recommendations: int = 5) -> List[Dict]:
        """
        Get outfit recommendations based on user preferences and occasion.
        
        Args:
            user_preferences: User style preferences and constraints
            items: Available clothing items
            occasion: Target occasion for the outfit
            num_recommendations: Number of recommendations to return
            
        Returns:
            List of recommended outfit combinations
        """
        try:
            if not items:
                return []
            
            # Filter items by occasion appropriateness
            occasion_appropriate_items = self._filter_by_occasion(items, occasion)
            
            # Generate outfit combinations
            outfit_combinations = self._generate_outfit_combinations(
                occasion_appropriate_items, user_preferences, occasion
            )
            
            # Score and rank combinations
            scored_outfits = self._score_outfit_combinations(
                outfit_combinations, user_preferences, occasion
            )
            
            # Return top recommendations
            recommendations = sorted(scored_outfits, key=lambda x: x['score'], reverse=True)
            return recommendations[:num_recommendations]
            
        except Exception as e:
            logger.error(f"Error getting outfit recommendations: {str(e)}")
            return []
    
    def get_similar_items(self, target_item: Dict, items: List[Dict], 
                         num_similar: int = 5) -> List[Dict]:
        """
        Get items similar to a target item using cosine similarity.
        
        Args:
            target_item: Target clothing item
            items: Available clothing items to compare against
            num_similar: Number of similar items to return
            
        Returns:
            List of similar items with similarity scores
        """
        try:
            if not items:
                return []
            
            # Prepare features for all items including target
            all_items = [target_item] + items
            feature_matrix = self.prepare_item_features(all_items)
            
            if feature_matrix.size == 0:
                return []
            
            # Calculate cosine similarity
            target_features = feature_matrix[0:1]  # First row is target item
            item_features = feature_matrix[1:]     # Rest are comparison items
            
            similarities = cosine_similarity(target_features, item_features)[0]
            
            # Create results with similarity scores
            similar_items = []
            for i, similarity in enumerate(similarities):
                item_with_score = items[i].copy()
                item_with_score['similarity_score'] = float(similarity)
                similar_items.append(item_with_score)
            
            # Sort by similarity and return top results
            similar_items.sort(key=lambda x: x['similarity_score'], reverse=True)
            return similar_items[:num_similar]
            
        except Exception as e:
            logger.error(f"Error getting similar items: {str(e)}")
            return []
    
    def get_color_coordinated_items(self, base_item: Dict, items: List[Dict]) -> List[Dict]:
        """
        Get items that coordinate well with a base item's color.
        
        Args:
            base_item: Base clothing item
            items: Available items to coordinate with
            
        Returns:
            List of color-coordinated items
        """
        try:
            if 'dominant_color' not in base_item:
                return []
            
            base_color = base_item['dominant_color']['name'].lower()
            coordinated_items = []
            
            for item in items:
                if 'dominant_color' not in item:
                    continue
                
                item_color = item['dominant_color']['name'].lower()
                compatibility_score = self._calculate_color_compatibility(base_color, item_color)
                
                if compatibility_score > 0.5:  # Threshold for good compatibility
                    item_with_score = item.copy()
                    item_with_score['color_compatibility_score'] = compatibility_score
                    coordinated_items.append(item_with_score)
            
            # Sort by compatibility score
            coordinated_items.sort(key=lambda x: x['color_compatibility_score'], reverse=True)
            return coordinated_items
            
        except Exception as e:
            logger.error(f"Error getting color coordinated items: {str(e)}")
            return []
    
    def _filter_by_occasion(self, items: List[Dict], occasion: str) -> List[Dict]:
        """
        Filter items appropriate for a specific occasion.
        
        Args:
            items: List of clothing items
            occasion: Target occasion
            
        Returns:
            Filtered list of appropriate items
        """
        if occasion not in self.occasion_styles:
            return items
        
        occasion_style = self.occasion_styles[occasion]
        appropriate_items = []
        
        for item in items:
            # Check if item matches occasion requirements
            if self._is_occasion_appropriate(item, occasion_style):
                appropriate_items.append(item)
        
        return appropriate_items
    
    def _is_occasion_appropriate(self, item: Dict, occasion_style: Dict) -> bool:
        """
        Check if an item is appropriate for an occasion.
        
        Args:
            item: Clothing item
            occasion_style: Occasion style requirements
            
        Returns:
            True if appropriate, False otherwise
        """
        # This is a simplified check - can be expanded based on requirements
        item_description = f"{item.get('category', '')} {item.get('style', '')} {item.get('description', '')}".lower()
        
        # Check for any style matches
        if 'style' in occasion_style:
            for style in occasion_style['style']:
                if style.lower() in item_description:
                    return True
        
        return True  # Default to appropriate if no specific restrictions
    
    def _generate_outfit_combinations(self, items: List[Dict], user_preferences: Dict, 
                                    occasion: str) -> List[Dict]:
        """
        Generate outfit combinations from available items.
        
        Args:
            items: Available clothing items
            user_preferences: User preferences
            occasion: Target occasion
            
        Returns:
            List of outfit combinations
        """
        # Group items by category
        items_by_category = {}
        for item in items:
            category = item.get('category', 'unknown')
            if category not in items_by_category:
                items_by_category[category] = []
            items_by_category[category].append(item)
        
        combinations = []
        
        # Generate basic outfit combinations
        # For simplicity, we'll create top + bottom combinations
        tops = items_by_category.get('shirts', []) + items_by_category.get('outerwear', [])
        bottoms = items_by_category.get('pants', []) + items_by_category.get('skirts', [])
        shoes = items_by_category.get('shoes', [])
        
        for top in tops[:10]:  # Limit combinations for performance
            for bottom in bottoms[:10]:
                outfit = {
                    'top': top,
                    'bottom': bottom,
                    'items': [top, bottom]
                }
                
                # Add shoes if available
                if shoes:
                    outfit['shoes'] = shoes[0]  # Simple selection
                    outfit['items'].append(shoes[0])
                
                combinations.append(outfit)
        
        return combinations
    
    def _score_outfit_combinations(self, combinations: List[Dict], user_preferences: Dict, 
                                 occasion: str) -> List[Dict]:
        """
        Score outfit combinations based on various factors.
        
        Args:
            combinations: List of outfit combinations
            user_preferences: User preferences
            occasion: Target occasion
            
        Returns:
            List of scored outfit combinations
        """
        scored_combinations = []
        
        for combination in combinations:
            score = 0.0
            
            # Color harmony score
            color_score = self._calculate_outfit_color_harmony(combination['items'])
            score += color_score * 0.4
            
            # Style consistency score
            style_score = self._calculate_style_consistency(combination['items'])
            score += style_score * 0.3
            
            # Occasion appropriateness score
            occasion_score = self._calculate_occasion_appropriateness(combination['items'], occasion)
            score += occasion_score * 0.3
            
            combination['score'] = score
            combination['color_score'] = color_score
            combination['style_score'] = style_score
            combination['occasion_score'] = occasion_score
            
            scored_combinations.append(combination)
        
        return scored_combinations
    
    def _calculate_color_compatibility(self, color1: str, color2: str) -> float:
        """
        Calculate compatibility score between two colors.
        
        Args:
            color1: First color name
            color2: Second color name
            
        Returns:
            Compatibility score (0-1)
        """
        # Check excellent combinations
        for combo in self.compatibility_rules['color_combinations']['excellent']:
            if (color1 in combo and color2 in combo) or (color2 in combo and color1 in combo):
                return 1.0
        
        # Check good combinations
        for combo in self.compatibility_rules['color_combinations']['good']:
            if (color1 in combo and color2 in combo) or (color2 in combo and color1 in combo):
                return 0.8
        
        # Check combinations to avoid
        for combo in self.compatibility_rules['color_combinations']['avoid']:
            if (color1 in combo and color2 in combo) or (color2 in combo and color1 in combo):
                return 0.2
        
        # Default neutral compatibility
        return 0.6
    
    def _calculate_outfit_color_harmony(self, items: List[Dict]) -> float:
        """
        Calculate color harmony score for an outfit.
        
        Args:
            items: List of clothing items in the outfit
            
        Returns:
            Color harmony score (0-1)
        """
        if len(items) < 2:
            return 1.0
        
        colors = []
        for item in items:
            if 'dominant_color' in item and 'name' in item['dominant_color']:
                colors.append(item['dominant_color']['name'].lower())
        
        if len(colors) < 2:
            return 0.5
        
        # Calculate pairwise color compatibility
        total_score = 0.0
        comparisons = 0
        
        for i in range(len(colors)):
            for j in range(i + 1, len(colors)):
                compatibility = self._calculate_color_compatibility(colors[i], colors[j])
                total_score += compatibility
                comparisons += 1
        
        return total_score / comparisons if comparisons > 0 else 0.5
    
    def _calculate_style_consistency(self, items: List[Dict]) -> float:
        """
        Calculate style consistency score for an outfit.
        
        Args:
            items: List of clothing items in the outfit
            
        Returns:
            Style consistency score (0-1)
        """
        # Extract style keywords from all items
        all_styles = []
        for item in items:
            style_text = f"{item.get('style', '')} {item.get('description', '')}"
            all_styles.extend(style_text.lower().split())
        
        if not all_styles:
            return 0.5
        
        # Count style keyword frequency
        style_counts = {}
        for style in all_styles:
            style_counts[style] = style_counts.get(style, 0) + 1
        
        # Calculate consistency based on common style keywords
        total_words = len(all_styles)
        max_frequency = max(style_counts.values()) if style_counts else 0
        
        consistency_score = max_frequency / total_words if total_words > 0 else 0.5
        return min(consistency_score * 2, 1.0)  # Scale to 0-1 range
    
    def _calculate_occasion_appropriateness(self, items: List[Dict], occasion: str) -> float:
        """
        Calculate how appropriate an outfit is for an occasion.
        
        Args:
            items: List of clothing items in the outfit
            occasion: Target occasion
            
        Returns:
            Appropriateness score (0-1)
        """
        if occasion not in self.occasion_styles:
            return 0.5
        
        occasion_requirements = self.occasion_styles[occasion]
        appropriateness_scores = []
        
        for item in items:
            score = 0.5  # Default neutral score
            
            # Check if item matches occasion style requirements
            if self._is_occasion_appropriate(item, occasion_requirements):
                score = 1.0
            
            appropriateness_scores.append(score)
        
        return sum(appropriateness_scores) / len(appropriateness_scores) if appropriateness_scores else 0.5
    
    def _save_models(self):
        """Save trained models to cache directory."""
        try:
            model_path = os.path.join(self.model_cache_dir, 'recommendation_models.pkl')
            models = {
                'scaler': self.scaler,
                'knn_model': self.knn_model,
                'pca': self.pca,
                'feature_weights': self.feature_weights
            }
            
            with open(model_path, 'wb') as f:
                pickle.dump(models, f)
            
            logger.info("Recommendation models saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving models: {str(e)}")
    
    def _load_models(self):
        """Load trained models from cache directory."""
        try:
            model_path = os.path.join(self.model_cache_dir, 'recommendation_models.pkl')
            
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    models = pickle.load(f)
                
                self.scaler = models.get('scaler', self.scaler)
                self.knn_model = models.get('knn_model', self.knn_model)
                self.pca = models.get('pca', self.pca)
                self.feature_weights = models.get('feature_weights', self.feature_weights)
                
                logger.info("Recommendation models loaded successfully")
                return True
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
        
        return False

# Global recommendation engine instance
_recommendation_engine_instance = None

def get_recommendation_engine() -> OutfitRecommendationEngine:
    """
    Get or create the global recommendation engine instance.
    
    Returns:
        OutfitRecommendationEngine instance
    """
    global _recommendation_engine_instance
    if _recommendation_engine_instance is None:
        _recommendation_engine_instance = OutfitRecommendationEngine()
    return _recommendation_engine_instance

def get_outfit_recommendations(user_preferences: Dict, items: List[Dict], 
                             occasion: str = "casual") -> List[Dict]:
    """
    Convenience function to get outfit recommendations.
    
    Args:
        user_preferences: User preferences
        items: Available clothing items
        occasion: Target occasion
        
    Returns:
        List of recommended outfits
    """
    engine = get_recommendation_engine()
    return engine.get_outfit_recommendations(user_preferences, items, occasion)

def get_similar_items(target_item: Dict, items: List[Dict]) -> List[Dict]:
    """
    Convenience function to get similar items.
    
    Args:
        target_item: Target item
        items: Available items
        
    Returns:
        List of similar items
    """
    engine = get_recommendation_engine()
    return engine.get_similar_items(target_item, items)

