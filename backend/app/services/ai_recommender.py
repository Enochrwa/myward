# This module provides functions for identifying items in an image using lightweight models
# and for generating basic recommendations.
# It uses EfficientDet-Lite0 from TensorFlow Hub for object detection.
# Enhanced with persistent caching to prevent re-downloading models.

import tensorflow as tf
from PIL import Image, ImageDraw # Pillow for image manipulation
import numpy as np
from typing import List, Dict, Union, Any
import logging
from .model_manager import get_model_manager

logger = logging.getLogger(__name__)

# COCO class names - EfficientDet models trained on COCO typically output IDs.
# We need a mapping to human-readable labels.
# This is a partial list for common items; a full list has 90 classes.
# You may need to expand this or use a utility function to load all COCO names.
COCO_CLASSES = {
    1: "person", 2: "bicycle", 3: "car", 4: "motorcycle", 5: "airplane",
    6: "bus", 7: "train", 8: "truck", 9: "boat", 10: "traffic light",
    11: "fire hydrant", 13: "stop sign", 14: "parking meter", 15: "bench",
    16: "bird", 17: "cat", 18: "dog", 19: "horse", 20: "sheep", 21: "cow",
    22: "elephant", 23: "bear", 24: "zebra", 25: "giraffe", 27: "backpack",
    28: "umbrella", 31: "handbag", 32: "tie", 33: "suitcase", 34: "frisbee",
    35: "skis", 36: "snowboard", 37: "sports ball", 38: "kite", 39: "baseball bat",
    40: "baseball glove", 41: "skateboard", 42: "surfboard", 43: "tennis racket",
    44: "bottle", 46: "wine glass", 47: "cup", 48: "fork", 49: "knife",
    50: "spoon", 51: "bowl", 52: "banana", 53: "apple", 54: "sandwich",
    55: "orange", 56: "broccoli", 57: "carrot", 58: "hot dog", 59: "pizza",
    60: "donut", 61: "cake", 62: "chair", 63: "couch", 64: "potted plant",
    65: "bed", 67: "dining table", 70: "toilet", 72: "tv", 73: "laptop",
    74: "mouse", 75: "remote", 76: "keyboard", 77: "cell phone", 78: "microwave",
    79: "oven", 80: "toaster", 81: "sink", 82: "refrigerator", 84: "book",
    85: "clock", 86: "vase", 87: "scissors", 88: "teddy bear", 89: "hair drier",
    90: "toothbrush"
}
# Relevant fashion/accessory items from COCO (subset for filtering)
# This helps in focusing on wardrobe-related items.
FASHION_ITEMS_LABELS = ["person", "backpack", "umbrella", "handbag", "tie", "suitcase",
                        "sports ball", "bottle", "wine glass", "cup", "hat", "shoe", "sunglasses", # Some models might have these
                        "watch", "scarf", "belt"]

def identify_items(image: Image.Image, confidence_threshold=0.3) -> Union[List[Dict[str, Any]], str]:
    """
    Identifies items in an image using EfficientDet-Lite0 with persistent caching.

    Args:
        image: A PIL Image object.
        confidence_threshold: Minimum score to consider a detection valid.

    Returns:
        A list of dictionaries, where each dictionary contains 'label', 'confidence',
        and 'box' for a detected item, or a string with an error message.
        Returns an empty list if no relevant items are found.
    """
    model_manager = get_model_manager()
    
    # Get the model (from cache or download)
    model = model_manager.get_model("efficientdet_lite0")
    
    if model is None:
        return "Error: Item identification model (EfficientDet-Lite0) could not be loaded."

    try:
        # Preprocess the image
        # 1. Convert to RGB
        image_rgb = image.convert("RGB")
        # 2. Convert PIL Image to NumPy array
        image_np = np.array(image_rgb)
        # 3. Add a batch dimension and ensure dtype is uint8 as expected by some TF Hub models
        # The model expects a tensor of shape [1, height, width, 3]
        image_tensor = tf.convert_to_tensor(image_np, dtype=tf.uint8)[tf.newaxis, ...]

        # Perform detection
        # The model returns a dictionary of tensors.
        detector_outputs = model(image_tensor)

        # Process results
        # These keys are standard for TF Object Detection API models on TF Hub
        detection_scores = detector_outputs['detection_scores'][0].numpy() # Get scores for the first (and only) image
        detection_classes = detector_outputs['detection_classes'][0].numpy().astype(np.int32) # Class IDs
        detection_boxes = detector_outputs['detection_boxes'][0].numpy() # Bounding boxes [ymin, xmin, ymax, xmax]

        identified_items_list = []

        for i in range(len(detection_scores)):
            score = detection_scores[i]
            if score >= confidence_threshold:
                class_id = detection_classes[i]
                label = COCO_CLASSES.get(class_id, f"Unknown Class ID: {class_id}")

                # Optional: Filter for fashion-related items
                # if label not in FASHION_ITEMS_LABELS:
                #     continue

                box = detection_boxes[i] # [ymin, xmin, ymax, xmax] in normalized coordinates

                # Convert normalized box to absolute coordinates (optional, if needed later)
                # img_height, img_width = image_np.shape[:2]
                # abs_box = [
                #     int(box[0] * img_height), int(box[1] * img_width),
                #     int(box[2] * img_height), int(box[3] * img_width)
                # ]

                identified_items_list.append({
                    "label": label,
                    "confidence": float(score),
                    "box_normalized": box.tolist() # Store normalized box
                })

        if not identified_items_list:
            return "No items identified with sufficient confidence."

        return identified_items_list

    except Exception as e:
        logger.error(f"Error during item identification with EfficientDet-Lite0: {e}")
        # tf.errors.InvalidArgumentError can occur if image tensor is not as expected
        if "uint8" in str(e).lower(): # Example of more specific error feedback
            return f"Error during item identification: Image data type mismatch. Details: {str(e)}"
        return f"Error during item identification: {str(e)}"

def get_basic_recommendations(identified_items: List[Dict[str, Any]]) -> List[str]:
    """
    Generates very basic recommendations based on identified items.
    This is a placeholder for more sophisticated recommendation logic.
    """
    if not identified_items or isinstance(identified_items, str):
        return ["Upload an image to get recommendations."]

    recommendations = [
        "Consider the occasion when choosing your outfit.",
        "Ensure your clothes fit well and are comfortable."
    ]

    item_names = [item['label'] for item in identified_items if isinstance(item, dict) and 'label' in item]

    if item_names:
        recommendations.append(f"This look featuring {', '.join(list(set(item_names))[:3])} could be interesting.")
    if any(item_label in FASHION_ITEMS_LABELS for item_label in item_names):
         recommendations.append("Accessorize to complete your look!")
    else:
        recommendations.append("Try to include some clear fashion items for more specific advice.")

    return recommendations


# Example usage (optional)
if __name__ == '__main__':
    # This part is for testing the module directly.
    # Requires Pillow, TensorFlow, TensorFlow Hub to be installed.
    try:
        # Create a dummy image (e.g., a white square)
        # Real object detection needs a meaningful image.
        # For a simple test, we'll just see if it runs without crashing.
        # Replace with a path to a real image for actual testing.
        try:
            # Try to open a test image if available, otherwise create a dummy one.
            # Make sure to have a 'test_image.jpg' in the same directory or provide a full path.
            # test_img = Image.open("test_image.jpg")
            # print("Using test_image.jpg for detection.")
            # Fallback to dummy image if test_image.jpg is not found
            test_img = Image.new('RGB', (320, 320), color='white') # EfficientDet expects min 320x320 for some versions
            logger.info("Using a dummy white image for detection testing.")
        except FileNotFoundError:
            test_img = Image.new('RGB', (320, 320), color='white')
            logger.warning("test_image.jpg not found. Using a dummy white image for detection testing.")

        logger.info("Attempting to identify items in the image...")
        
        items_result = identify_items(test_img, confidence_threshold=0.2) # Lower threshold for dummy image
        if isinstance(items_result, list):
            if items_result:
                logger.info(f"Successfully identified items (first 3): {items_result[:3]}")
                for item in items_result:
                    logger.info(f"  - Label: {item['label']}, Confidence: {item['confidence']:.2f}")
                recommendations = get_basic_recommendations(items_result)
                logger.info("Recommendations:")
                for rec in recommendations:
                    logger.info(f"  - {rec}")
            else:
                logger.info("No items identified in the dummy image, which is expected.")
                recommendations = get_basic_recommendations(items_result) # Test with empty list
                logger.info("Recommendations (for no items):")
                for rec in recommendations:
                    logger.info(f"  - {rec}")

        elif isinstance(items_result, str) and items_result.startswith("No items identified"):
            logger.info(items_result) # Expected for a blank image
            recommendations = get_basic_recommendations([])
            logger.info("Recommendations (for no items):")
            for rec in recommendations:
                logger.info(f"  - {rec}")
        else: # Error string
            logger.error(f"Item identification failed: {items_result}")

    except Exception as e:
        logger.error(f"Error in example usage: {e}")
