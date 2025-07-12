# This module provides style detection from images using a rule-based approach
# combined with color analysis and basic pattern recognition.

from PIL import Image
import numpy as np
from typing import List, Tuple
import os
import logging # Added for logging

# DEMO_MODE can be set globally, e.g., via an environment variable or config file
DEMO_MODE = os.getenv("AI_DEMO_MODE", "false").lower() == "true"
logger = logging.getLogger(__name__) # Added logger

def analyze_color_temperature(colors_hex: List[str]) -> str:
    """Analyze if colors are warm, cool, or neutral"""
    if not colors_hex:
        return "neutral"
    
    warm_count = 0
    cool_count = 0
    
    for hex_color in colors_hex:
        # Convert hex to RGB
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            continue
            
        try:
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            # Simple warm/cool detection based on RGB values
            if r > b and (r > 150 or (r > g and g > 100)):  # Reds, oranges, yellows
                warm_count += 1
            elif b > r and (b > 150 or (b > g and g < 150)):  # Blues, purples
                cool_count += 1
        except ValueError:
            continue
    
    if warm_count > cool_count:
        return "warm"
    elif cool_count > warm_count:
        return "cool"
    else:
        return "neutral"

def analyze_brightness(image: Image.Image) -> str:
    """Analyze overall brightness of the image"""
    try:
        # Convert to grayscale and get average brightness
        gray_image = image.convert('L')
        gray_array = np.array(gray_image)
        avg_brightness = np.mean(gray_array)
        
        if avg_brightness > 180:
            return "very bright"
        elif avg_brightness > 140:
            return "bright"
        elif avg_brightness > 100:
            return "medium"
        elif avg_brightness > 60:
            return "dark"
        else:
            return "very dark"
    except Exception:
        return "medium"

def detect_style(image: Image.Image) -> str:
    """
    Detects the style of an outfit in an image using rule-based analysis.
    
    Args:
        image: A PIL Image object.
    
    Returns:
        A string describing the detected style.
    """
    if DEMO_MODE:
        return "Demo Style: Casual Everyday Wear"
    
    try:
        # Extract basic image features for style analysis
        from .ai_services import extract_colors
        
        # Get dominant colors
        colors = extract_colors(image, num_colors=5)
        
        # Analyze color temperature
        color_temp = analyze_color_temperature(colors)
        
        # Analyze brightness
        brightness = analyze_brightness(image)
        
        # Rule-based style detection
        style_indicators = []
        
        # Color-based style indicators
        if color_temp == "warm":
            style_indicators.append("warm-toned")
        elif color_temp == "cool":
            style_indicators.append("cool-toned")
        
        # Brightness-based style indicators
        if brightness in ["very bright", "bright"]:
            style_indicators.append("light and airy")
        elif brightness in ["dark", "very dark"]:
            style_indicators.append("dramatic")
        
        # Check for specific color patterns
        black_count = sum(1 for c in colors if c.lower() in ['#000000', '#1a1a1a', '#2d2d2d'])
        white_count = sum(1 for c in colors if c.lower() in ['#ffffff', '#f5f5f5', '#fafafa'])
        
        if black_count >= 2:
            style_indicators.append("edgy")
        if white_count >= 2:
            style_indicators.append("minimalist")
        if black_count >= 1 and white_count >= 1:
            style_indicators.append("classic")
        
        # Check for colorful vs monochromatic
        unique_color_families = len(set(colors))
        if unique_color_families >= 4:
            style_indicators.append("vibrant")
        elif unique_color_families <= 2:
            style_indicators.append("monochromatic")
        
        # Combine indicators into style description
        if not style_indicators:
            return "Contemporary Casual"
        
        # Create style description based on indicators
        if "edgy" in style_indicators and "dramatic" in style_indicators:
            return "Edgy Contemporary"
        elif "minimalist" in style_indicators and "classic" in style_indicators:
            return "Modern Minimalist"
        elif "vibrant" in style_indicators and "warm-toned" in style_indicators:
            return "Bohemian Chic"
        elif "cool-toned" in style_indicators and "light and airy" in style_indicators:
            return "Scandinavian Minimal"
        elif "classic" in style_indicators:
            return "Timeless Classic"
        elif "dramatic" in style_indicators:
            return "Statement Bold"
        elif "warm-toned" in style_indicators:
            return "Cozy Casual"
        elif "cool-toned" in style_indicators:
            return "Modern Professional"
        else:
            # Fallback based on first indicator
            primary_indicator = style_indicators[0].replace("-", " ").title()
            return f"{primary_indicator} Style"
            
    except Exception as e:
        logger.error(f"Error in style detection: {e}")
        return "Contemporary Casual"

# Example usage (optional)
if __name__ == '__main__':
    # This part is for testing the module directly.
    try:
        # Create a dummy image for testing (not actually processed by the current placeholder)
        img = Image.new('RGB', (100, 100), color = 'blue')
        logger.info("Attempting to 'detect' style for a dummy image...")
        style_result = detect_style(img)
        logger.info(f"Detected style: {style_result}")

        # Test with demo mode
        DEMO_MODE = True # This will be module-level, so re-assigning here for test
        logger.info("Attempting to 'detect' style for a dummy image (DEMO_MODE=True)...")
        # To correctly test demo mode, the module level DEMO_MODE would need to be True
        # or the function needs to accept it as a parameter.
        # For this conversion, we assume the logger is desired regardless of DEMO_MODE state here.
        style_result_demo = detect_style(img) # This will use the module-level DEMO_MODE
        logger.info(f"Detected style (Demo): {style_result_demo}")

    except Exception as e:
        logger.error(f"Error in example usage: {e}")
