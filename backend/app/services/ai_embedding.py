# This module provides functions for extracting image embeddings using lightweight models.
# It uses MobileNetV2 from TensorFlow Hub for efficient embedding generation.
# Enhanced with persistent caching to prevent re-downloading models.

import tensorflow as tf
from PIL import Image
import numpy as np
from typing import List, Optional, Union
import logging
import asyncio # Added for asyncio.to_thread
from .model_manager import get_model_manager

logger = logging.getLogger(__name__)

def _extract_embedding_sync(model, image_batch: np.ndarray) -> List[float]:
    """Synchronous part of embedding extraction."""
    input_tensor = tf.constant(image_batch)

    if hasattr(model, 'signatures') and 'serving_default' in model.signatures:
        try:
            output_dict = model.signatures['serving_default'](input_tensor)
            if not output_dict:
                raise ValueError("Signature output dictionary is empty.")
            output_key = list(output_dict.keys())[0]
            embedding_tensor = output_dict[output_key]
            
            if not isinstance(embedding_tensor, tf.Tensor):
                if isinstance(embedding_tensor, (list, tuple)) and \
                   len(embedding_tensor) > 0 and \
                   isinstance(embedding_tensor[0], tf.Tensor):
                    embedding_tensor = embedding_tensor[0]
                else:
                    raise ValueError(f"Expected a TensorFlow tensor from signature, got {type(embedding_tensor)} for key '{output_key}'.")
        except Exception as sig_e:
            logger.error(f"Error using 'serving_default' signature: {sig_e}. Model type: {type(model)}")
            raise ValueError(f"Error processing model signature: {str(sig_e)}") # Raise to be caught by async wrapper
    
    elif callable(model):
        try:
            embedding_tensor = model(input_tensor)
        except Exception as call_e:
            logger.error(f"Error calling model directly: {call_e}. Model type: {type(model)}")
            raise ValueError(f"Error calling model: {str(call_e)}") # Raise to be caught by async wrapper
    else:
        logger.error(f"Model not callable or valid SavedModel. Type: {type(model)}")
        raise ValueError("Model is not in a recognized callable or SavedModel format.")

    return embedding_tensor.numpy().flatten().tolist()

async def get_image_embedding_async(image: Image.Image) -> Union[List[float], str]:
    """
    Asynchronously extracts image embedding using MobileNetV2.
    Offloads synchronous TensorFlow operations to a thread pool.

    Args:
        image: A PIL Image object.

    Returns:
        A list of floats representing the image embedding, or a string with an error message.
    """
    model_manager = get_model_manager()
    model = model_manager.get_model("mobilenet_v2") # This part is mostly quick (cached) or I/O for download
    
    if model is None:
        logger.error("Image embedding model (MobileNetV2) could not be loaded.")
        return "Error: Image embedding model could not be loaded."

    try:
        # Preprocessing (can be done in the main thread or offloaded if very heavy)
        image = image.convert("RGB")
        image_resized = image.resize((224, 224))
        image_array = np.array(image_resized) / 255.0
        image_batch = np.expand_dims(image_array, axis=0).astype(np.float32)

        # Offload the synchronous TensorFlow model inference to a thread
        embedding = await asyncio.to_thread(_extract_embedding_sync, model, image_batch)
        return embedding
        
    except ValueError as ve: # Catch errors raised from _extract_embedding_sync
        logger.error(f"ValueError during async embedding extraction: {ve}", exc_info=True)
        return str(ve)
    except Exception as e:
        logger.error(f"Unexpected error during async image embedding extraction: {e}", exc_info=True)
        return f"Unexpected error during image embedding extraction: {str(e)}"

# Keep the original synchronous version if it's still used elsewhere, or mark for deprecation.
# For now, let's assume new code will use the async version.
# If wardrobe.py is to call this, wardrobe.py's endpoint will need to be async.
def get_image_embedding(image: Image.Image) -> Union[List[float], str]:
    """
    Synchronous wrapper for image embedding extraction (for compatibility or non-async contexts).
    Consider deprecating if all callers can switch to async.
    """
    # This is a simplified sync version. For true sync execution without asyncio context,
    # it would directly call the core logic. If called from an async context without await,
    # it would block.
    # For now, this just calls the internal sync logic directly.
    
    model_manager = get_model_manager()
    model = model_manager.get_model("mobilenet_v2")
    
    if model is None:
        logger.error("Image embedding model (MobileNetV2) could not be loaded for sync call.")
        return "Error: Image embedding model could not be loaded."

    try:
        image = image.convert("RGB")
        image_resized = image.resize((224, 224))
        image_array = np.array(image_resized) / 255.0
        image_batch = np.expand_dims(image_array, axis=0).astype(np.float32)
        
        return _extract_embedding_sync(model, image_batch)
    except ValueError as ve:
        logger.error(f"ValueError during sync embedding extraction: {ve}", exc_info=True)
        return str(ve)
    except Exception as e:
        logger.error(f"Unexpected error during sync image embedding extraction: {e}", exc_info=True)
        return f"Unexpected error during sync image embedding extraction: {str(e)}"


# Example usage (optional, can be removed or commented out)
async def main_async_example():
    try:
        img = Image.new('RGB', (224, 224), color = 'black')
        logger.info("Attempting to extract embedding for a dummy image (async)...")
        
        embedding_result = await get_image_embedding_async(img)
        if isinstance(embedding_result, list):
            logger.info(f"Successfully extracted embedding (async) (first 10 features): {embedding_result[:10]}")
            logger.info(f"Embedding dimension (async): {len(embedding_result)}")
        else:
            logger.error(f"Embedding extraction failed (async): {embedding_result}")

    except Exception as e:
        logger.error(f"Error in async example usage: {e}")

if __name__ == '__main__':
    # This part is for testing the module directly.
    # It requires Pillow and TensorFlow to be installed.
    # Create a dummy black image for testing
    try:
        img = Image.new('RGB', (224, 224), color = 'black')
        logger.info("Attempting to extract embedding for a dummy image...")
        
        embedding_result = get_image_embedding(img)
        if isinstance(embedding_result, list):
            logger.info(f"Successfully extracted embedding (first 10 features): {embedding_result[:10]}")
            logger.info(f"Embedding dimension: {len(embedding_result)}")
        else:
            logger.error(f"Embedding extraction failed: {embedding_result}")

    except Exception as e:
        logger.error(f"Error in example usage: {e}")
