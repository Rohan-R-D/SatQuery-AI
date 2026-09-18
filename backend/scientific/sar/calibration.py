import numpy as np
from typing import Tuple, Dict, Any
from scientific.sar.speckle_filter import refined_lee_filter


class SARPreprocessor:
    """
    Standardized SAR Radiometric and Polarimetric Preprocessor for Sentinel-1 / RISAT C-band rasters.
    Converts raw DN intensity to calibrated decibel scale backscatter (sigma0 dB)
    and constructs normalized 3-channel composites for VLM tokenizers.
    """
    def __init__(self, vv_db_range: Tuple[float, float] = (-25.0, 0.0), vh_db_range: Tuple[float, float] = (-32.0, -5.0)):
        self.vv_min, self.vv_max = vv_db_range
        self.vh_min, self.vh_max = vh_db_range

    def dn_to_linear(self, dn_array: np.ndarray, calib_factor: float = 1.0) -> np.ndarray:
        """Converts raw Digital Numbers to linear power backscatter intensity."""
        intensity = (dn_array.astype(np.float64) ** 2) * calib_factor
        return np.maximum(intensity, 1e-7)

    def linear_to_db(self, intensity_array: np.ndarray) -> np.ndarray:
        """Converts linear intensity to decibel scale (dB)."""
        safe_intensity = np.maximum(intensity_array, 1e-7)
        return 10.0 * np.log10(safe_intensity)

    def normalize_band(self, band_db: np.ndarray, db_min: float, db_max: float) -> np.ndarray:
        """Min-max normalizes dB SAR band to [0, 255] uint8."""
        stretched = (band_db - db_min) / (db_max - db_min)
        clipped = np.clip(stretched, 0.0, 1.0)
        return (clipped * 255.0).astype(np.uint8)

    def process_sar_channel(self, raw_channel: np.ndarray, channel_type: str = "VV") -> Tuple[np.ndarray, Dict[str, Any]]:
        """Calibrates, filters, and computes statistical properties of a single SAR channel."""
        lin = self.dn_to_linear(raw_channel)
        filtered_lin = refined_lee_filter(lin, win_size=7)
        db_vals = self.linear_to_db(filtered_lin)

        db_min = self.vv_min if channel_type == "VV" else self.vh_min
        db_max = self.vv_max if channel_type == "VV" else self.vh_max
        norm_uint8 = self.normalize_band(db_vals, db_min, db_max)

        stats = {
            "mean_db": round(float(np.mean(db_vals)), 2),
            "min_db": round(float(np.min(db_vals)), 2),
            "max_db": round(float(np.max(db_vals)), 2),
            "std_db": round(float(np.std(db_vals)), 2)
        }
        return norm_uint8, stats

    def create_polarimetric_composite(self, vv_raw: np.ndarray, vh_raw: np.ndarray) -> np.ndarray:
        """
        Creates a 3-channel pseudo-RGB composite optimized for VLM vision backbones:
        Channel R: Normalized Filtered VV Backscatter (Surface roughness & soil)
        Channel G: Normalized Filtered VH Backscatter (Volume scattering & canopy)
        Channel B: Dual-Pol Ratio / NDPI Structural Index
        """
        vv_lin = self.dn_to_linear(vv_raw)
        vh_lin = self.dn_to_linear(vh_raw)

        vv_filt_lin = refined_lee_filter(vv_lin)
        vh_filt_lin = refined_lee_filter(vh_lin)

        vv_filt_db = self.linear_to_db(vv_filt_lin)
        vh_filt_db = self.linear_to_db(vh_filt_lin)

        # Cross-polarization ratio
        ratio_db = vh_filt_db - vv_filt_db

        ch_r = self.normalize_band(vv_filt_db, self.vv_min, self.vv_max)
        ch_g = self.normalize_band(vh_filt_db, self.vh_min, self.vh_max)
        ch_b = self.normalize_band(ratio_db, -15.0, 0.0)

        return np.stack([ch_r, ch_g, ch_b], axis=-1)


sar_preprocessor = SARPreprocessor()
