# backend/app/services/user_style_profile_service.py
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import func
from datetime import datetime
from typing import List, Dict, Any, Optional, Set
import json

from .. import model as models # SQLAlchemy models
from .. import tables as schemas # Pydantic schemas

# Helper function to update JSON list fields (ensuring uniqueness and managing counts)
def _update_json_list_field(current_values_json: Optional[str], new_items: List[str], add: bool = True, max_items: int = 20) -> str:
    """
    Updates a JSON field that stores a list of strings, optionally with frequency counts.
    For simplicity in this version, it will store a list of unique items, recency biased.
    """
    current_list: List[str] = []
    if current_values_json:
        try:
            loaded_list = json.loads(current_values_json)
            if isinstance(loaded_list, list):
                current_list = loaded_list
        except json.JSONDecodeError:
            pass # Start with an empty list if JSON is invalid

    updated_set = set(current_list)

    if add:
        for item in new_items:
            if item: # Ensure item is not None or empty
                # If item already exists, remove to re-add at the end (recency)
                if item in updated_set:
                    updated_set.remove(item)
                updated_set.add(item)
        # Convert set back to list, then manage recency by taking the latest additions
        # This simplistic approach keeps most recent `max_items` unique items.
        temp_list = list(updated_set)
        # A more robust recency would involve timestamps or ordered list management.
        # For now, just add new items and trim.
        # If we want true recency, we'd do:
        # current_list = [x for x in current_list if x not in new_items] # remove items to re-add
        # current_list.extend(new_items)
        # final_list = list(dict.fromkeys(current_list)) # unique, preserves order of last appearance
        # final_list = final_list[-max_items:]
        
        # Simpler: just add and trim
        final_list = list(updated_set) # Order is not guaranteed here from set.
        # To maintain some order of insertion for new items:
        new_unique_items_to_add = [item for item in new_items if item and item not in current_list]
        current_list.extend(new_unique_items_to_add)
        final_list = list(dict.fromkeys(current_list)) # Unique, preserves order of last appearance
        
    else: # Remove items
        final_list = [val for val in current_list if val not in new_items]
        
    return json.dumps(final_list[-max_items:])


def _update_json_dict_field(current_values_json: Optional[str], updates: Dict[str, Any], sub_key_to_update: Optional[str] = None, items_to_add: Optional[List[str]] = None, max_list_items: int = 10) -> str:
    """
    Updates a JSON field that stores a dictionary.
    If sub_key_to_update and items_to_add are provided, it treats current_values_json[sub_key_to_update] as a list.
    Otherwise, it merges `updates` into the top-level dictionary.
    """
    current_dict: Dict[str, Any] = {}
    if current_values_json:
        try:
            loaded_dict = json.loads(current_values_json)
            if isinstance(loaded_dict, dict):
                current_dict = loaded_dict
        except json.JSONDecodeError:
            pass

    if sub_key_to_update and items_to_add: # Updating a list within the dictionary
        sub_list_json = json.dumps(current_dict.get(sub_key_to_update, []))
        updated_sub_list_json = _update_json_list_field(sub_list_json, items_to_add, add=True, max_items=max_list_items)
        current_dict[sub_key_to_update] = json.loads(updated_sub_list_json)
    else: # Merging at the top level
        for key, value in updates.items():
            # Basic merge, for lists, it could append or replace based on strategy
            # For this version, it will overwrite if keys conflict, unless value is a list to extend
            if isinstance(current_dict.get(key), list) and isinstance(value, list):
                existing_list_json = json.dumps(current_dict[key])
                updated_list_json = _update_json_list_field(existing_list_json,value, add=True, max_items=max_list_items * 2) # larger max for general dict lists
                current_dict[key] = json.loads(updated_list_json)
            else:
                 current_dict[key] = value # Overwrite for non-lists or if types don't match for list merging
                 
    return json.dumps(current_dict)


def get_or_create_user_style_profile(db: Session, user_id: int) -> models.UserStyleProfile:
    db_style_profile = db.query(models.UserStyleProfile).filter(models.UserStyleProfile.user_id == user_id).first()
    if not db_style_profile:
        db_style_profile = models.UserStyleProfile(
            user_id=user_id,
            preferred_colors=json.dumps([]),
            preferred_categories=json.dumps([]),
            preferred_brands=json.dumps([]),
            style_keywords=json.dumps([]),
            seasonal_preferences=json.dumps({}), # E.g., {"spring": {"colors": [], "styles": []}}
            occasion_preferences=json.dumps({}), # E.g., {"formal": {"colors": [], "styles": []}}
            last_updated=datetime.utcnow()
        )
        db.add(db_style_profile)
        # No commit here, assume calling function will commit.
        # However, for get_or_create, it's often better to commit immediately.
        # Let's try committing here for atomicity of get_or_create.
        try:
            db.commit()
            db.refresh(db_style_profile)
        except Exception as e:
            db.rollback()
            # Re-fetch in case of concurrent creation, or raise error
            db_style_profile = db.query(models.UserStyleProfile).filter(models.UserStyleProfile.user_id == user_id).first()
            if not db_style_profile:
                raise e # Re-raise if still not found after rollback & re-fetch
            
    return db_style_profile

def sync_user_profile_to_style_profile(db: Session, user_id: int) -> Optional[models.UserStyleProfile]:
    user_profile = db.query(models.UserProfile).filter(models.UserProfile.user_id == user_id).first()
    if not user_profile:
        return None

    style_profile = get_or_create_user_style_profile(db, user_id)

    if user_profile.preferred_colors:
        # This will overwrite existing preferred_colors in UserStyleProfile with UserProfile's list
        style_profile.preferred_colors = _update_json_list_field(None, user_profile.preferred_colors, add=True)
    
    # For preferred_styles from UserProfile, add them to style_keywords in UserStyleProfile
    if user_profile.preferred_styles:
        style_profile.style_keywords = _update_json_list_field(
            style_profile.style_keywords,
            [style.lower() for style in user_profile.preferred_styles],
            add=True
        )
    
    # Note: UserProfile.avoided_colors are not directly mapped here.
    # This logic could be integrated into recommendation filtering instead.

    style_profile.last_updated = datetime.utcnow()
    # db.commit() # Assume calling function will commit
    return style_profile

def update_style_profile_from_item_interaction(
    db: Session, user_id: int, item_id: int, interaction_type: str # "favorite" or "unfavorite"
) -> Optional[models.UserStyleProfile]:
    
    item = db.query(models.WardrobeItem).filter(models.WardrobeItem.id == item_id, models.WardrobeItem.user_id == user_id).first()
    if not item:
        return None

    style_profile = get_or_create_user_style_profile(db, user_id)
    
    add_preference = interaction_type == "favorite"

    # Preferred Colors
    if item.dominant_color_name:
        style_profile.preferred_colors = _update_json_list_field(
            style_profile.preferred_colors, [item.dominant_color_name.lower()], add=add_preference
        )

    # Preferred Categories
    if item.category:
        style_profile.preferred_categories = _update_json_list_field(
            style_profile.preferred_categories, [item.category.lower()], add=add_preference
        )

    # Preferred Brands
    if item.brand:
        style_profile.preferred_brands = _update_json_list_field(
            style_profile.preferred_brands, [item.brand.lower()], add=add_preference
        )

    # Style Keywords from item's own style_features
    if item.style_features:
        item_style_features = item.style_features # This is already a dict
        keywords_to_update = []
        if isinstance(item_style_features.get("identified_styles"), list):
            keywords_to_update.extend([s.lower() for s in item_style_features["identified_styles"]])
        if isinstance(item_style_features.get("raw_keywords"), list):
            keywords_to_update.extend([kw.lower() for kw in item_style_features["raw_keywords"]])
        
        if keywords_to_update:
            style_profile.style_keywords = _update_json_list_field(
                style_profile.style_keywords, keywords_to_update, add=add_preference
            )
            
    style_profile.last_updated = datetime.utcnow()
    # db.commit() # Assume calling function will commit
    return style_profile

def update_style_profile_from_outfit_history(
    db: Session, user_id: int, outfit_id: int, style_history_entry: models.StyleHistory
) -> Optional[models.UserStyleProfile]:
    
    outfit = db.query(models.Outfit).filter(models.Outfit.id == outfit_id, models.Outfit.user_id == user_id).first()
    if not outfit:
        return None

    style_profile = get_or_create_user_style_profile(db, user_id)
    
    # General preferences from outfit items
    all_item_colors: List[str] = []
    all_item_categories: List[str] = []
    all_item_brands: List[str] = []
    all_item_style_keywords: List[str] = []

    for item in outfit.items: # outfit.items should be the list of WardrobeItem objects
        if item.dominant_color_name: all_item_colors.append(item.dominant_color_name.lower())
        if item.category: all_item_categories.append(item.category.lower())
        if item.brand: all_item_brands.append(item.brand.lower())
        if item.style_features:
            item_sf = item.style_features
            if isinstance(item_sf.get("identified_styles"), list):
                all_item_style_keywords.extend([s.lower() for s in item_sf["identified_styles"]])
            if isinstance(item_sf.get("raw_keywords"), list):
                all_item_style_keywords.extend([kw.lower() for kw in item_sf["raw_keywords"]])

    if all_item_colors:
        style_profile.preferred_colors = _update_json_list_field(style_profile.preferred_colors, all_item_colors, add=True)
    if all_item_categories:
        style_profile.preferred_categories = _update_json_list_field(style_profile.preferred_categories, all_item_categories, add=True)
    if all_item_brands:
        style_profile.preferred_brands = _update_json_list_field(style_profile.preferred_brands, all_item_brands, add=True)
    if all_item_style_keywords:
        style_profile.style_keywords = _update_json_list_field(style_profile.style_keywords, all_item_style_keywords, add=True)

    # Occasion-specific preferences
    occasion_name: Optional[str] = None
    if style_history_entry.notes: # Assuming occasion might be in notes or linked via outfit.
        # A more robust way would be to link StyleHistory to an Occasion table entry if it exists
        # For now, let's assume notes might contain occasion type if not directly linked.
        # This part is speculative. A direct link from StyleHistory to Occasion model would be better.
        # If outfit is linked to an Occasion (models.Occasion.outfit_assigned)
        # We'd need to fetch that Occasion record.
        # For now, we don't have a direct occasion_id on StyleHistory, but Outfit can be linked to Occasions.
        # Let's check if the outfit itself is linked to an occasion.
        # This is not straightforward as an outfit can be linked to multiple occasions.
        # And StyleHistory is for a specific instance of wearing.
        # A potential improvement: add an optional `occasion_id` to `StyleHistory` model.
        # For now, this part of occasion learning is limited.
        # Let's assume for a moment we can get an occasion_name string.
        # Example: occasion_name = "formal_event" (hypothetical)
        pass # Placeholder for more robust occasion detection from style_history_entry

    # If we had an occasion_name:
    # if occasion_name:
    #    current_occasion_prefs_json = style_profile.occasion_preferences
    #    # Load current dict
    #    occasion_prefs_dict = json.loads(current_occasion_prefs_json) if current_occasion_prefs_json else {}
    #    occasion_key_data = occasion_prefs_dict.get(occasion_name, {})
    #
    #    # Update colors for this occasion
    #    occasion_colors_json = json.dumps(occasion_key_data.get("colors", []))
    #    updated_occasion_colors_json = _update_json_list_field(occasion_colors_json, all_item_colors, add=True)
    #    occasion_key_data["colors"] = json.loads(updated_occasion_colors_json)
    #    
    #    # Update styles for this occasion (using identified_styles from items)
    #    item_identified_styles = []
    #    for item in outfit.items:
    #        if item.style_features and isinstance(item.style_features.get("identified_styles"), list):
    #            item_identified_styles.extend([s.lower() for s in item.style_features["identified_styles"]])
    #    
    #    occasion_styles_json = json.dumps(occasion_key_data.get("styles", []))
    #    updated_occasion_styles_json = _update_json_list_field(occasion_styles_json, list(set(item_identified_styles)), add=True)
    #    occasion_key_data["styles"] = json.loads(updated_occasion_styles_json)
    #
    #    occasion_prefs_dict[occasion_name] = occasion_key_data
    #    style_profile.occasion_preferences = json.dumps(occasion_prefs_dict)


    style_profile.last_updated = datetime.utcnow()
    # db.commit() # Assume calling function will commit
    return style_profile

# Placeholder for future, more advanced preference learning
def learn_style_vector_from_interactions(db: Session, user_id: int):
    # This would involve fetching all user interactions (favorites, outfits worn, ratings)
    # and potentially using ML techniques (e.g., collaborative filtering, content-based filtering with embeddings)
    # to derive a style_vector. For now, this is out of scope for direct implementation.
    pass
