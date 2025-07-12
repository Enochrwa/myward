# This module provides occasion analysis for outfits using rule-based logic
# and semantic analysis of clothing items and styles.

from typing import List, Dict, Any, Optional
import re
import logging # Added for logging

# Define occasion categories and their characteristics
OCCASION_MAPPING = {
    "formal": {
        "keywords": ["formal", "business", "professional", "office", "meeting", "interview", "conference"],
        "styles": ["classic", "professional", "minimalist", "elegant"],
        "colors": ["black", "navy", "gray", "white", "dark"],
        "items": ["blazer", "suit", "dress shirt", "tie", "formal shoes", "dress", "heels"]
    },
    "casual": {
        "keywords": ["casual", "everyday", "relaxed", "comfortable", "weekend", "home"],
        "styles": ["casual", "cozy", "comfortable", "relaxed"],
        "colors": ["any"],
        "items": ["jeans", "t-shirt", "sneakers", "hoodie", "cardigan", "casual dress"]
    },
    "party": {
        "keywords": ["party", "celebration", "night out", "club", "dancing", "festive"],
        "styles": ["bold", "statement", "glamorous", "edgy", "vibrant"],
        "colors": ["bright", "metallic", "bold", "red", "gold", "silver"],
        "items": ["dress", "heels", "jewelry", "clutch", "statement piece"]
    },
    "wedding": {
        "keywords": ["wedding", "ceremony", "reception", "bridal", "guest"],
        "styles": ["elegant", "classic", "sophisticated", "formal"],
        "colors": ["pastels", "navy", "burgundy", "emerald", "avoid white"],
        "items": ["dress", "suit", "heels", "formal shoes", "elegant accessories"]
    },
    "church": {
        "keywords": ["church", "religious", "service", "worship", "conservative"],
        "styles": ["modest", "conservative", "classic", "respectful"],
        "colors": ["modest", "not too bright", "conservative"],
        "items": ["modest dress", "blouse", "skirt", "conservative top", "closed shoes"]
    },
    "outdoor": {
        "keywords": ["outdoor", "hiking", "camping", "sports", "active", "exercise"],
        "styles": ["sporty", "functional", "comfortable", "practical"],
        "colors": ["any", "earth tones", "bright for visibility"],
        "items": ["athletic wear", "sneakers", "jacket", "comfortable pants"]
    },
    "date": {
        "keywords": ["date", "romantic", "dinner", "restaurant", "romantic evening"],
        "styles": ["romantic", "elegant", "attractive", "stylish"],
        "colors": ["romantic", "flattering", "red", "soft colors"],
        "items": ["dress", "nice top", "heels", "jewelry", "attractive outfit"]
    }
}

def analyze_style_for_occasion(style: str) -> List[str]:
    """Analyze which occasions a style is suitable for"""
    style_lower = style.lower()
    suitable_occasions = []
    
    for occasion, characteristics in OCCASION_MAPPING.items():
        # Check if style matches any of the occasion's preferred styles
        for preferred_style in characteristics["styles"]:
            if preferred_style in style_lower:
                suitable_occasions.append(occasion)
                break
    
    return suitable_occasions

def analyze_colors_for_occasion(colors: List[str]) -> Dict[str, float]:
    """Analyze how well colors suit different occasions"""
    occasion_scores = {}
    
    for occasion, characteristics in OCCASION_MAPPING.items():
        score = 0.0
        color_preferences = characteristics["colors"]
        
        if "any" in color_preferences:
            score = 0.7  # Neutral score for occasions that accept any color
        else:
            # Analyze each color against occasion preferences
            for color in colors:
                color_lower = color.lower()
                
                # Check for specific color mentions
                for pref_color in color_preferences:
                    if pref_color in color_lower or color_lower in pref_color:
                        score += 0.3
                
                # Special checks for color characteristics
                if "bright" in color_preferences and is_bright_color(color):
                    score += 0.2
                elif "dark" in color_preferences and is_dark_color(color):
                    score += 0.2
                elif "pastels" in color_preferences and is_pastel_color(color):
                    score += 0.2
                elif "metallic" in color_preferences and is_metallic_color(color):
                    score += 0.2
        
        # Normalize score
        occasion_scores[occasion] = min(1.0, score)
    
    return occasion_scores

def is_bright_color(hex_color: str) -> bool:
    """Check if a color is bright/vibrant"""
    try:
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        # Simple brightness check
        brightness = (r + g + b) / 3
        saturation = max(r, g, b) - min(r, g, b)
        return brightness > 150 and saturation > 100
    except:
        return False

def is_dark_color(hex_color: str) -> bool:
    """Check if a color is dark"""
    try:
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        brightness = (r + g + b) / 3
        return brightness < 100
    except:
        return False

def is_pastel_color(hex_color: str) -> bool:
    """Check if a color is pastel (light and soft)"""
    try:
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        brightness = (r + g + b) / 3
        saturation = max(r, g, b) - min(r, g, b)
        return brightness > 180 and saturation < 80
    except:
        return False

def is_metallic_color(hex_color: str) -> bool:
    """Check if a color appears metallic"""
    metallic_colors = ["#c0c0c0", "#ffd700", "#b87333", "#cd7f32"]  # Silver, gold, bronze, copper
    try:
        hex_color = hex_color.lower()
        for metallic in metallic_colors:
            # Simple distance check (could be improved)
            if abs(int(hex_color[1:3], 16) - int(metallic[1:3], 16)) < 50:
                return True
    except:
        pass
    return False

def analyze_items_for_occasion(identified_items: List[str]) -> Dict[str, float]:
    """Analyze how well identified items suit different occasions"""
    occasion_scores = {}
    
    for occasion, characteristics in OCCASION_MAPPING.items():
        score = 0.0
        preferred_items = characteristics["items"]
        
        for item in identified_items:
            item_lower = item.lower()
            
            # Check if item matches any preferred items for this occasion
            for preferred_item in preferred_items:
                if preferred_item in item_lower or any(word in item_lower for word in preferred_item.split()):
                    score += 0.4
                    break
        
        # Normalize score based on number of items
        if identified_items:
            occasion_scores[occasion] = min(1.0, score)
        else:
            occasion_scores[occasion] = 0.0
    
    return occasion_scores

def determine_occasion_suitability(
    style: str,
    colors: List[str],
    identified_items: List[str],
    confidence_threshold: float = 0.6
) -> str:
    """
    Determine the most suitable occasions for an outfit based on style, colors, and items.
    
    Args:
        style: Detected style of the outfit
        colors: List of dominant colors in hex format
        identified_items: List of identified clothing items
        confidence_threshold: Minimum confidence to suggest an occasion
    
    Returns:
        String describing occasion suitability
    """
    
    # Get scores from different analysis methods
    style_occasions = analyze_style_for_occasion(style)
    color_scores = analyze_colors_for_occasion(colors)
    item_scores = analyze_items_for_occasion(identified_items)
    
    # Combine scores with weights
    final_scores = {}
    style_weight = 0.4
    color_weight = 0.3
    item_weight = 0.3
    
    for occasion in OCCASION_MAPPING.keys():
        style_score = 1.0 if occasion in style_occasions else 0.0
        color_score = color_scores.get(occasion, 0.0)
        item_score = item_scores.get(occasion, 0.0)
        
        final_scores[occasion] = (
            style_score * style_weight +
            color_score * color_weight +
            item_score * item_weight
        )
    
    # Find the best matching occasions
    suitable_occasions = []
    for occasion, score in final_scores.items():
        if score >= confidence_threshold:
            suitable_occasions.append((occasion, score))
    
    # Sort by score
    suitable_occasions.sort(key=lambda x: x[1], reverse=True)
    
    if not suitable_occasions:
        return "This outfit has a versatile style that could work for various casual occasions."
    
    # Create description
    if len(suitable_occasions) == 1:
        occasion, score = suitable_occasions[0]
        return f"This outfit is well-suited for {occasion} occasions (confidence: {score:.0%})."
    else:
        top_occasions = [occ for occ, _ in suitable_occasions[:3]]
        return f"This outfit would work well for {', '.join(top_occasions[:-1])} and {top_occasions[-1]} occasions."

# Example usage
if __name__ == "__main__":
    # Test the occasion analysis
    test_style = "Modern Professional"
    test_colors = ["#000000", "#FFFFFF", "#2563EB"]
    test_items = ["blazer", "dress shirt", "formal shoes"]
    
    logger = logging.getLogger(__name__) # Added logger for example
    result = determine_occasion_suitability(test_style, test_colors, test_items)
    logger.info(f"Occasion analysis result: {result}")

