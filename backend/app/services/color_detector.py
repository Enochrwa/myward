"""
Color Detection Service using ColorThief

This module provides functionality to extract dominant colors from clothing images
using the ColorThief library for color palette analysis.
"""

import io
import logging
from typing import Dict, List, Tuple, Optional
from colorthief import ColorThief
from PIL import Image
import webcolors
import numpy as np
import asyncio
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ColorDetector:
    """
    Color detection service using ColorThief for dominant color extraction.
    
    This class provides methods to extract dominant colors and color palettes
    from clothing item images.
    """
    
    def __init__(self):
        """Initialize the color detector."""
        self.color_names = self._load_color_names()
    
    def _load_color_names(self) -> Dict[str, Tuple[int, int, int]]:
        """
        Load common color names and their RGB values.
        
        Returns:
            Dictionary mapping color names to RGB tuples
        """
        return {
            # Basic colors
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255),
            'yellow': (255, 255, 0),
            'orange': (255, 165, 0),
            'purple': (128, 0, 128),
            'pink': (255, 192, 203),
            'brown': (165, 42, 42),
            'black': (0, 0, 0),
            'white': (255, 255, 255),
            'gray': (128, 128, 128),
            'grey': (128, 128, 128),
            
            # Extended colors
            'navy': (0, 0, 128),
            'maroon': (128, 0, 0),
            'olive': (128, 128, 0),
            'lime': (0, 255, 0),
            'aqua': (0, 255, 255),
            'teal': (0, 128, 128),
            'silver': (192, 192, 192),
            'fuchsia': (255, 0, 255),
            'beige': (245, 245, 220),
            'tan': (210, 180, 140),
            'khaki': (240, 230, 140),
            'coral': (255, 127, 80),
            'salmon': (250, 128, 114),
            'gold': (255, 215, 0),
            'indigo': (75, 0, 130),
            'violet': (238, 130, 238),
            'turquoise': (64, 224, 208),
            'crimson': (220, 20, 60),
            'magenta': (255, 0, 255),
            'cyan': (0, 255, 255),
            
            # Fashion-specific colors
            'burgundy': (128, 0, 32),
            'emerald': (80, 200, 120),
            'sapphire': (15, 82, 186),
            'ruby': (224, 17, 95),
            'pearl': (234, 224, 200),
            'ivory': (255, 255, 240),
            'cream': (255, 253, 208),
            'charcoal': (54, 69, 79),
            'slate': (112, 128, 144),
            'mint': (189, 252, 201),
            'lavender': (230, 230, 250),
            'rose': (255, 228, 225),
            'peach': (255, 218, 185),
            'mustard': (255, 219, 88),
            'forest': (34, 139, 34),
            'denim': (21, 96, 189),
            'camel': (193, 154, 107),
            'chocolate': (210, 105, 30)
        }
    
    def extract_dominant_color(self, image_data: bytes, quality: int = 1) -> Dict[str, any]:
        """
        Extract the dominant color from an image.
        
        Args:
            image_data: Raw image bytes
            quality: Quality setting for color extraction (1=best, 10=fastest)
            
        Returns:
            Dictionary containing dominant color information
        """
        try:
            # Create a BytesIO object from image data
            image_stream = io.BytesIO(image_data)
            
            # Create ColorThief object
            color_thief = ColorThief(image_stream)
            
            # Get dominant color (RGB tuple)
            dominant_color_rgb = color_thief.get_color(quality=quality)
            
            # Convert to hex
            dominant_color_hex = self._rgb_to_hex(dominant_color_rgb)
            
            # Get closest color name
            color_name = self._get_closest_color_name(dominant_color_rgb)
            
            # Calculate color properties
            color_properties = self._analyze_color_properties(dominant_color_rgb)
            
            result = {
                "dominant_color": {
                    "rgb": dominant_color_rgb,
                    "hex": dominant_color_hex,
                    "name": color_name
                },
                "properties": color_properties,
                "success": True
            }
            
            logger.info(f"Extracted dominant color: {color_name} ({dominant_color_hex})")
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting dominant color: {str(e)}")
            return {
                "dominant_color": {
                    "rgb": (128, 128, 128),
                    "hex": "#808080",
                    "name": "gray"
                },
                "properties": {
                    "brightness": "medium",
                    "saturation": "medium",
                    "temperature": "neutral"
                },
                "success": False,
                "error": str(e)
            }
    
    def extract_color_palette(self, image_data: bytes, color_count: int = 5, quality: int = 1) -> Dict[str, any]:
        """
        Extract a color palette from an image.
        
        Args:
            image_data: Raw image bytes
            color_count: Number of colors to extract
            quality: Quality setting for color extraction
            
        Returns:
            Dictionary containing color palette information
        """
        try:
            # Create a BytesIO object from image data
            image_stream = io.BytesIO(image_data)
            
            # Create ColorThief object
            color_thief = ColorThief(image_stream)
            
            # Get color palette
            palette_rgb = color_thief.get_palette(color_count=color_count, quality=quality)
            
            # Process each color in the palette
            palette = []
            for rgb in palette_rgb:
                color_info = {
                    "rgb": rgb,
                    "hex": self._rgb_to_hex(rgb),
                    "name": self._get_closest_color_name(rgb),
                    "properties": self._analyze_color_properties(rgb)
                }
                palette.append(color_info)
            
            # Analyze palette harmony
            harmony_analysis = self._analyze_color_harmony(palette_rgb)
            
            result = {
                "palette": palette,
                "dominant_color": palette[0] if palette else None,
                "harmony_analysis": harmony_analysis,
                "color_count": len(palette),
                "success": True
            }
            
            logger.info(f"Extracted color palette with {len(palette)} colors")
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting color palette: {str(e)}")
            return {
                "palette": [],
                "dominant_color": None,
                "harmony_analysis": {
                    "scheme": "unknown",
                    "temperature": "neutral",
                    "contrast": "medium"
                },
                "color_count": 0,
                "success": False,
                "error": str(e)
            }
    
    def _rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """
        Convert RGB tuple to hex string.
        
        Args:
            rgb: RGB color tuple
            
        Returns:
            Hex color string
        """
        return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])
    
    def _get_closest_color_name(self, rgb: Tuple[int, int, int]) -> str:
        """
        Get the closest color name for an RGB value.
        
        Args:
            rgb: RGB color tuple
            
        Returns:
            Closest color name
        """
        try:
            # Try to get exact match from webcolors
            return webcolors.rgb_to_name(rgb)
        except ValueError:
            # Find closest color from our predefined colors
            min_distance = float('inf')
            closest_color = 'gray'
            
            for color_name, color_rgb in self.color_names.items():
                distance = self._color_distance(rgb, color_rgb)
                if distance < min_distance:
                    min_distance = distance
                    closest_color = color_name
            
            return closest_color
    
    def _color_distance(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> float:
        """
        Calculate Euclidean distance between two RGB colors.
        
        Args:
            color1: First RGB color
            color2: Second RGB color
            
        Returns:
            Distance between colors
        """
        return np.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(color1, color2)))
    
    def _analyze_color_properties(self, rgb: Tuple[int, int, int]) -> Dict[str, str]:
        """
        Analyze color properties like brightness, saturation, and temperature.
        
        Args:
            rgb: RGB color tuple
            
        Returns:
            Dictionary of color properties
        """
        r, g, b = rgb
        
        # Calculate brightness (perceived luminance)
        brightness_value = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        if brightness_value < 0.3:
            brightness = "dark"
        elif brightness_value > 0.7:
            brightness = "light"
        else:
            brightness = "medium"
        
        # Calculate saturation
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        if max_val == 0:
            saturation_value = 0
        else:
            saturation_value = (max_val - min_val) / max_val
        
        if saturation_value < 0.3:
            saturation = "low"
        elif saturation_value > 0.7:
            saturation = "high"
        else:
            saturation = "medium"
        
        # Calculate color temperature (warm/cool)
        if r > b + 20:
            temperature = "warm"
        elif b > r + 20:
            temperature = "cool"
        else:
            temperature = "neutral"
        
        return {
            "brightness": brightness,
            "saturation": saturation,
            "temperature": temperature
        }
    
    def _analyze_color_harmony(self, palette_rgb: List[Tuple[int, int, int]]) -> Dict[str, str]:
        """
        Analyze color harmony in a palette.
        
        Args:
            palette_rgb: List of RGB color tuples
            
        Returns:
            Dictionary of harmony analysis
        """
        if len(palette_rgb) < 2:
            return {
                "scheme": "monochromatic",
                "temperature": "neutral",
                "contrast": "low"
            }
        
        # Analyze temperature distribution
        warm_count = 0
        cool_count = 0
        
        for rgb in palette_rgb:
            r, g, b = rgb
            if r > b + 20:
                warm_count += 1
            elif b > r + 20:
                cool_count += 1
        
        if warm_count > cool_count * 2:
            temperature = "warm"
        elif cool_count > warm_count * 2:
            temperature = "cool"
        else:
            temperature = "mixed"
        
        # Analyze contrast
        brightness_values = []
        for rgb in palette_rgb:
            r, g, b = rgb
            brightness = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            brightness_values.append(brightness)
        
        brightness_range = max(brightness_values) - min(brightness_values)
        if brightness_range < 0.3:
            contrast = "low"
        elif brightness_range > 0.7:
            contrast = "high"
        else:
            contrast = "medium"
        
        # Determine color scheme
        if len(set(palette_rgb)) == 1:
            scheme = "monochromatic"
        elif len(palette_rgb) == 2:
            scheme = "complementary"
        elif len(palette_rgb) == 3:
            scheme = "triadic"
        else:
            scheme = "complex"
        
        return {
            "scheme": scheme,
            "temperature": temperature,
            "contrast": contrast
        }
    
    def get_color_suggestions(self, dominant_color_rgb: Tuple[int, int, int]) -> Dict[str, List[Dict]]:
        """
        Get color suggestions that would work well with the dominant color.
        
        Args:
            dominant_color_rgb: RGB tuple of the dominant color
            
        Returns:
            Dictionary of color suggestions by category
        """
        try:
            r, g, b = dominant_color_rgb
            
            # Generate complementary color
            comp_r = 255 - r
            comp_g = 255 - g
            comp_b = 255 - b
            complementary = (comp_r, comp_g, comp_b)
            
            # Generate analogous colors (adjacent on color wheel)
            analogous = []
            for shift in [-30, 30]:  # Simplified hue shift
                new_r = max(0, min(255, r + shift))
                new_g = max(0, min(255, g + shift // 2))
                new_b = max(0, min(255, b - shift // 2))
                analogous.append((new_r, new_g, new_b))
            
            # Generate neutral colors that work well
            neutrals = [
                (255, 255, 255),  # white
                (240, 240, 240),  # light gray
                (128, 128, 128),  # medium gray
                (64, 64, 64),     # dark gray
                (0, 0, 0),        # black
                (245, 245, 220),  # beige
                (139, 69, 19)     # brown
            ]
            
            suggestions = {
                "complementary": [
                    {
                        "rgb": complementary,
                        "hex": self._rgb_to_hex(complementary),
                        "name": self._get_closest_color_name(complementary)
                    }
                ],
                "analogous": [
                    {
                        "rgb": color,
                        "hex": self._rgb_to_hex(color),
                        "name": self._get_closest_color_name(color)
                    }
                    for color in analogous
                ],
                "neutrals": [
                    {
                        "rgb": color,
                        "hex": self._rgb_to_hex(color),
                        "name": self._get_closest_color_name(color)
                    }
                    for color in neutrals
                ]
            }
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating color suggestions: {str(e)}")
            return {
                "complementary": [],
                "analogous": [],
                "neutrals": []
            }

# Global color detector instance
_color_detector_instance = None
_color_detector_lock = asyncio.Lock() # For async instance creation

async def get_color_detector_async() -> ColorDetector:
    """
    Asynchronously get or create the global ColorDetector instance.
    """
    global _color_detector_instance
    if _color_detector_instance is None:
        async with _color_detector_lock:
            if _color_detector_instance is None: # Double check
                # ColorDetector init is lightweight, but for consistency:
                _color_detector_instance = await asyncio.to_thread(ColorDetector)
    return _color_detector_instance

def get_color_detector() -> ColorDetector:
    """
    Get or create the global color detector instance (synchronous).
    """
    global _color_detector_instance
    if _color_detector_instance is None:
        _color_detector_instance = ColorDetector()
    return _color_detector_instance

async def detect_dominant_color_async(image_data: bytes, quality: int = 1) -> Dict[str, any]:
    """
    Asynchronously detect dominant color from image.
    Offloads ColorThief operations to a thread pool.
    """
    detector = await get_color_detector_async()
    return await asyncio.to_thread(detector.extract_dominant_color, image_data, quality)

def detect_dominant_color(image_data: bytes, quality: int = 1) -> Dict[str, any]:
    """
    Convenience function to detect dominant color from image (synchronous).
    """
    detector = get_color_detector()
    return detector.extract_dominant_color(image_data, quality)

async def extract_color_palette_async(image_data: bytes, color_count: int = 5, quality: int = 1) -> Dict[str, any]:
    """
    Asynchronously extract color palette from image.
    Offloads ColorThief operations to a thread pool.
    """
    detector = await get_color_detector_async()
    return await asyncio.to_thread(detector.extract_color_palette, image_data, color_count, quality)

def extract_color_palette(image_data: bytes, color_count: int = 5, quality: int = 1) -> Dict[str, any]:
    """
    Convenience function to extract color palette from image (synchronous).
    """
    detector = get_color_detector()
    return detector.extract_color_palette(image_data, color_count, quality)

# Need to import asyncio at the top of the file
# import asyncio

