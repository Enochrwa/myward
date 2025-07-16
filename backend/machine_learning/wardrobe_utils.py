import os, json, re
import numpy as np
import cv2
from sklearn.cluster import KMeans
from collections import Counter
import webcolors
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import Model

# Import your color utility functions
from utils.color_utils import get_color_name, get_all_css3_colors
resnet_model = ResNet50(weights='imagenet', include_top=False, pooling='avg')

def extract_features(img_path):
    try:
        img = image.load_img(img_path, target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        features = resnet_model.predict(x)
        return features[0]
    except Exception as e:
        print(f"Error processing {img_path}: {e}")
        return None

def remove_background(img):
    """Remove background using GrabCut algorithm"""
    height, width = img.shape[:2]
    
    # Create mask for GrabCut
    mask = np.zeros((height, width), np.uint8)
    
    # Define rectangle around the clothing item (assuming center focus)
    rect = (int(width*0.1), int(height*0.1), int(width*0.8), int(height*0.8))
    
    # Initialize foreground and background models
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)
    
    # Apply GrabCut
    cv2.grabCut(img, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
    
    # Create mask where sure and likely foreground pixels are True
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    
    # Apply mask to original image
    result = img * mask2[:, :, np.newaxis]
    
    return result, mask2

def extract_dominant_colors(img_path, n_colors=5, remove_bg=True):
    """Extract dominant colors using KMeans clustering"""
    try:
        # Load image
        img = cv2.imread(img_path)
        if img is None:
            return None
            
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Remove background if requested
        if remove_bg:
            img, mask = remove_background(img)
            # Only use non-zero pixels (foreground)
            pixels = img[mask > 0]
        else:
            pixels = img.reshape(-1, 3)
        
        # Remove black pixels (background artifacts)
        pixels = pixels[np.sum(pixels, axis=1) > 30]
        
        if len(pixels) == 0:
            return None
            
        # Apply KMeans clustering
        kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
        kmeans.fit(pixels)
        
        # Get colors and their frequencies
        colors = kmeans.cluster_centers_.astype(int)
        labels = kmeans.labels_
        
        # Calculate color percentages
        label_counts = Counter(labels)
        total_pixels = len(labels)
        
        color_info = []
        for i, color in enumerate(colors):
            percentage = (label_counts[i] / total_pixels) * 100
            
            # Convert to hex
            hex_color = "#{:02x}{:02x}{:02x}".format(color[0], color[1], color[2])
            
            # Use the fixed color name function from utils
            color_name = get_color_name(color.tolist())
            
            # Calculate color properties
            hsv_color = cv2.cvtColor(np.uint8([[color]]), cv2.COLOR_RGB2HSV)[0][0]
            
            color_info.append({
                "rgb": color.tolist(),
                "hex": hex_color,
                "name": color_name,
                "percentage": round(percentage, 2),
                "hsv": hsv_color.tolist(),
                "brightness": int(np.mean(color)),
                "saturation": int(hsv_color[1]),
                "hue": int(hsv_color[0])
            })
        
        # Sort by percentage (most dominant first)
        color_info.sort(key=lambda x: x['percentage'], reverse=True)
        
        return color_info
        
    except Exception as e:
        print(f"Error extracting colors from {img_path}: {e}")
        return None

def get_color_name_fallback(rgb_color):
    """
    Alternative implementation using the static color dictionary
    This is a backup in case the utils import fails
    """
    def get_css3_colors():
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
    
    try:
        # Try to get exact name
        return webcolors.rgb_to_name(rgb_color, spec='css3')
    except ValueError:
        # Find closest color name using static dictionary
        min_distance = float("inf")
        closest_name = None
        
        for name, hex_code in get_css3_colors().items():
            r_c, g_c, b_c = webcolors.hex_to_rgb(hex_code)
            rd = (r_c - rgb_color[0]) ** 2
            gd = (g_c - rgb_color[1]) ** 2
            bd = (b_c - rgb_color[2]) ** 2
            distance = rd + gd + bd
            
            if distance < min_distance:
                min_distance = distance
                closest_name = name
        
        return closest_name

def analyze_color_harmony(colors):
    """Analyze color relationships and harmony"""
    if len(colors) < 2:
        return {"harmony_type": "monochromatic", "compatibility_score": 1.0}
    
    hues = [color['hue'] for color in colors[:3]]  # Use top 3 colors
    
    # Calculate hue differences
    hue_diffs = []
    for i in range(len(hues)):
        for j in range(i+1, len(hues)):
            diff = abs(hues[i] - hues[j])
            diff = min(diff, 180 - diff)  # Account for circular nature of hue
            hue_diffs.append(diff)
    
    avg_hue_diff = np.mean(hue_diffs)
    
    # Determine harmony type
    if avg_hue_diff < 30:
        harmony_type = "monochromatic"
    elif 30 <= avg_hue_diff < 60:
        harmony_type = "analogous"
    elif 60 <= avg_hue_diff < 120:
        harmony_type = "complementary"
    else:
        harmony_type = "triadic"
    
    # Calculate compatibility score (0-1)
    compatibility_score = 1.0 - (avg_hue_diff / 180)
    
    return {
        "harmony_type": harmony_type,
        "compatibility_score": round(compatibility_score, 2),
        "average_hue_difference": round(avg_hue_diff, 2)
    }

def extract_texture_features(img_path):
    """Extract texture features using Local Binary Patterns"""
    try:
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return None
            
        # Calculate Local Binary Pattern
        def lbp(img, radius=1, n_points=8):
            h, w = img.shape
            lbp_img = np.zeros((h, w), dtype=np.uint8)
            
            for i in range(radius, h - radius):
                for j in range(radius, w - radius):
                    center = img[i, j]
                    binary_string = ""
                    
                    for p in range(n_points):
                        angle = 2 * np.pi * p / n_points
                        x = int(i + radius * np.cos(angle))
                        y = int(j + radius * np.sin(angle))
                        
                        if img[x, y] >= center:
                            binary_string += "1"
                        else:
                            binary_string += "0"
                    
                    lbp_img[i, j] = int(binary_string, 2)
            
            return lbp_img
        
        lbp_img = lbp(img)
        
        # Calculate texture statistics
        texture_stats = {
            "mean": float(np.mean(lbp_img)),
            "std": float(np.std(lbp_img)),
            "entropy": float(-np.sum(np.histogram(lbp_img, bins=256)[0] * np.log2(np.histogram(lbp_img, bins=256)[0] + 1e-10))),
            "contrast": float(np.std(img)),
            "homogeneity": float(1 / (1 + np.var(img)))
        }
        
        return texture_stats
        
    except Exception as e:
        print(f"Error extracting texture from {img_path}: {e}")
        return None

def get_season_compatibility(colors):
    """Determine seasonal compatibility based on color analysis"""
    if not colors:
        return "unknown"
    
    # Analyze dominant colors for seasonal characteristics
    avg_saturation = np.mean([color['saturation'] for color in colors[:3]])
    avg_brightness = np.mean([color['brightness'] for color in colors[:3]])
    
    # Simple seasonal classification
    if avg_brightness > 180 and avg_saturation < 100:
        return "summer"
    elif avg_brightness < 100 and avg_saturation > 150:
        return "winter"
    elif avg_brightness > 150 and avg_saturation > 120:
        return "spring"
    else:
        return "autumn"

def infer_category_from_folder(folder_name):
    # Extract last meaningful word like "Dress", "Tee", "Romper", etc.
    match = re.search(r'([A-Za-z]+)$', folder_name)
    return match.group(1).lower() if match else "unknown"

def build_wardrobe_features(image_folder="img/"):
    all_items = []
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    for subfolder in os.listdir(image_folder):
        subfolder_path = os.path.join(image_folder, subfolder)
        if not os.path.isdir(subfolder_path): 
            continue

        inferred_category = infer_category_from_folder(subfolder)
        print(f"Processing category: {inferred_category}")

        for filename in os.listdir(subfolder_path):
            if not filename.lower().endswith((".jpg", ".png", ".jpeg")):
                continue
                
            image_path = os.path.join(subfolder_path, filename)
            print(f"Processing: {filename}")
            
            # Extract ResNet features
            features = extract_features(image_path)
            if features is None: 
                continue
            
            # Extract color information
            colors = extract_dominant_colors(image_path, n_colors=5)
            if colors is None:
                continue
            
            # Extract texture features
            texture = extract_texture_features(image_path)
            
            # Analyze color harmony
            color_harmony = analyze_color_harmony(colors)
            
            # Get season compatibility
            season = get_season_compatibility(colors)
            
            # Get image metadata
            img = cv2.imread(image_path)
            height, width = img.shape[:2] if img is not None else (0, 0)
            
            item_data = {
                "product": subfolder,
                "filename": filename,
                "filepath": image_path,
                "category": inferred_category,
                "embedding": features.tolist(),
                "colors": colors,
                "color_harmony": color_harmony,
                "texture_features": texture,
                "season_compatibility": season,
                "metadata": {
                    "image_width": width,
                    "image_height": height,
                    "dominant_color": colors[0]['hex'] if colors else None,
                    "color_palette": [color['hex'] for color in colors[:3]],
                    "primary_color_name": colors[0]['name'] if colors else None,
                    "color_diversity": len(set(color['name'] for color in colors)),
                    "brightness_level": "bright" if colors and colors[0]['brightness'] > 150 else "dark",
                    "saturation_level": "saturated" if colors and colors[0]['saturation'] > 100 else "muted"
                }
            }
            
            all_items.append(item_data)

    # Save detailed wardrobe data
    with open("data/wardrobe_features.json", "w") as f:
        json.dump(all_items, f, indent=2)
    
    # Save color summary
    color_summary = {}
    for item in all_items:
        category = item['category']
        if category not in color_summary:
            color_summary[category] = {'colors': [], 'count': 0}
        
        color_summary[category]['count'] += 1
        if item['colors']:
            color_summary[category]['colors'].extend([c['name'] for c in item['colors'][:2]])
    
    # Get most common colors per category
    for category in color_summary:
        color_counts = Counter(color_summary[category]['colors'])
        color_summary[category]['most_common_colors'] = color_counts.most_common(5)
        del color_summary[category]['colors']
    
    with open("data/color_summary.json", "w") as f:
        json.dump(color_summary, f, indent=2)
    
    print(f"Processed {len(all_items)} items")
    print(f"Data saved to data/wardrobe_features.json and data/color_summary.json")
    
    return all_items

# Usage example
if __name__ == "__main__":
    # Build wardrobe features with color analysis
    wardrobe_items = build_wardrobe_features()
    
    # Print sample color information
    if wardrobe_items:
        sample_item = wardrobe_items[0]
        print("\nSample color analysis:")
        print(f"Item: {sample_item['filename']}")
        print(f"Category: {sample_item['category']}")
        print(f"Season: {sample_item['season_compatibility']}")
        print(f"Dominant colors:")
        for color in sample_item['colors'][:3]:
            print(f"  - {color['name']}: {color['hex']} ({color['percentage']:.1f}%)")
        print(f"Color harmony: {sample_item['color_harmony']['harmony_type']}")