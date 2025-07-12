"""
Machine Learning-based Personalized Recommendation System

This module implements a machine learning model that learns from user behavior
and preferences to provide personalized clothing recommendations.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class UserBehaviorAnalyzer:
    """Analyzes user behavior patterns to understand preferences"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.kmeans = KMeans(n_clusters=5, random_state=42)
        self.tfidf_vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
    
    def analyze_user_preferences(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze user behavior to extract preferences
        
        Args:
            user_data: Dictionary containing user's wardrobe, outfits, and interaction history
        
        Returns:
            Dictionary with analyzed preferences
        """
        preferences = {
            "color_preferences": self._analyze_color_preferences(user_data),
            "style_preferences": self._analyze_style_preferences(user_data),
            "category_preferences": self._analyze_category_preferences(user_data),
            "occasion_patterns": self._analyze_occasion_patterns(user_data),
            "seasonal_preferences": self._analyze_seasonal_preferences(user_data),
            "brand_preferences": self._analyze_brand_preferences(user_data),
            "price_sensitivity": self._analyze_price_sensitivity(user_data)
        }
        
        return preferences
    
    def _analyze_color_preferences(self, user_data: Dict[str, Any]) -> Dict[str, float]:
        """Analyze user's color preferences based on wardrobe and outfit history"""
        color_counts = {}
        total_items = 0
        
        # Analyze wardrobe items
        wardrobe_items = user_data.get("wardrobe_items", [])
        for item in wardrobe_items:
            colors = item.get("colors", [])
            for color in colors:
                color_counts[color] = color_counts.get(color, 0) + 1
                total_items += 1
        
        # Analyze outfit history (items used more frequently get higher weight)
        outfit_history = user_data.get("outfit_history", [])
        for outfit in outfit_history:
            items = outfit.get("items", [])
            for item in items:
                colors = item.get("colors", [])
                for color in colors:
                    # Weight by frequency of use
                    color_counts[color] = color_counts.get(color, 0) + 2
                    total_items += 2
        
        # Convert to preferences (normalized scores)
        if total_items > 0:
            color_preferences = {color: count / total_items for color, count in color_counts.items()}
        else:
            color_preferences = {}
        
        return color_preferences
    
    def _analyze_style_preferences(self, user_data: Dict[str, Any]) -> Dict[str, float]:
        """Analyze user's style preferences"""
        style_counts = {}
        total_items = 0
        
        # Analyze wardrobe items
        wardrobe_items = user_data.get("wardrobe_items", [])
        for item in wardrobe_items:
            style = item.get("style", "casual")
            style_counts[style] = style_counts.get(style, 0) + 1
            total_items += 1
        
        # Analyze outfit history with higher weight
        outfit_history = user_data.get("outfit_history", [])
        for outfit in outfit_history:
            items = outfit.get("items", [])
            for item in items:
                style = item.get("style", "casual")
                style_counts[style] = style_counts.get(style, 0) + 3
                total_items += 3
        
        # Normalize
        if total_items > 0:
            style_preferences = {style: count / total_items for style, count in style_counts.items()}
        else:
            style_preferences = {}
        
        return style_preferences
    
    def _analyze_category_preferences(self, user_data: Dict[str, Any]) -> Dict[str, float]:
        """Analyze user's category preferences"""
        category_counts = {}
        total_items = 0
        
        wardrobe_items = user_data.get("wardrobe_items", [])
        for item in wardrobe_items:
            category = item.get("category", "unknown")
            category_counts[category] = category_counts.get(category, 0) + 1
            total_items += 1
        
        if total_items > 0:
            category_preferences = {cat: count / total_items for cat, count in category_counts.items()}
        else:
            category_preferences = {}
        
        return category_preferences
    
    def _analyze_occasion_patterns(self, user_data: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        """Analyze patterns for different occasions"""
        occasion_patterns = {}
        
        outfit_history = user_data.get("outfit_history", [])
        for outfit in outfit_history:
            occasion = outfit.get("occasion", "casual")
            if occasion not in occasion_patterns:
                occasion_patterns[occasion] = {"styles": {}, "colors": {}, "categories": {}}
            
            items = outfit.get("items", [])
            for item in items:
                # Track styles for this occasion
                style = item.get("style", "casual")
                occasion_patterns[occasion]["styles"][style] = \
                    occasion_patterns[occasion]["styles"].get(style, 0) + 1
                
                # Track colors for this occasion
                colors = item.get("colors", [])
                for color in colors:
                    occasion_patterns[occasion]["colors"][color] = \
                        occasion_patterns[occasion]["colors"].get(color, 0) + 1
                
                # Track categories for this occasion
                category = item.get("category", "unknown")
                occasion_patterns[occasion]["categories"][category] = \
                    occasion_patterns[occasion]["categories"].get(category, 0) + 1
        
        # Normalize each occasion's patterns
        for occasion, patterns in occasion_patterns.items():
            for pattern_type, counts in patterns.items():
                total = sum(counts.values())
                if total > 0:
                    occasion_patterns[occasion][pattern_type] = \
                        {item: count / total for item, count in counts.items()}
        
        return occasion_patterns
    
    def _analyze_seasonal_preferences(self, user_data: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        """Analyze seasonal preferences"""
        seasonal_patterns = {"spring": {}, "summer": {}, "autumn": {}, "winter": {}}
        
        outfit_history = user_data.get("outfit_history", [])
        for outfit in outfit_history:
            date_str = outfit.get("date", "")
            if not date_str:
                continue
            
            try:
                date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                season = self._get_season(date)
                
                items = outfit.get("items", [])
                for item in items:
                    category = item.get("category", "unknown")
                    seasonal_patterns[season][category] = \
                        seasonal_patterns[season].get(category, 0) + 1
            except:
                continue
        
        # Normalize
        for season, categories in seasonal_patterns.items():
            total = sum(categories.values())
            if total > 0:
                seasonal_patterns[season] = {cat: count / total for cat, count in categories.items()}
        
        return seasonal_patterns
    
    def _analyze_brand_preferences(self, user_data: Dict[str, Any]) -> Dict[str, float]:
        """Analyze brand preferences"""
        brand_counts = {}
        total_items = 0
        
        wardrobe_items = user_data.get("wardrobe_items", [])
        for item in wardrobe_items:
            brand = item.get("brand", "unknown")
            if brand and brand != "unknown":
                brand_counts[brand] = brand_counts.get(brand, 0) + 1
                total_items += 1
        
        if total_items > 0:
            brand_preferences = {brand: count / total_items for brand, count in brand_counts.items()}
        else:
            brand_preferences = {}
        
        return brand_preferences
    
    def _analyze_price_sensitivity(self, user_data: Dict[str, Any]) -> Dict[str, float]:
        """Analyze user's price sensitivity"""
        prices = []
        
        wardrobe_items = user_data.get("wardrobe_items", [])
        for item in wardrobe_items:
            price = item.get("price", 0)
            if price > 0:
                prices.append(price)
        
        if not prices:
            return {"average_price": 0, "price_range": "unknown", "sensitivity": "medium"}
        
        avg_price = np.mean(prices)
        price_std = np.std(prices)
        
        # Categorize price sensitivity
        if avg_price < 50:
            sensitivity = "high"  # Budget-conscious
        elif avg_price > 200:
            sensitivity = "low"   # Premium buyer
        else:
            sensitivity = "medium"
        
        return {
            "average_price": avg_price,
            "price_std": price_std,
            "sensitivity": sensitivity,
            "min_price": min(prices),
            "max_price": max(prices)
        }
    
    def _get_season(self, date: datetime) -> str:
        """Determine season from date"""
        month = date.month
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "autumn"

class PersonalizedRecommendationModel:
    """ML model for personalized recommendations"""
    
    def __init__(self):
        self.behavior_analyzer = UserBehaviorAnalyzer()
        self.item_similarity_matrix = None
        self.user_profiles = {}
        self.item_features = None
        self.is_trained = False
    
    def train_model(self, training_data: List[Dict[str, Any]]):
        """
        Train the recommendation model
        
        Args:
            training_data: List of user data dictionaries
        """
        logger.info("Training personalized recommendation model...")
        
        # Extract user profiles
        for user_data in training_data:
            user_id = user_data.get("user_id")
            if user_id:
                self.user_profiles[user_id] = self.behavior_analyzer.analyze_user_preferences(user_data)
        
        # Build item similarity matrix
        all_items = []
        for user_data in training_data:
            all_items.extend(user_data.get("wardrobe_items", []))
        
        if all_items:
            self._build_item_similarity_matrix(all_items)
        
        self.is_trained = True
        logger.info(f"Model trained with {len(self.user_profiles)} user profiles and {len(all_items)} items")
    
    def _build_item_similarity_matrix(self, items: List[Dict[str, Any]]):
        """Build item-to-item similarity matrix"""
        # Create feature vectors for items
        item_features = []
        item_ids = []
        
        for item in items:
            features = self._extract_item_features(item)
            item_features.append(features)
            item_ids.append(item.get("id", ""))
        
        if item_features:
            # Convert to numpy array and calculate similarity
            feature_matrix = np.array(item_features)
            self.item_similarity_matrix = cosine_similarity(feature_matrix)
            self.item_ids = item_ids
    
    def _extract_item_features(self, item: Dict[str, Any]) -> List[float]:
        """Extract numerical features from an item"""
        features = []
        
        # Color features (simplified - use color counts)
        colors = item.get("colors", [])
        color_features = [1 if color in colors else 0 for color in 
                         ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF", "#000000", "#FFFFFF"]]
        features.extend(color_features)
        
        # Style features (one-hot encoding)
        style = item.get("style", "casual")
        style_features = [1 if style == s else 0 for s in 
                         ["casual", "formal", "business", "sporty", "elegant", "trendy"]]
        features.extend(style_features)
        
        # Category features (one-hot encoding)
        category = item.get("category", "unknown")
        category_features = [1 if category == c else 0 for c in 
                           ["tops", "bottoms", "shoes", "accessories", "outerwear", "dresses"]]
        features.extend(category_features)
        
        # Price feature (normalized)
        price = item.get("price", 0)
        price_normalized = min(price / 1000, 1.0)  # Normalize to 0-1 range
        features.append(price_normalized)
        
        return features
    
    def get_personalized_recommendations(
        self,
        user_id: str,
        target_item: Optional[Dict[str, Any]] = None,
        occasion: Optional[str] = None,
        num_recommendations: int = 5,
        available_items: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get personalized recommendations for a user
        
        Args:
            user_id: User identifier
            target_item: Optional item to find matches for
            occasion: Optional occasion context
            num_recommendations: Number of recommendations to return
            available_items: Available items to recommend from
        
        Returns:
            List of recommended items with scores
        """
        if not self.is_trained:
            logger.warning("Model not trained. Returning empty recommendations.")
            return []
        
        user_profile = self.user_profiles.get(user_id)
        if not user_profile:
            logger.warning(f"No profile found for user {user_id}")
            return []
        
        if not available_items:
            available_items = []
        
        recommendations = []
        
        for item in available_items:
            score = self._calculate_personalized_score(
                item, user_profile, target_item, occasion
            )
            
            if score > 0.3:  # Minimum threshold
                recommendations.append({
                    **item,
                    "recommendation_score": score,
                    "recommendation_reasons": self._get_recommendation_reasons(
                        item, user_profile, target_item, occasion
                    )
                })
        
        # Sort by score and return top recommendations
        recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)
        return recommendations[:num_recommendations]
    
    def _calculate_personalized_score(
        self,
        item: Dict[str, Any],
        user_profile: Dict[str, Any],
        target_item: Optional[Dict[str, Any]] = None,
        occasion: Optional[str] = None
    ) -> float:
        """Calculate personalized recommendation score"""
        score = 0.0
        
        # Color preference score (25% weight)
        color_prefs = user_profile.get("color_preferences", {})
        item_colors = item.get("colors", [])
        color_score = sum(color_prefs.get(color, 0) for color in item_colors)
        score += color_score * 0.25
        
        # Style preference score (25% weight)
        style_prefs = user_profile.get("style_preferences", {})
        item_style = item.get("style", "casual")
        style_score = style_prefs.get(item_style, 0)
        score += style_score * 0.25
        
        # Category preference score (15% weight)
        category_prefs = user_profile.get("category_preferences", {})
        item_category = item.get("category", "unknown")
        category_score = category_prefs.get(item_category, 0)
        score += category_score * 0.15
        
        # Occasion appropriateness (20% weight)
        if occasion:
            occasion_patterns = user_profile.get("occasion_patterns", {})
            if occasion in occasion_patterns:
                occasion_style_prefs = occasion_patterns[occasion].get("styles", {})
                occasion_color_prefs = occasion_patterns[occasion].get("colors", {})
                
                occasion_score = (
                    occasion_style_prefs.get(item_style, 0) * 0.6 +
                    sum(occasion_color_prefs.get(color, 0) for color in item_colors) * 0.4
                )
                score += occasion_score * 0.20
        
        # Item similarity (if target item provided) (15% weight)
        if target_item and self.item_similarity_matrix is not None:
            similarity_score = self._get_item_similarity(target_item, item)
            score += similarity_score * 0.15
        
        return min(1.0, max(0.0, score))
    
    def _get_item_similarity(self, item1: Dict[str, Any], item2: Dict[str, Any]) -> float:
        """Get similarity score between two items"""
        if not self.item_similarity_matrix:
            return 0.0
        
        item1_id = item1.get("id", "")
        item2_id = item2.get("id", "")
        
        try:
            idx1 = self.item_ids.index(item1_id)
            idx2 = self.item_ids.index(item2_id)
            return self.item_similarity_matrix[idx1][idx2]
        except (ValueError, IndexError):
            return 0.0
    
    def _get_recommendation_reasons(
        self,
        item: Dict[str, Any],
        user_profile: Dict[str, Any],
        target_item: Optional[Dict[str, Any]] = None,
        occasion: Optional[str] = None
    ) -> List[str]:
        """Generate human-readable reasons for the recommendation"""
        reasons = []
        
        # Check color preferences
        color_prefs = user_profile.get("color_preferences", {})
        item_colors = item.get("colors", [])
        preferred_colors = [color for color in item_colors if color_prefs.get(color, 0) > 0.1]
        if preferred_colors:
            reasons.append(f"Matches your preferred colors")
        
        # Check style preferences
        style_prefs = user_profile.get("style_preferences", {})
        item_style = item.get("style", "casual")
        if style_prefs.get(item_style, 0) > 0.2:
            reasons.append(f"Fits your {item_style} style preference")
        
        # Check occasion appropriateness
        if occasion:
            occasion_patterns = user_profile.get("occasion_patterns", {})
            if occasion in occasion_patterns:
                reasons.append(f"Perfect for {occasion} occasions")
        
        # Check similarity to target item
        if target_item:
            reasons.append(f"Complements your {target_item.get('name', 'selected item')}")
        
        return reasons if reasons else ["Recommended based on your profile"]
    
    def update_user_profile(self, user_id: str, new_data: Dict[str, Any]):
        """Update user profile with new data"""
        if user_id in self.user_profiles:
            # Merge new preferences with existing ones
            new_preferences = self.behavior_analyzer.analyze_user_preferences(new_data)
            
            # Simple averaging for now (could be more sophisticated)
            existing_prefs = self.user_profiles[user_id]
            for pref_type, prefs in new_preferences.items():
                if pref_type in existing_prefs and isinstance(prefs, dict):
                    for key, value in prefs.items():
                        if key in existing_prefs[pref_type]:
                            existing_prefs[pref_type][key] = (existing_prefs[pref_type][key] + value) / 2
                        else:
                            existing_prefs[pref_type][key] = value
                else:
                    existing_prefs[pref_type] = prefs
        else:
            self.user_profiles[user_id] = self.behavior_analyzer.analyze_user_preferences(new_data)
    
    def save_model(self, filepath: str):
        """Save the trained model"""
        model_data = {
            "user_profiles": self.user_profiles,
            "item_similarity_matrix": self.item_similarity_matrix.tolist() if self.item_similarity_matrix is not None else None,
            "item_ids": getattr(self, "item_ids", []),
            "is_trained": self.is_trained
        }
        
        with open(filepath, 'w') as f:
            json.dump(model_data, f, indent=2)
        
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load a trained model"""
        try:
            with open(filepath, 'r') as f:
                model_data = json.load(f)
            
            self.user_profiles = model_data.get("user_profiles", {})
            similarity_matrix = model_data.get("item_similarity_matrix")
            if similarity_matrix:
                self.item_similarity_matrix = np.array(similarity_matrix)
            self.item_ids = model_data.get("item_ids", [])
            self.is_trained = model_data.get("is_trained", False)
            
            logger.info(f"Model loaded from {filepath}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")

# Example usage
if __name__ == "__main__":
    # Example training data
    training_data = [
        {
            "user_id": "user1",
            "wardrobe_items": [
                {"id": "1", "name": "Blue Shirt", "colors": ["#0000FF"], "style": "business", "category": "tops", "price": 50},
                {"id": "2", "name": "Black Pants", "colors": ["#000000"], "style": "business", "category": "bottoms", "price": 80}
            ],
            "outfit_history": [
                {
                    "date": "2024-01-15",
                    "occasion": "work",
                    "items": [
                        {"id": "1", "colors": ["#0000FF"], "style": "business", "category": "tops"},
                        {"id": "2", "colors": ["#000000"], "style": "business", "category": "bottoms"}
                    ]
                }
            ]
        }
    ]
    
    # Train model
    model = PersonalizedRecommendationModel()
    model.train_model(training_data)
    
    # Get recommendations
    available_items = [
        {"id": "3", "name": "White Shirt", "colors": ["#FFFFFF"], "style": "business", "category": "tops", "price": 45},
        {"id": "4", "name": "Red Dress", "colors": ["#FF0000"], "style": "elegant", "category": "dresses", "price": 120}
    ]
    
    recommendations = model.get_personalized_recommendations(
        user_id="user1",
        occasion="work",
        available_items=available_items
    )
    
    for rec in recommendations:
        print(f"Recommendation: {rec['name']} - Score: {rec['recommendation_score']:.2f}")
        print(f"Reasons: {', '.join(rec['recommendation_reasons'])}")

