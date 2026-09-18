import numpy as np
import pytest
from scientific.preprocessing.alignment import CoregistrationQualityGate
from scientific.sar.speckle_filter import refined_lee_filter
from scientific.sar.calibration import SARPreprocessor
from scientific.indices.spectral import calculate_ndvi, calculate_ndwi, calculate_ndbi, compute_spectral_summary
from scientific.geometry.georeferencing import pixel_to_geojson_polygon, regions_to_geojson_feature_collection
from scientific.change_detection.opencv_baseline import OpenCVChangeDetector


def test_coregistration_quality_gate_identical_images():
    """Verify co-registration on identical images passes with low RMSE."""
    gate = CoregistrationQualityGate()
    # Create high-entropy synthetic scene with distinct features
    img = np.zeros((300, 300, 3), dtype=np.uint8)
    for x, y in [(50, 50), (120, 80), (200, 200), (80, 220), (220, 60)]:
        img[y:y+30, x:x+30] = [200, 220, 240]

    aligned_img, report = gate.align_and_validate(img, img)
    assert report["passed"] is True
    assert report["rmse"] <= 0.8
    assert report["nmi"] >= 0.45


def test_refined_lee_filter():
    """Verify Refined Lee filter preserves mean intensity while smoothing noise."""
    np.random.seed(42)
    clean_signal = np.full((100, 100), 50.0)
    clean_signal[40:60, 40:60] = 150.0  # Sharp rectangular feature

    speckle_noise = np.random.gamma(4, 0.25, (100, 100))
    noisy_sar = clean_signal * speckle_noise

    filtered = refined_lee_filter(noisy_sar, win_size=7)
    assert filtered.shape == (100, 100)
    assert np.all(filtered > 0)
    # Variance in homogeneous region should decrease
    assert np.var(filtered[:30, :30]) < np.var(noisy_sar[:30, :30])


def test_sar_calibration_and_composite():
    """Verify SAR dB conversion and 3-channel composite construction."""
    preprocessor = SARPreprocessor()
    vv_raw = np.random.randint(10, 200, (64, 64), dtype=np.uint8)
    vh_raw = np.random.randint(5, 120, (64, 64), dtype=np.uint8)

    composite = preprocessor.create_polarimetric_composite(vv_raw, vh_raw)
    assert composite.shape == (64, 64, 3)
    assert composite.dtype == np.uint8
    assert np.min(composite) >= 0
    assert np.max(composite) <= 255


def test_spectral_indices():
    """Verify mathematical calculation of NDVI, NDWI, and NDBI."""
    nir = np.full((10, 10), 0.8)
    red = np.full((10, 10), 0.2)
    green = np.full((10, 10), 0.1)
    swir = np.full((10, 10), 0.3)

    ndvi = calculate_ndvi(nir, red)
    # (0.8 - 0.2) / (0.8 + 0.2) = 0.6 / 1.0 = 0.6
    assert np.allclose(ndvi, 0.6, atol=1e-5)

    ndwi = calculate_ndwi(green, nir)
    # (0.1 - 0.8) / (0.1 + 0.8) = -0.7 / 0.9 = -0.777...
    assert np.allclose(ndwi, -0.777777, atol=1e-4)

    ndbi = calculate_ndbi(swir, nir)
    # (0.3 - 0.8) / (0.3 + 0.8) = -0.5 / 1.1 = -0.4545...
    assert np.allclose(ndbi, -0.454545, atol=1e-4)


def test_geojson_georeferencing():
    """Verify pixel boxes export to valid GeoJSON FeatureCollection."""
    regions = [
        {"x": 50, "y": 60, "width": 80, "height": 40, "label": "water_body", "confidence": 0.95}
    ]
    fc = regions_to_geojson_feature_collection(regions, image_width=500, image_height=500)
    assert fc["type"] == "FeatureCollection"
    assert len(fc["features"]) == 1
    feat = fc["features"][0]
    assert feat["geometry"]["type"] == "Polygon"
    assert feat["properties"]["label"] == "water_body"
    assert feat["properties"]["confidence"] == 0.95


def test_opencv_change_detection():
    """Verify deterministic change detection maps pixel differences."""
    t1 = np.zeros((100, 100, 3), dtype=np.uint8)
    t2 = np.zeros((100, 100, 3), dtype=np.uint8)
    # Add changed rectangle of size 20x20 = 400 pixels
    t2[30:50, 30:50] = [255, 255, 255]

    res = OpenCVChangeDetector.detect_changes(t1, t2, threshold_val=30, min_region_area=20)
    assert res["changed_pixels"] >= 350
    assert res["change_percentage"] > 3.0
    assert len(res["regions"]) >= 1
    assert len(res["artifacts"]) >= 2
