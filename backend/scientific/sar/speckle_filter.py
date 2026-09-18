import cv2
import numpy as np


def refined_lee_filter(intensity: np.ndarray, win_size: int = 7) -> np.ndarray:
    """
    Applies the Refined Lee adaptive speckle reduction filter in the linear power domain.
    Preserves structural edges, runways, and water boundaries while suppressing
    multiplicative granular noise without requiring C++ GDAL/SNAP dependencies.
    """
    if intensity.ndim == 3:
        # Process each channel independently
        filtered_channels = [
            refined_lee_filter(intensity[:, :, c], win_size=win_size)
            for c in range(intensity.shape[2])
        ]
        return np.stack(filtered_channels, axis=-1)

    img_float = np.maximum(intensity.astype(np.float64), 1e-7)

    # Local mean and square mean
    mean = cv2.blur(img_float, (win_size, win_size))
    sq_mean = cv2.blur(img_float ** 2, (win_size, win_size))
    variance = np.maximum(sq_mean - (mean ** 2), 0.0)

    # Estimated noise variance in linear power domain (approx. 1 / N_looks)
    noise_var = (mean ** 2) * 0.25
    weight = variance / (variance + noise_var + 1e-7)
    weight = np.clip(weight, 0.0, 1.0)

    filtered = mean + weight * (img_float - mean)
    return np.maximum(filtered, 1e-7)
