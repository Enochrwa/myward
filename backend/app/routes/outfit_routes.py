from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from ..security import get_current_user
from ..model import User
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any
import json
import numpy as np
import uuid
from PIL import Image
from ..db.database import get_database_connection
from ..utils.constants import CATEGORY_PART_MAPPING, CLOTHING_PARTS, OUTFIT_RULES
from ..utils.cluster import main as run_clustering
from ..services.outfit_creation_service import SmartOutfitCreator
from ..services.occasion_weather_outfits import WeatherService, WeatherOccasionRequest, WeatherData,SmartOutfitRecommender  # Assuming you have this or define it similarly to your example
import os

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


@router.get("/recommend/{image_id}")
def recommend_outfit(image_id: str, current_user: User = Depends(get_current_user)):
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM images WHERE id = %s AND user_id = %s", (image_id, current_user.id))
    base_item = cursor.fetchone()
    if not base_item:
        raise HTTPException(status_code=404, detail="Image not found or you do not own it.")

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
            cursor.execute("""
                SELECT * FROM images 
                WHERE category = %s AND gender = %s AND cluster_id = %s
            """, (category, gender, base_cluster_id))
            candidates = cursor.fetchall()
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
def save_custom_outfit(outfit: dict, user: User = Depends(get_current_user)):
    user_id = user.id
    outfit_id = str(uuid.uuid4())
    
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    # Stitch preview image
    images_to_stitch = []
    for item_id in outfit.get("clothing_items", []):
        cursor.execute("SELECT filename FROM images WHERE id = %s AND user_id = %s", (item_id,user_id))
        row = cursor.fetchone()
        if row:
            images_to_stitch.append(f"uploads/{row['filename']}")

    preview_image_filename = f"outfit_{outfit_id}.jpg"
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
        
        new_im.save(f"uploads/{preview_image_filename}", 'JPEG')
    else:
        preview_image_filename = None

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
        preview_image_filename
    )

    cursor.execute(query, values)
    connection.commit()

    return {"message": "Outfit saved successfully", "outfit_id": outfit_id, "preview_image_url": build_image_url(preview_image_filename)}


@router.get("/user")
def get_user_outfits(current_user: User = Depends(get_current_user)):
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM outfits WHERE user_id = %s"
    cursor.execute(query, (current_user.id,))
    outfits = cursor.fetchall()

    for outfit in outfits:
        outfit['preview_image_url'] = build_image_url(outfit['preview_image'])

    return outfits


@router.post("/cluster")
def cluster_images(current_user: User = Depends(get_current_user)):
    if not current_user.role == "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    try:
        run_clustering()
        return {"message": "Clustering process started successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{outfit_id}")
def delete_outfit(outfit_id: str, current_user: User = Depends(get_current_user)):
    connection = get_database_connection()
    cursor = connection.cursor()
    query = "DELETE FROM outfits WHERE id = %s AND user_id = %s"
    cursor.execute(query, (outfit_id, current_user.id))
    connection.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Outfit not found or you do not own it")
    return {"message": "Outfit deleted successfully", "outfit_id": outfit_id}


class SmartOutfitRequest(BaseModel):
    wardrobe_items: List[Dict[str, Any]]
    preferences: Dict[str, Any]




@router.get("/user-clothes")
def get_user_images(user = Depends(get_current_user)):
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)
    
    if user and user.role == 'admin':
        query = "SELECT * FROM images"
        cursor.execute(query)
    else:
        query = "SELECT * FROM images WHERE user_id = %s"
        cursor.execute(query, (user.id,))
        
    images = cursor.fetchall()
    for item in images:
        item['image_url'] = build_image_url(item['filename'])
    return images

@router.get("/user-clothes/{user_id}")
def get_user_clothes_by_id(user_id: int, current_user: User = Depends(get_current_user)):
    if not current_user.role == "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = "SELECT * FROM images WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    
    images = cursor.fetchall()
    for item in images:
        item['image_url'] = build_image_url(item['filename'])
    
    return images

@router.get("/user-items")
def get_user_images(user = Depends(get_current_user)):
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM images WHERE user_id = %s"
    cursor.execute(query, (user.id,))
    
    images = cursor.fetchall()
    for item in images:
        item['image_url'] = build_image_url(item['filename'])
    return images

@router.get("/user-clothes-admin/{user_id}/")  # <== Fix route
def get_user_images(user_id: str):
    try:
        connection = get_database_connection()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM images WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        images = cursor.fetchall()
        
        for item in images:
            item['image_url'] = build_image_url(item['filename'])

        return {"status": "success", "data": images}  # <== Proper return
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{outfit_id}/toggle-favorite")
def toggle_favorite_outfit(outfit_id: str, user: dict = Depends(get_current_user)):
    user_id = user['id']
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    # First, get the current favorite status
    cursor.execute("SELECT is_favorite FROM outfits WHERE id = %s AND user_id = %s", (outfit_id, user_id))
    outfit = cursor.fetchone()

    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found.")

    new_status = not outfit['is_favorite']

    # Update the favorite status
    query = "UPDATE outfits SET is_favorite = %s WHERE id = %s AND user_id = %s"
    cursor.execute(query, (new_status, outfit_id, user_id))
    connection.commit()

    return {"message": "Favorite status updated successfully", "outfit_id": outfit_id, "is_favorite": new_status}




@router.put("/{outfit_id}")
def update_outfit(outfit_id: str, outfit: dict, user: dict = Depends(get_current_user)):
    user_id = user.id
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        UPDATE outfits
        SET name = %s,
            gender = %s,
            clothing_parts = %s,
            clothing_items = %s,
            score = %s,
            description = %s,
            is_favorite = %s,
            dominant_colors = %s,
            styles = %s,
            occasions = %s
        WHERE id = %s AND user_id = %s
    """
    
    values = (
        outfit.get("name"),
        outfit.get("gender"),
        json.dumps(outfit.get("clothing_parts")),
        json.dumps(outfit.get("clothing_items")),
        outfit.get("score"),
        outfit.get("description"),
        outfit.get("is_favorite", False),
        json.dumps(outfit.get("dominant_colors")),
        json.dumps(outfit.get("styles")),
        json.dumps(outfit.get("occasions")),
        outfit_id,
        user_id
    )

    cursor.execute(query, values)
    connection.commit()

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Outfit not found or user not authorized.")

    return {"message": "Outfit updated successfully", "outfit_id": outfit_id}


class SmartOutfitRequest(BaseModel):
    wardrobe_items: List[Dict[str, Any]]
    preferences: Dict[str, Any]


@router.post("/generate-smart-outfits")
def generate_smart_outfits(request: SmartOutfitRequest):
    creator = SmartOutfitCreator()
    recommendations = creator.create_smart_outfits(
        wardrobe_items=request.wardrobe_items,
        preferences=request.preferences,
        top_n=10
    )
    return recommendations



@router.post("/recommend/weather-occasion")
def recommend_weather_occasion(request: WeatherOccasionRequest):
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Weather API key not configured.")
    
    weather_service = WeatherService(api_key)
    weather = weather_service.get_current_weather(request.city, request.country_code)

    recommender = SmartOutfitRecommender(weather_service)
    recommender.load_wardrobe(request.wardrobe_items)
    recommendations = recommender.generate_outfit_combinations(
        weather=weather,
        occasion=request.occasion,
        max_combinations=10, # Increased combinations
        creativity=getattr(request, 'creativity', 0.5)
    )

    # Format response to match your frontend expectations
    result = []
    for outfit in recommendations:
        result.append({
            "items": [
                {
                    "id": item.id,
                    "image_url": f"http://127.0.0.1:8000/uploads/{item.filename}",
                    "category": item.category,
                    "style": item.style,
                    "occasion": item.occasion,
                    "season": item.season,
                    "color": item.dominant_color
                }
                for item in outfit.items
            ],
            "score": outfit.overall_score()
        })

    return result



