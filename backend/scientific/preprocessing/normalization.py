from io import BytesIO

import numpy as np
from PIL import Image

from scientific.raster_loader import RasterData


def preview_png(raster: RasterData, band_indices: tuple[int, ...] | None = None) -> bytes:
    count = raster.bands.shape[0]
    if band_indices is None:
        if count == 1:
            band_indices = (0, 0, 0)
        elif count == 3:
            band_indices = (0, 1, 2)
        else:
            raise ValueError("Multispectral previews require an explicit RGB band mapping")
    if len(band_indices) != 3 or any(i < 0 or i >= count for i in band_indices):
        raise ValueError("RGB mapping must contain three valid zero-based band indices")
    channels = []
    for index in band_indices:
        band = raster.bands[index].astype(np.float64)
        valid = raster.valid_mask[index]
        if not valid.any():
            raise ValueError("Preview band contains no valid samples")
        if raster.bands.dtype == np.uint8:
            channel = np.where(valid, band, 0)
        else:
            low, high = np.percentile(band[valid], (2, 98))
            channel = np.zeros_like(band)
            if high > low:
                channel[valid] = np.clip((band[valid] - low) / (high - low), 0, 1) * 255
        channels.append(channel.astype(np.uint8))
    buffer = BytesIO()
    Image.fromarray(np.stack(channels, axis=-1)).save(buffer, format="PNG")
    return buffer.getvalue()


def normalized_difference(first: np.ndarray, second: np.ndarray, valid_mask: np.ndarray | None = None) -> np.ndarray:
    first = np.asarray(first, dtype=np.float64)
    second = np.asarray(second, dtype=np.float64)
    if first.shape != second.shape:
        raise ValueError("Bands must share a spatial grid")
    denominator = first + second
    valid = np.isfinite(first) & np.isfinite(second) & (np.abs(denominator) > 1e-12)
    if valid_mask is not None:
        if valid_mask.shape != first.shape:
            raise ValueError("Mask must match band dimensions")
        valid &= valid_mask
    result = np.full(first.shape, np.nan)
    np.divide(first - second, denominator, out=result, where=valid)
    return result
