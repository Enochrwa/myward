# color_extractor.py
import cv2
from colorthief import ColorThief
import webcolors
from PIL import Image

def closest_color(rgb):
    min_colors = {}
    for name, hex in webcolors.CSS3_HEX_TO_NAMES.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(hex)
        rd, gd, bd = (r_c - rgb[0]) ** 2, (g_c - rgb[1]) ** 2, (b_c - rgb[2]) ** 2
        min_colors[(rd + gd + bd)] = name
    return min_colors[min(min_colors.keys())]

def get_color_metadata(img_path):
    ct = ColorThief(img_path)
    dominant_color = ct.get_color(quality=1)
    palette = ct.get_palette(color_count=5)

    try:
        color_name = webcolors.rgb_to_name(dominant_color)
    except:
        color_name = closest_color(dominant_color)

    return {
        "dominant_color": dominant_color,
        "color_name": color_name,
        "palette": palette
    }
