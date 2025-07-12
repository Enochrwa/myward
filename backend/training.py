from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
from PIL import Image
import torch

model = VisionEncoderDecoderModel.from_pretrained("ydshieh/vit-gpt2-coco-en")
feature_extractor = ViTImageProcessor.from_pretrained("ydshieh/vit-gpt2-coco-en")
tokenizer = AutoTokenizer.from_pretrained("ydshieh/vit-gpt2-coco-en")

def generate_caption(image_path):
    image = Image.open(image_path).convert("RGB")
    pixel_values = feature_extractor(images=image, return_tensors="pt").pixel_values
    output_ids = model.generate(pixel_values, max_length=16, num_beams=4)
    return tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()

# Example:
print(generate_caption("wardrobe_images/wardrobe_images/kimono/pexels_white_kimono_traditional_1.jpg"))
