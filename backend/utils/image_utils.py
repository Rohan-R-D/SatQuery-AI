import io
from PIL import Image
import numpy as np
from config import settings

# Enforce decompression bomb defense
Image.MAX_IMAGE_PIXELS = settings.MAX_IMAGE_PIXELS

def load_image_bytes(image_bytes: bytes) -> Image.Image:
    """Load PIL Image from raw bytes."""
    with Image.open(io.BytesIO(image_bytes)) as img:
        width, height = img.size
        if width * height > settings.MAX_IMAGE_PIXELS:
            raise ValueError(f"Image dimensions ({width}x{height}) exceed maximum allowed limit of {settings.MAX_IMAGE_PIXELS} pixels.")
        return img.convert("RGB")

def get_image_dimensions(image_bytes: bytes) -> tuple[int, int]:
    """Return (width, height) of an image from raw bytes."""
    with Image.open(io.BytesIO(image_bytes)) as img:
        width, height = img.size
        if width * height > settings.MAX_IMAGE_PIXELS:
            raise ValueError(f"Image dimensions ({width}x{height}) exceed maximum allowed limit of {settings.MAX_IMAGE_PIXELS} pixels.")
        return img.size

def image_to_numpy(img: Image.Image) -> np.ndarray:
    """Convert PIL image to numpy array."""
    return np.array(img)
