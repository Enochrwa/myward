from fastapi import APIRouter, HTTPException
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any
import json
import numpy as np
import random
from ..db.database import get_database_connection

router = APIRouter(prefix="/outfit")


def build_image_url(filename: str) -> str:
    BASE_URL = "http://127.0.0.1:8000/uploads/"
    return BASE_URL + filename if filename else None


def clean_item(item: Dict[str, Any]) -> Dict[str, Any]:
    item.pop('resnet_features', None)
    item.pop('opencv_features', None)

    for key in ['season', 'occasion']:
        raw_value = item.get(key)
        try:
            item[key] = json.loads(raw_value) if raw_value else []
        except (TypeError, json.JSONDecodeError):
            item[key] = [raw_value] if raw_value else []

    item['image_url'] = build_image_url(item['filename'])
    return item


def fetch_items_with_features(cursor, category: str, gender: str) -> List[Dict[str, Any]]:
    query = """
        SELECT * FROM images
        WHERE category = %s AND gender = %s
    """
    cursor.execute(query, (category, gender))
    return cursor.fetchall()


# Dynamic rules based on `clothing_part`
CATEGORY_PART_MAPPING = {
    "Overcoat": "outerwear", "bag": "accessory", "blazers": "outerwear", "blouse": "top", "coats": "outerwear",
    "croptop": "top", "dress": "full_body", "hat": "accessory", "hoodie": "outerwear", "jacket": "outerwear",
    "jeans": "bottom", "outwear": "outerwear", "shirt": "top", "shoes": "accessory", "shorts": "bottom",
    "skirt": "bottom", "suit": "full_body", "sunglasses": "accessory", "sweater": "top", "trousers": "bottom", "tshirt": "top"
}

OUTFIT_RULES = {
    "full_body": ["accessory", "outerwear"],
    "top": ["bottom", "outerwear", "accessory", "shoes"],
    "bottom": ["top", "outerwear", "accessory", "shoes"],
    "outerwear": ["top", "bottom", "accessory", "shoes"],
    "accessory": [],
}


@router.get("/recommend/{image_id}")
def recommend_outfit(image_id: str):
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM images WHERE id = %s", (image_id,))
    base_item = cursor.fetchone()
    if not base_item:
        raise HTTPException(status_code=404, detail="Image not found.")

    query_vector = np.array(json.loads(base_item['resnet_features']), dtype=np.float32)
    base_item = clean_item(base_item)

    gender = base_item.get('gender') or ""
    season = base_item.get('season', [])
    occasion = base_item.get('occasion', [])

    base_category = base_item['category']
    base_clothing_part = CATEGORY_PART_MAPPING.get(base_category, "accessory")
    allowed_parts = OUTFIT_RULES.get(base_clothing_part, [])

    # Build list of categories to fetch based on allowed clothing parts
    allowed_categories = [cat for cat, part in CATEGORY_PART_MAPPING.items() if part in allowed_parts]

    outfit = {base_category: base_item}

    for category in allowed_categories:
        candidates = fetch_items_with_features(cursor, category, gender)
        if not candidates:
            continue

        features = []
        items = []
        for item in candidates:
            try:
                vec = np.array(json.loads(item['resnet_features']), dtype=np.float32)
                features.append(vec)
                items.append(item)
            except Exception:
                continue

        if not features:
            continue

        features = np.vstack(features)
        similarities = cosine_similarity([query_vector], features)[0]
        sorted_indices = similarities.argsort()[::-1]

        for idx in sorted_indices:
            candidate = clean_item(items[idx])
            candidate_season = candidate.get('season', [])
            candidate_occasion = candidate.get('occasion', [])

            if season and not any(s in candidate_season for s in season):
                continue
            if occasion and not any(o in candidate_occasion for o in occasion):
                continue

            outfit[category] = candidate
            break
        else:
            outfit[category] = clean_item(items[sorted_indices[0]])

    return {
        "query_image_id": image_id,
        "base_category": base_category,
        "outfit": outfit
    }
