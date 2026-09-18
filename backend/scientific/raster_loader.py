from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import numpy as np
import rasterio
from rasterio.io import MemoryFile
from PIL import Image
from config import settings

Image.MAX_IMAGE_PIXELS = settings.MAX_IMAGE_PIXELS


@dataclass(frozen=True)
class RasterData:
    bands: np.ndarray
    valid_mask: np.ndarray
    metadata: dict


def load_raster(source: bytes | str | Path, max_pixels: int = 50_000_000) -> RasterData:
    if max_pixels <= 0:
        raise ValueError("max_pixels must be positive")
    content = source if isinstance(source, bytes) else Path(source).read_bytes()
    if not content:
        raise ValueError("Raster is empty")
    is_tiff = content[:4] in (b"II*\x00", b"MM\x00*", b"II+\x00", b"MM\x00+")
    if is_tiff:
        with MemoryFile(content) as memory:
            with memory.open() as dataset:
                if dataset.width * dataset.height * dataset.count > max_pixels:
                    raise ValueError(f"Raster exceeds sample limit of {max_pixels:,} pixels")
                bands = dataset.read()
                valid = (dataset.read_masks() > 0) & np.isfinite(bands)
                crs = dataset.crs
                metadata = {
                    "width": dataset.width,
                    "height": dataset.height,
                    "band_count": dataset.count,
                    "dtype": str(bands.dtype),
                    "crs": crs.to_string() if crs else None,
                    "transform": list(dataset.transform)[:6] if crs else None,
                    "bounds": list(dataset.bounds) if crs else None,
                    "resolution": list(dataset.res) if crs else None,
                    "nodata": dataset.nodata if dataset.nodata is not None and np.isfinite(dataset.nodata) else None,
                    "band_descriptions": list(dataset.descriptions),
                    "georeferenced": bool(crs and dataset.transform != rasterio.Affine.identity()),
                }
                return RasterData(bands, valid, metadata)
    with Image.open(BytesIO(content)) as image:
        if image.format not in {"PNG", "JPEG"}:
            raise ValueError("Only TIFF, PNG, and JPEG rasters are supported")
        if image.width * image.height > max_pixels:
            raise ValueError(f"Raster exceeds sample limit of {max_pixels:,} pixels")
        bands = np.array(image.convert("RGB")).transpose(2, 0, 1)
        return RasterData(bands, np.ones(bands.shape, dtype=bool), {
            "width": image.width,
            "height": image.height,
            "band_count": 3,
            "dtype": str(bands.dtype),
            "crs": None,
            "transform": None,
            "bounds": None,
            "resolution": None,
            "nodata": None,
            "band_descriptions": ["red", "green", "blue"],
            "georeferenced": False,
        })
