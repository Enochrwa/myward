# utils/color_utils.py
import webcolors
import numpy as np
from typing import Tuple, Dict, List
import colorsys


def get_all_css3_colors() -> Dict[str, str]:
    """Return a static list of CSS3 color names and their HEX codes."""
    return {
        'aliceblue': '#f0f8ff', 'antiquewhite': '#faebd7', 'aqua': '#00ffff',
        'aquamarine': '#7fffd4', 'azure': '#f0ffff', 'beige': '#f5f5dc',
        'bisque': '#ffe4c4', 'black': '#000000', 'blanchedalmond': '#ffebcd',
        'blue': '#0000ff', 'blueviolet': '#8a2be2', 'brown': '#a52a2a',
        'burlywood': '#deb887', 'cadetblue': '#5f9ea0', 'chartreuse': '#7fff00',
        'chocolate': '#d2691e', 'coral': '#ff7f50', 'cornflowerblue': '#6495ed',
        'cornsilk': '#fff8dc', 'crimson': '#dc143c', 'cyan': '#00ffff',
        'darkblue': '#00008b', 'darkcyan': '#008b8b', 'darkgoldenrod': '#b8860b',
        'darkgray': '#a9a9a9', 'darkgreen': '#006400', 'darkgrey': '#a9a9a9',
        'darkkhaki': '#bdb76b', 'darkmagenta': '#8b008b', 'darkolivegreen': '#556b2f',
        'darkorange': '#ff8c00', 'darkorchid': '#9932cc', 'darkred': '#8b0000',
        'darksalmon': '#e9967a', 'darkseagreen': '#8fbc8f', 'darkslateblue': '#483d8b',
        'darkslategray': '#2f4f4f', 'darkslategrey': '#2f4f4f', 'darkturquoise': '#00ced1',
        'darkviolet': '#9400d3', 'deeppink': '#ff1493', 'deepskyblue': '#00bfff',
        'dimgray': '#696969', 'dimgrey': '#696969', 'dodgerblue': '#1e90ff',
        'firebrick': '#b22222', 'floralwhite': '#fffaf0', 'forestgreen': '#228b22',
        'fuchsia': '#ff00ff', 'gainsboro': '#dcdcdc', 'ghostwhite': '#f8f8ff',
        'gold': '#ffd700', 'goldenrod': '#daa520', 'gray': '#808080',
        'green': '#008000', 'greenyellow': '#adff2f', 'grey': '#808080',
        'honeydew': '#f0fff0', 'hotpink': '#ff69b4', 'indianred': '#cd5c5c',
        'indigo': '#4b0082', 'ivory': '#fffff0', 'khaki': '#f0e68c',
        'lavender': '#e6e6fa', 'lavenderblush': '#fff0f5', 'lawngreen': '#7cfc00',
        'lemonchiffon': '#fffacd', 'lightblue': '#add8e6', 'lightcoral': '#f08080',
        'lightcyan': '#e0ffff', 'lightgoldenrodyellow': '#fafad2', 'lightgray': '#d3d3d3',
        'lightgreen': '#90ee90', 'lightgrey': '#d3d3d3', 'lightpink': '#ffb6c1',
        'lightsalmon': '#ffa07a', 'lightseagreen': '#20b2aa', 'lightskyblue': '#87cefa',
        'lightslategray': '#778899', 'lightslategrey': '#778899', 'lightsteelblue': '#b0c4de',
        'lightyellow': '#ffffe0', 'lime': '#00ff00', 'limegreen': '#32cd32',
        'linen': '#faf0e6', 'magenta': '#ff00ff', 'maroon': '#800000',
        'mediumaquamarine': '#66cdaa', 'mediumblue': '#0000cd', 'mediumorchid': '#ba55d3',
        'mediumpurple': '#9370db', 'mediumseagreen': '#3cb371', 'mediumslateblue': '#7b68ee',
        'mediumspringgreen': '#00fa9a', 'mediumturquoise': '#48d1cc', 'mediumvioletred': '#c71585',
        'midnightblue': '#191970', 'mintcream': '#f5fffa', 'mistyrose': '#ffe4e1',
        'moccasin': '#ffe4b5', 'navajowhite': '#ffdead', 'navy': '#000080',
        'oldlace': '#fdf5e6', 'olive': '#808000', 'olivedrab': '#6b8e23',
        'orange': '#ffa500', 'orangered': '#ff4500', 'orchid': '#da70d6',
        'palegoldenrod': '#eee8aa', 'palegreen': '#98fb98', 'paleturquoise': '#afeeee',
        'palevioletred': '#db7093', 'papayawhip': '#ffefd5', 'peachpuff': '#ffdab9',
        'peru': '#cd853f', 'pink': '#ffc0cb', 'plum': '#dda0dd',
        'powderblue': '#b0e0e6', 'purple': '#800080', 'red': '#ff0000',
        'rosybrown': '#bc8f8f', 'royalblue': '#4169e1', 'saddlebrown': '#8b4513',
        'salmon': '#fa8072', 'sandybrown': '#f4a460', 'seagreen': '#2e8b57',
        'seashell': '#fff5ee', 'sienna': '#a0522d', 'silver': '#c0c0c0',
        'skyblue': '#87ceeb', 'slateblue': '#6a5acd', 'slategray': '#708090',
        'slategrey': '#708090', 'snow': '#fffafa', 'springgreen': '#00ff7f',
        'steelblue': '#4682b4', 'tan': '#d2b48c', 'teal': '#008080',
        'thistle': '#d8bfd8', 'tomato': '#ff6347', 'turquoise': '#40e0d0',
        'violet': '#ee82ee', 'wheat': '#f5deb3', 'white': '#ffffff',
        'whitesmoke': '#f5f5f5', 'yellow': '#ffff00', 'yellowgreen': '#9acd32'
    }


def rgb_to_hex(r: float, g: float, b: float) -> str:
    """Convert RGB values to HEX format"""
    return "#{:02x}{:02x}{:02x}".format(int(r), int(g), int(b))

def hex_to_rgb(hex_code: str) -> Tuple[int, int, int]:
    """Convert HEX to RGB"""
    return webcolors.hex_to_rgb(hex_code)

def closest_color(requested_rgb: Tuple[float, float, float]) -> str:
    """Find the closest CSS3 color name for given RGB values"""
    min_distance = float("inf")
    closest_name = None
    
    for name, hex_code in get_all_css3_colors().items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(hex_code)
        rd = (r_c - requested_rgb[0]) ** 2
        gd = (g_c - requested_rgb[1]) ** 2
        bd = (b_c - requested_rgb[2]) ** 2
        distance = rd + gd + bd
        
        if distance < min_distance:
            min_distance = distance
            closest_name = name
    
    return closest_name

def get_color_name(rgb_triplet: List[float]) -> str:
    """Get color name from RGB values"""
    try:
        return webcolors.rgb_to_name(tuple(map(int, rgb_triplet)), spec='css3')
    except ValueError:
        return closest_color(rgb_triplet)

def get_tone(rgb_triplet: List[float]) -> str:
    """Determine if color is light or dark"""
    r, g, b = rgb_triplet
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    if brightness > 180:
        return "Light"
    elif brightness > 80:
        return "Medium"
    else:
        return "Dark"

def get_temperature(rgb_triplet: List[float]) -> str:
    """Determine if color is warm or cool"""
    r, g, b = rgb_triplet
    # More sophisticated temperature calculation
    if r > b and (r - b) > 30:
        return "Warm"
    elif b > r and (b - r) > 30:
        return "Cool"
    else:
        return "Neutral"

def get_saturation(rgb_triplet: List[float]) -> str:
    """Get color saturation level"""
    r, g, b = [x/255.0 for x in rgb_triplet]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    
    if s > 0.7:
        return "High"
    elif s > 0.3:
        return "Medium"
    else:
        return "Low"

def get_color_harmony(color1_rgb: List[float], color2_rgb: List[float]) -> str:
    """Determine color harmony relationship between two colors"""
    def rgb_to_hue(rgb):
        r, g, b = [x/255.0 for x in rgb]
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        return h * 360
    
    hue1 = rgb_to_hue(color1_rgb)
    hue2 = rgb_to_hue(color2_rgb)
    
    hue_diff = abs(hue1 - hue2)
    if hue_diff > 180:
        hue_diff = 360 - hue_diff
    
    if hue_diff < 30:
        return "Analogous"
    elif 150 < hue_diff < 210:
        return "Complementary"
    elif 90 < hue_diff < 150:
        return "Triadic"
    else:
        return "Split-Complementary"

def colors_match(color1_rgb: List[float], color2_rgb: List[float]) -> bool:
    """Determine if two colors match well together"""
    temp1 = get_temperature(color1_rgb)
    temp2 = get_temperature(color2_rgb)
    tone1 = get_tone(color1_rgb)
    tone2 = get_tone(color2_rgb)
    harmony = get_color_harmony(color1_rgb, color2_rgb)
    
    # Colors match if they have compatible temperatures and good harmony
    temp_match = (temp1 == temp2) or "Neutral" in [temp1, temp2]
    harmony_match = harmony in ["Analogous", "Complementary", "Triadic"]
    tone_contrast = (tone1 == "Light" and tone2 == "Dark") or (tone1 == "Dark" and tone2 == "Light")
    
    return temp_match and (harmony_match or tone_contrast)

def get_color_palette(rgb_triplet: List[float]) -> Dict[str, str]:
    """Get a color palette based on the input color"""
    r, g, b = [x/255.0 for x in rgb_triplet]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    
    # Generate complementary color
    comp_h = (h + 0.5) % 1.0
    comp_r, comp_g, comp_b = colorsys.hsv_to_rgb(comp_h, s, v)
    
    # Generate analogous colors
    analog1_h = (h + 0.083) % 1.0  # +30 degrees
    analog2_h = (h - 0.083) % 1.0  # -30 degrees
    
    analog1_r, analog1_g, analog1_b = colorsys.hsv_to_rgb(analog1_h, s, v)
    analog2_r, analog2_g, analog2_b = colorsys.hsv_to_rgb(analog2_h, s, v)
    
    return {
        "original": rgb_to_hex(*rgb_triplet),
        "complementary": rgb_to_hex(comp_r*255, comp_g*255, comp_b*255),
        "analogous1": rgb_to_hex(analog1_r*255, analog1_g*255, analog1_b*255),
        "analogous2": rgb_to_hex(analog2_r*255, analog2_g*255, analog2_b*255)
    }