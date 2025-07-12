# This module coordinates AI services for outfit analysis.
# It now uses lightweight models for embedding, style detection (placeholder),
# and item identification, or can operate in a demo mode with static data.

import os
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from PIL import Image
import io
import numpy as np
from typing import List, Optional, Union, Any # Added Union, Any
from sklearn.cluster import KMeans
import logging # Added for logging

from .. import tables as schemas # models import removed as it wasn't used directly here
# Import new lightweight AI modules
from .ai_embedding import get_image_embedding
from .ai_style import detect_style as lw_detect_style # Alias to avoid conflict if needed
from .ai_recommender import identify_items as lw_identify_items, get_basic_recommendations

# --- Global Configuration ---
# DEMO_MODE can be triggered by an environment variable for easier configuration
DEMO_MODE = os.getenv("AI_DEMO_MODE", "false").lower() == "true"

logger = logging.getLogger(__name__) # Added logger

if DEMO_MODE:
    logger.info("AI Services are running in DEMO MODE.")

# --- AI Functions ---

# extract_colors remains the same as it uses scikit-learn (considered lightweight enough)
def extract_colors(image: Image.Image, num_colors=5) -> List[str]:
    """
    Extracts dominant colors from an image using KMeans clustering.
    """
    try:
        image_work = image.copy() # Work on a copy
        image_work.thumbnail((100, 100))
        image_arr = np.array(image_work)

        if image_arr.ndim == 2:
            image_arr = np.stack((image_arr,)*3, axis=-1)
        elif image_arr.shape[2] == 4:
            image_arr = image_arr[:, :, :3]

        if image_arr.shape[0] == 0 or image_arr.shape[1] == 0 : # Check for empty image after thumbnail
             raise ValueError("Image became empty after thumbnailing, check input image.")

        pixels = image_arr.reshape(-1, 3)
        if pixels.shape[0] < num_colors: # Not enough pixels for desired clusters
            # Fallback: return fewer colors or a default palette
            # For simplicity, returning a default if too few pixels
            logger.warning(f"Not enough pixels to extract {num_colors} colors. Returning default.")
            return ["#FFFFFF", "#000000", "#CCCCCC"]


        kmeans = KMeans(n_clusters=num_colors, random_state=0, n_init='auto').fit(pixels)
        dominant_colors = kmeans.cluster_centers_.astype(int)
        hex_colors = [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in dominant_colors]
        return hex_colors
    except Exception as e:
        logger.error(f"Error during color extraction: {e}")
        return ["#EAEAEA", "#B0B0B0", "#505050", "#202020", "#F0F0F0"] # Default palette on error

# --- Main Service Function ---

async def analyze_outfit_image_service(
    file: UploadFile,
    db: Session, # db and user are kept for potential future use (e.g., saving analysis)
    user: schemas.User
) -> schemas.OutfitAnalysisResponse:
    try:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="No image data received.")
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

    # --- DEMO MODE ---
    if DEMO_MODE:
        logger.info(f"DEMO MODE: Analyzing {file.filename}")
        # Static data for demo mode
        demo_style = "Demo: Chic Casual"
        demo_colors = ["#FFD700", "#4682B4", "#32CD32", "#FF69B4", "#FFFFFF"]
        demo_items = [ # Simulating structure from identify_items
            {"label": "Demo Blazer", "confidence": 0.9, "box_normalized": [0.1,0.1,0.5,0.5]},
            {"label": "Demo White Shirt", "confidence": 0.85, "box_normalized": [0.15,0.15,0.45,0.45]},
            {"label": "Demo Jeans", "confidence": 0.92, "box_normalized": [0.5,0.1,0.9,0.5]}
        ]
        # Extract item names for recommendations and response
        demo_item_names = [item['label'] for item in demo_items]
        demo_recommendations = get_basic_recommendations(demo_items) # Use recommender with demo items
        demo_embedding_info = "Demo mode: Embeddings not generated."

        return schemas.OutfitAnalysisResponse(
            fileName=file.filename,
            contentType=file.content_type,
            style=demo_style,
            dominantColors=demo_colors,
            # identifiedItems expects List[str] in the original schema based on usage.
            # The new identify_items returns List[Dict]. We need to adapt.
            # For now, let's extract labels for compatibility.
            identifiedItems=demo_item_names,
            occasionSuitability="Demo: Suitable for casual outings",
            confidenceScore=0.90, # Static confidence for demo
            recommendations=demo_recommendations,
            # Embedding field is not in OutfitAnalysisResponse, so no need to pass demo_embedding_info to it.
            # It was mentioned it's stored for later use, which is outside this function's direct return.
            colorPalette=[{"color": c, "name": "Demo Color", "percentage": round(100/len(demo_colors),1)} for c in demo_colors],
            styleInsights=[{"category": "Overall Style", "score": 85, "description": f"The outfit is a classic example of: {demo_style}"}],
            debug_info=f"Analyzed with lightweight models (DEMO MODE). Embedding status: {demo_embedding_info}"
        )

    # --- REGULAR (Lightweight Models) MODE ---
    logger.info(f"Lightweight AI: Analyzing {file.filename}")
    # 1. Extract Image Embedding (returns List[float] or error string)
    # Not directly in OutfitAnalysisResponse, but could be logged or stored.
    image_embedding_result = get_image_embedding(image.copy())
    embedding_status_message = "Embedding extracted."
    if isinstance(image_embedding_result, str): # Error occurred
        embedding_status_message = image_embedding_result # Record the error/message
        # No critical failure for the response, just noting embedding failed.

    # 2. Extract Colors (already lightweight)
    extracted_colors = extract_colors(image.copy())

    # 3. Detect Style (lightweight placeholder)
    # lw_detect_style returns a string (style description or error/placeholder message)
    detected_style_result = lw_detect_style(image.copy())

    # 4. Identify Items (lightweight EfficientDet-Lite0)
    # lw_identify_items returns List[Dict] or error string
    identified_items_result = lw_identify_items(image.copy())

    # Prepare identified_items_for_response: List[str] as likely expected by original schema
    # And identified_items_for_recommendations: List[Dict] for our get_basic_recommendations
    final_identified_item_names: List[str] = []
    processed_identified_items: Union[List[Dict[str, Any]], str] = [] # For recommendations

    if isinstance(identified_items_result, str): # Error or "no items" message
        final_identified_item_names = [identified_items_result] # Pass message as a list item
        processed_identified_items = [] # No items for recommendations
    elif isinstance(identified_items_result, list) and not identified_items_result: # Empty list (no items found)
        final_identified_item_names = ["No specific items identified."]
        processed_identified_items = []
    elif isinstance(identified_items_result, list): # Successfully got list of dicts
        # Filter out any non-string labels just in case, though model should give strings
        final_identified_item_names = [str(item.get('label', 'Unknown Item')) for item in identified_items_result if isinstance(item, dict)]
        if not final_identified_item_names: # If all items somehow lacked labels
             final_identified_item_names = ["Items detected but labels are missing."]
        processed_identified_items = identified_items_result


    # 5. Get Recommendations (based on identified items)
    recommendations = get_basic_recommendations(processed_identified_items if isinstance(processed_identified_items, list) else [])

    # 6. Occasion Suitability Analysis (using new service)
    from .occasion_analysis import determine_occasion_suitability
    occasion_suitability = determine_occasion_suitability(
        style=str(detected_style_result),
        colors=extracted_colors if isinstance(extracted_colors, list) else [],
        identified_items=final_identified_item_names
    )


    # Constructing the response
    # The schema for OutfitAnalysisResponse needs to be checked carefully.
    # Specifically: identifiedItems: List[str] vs List[Dict], colorPalette structure.
    # Assuming identifiedItems expects List[str] of item names.
    # Assuming style expects a string.

    # Confidence score can be an average or placeholder
    # For now, a placeholder as individual models return different types of confidences or none.
    overall_confidence = 0.65 # Placeholder for lightweight mode aggregate

    # Color Palette: Ensure it's robust against empty extracted_colors
    color_palette_resp = []
    if extracted_colors and isinstance(extracted_colors, list) and not any("Error" in c for c in extracted_colors):
        try:
            # Prevent division by zero if extracted_colors is empty after filtering
            num_valid_colors = len(extracted_colors)
            if num_valid_colors > 0:
                color_palette_resp = [
                    {"color": c, "name": "Dominant Color",
                      "percentage": round(100.0 / num_valid_colors, 1)}
                    for c in extracted_colors
                ]
            else: # Handle case where extracted_colors might be empty or contain errors
                color_palette_resp = [{"color": "#FFFFFF", "name": "Default", "percentage": 100.0}]
        except ZeroDivisionError: # Should be caught by num_valid_colors > 0
            color_palette_resp = [{"color": "#FFFFFF", "name": "ErrorCalculatingPalette", "percentage": 100.0}]
    else: # Handle error case from extract_colors or empty list
        color_palette_resp = [{"color": c, "name": "Color Extraction Issue", "percentage": 0} for c in (extracted_colors if isinstance(extracted_colors, list) else ["#Error"])]


    # Style Insights: Based on detected_style_result (which is a string)
    style_insights_resp = []
    if detected_style_result and "under development" not in detected_style_result.lower() and "error" not in detected_style_result.lower():
        style_insights_resp = [{"category": "Overall Style", "score": 60, "description": f"Style notes: {detected_style_result}."}]
    else:
        style_insights_resp = [{"category": "Overall Style", "score": 0, "description": detected_style_result}]


    return schemas.OutfitAnalysisResponse(
        fileName=file.filename,
        contentType=file.content_type,
        style=str(detected_style_result), # Ensure it's a string
        dominantColors=extracted_colors if isinstance(extracted_colors, list) else [str(extracted_colors)],
        identifiedItems=final_identified_item_names, # List of strings
        occasionSuitability=occasion_suitability,
        confidenceScore=overall_confidence,
        recommendations=recommendations,
        colorPalette=color_palette_resp,
        styleInsights=style_insights_resp,
        debug_info=f"Analyzed with lightweight models. Embedding status: {embedding_status_message}"
    )

# --- get_fashion_trends_service remains unchanged (already mocked) ---
async def get_fashion_trends_service(db: Session, user: Optional[schemas.User] = None) -> schemas.TrendForecastResponse:
    # Mock implementation for now... (content is the same as before)
    mock_trends_data = [
        schemas.TrendDataItem(
            id='1', name='Neo-Cottagecore AI', category='Aesthetic Movement (Backend)', popularity=94, growth=267,
            description='Backend AI: A futuristic take on cottagecore with sustainable tech fabrics and earthy tones.',
            colors=['Sage Green', 'Mushroom Brown', 'Lavender', 'Cream'], season='Spring 2025', confidence=96,
            outfitImages=['https://via.placeholder.com/150/A2D2A2/000000?text=NeoCottage1', 'https://via.placeholder.com/150/D2A2D2/000000?text=NeoCottage2'],
            celebrities=['Celeb A (AI)', 'Celeb B (AI)'], hashtags=['#NeoCottagecoreAI', '#SustainableFashionAI'],
            priceRange='$100-$350', occasion=['Casual AI', 'Work From Home AI']
        ),
        schemas.TrendDataItem(
            id='2', name='Cyber-Minimalism AI', category='Fashion Tech (Backend)', popularity=89, growth=189,
            description='Backend AI: Clean lines meet smart fabrics with embedded tech and holographic accents.',
            colors=['Chrome Silver', 'Deep Black', 'Electric Blue', 'Pure White'], season='Fall 2025', confidence=92,
            outfitImages=['https://via.placeholder.com/150/C0C0C0/FFFFFF?text=CyberMin1', 'https://via.placeholder.com/150/0000FF/FFFFFF?text=CyberMin2'],
            celebrities=['Celeb C (AI)', 'Celeb D (AI)'], hashtags=['#CyberMinimalAI', '#TechWearAI'],
            priceRange='$180-$850', occasion=['Night Out AI', 'Creative Events AI']
        )
    ]
    mock_personalized_recommendations = schemas.PersonalizedRecommendations(
        mustHave=['AI: Smart casual blazer', 'AI: Sustainable denim'],
        avoid=['AI: Fast fashion basics', 'AI: Overly specific trends'],
        investIn=['AI: Quality tech outerwear', 'AI: Versatile pieces']
    )
    mock_seasonal_predictions = schemas.SeasonalPredictions(
        emerging=['AI: Biometric jewelry', 'AI: Climate-responsive clothing'],
        declining=['AI: Logo-heavy designs', 'AI: Single-use items'],
        stable=['AI: Classic denim', 'AI: White shirts (backend)']
    )
    return schemas.TrendForecastResponse(
        trends=mock_trends_data,
        personalizedRecommendations=mock_personalized_recommendations,
        seasonalPredictions=mock_seasonal_predictions
    )
