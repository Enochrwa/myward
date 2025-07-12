from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from itertools import combinations

# Placeholder for more sophisticated color harmony logic
# For now, we'll use a simplified approach.

# Helper to convert hex to RGB
def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        return (128, 128, 128)  # Default gray for invalid colors
    try:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        return (128, 128, 128)

# Helper to convert RGB to HSV
def rgb_to_hsv(r: int, g: int, b: int) -> Tuple[float, float, float]:
    r, g, b = r/255.0, g/255.0, b/255.0
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    diff = max_val - min_val
    
    # Hue calculation
    if diff == 0:
        h = 0
    elif max_val == r:
        h = (60 * ((g - b) / diff) + 360) % 360
    elif max_val == g:
        h = (60 * ((b - r) / diff) + 120) % 360
    else:
        h = (60 * ((r - g) / diff) + 240) % 360
    
    # Saturation calculation
    s = 0 if max_val == 0 else diff / max_val
    
    # Value calculation
    v = max_val
    
    return h, s, v

def is_neutral_color(r: int, g: int, b: int) -> bool:
    """Check if a color is neutral (low saturation)"""
    _, s, _ = rgb_to_hsv(r, g, b)
    return s < 0.2  # Low saturation indicates neutral

def get_color_harmony_type(colors_hex: List[str]) -> str:
    """Determine the type of color harmony present"""
    if len(colors_hex) < 2:
        return "monochromatic"
    
    hsv_colors = []
    neutral_count = 0
    
    for hex_color in colors_hex:
        r, g, b = hex_to_rgb(hex_color)
        if is_neutral_color(r, g, b):
            neutral_count += 1
        else:
            h, s, v = rgb_to_hsv(r, g, b)
            hsv_colors.append((h, s, v))
    
    # If mostly neutrals, it's a neutral palette
    if neutral_count >= len(colors_hex) * 0.7:
        return "neutral"
    
    if len(hsv_colors) < 2:
        return "neutral"
    
    # Analyze hue relationships
    hues = [h for h, s, v in hsv_colors]
    hue_diffs = []
    
    for i in range(len(hues)):
        for j in range(i + 1, len(hues)):
            diff = min(abs(hues[i] - hues[j]), 360 - abs(hues[i] - hues[j]))
            hue_diffs.append(diff)
    
    if not hue_diffs:
        return "monochromatic"
    
    avg_hue_diff = sum(hue_diffs) / len(hue_diffs)
    max_hue_diff = max(hue_diffs)
    
    # Classify harmony type based on hue differences
    if max_hue_diff < 30:
        return "analogous"  # Similar hues
    elif any(150 <= diff <= 210 for diff in hue_diffs):
        return "complementary"  # Opposite hues
    elif any(90 <= diff <= 150 for diff in hue_diffs):
        return "triadic"  # Three evenly spaced hues
    elif avg_hue_diff > 60:
        return "diverse"  # Many different hues
    else:
        return "related"  # Somewhat related hues

# Enhanced color harmony checks
def check_color_harmony(colors_hex: List[str]) -> float:
    if not colors_hex or len(colors_hex) < 2:
        return 1.0  # Neutral score if not enough colors to compare

    # Remove duplicates while preserving order
    unique_colors = list(dict.fromkeys(colors_hex))
    
    if len(unique_colors) == 1:
        return 1.0  # Single color is always harmonious
    
    harmony_type = get_color_harmony_type(unique_colors)
    
    # Score based on harmony type
    harmony_scores = {
        "neutral": 0.95,      # Neutral palettes are very safe
        "monochromatic": 0.90, # Single hue variations
        "analogous": 0.85,     # Adjacent hues work well
        "complementary": 0.75, # Can be striking but harder to balance
        "triadic": 0.70,       # More complex but can work
        "related": 0.65,       # Somewhat related hues
        "diverse": 0.45        # Many different hues can clash
    }
    
    base_score = harmony_scores.get(harmony_type, 0.6)
    
    # Additional factors
    rgb_colors = [hex_to_rgb(c) for c in unique_colors]
    
    # Check for extreme contrasts (very bright + very dark)
    brightness_values = [sum(rgb) / 3 for rgb in rgb_colors]
    brightness_range = max(brightness_values) - min(brightness_values)
    
    # Moderate contrast is good, extreme contrast can be jarring
    if brightness_range > 200:  # Very high contrast
        base_score *= 0.8
    elif brightness_range < 50:  # Very low contrast
        base_score *= 0.9
    
    # Check saturation balance
    saturations = []
    for hex_color in unique_colors:
        r, g, b = hex_to_rgb(hex_color)
        _, s, _ = rgb_to_hsv(r, g, b)
        saturations.append(s)
    
    # Prefer balanced saturation levels
    saturation_variance = np.var(saturations) if saturations else 0
    if saturation_variance > 0.3:  # High variance in saturation
        base_score *= 0.85
    
    # Bonus for classic color combinations
    if len(unique_colors) == 2:
        # Check for classic two-color combinations
        if harmony_type in ["neutral", "analogous"]:
            base_score *= 1.1
    elif len(unique_colors) == 3:
        # Three colors can work well if balanced
        if harmony_type in ["neutral", "analogous", "triadic"]:
            base_score *= 1.05
    
    # Penalty for too many colors
    if len(unique_colors) > 5:
        base_score *= 0.7
    
    return min(1.0, max(0.0, base_score))


class OutfitMatchingService:
    def __init__(self):
        # Potentially load models or configurations if needed in the future
        pass

    def calculate_compatibility_score(
        self,
        item_features: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculates an overall compatibility score for a list of items.
        Each item in item_features should be a dict with at least:
        {
            "id": "item_id", // Or some identifier
            "embedding": List[float], // Image embedding
            "colors": List[str] // List of dominant hex colors
        }
        """
        if not item_features or len(item_features) < 2:
            return {
                "score": 0.0,
                "message": "Not enough items to compare.",
                "style_cohesion_score": 0.0,
                "color_harmony_score": 0.0
            }

        embeddings = [np.array(item["embedding"]) for item in item_features if item.get("embedding")]

        # 1. Style Cohesion (using embeddings)
        style_cohesion_score = 0.0
        if len(embeddings) >= 2:
            pairwise_similarities = []
            for emb1, emb2 in combinations(embeddings, 2):
                similarity = cosine_similarity(emb1.reshape(1, -1), emb2.reshape(1, -1))[0][0]
                pairwise_similarities.append(similarity)

            if pairwise_similarities:
                style_cohesion_score = np.mean(pairwise_similarities)
                # Normalize to 0-1 range (cosine similarity is -1 to 1, but embeddings usually non-negative relations)
                style_cohesion_score = (style_cohesion_score + 1) / 2
        else: # Not enough embeddings to compare
             style_cohesion_score = 0.5 # Neutral score

        # 2. Color Harmony
        # Collect all dominant colors from all items in the outfit
        all_dominant_colors_hex = []
        for item in item_features:
            if item.get("colors"):
                all_dominant_colors_hex.extend(item["colors"])

        # Use unique colors for harmony check to avoid penalizing multiple items of same color
        unique_colors_hex = list(set(all_dominant_colors_hex))
        color_harmony_score = check_color_harmony(unique_colors_hex)

        # 3. Combine scores (simple weighted average for now)
        # Weights can be tuned
        style_weight = 0.7
        color_weight = 0.3
        overall_score = (style_cohesion_score * style_weight) + (color_harmony_score * color_weight)

        # Ensure score is between 0 and 1
        overall_score = max(0, min(1, overall_score))

        return {
            "score": round(overall_score, 3),
            "style_cohesion_score": round(style_cohesion_score, 3),
            "color_harmony_score": round(color_harmony_score, 3),
            "message": "Compatibility calculated."
        }

# Example usage (for testing or if used directly):
# if __name__ == "__main__":
#     matcher = OutfitMatchingService()
#     # Example item features (embeddings would be large lists of floats)
#     mock_embedding_1 = [0.1] * 512 # Example embedding size for ViT base
#     mock_embedding_2 = [0.15] * 512
#     mock_embedding_3 = [0.5] * 512

#     items = [
#         {"id": "item1", "embedding": mock_embedding_1, "colors": ["#FF0000", "#FFFFFF"]},
#         {"id": "item2", "embedding": mock_embedding_2, "colors": ["#0000FF", "#F0F0F0"]},
#         # Item with different style embedding and potentially clashing color
#         {"id": "item3", "embedding": mock_embedding_3, "colors": ["#00FF00"]},
#     ]
#     result = matcher.calculate_compatibility_score(items)
#     print(result)

#     items_single = [
#          {"id": "item1", "embedding": mock_embedding_1, "colors": ["#FF0000", "#FFFFFF"]},
#     ]
#     result_single = matcher.calculate_compatibility_score(items_single)
#     print(result_single)

#     items_no_embeddings = [
#         {"id": "item1", "colors": ["#FF0000", "#FFFFFF"]},
#         {"id": "item2", "colors": ["#0000FF", "#F0F0F0"]},
#     ]
#     result_no_emb = matcher.calculate_compatibility_score(items_no_embeddings)
#     print(result_no_emb)
