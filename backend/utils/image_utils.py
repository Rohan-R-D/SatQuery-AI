import io
from PIL import Image
import numpy as np

def load_image_bytes(image_bytes: bytes) -> Image.Image:
    """Load PIL Image from raw bytes."""
    return Image.open(io.BytesIO(image_bytes)).convert("RGB")

def get_image_dimensions(image_bytes: bytes) -> tuple[int, int]:
    """Return (width, height) of an image from raw bytes."""
    with Image.open(io.BytesIO(image_bytes)) as img:
        return img.size

def image_to_numpy(img: Image.Image) -> np.ndarray:
    """Convert PIL image to numpy array."""
    return np.array(img)
