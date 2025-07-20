from fastapi import APIRouter, HTTPException
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any
import json
import numpy as np
import random
import uuid
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

    # Save the outfit
    outfit_id = str(uuid.uuid4())
    user_id = "123" # TODO: get from auth
    clothing_parts = {}
    clothing_items = []
    for category, item in outfit.items():
        clothing_parts[CATEGORY_PART_MAPPING.get(category, "accessory")] = item["id"]
        clothing_items.append(item["id"])

    query = """
        INSERT INTO outfits (id, user_id, name, gender, clothing_parts, clothing_items)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    values = (
        outfit_id,
        user_id,
        f"Recommended Outfit {outfit_id}",
        gender,
        json.dumps(clothing_parts),
        json.dumps(clothing_items),
    )

    cursor.execute(query, values)
    connection.commit()


    return {
        "query_image_id": image_id,
        "base_category": base_category,
        "outfit": outfit,
        "outfit_id": outfit_id
    }


from PIL import Image
import io

@router.post("/custom")
def save_custom_outfit(outfit: dict):
    # TODO: get user_id from auth token
    user_id = "123"
    outfit_id = str(uuid.uuid4())
    
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    # Image composition
    images_to_stitch = []
    for item_id in outfit.get("clothing_items", []):
        cursor.execute("SELECT filename FROM images WHERE id = %s", (item_id,))
        row = cursor.fetchone()
        if row:
            images_to_stitch.append(f"uploads/{row['filename']}")

    if images_to_stitch:
        images = [Image.open(i) for i in images_to_stitch]
        widths, heights = zip(*(i.size for i in images))

        total_width = sum(widths)
        max_height = max(heights)

        new_im = Image.new('RGB', (total_width, max_height))

        x_offset = 0
        for im in images:
            new_im.paste(im, (x_offset,0))
            x_offset += im.size[0]
        
        output = io.BytesIO()
        new_im.save(output, format='JPEG')
        preview_image = output.getvalue()
    else:
        preview_image = None


    query = """
        INSERT INTO outfits (id, user_id, name, gender, clothing_parts, clothing_items, preview_image)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    values = (
        outfit_id,
        user_id,
        outfit.get("name"),
        outfit.get("gender"),
        json.dumps(outfit.get("clothing_parts")),
        json.dumps(outfit.get("clothing_items")),
        preview_image
    )

    cursor.execute(query, values)
    connection.commit()

    return {"message": "Outfit saved successfully", "outfit_id": outfit_id}


@router.get("/user/{user_id}")
def get_user_outfits(user_id: str):
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM outfits WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    outfits = cursor.fetchall()

    return outfits


@router.delete("/{outfit_id}")
def delete_outfit(outfit_id: str):
    connection = get_database_connection()
    cursor = connection.cursor()

    query = "DELETE FROM outfits WHERE id = %s"
    cursor.execute(query, (outfit_id,))
    connection.commit()

    return {"message": "Outfit deleted successfully", "outfit_id": outfit_id}
