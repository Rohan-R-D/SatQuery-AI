import numpy as np
from typing import Optional, Dict, Any


def calculate_ndvi(nir_band: np.ndarray, red_band: np.ndarray, valid_mask: Optional[np.ndarray] = None) -> np.ndarray:
    """
    Computes Normalized Difference Vegetation Index: (NIR - Red) / (NIR + Red)
    Values range from -1.0 to +1.0 (dense vegetation > 0.4).
    """
    nir = np.asarray(nir_band, dtype=np.float64)
    red = np.asarray(red_band, dtype=np.float64)

    denominator = nir + red
    valid = (np.abs(denominator) > 1e-7) & np.isfinite(nir) & np.isfinite(red)
    if valid_mask is not None:
        valid &= valid_mask

    result = np.full(nir.shape, np.nan, dtype=np.float64)
    np.divide(nir - red, denominator, out=result, where=valid)
    return result


def calculate_ndwi(green_band: np.ndarray, nir_band: np.ndarray, valid_mask: Optional[np.ndarray] = None) -> np.ndarray:
    """
    Computes Normalized Difference Water Index: (Green - NIR) / (Green + NIR)
    Values > 0.0 indicate open water bodies.
    """
    green = np.asarray(green_band, dtype=np.float64)
    nir = np.asarray(nir_band, dtype=np.float64)

    denominator = green + nir
    valid = (np.abs(denominator) > 1e-7) & np.isfinite(green) & np.isfinite(nir)
    if valid_mask is not None:
        valid &= valid_mask

    result = np.full(green.shape, np.nan, dtype=np.float64)
    np.divide(green - nir, denominator, out=result, where=valid)
    return result


def calculate_ndbi(swir_band: np.ndarray, nir_band: np.ndarray, valid_mask: Optional[np.ndarray] = None) -> np.ndarray:
    """
    Computes Normalized Difference Built-up Index: (SWIR - NIR) / (SWIR + NIR)
    Values > 0.0 indicate high-density built-up urban structures.
    """
    swir = np.asarray(swir_band, dtype=np.float64)
    nir = np.asarray(nir_band, dtype=np.float64)

    denominator = swir + nir
    valid = (np.abs(denominator) > 1e-7) & np.isfinite(swir) & np.isfinite(nir)
    if valid_mask is not None:
        valid &= valid_mask

    result = np.full(swir.shape, np.nan, dtype=np.float64)
    np.divide(swir - nir, denominator, out=result, where=valid)
    return result


def compute_spectral_summary(rgb_or_multispectral: np.ndarray) -> Dict[str, Any]:
    """
    Computes high-level spectral statistics from standard 3-channel RGB or multi-band imagery.
    If only 3 channels (RGB) are present, computes Visible Vegetation and Water approximations.
    """
    if rgb_or_multispectral.ndim == 3 and rgb_or_multispectral.shape[2] >= 3:
        r = rgb_or_multispectral[:, :, 0].astype(np.float64)
        g = rgb_or_multispectral[:, :, 1].astype(np.float64)
        b = rgb_or_multispectral[:, :, 2].astype(np.float64)

        # Visible Atmospherically Resistant Index (VARI): (Green - Red) / (Green + Red - Blue + eps)
        vari_denom = g + r - b
        vari_valid = np.abs(vari_denom) > 1e-7
        vari = np.divide(g - r, vari_denom, where=vari_valid, out=np.zeros_like(g))

        # Green-Blue Water Index approximation
        gb_water = np.divide(g - r, g + r + 1e-7)

        veg_pixels = int(np.sum(vari > 0.15))
        water_pixels = int(np.sum((b > g) & (b > r) & (r < 80)))
        total_pixels = r.size

        return {
            "mean_red": round(float(np.mean(r)), 1),
            "mean_green": round(float(np.mean(g)), 1),
            "mean_blue": round(float(np.mean(b)), 1),
            "estimated_vegetation_pct": round((veg_pixels / total_pixels) * 100, 2),
            "estimated_water_pct": round((water_pixels / total_pixels) * 100, 2),
            "index_type": "visible_approximations"
        }

    return {"index_type": "unavailable", "message": "Insufficient bands for spectral analysis"}
