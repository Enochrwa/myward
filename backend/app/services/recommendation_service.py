import os
import joblib
import numpy as np
from typing import List
from sklearn.neighbors import NearestNeighbors

from .database_service import db_service, ClothingItemResponse


# Configuration
ML_READY_DIR = "ML_Ready"
KNN_TEMPLATE = "knn_{category}.joblib"


class RecommendationService:
    def __init__(self):
        self._knn_cache = {}

    def get_knn_model(self, category: str) -> NearestNeighbors:
        """
        Loads a KNN model for a specific category, caching it for future use.
        """
        if category not in self._knn_cache:
            model_path = os.path.join(ML_READY_DIR, KNN_TEMPLATE.format(category=category))
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"KNN model for category '{category}' not found.")
            self._knn_cache[category] = joblib.load(model_path)
        return self._knn_cache[category]

    def recommend_similar_items(self, item_id: str, top_k: int = 5) -> List[ClothingItemResponse]:
        """
        Recommends items similar to a given item based on its ResNet features.
        """
        # 1. Get the target item's features and category from the database
        target_item = db_service.get_clothing_item_by_id(item_id)
        target_item_features = target_item.resnet_features
        if not target_item_features:
            raise ValueError("Features for the target item not found.")

        # target_item_details = db_service.get_clothing_item_by_id(item_id)
        # if not target_item_details:
        #     raise ValueError("Target item details not found.")
        
        category = target_item.clothing_type_name
        query_features = np.array(target_item.resnet_features).reshape(1, -1)

        # 2. Load the corresponding KNN model
        knn_model = self.get_knn_model(category)

        # 3. Find the nearest neighbors
        distances, indices = knn_model.kneighbors(query_features, n_neighbors=top_k + 1)

        # 4. Get the item IDs from the file map
        # This part needs to be adapted to your new database structure.
        # Assuming you have a way to map the indices back to your database item IDs.
        # For now, I'll simulate this with a placeholder.
        # You'll need to replace this with your actual logic.
        
        # Placeholder: you need to implement this mapping
        # This could involve querying your database for all items in the category,
        # and then mapping the indices to the corresponding item IDs.
        all_items_in_category = db_service.get_all_items_in_category(category) # This is not efficient
        
        recommended_item_ids = [all_items_in_category[i].id for i in indices[0]]
        
        # 5. Exclude the query item itself and fetch the details of the recommended items
        recommended_items = []
        for recommended_id in recommended_item_ids:
            if recommended_id != item_id:
                item_details = db_service.get_clothing_item_by_id(recommended_id)
                if item_details:
                    recommended_items.append(item_details)
                if len(recommended_items) == top_k:
                    break
        
        return recommended_items


recommendation_service = RecommendationService()
