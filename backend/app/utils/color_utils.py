import webcolors
from typing import Tuple, List, Dict

def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Converts RGB to HEX"""
    return f"#{r:02x}{g:02x}{b:02x}"

def get_color_name(rgb_tuple: Tuple[int, int, int]) -> str:
    """Gets the name of a color from its RGB values"""
    try:
        return webcolors.rgb_to_name(rgb_tuple)
    except ValueError:
        return "Unknown"

def get_tone(rgb_tuple: Tuple[int, int, int]) -> str:
    """Gets the tone of a color"""
    h, s, v = webcolors.rgb_to_hsv(rgb_tuple)
    if v < 0.3:
        return "Dark"
    elif v > 0.7:
        return "Light"
    else:
        return "Medium"

def get_temperature(rgb_tuple: Tuple[int, int, int]) -> str:
    """Gets the temperature of a color"""
    h, s, v = webcolors.rgb_to_hsv(rgb_tuple)
    if 30 < h <= 180:
        return "Cool"
    elif 180 < h <= 330:
        return "Warm"
    else:
        return "Neutral"

def get_saturation(rgb_tuple: Tuple[int, int, int]) -> str:
    """Gets the saturation of a color"""
    h, s, v = webcolors.rgb_to_hsv(rgb_tuple)
    if s < 0.3:
        return "Low"
    elif s > 0.7:
        return "High"
    else:
        return "Medium"

def get_color_palette(rgb_tuple: Tuple[int, int, int]) -> Dict[str, str]:
    """Generates a color palette from a single color"""
    hex_color = rgb_to_hex(*rgb_tuple)
    return {
        "original": hex_color,
        "complementary": rgb_to_hex(255 - rgb_tuple[0], 255 - rgb_tuple[1], 255 - rgb_tuple[2]),
        "analogous1": rgb_to_hex((rgb_tuple[0] + 30) % 256, rgb_tuple[1], rgb_tuple[2]),
        "analogous2": rgb_to_hex(rgb_tuple[0], (rgb_tuple[1] + 30) % 256, rgb_tuple[2]),
    }

def colors_match(color1_rgb: Tuple[int, int, int], color2_rgb: Tuple[int, int, int]) -> bool:
    """Checks if two colors are similar"""
    return webcolors.rgb_to_name(color1_rgb) == webcolors.rgb_to_name(color2_rgb)

def get_color_harmony(color1_rgb: Tuple[int, int, int], color2_rgb: Tuple[int, int, int]) -> str:
    """Gets the color harmony between two colors"""
    h1, s1, v1 = webcolors.rgb_to_hsv(color1_rgb)
    h2, s2, v2 = webcolors.rgb_to_hsv(color2_rgb)

    hue_diff = abs(h1 - h2)

    if hue_diff < 30:
        return "analogous"
    elif 150 < hue_diff < 210:
        return "complementary"
    elif 90 < hue_diff < 150:
        return "triadic"
    else:
        return "neutral"
