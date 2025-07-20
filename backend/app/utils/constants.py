CATEGORY_PART_MAPPING = {
    "Overcoat": "outerwear", "bag": "accessory", "blazers": "outerwear", "blouse": "top", "coats": "outerwear",
    "croptop": "top", "dress": "full_body", "hat": "accessory", "hoodie": "outerwear", "jacket": "outerwear",
    "jeans": "bottom", "outwear": "outerwear", "shirt": "top", "shoes": "accessory", "shorts": "bottom",
    "skirt": "bottom", "suit": "full_body", "sunglasses": "accessory", "sweater": "top", "trousers": "bottom", "tshirt": "top"
}

CLOTHING_PARTS = {
    "top": ["shirt", "tshirt", "blouse", "sweater", "hoodie", "croptop"],
    "bottom": ["jeans", "trousers", "shorts", "skirt"],
    "outerwear": ["jacket", "coat", "overcoat", "blazers"],
    "full_body": ["dress", "suit"],
    "accessory": ["bag", "shoes", "sunglasses", "hat"]
}

OUTFIT_RULES = {
    "full_body": ["accessory", "outerwear"],
    "top": ["bottom", "outerwear", "accessory"],
    "bottom": ["top", "outerwear", "accessory"],
    "outerwear": ["top", "bottom", "accessory"],
    "accessory": ["top", "bottom", "outerwear"],
    "unknown": ["top", "bottom", "outerwear", "accessory"]
}
