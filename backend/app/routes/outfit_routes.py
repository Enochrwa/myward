from fastapi import APIRouter, HTTPException
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any
import json
import numpy as np
import uuid
from PIL import Image
import io
from ..db.database import get_database_connection
from ..utils.constants import CATEGORY_PART_MAPPING, CLOTHING_PARTS, OUTFIT_RULES


router = APIRouter(prefix="/outfit")


def build_image_url(filename: str) -> str:
    return f"http://127.0.0.1:8000/uploads/{filename}" if filename else None


def clean_item(item: Dict[str, Any]) -> Dict[str, Any]:
    item.pop('resnet_features', None)
    item.pop('opencv_features', None)

    for key in ['season', 'occasion']:
        raw_value = item.get(key)
        try:
            item[key] = json.loads(raw_value) if raw_value else []
        except:
            item[key] = [raw_value] if raw_value else []

    item['image_url'] = build_image_url(item['filename'])
    return item


def fetch_items_with_features(cursor, category: str, gender: str, cluster_id: int) -> List[Dict[str, Any]]:
    query = """
        SELECT * FROM images
        WHERE category = %s AND gender = %s AND cluster_id = %s
    """
    cursor.execute(query, (category, gender, cluster_id))
    return cursor.fetchall()


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
    base_cluster_id = base_item.get('cluster_id')

    base_part = CATEGORY_PART_MAPPING.get(base_category, "unknown")
    recommended_parts = OUTFIT_RULES.get(base_part, [])

    outfit = {base_category: base_item}

    for part in recommended_parts:
        for category in CLOTHING_PARTS.get(part, []):
            candidates = fetch_items_with_features(cursor, category, gender, base_cluster_id)
            if not candidates:
                continue
            
            features, items = [], []
            for item in candidates:
                try:
                    vec = np.array(json.loads(item['resnet_features']), dtype=np.float32)
                    features.append(vec)
                    items.append(item)
                except:
                    continue

            if not features:
                continue

            features = np.vstack(features)
            similarities = cosine_similarity([query_vector], features)[0]
            idx = similarities.argmax()

            candidate = clean_item(items[idx])
            if season and not any(s in candidate.get('season', []) for s in season):
                continue
            if occasion and not any(o in candidate.get('occasion', []) for o in occasion):
                continue
            outfit[category] = candidate
            break

    return {
        "query_image_id": image_id,
        "base_category": base_category,
        "outfit": outfit
    }


@router.post("/custom")
def save_custom_outfit(outfit: dict):
    user_id = "123"  # TODO: Replace with authenticated user id
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
            new_im.paste(im, (x_offset, 0))
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
