import json
import tempfile
from pathlib import Path

import numpy as np
import pytest

from scientific.datasets.bigearthnet import (
    CORINE_19_CLASSES,
    BigEarthNetDataset,
    BigEarthNetSample,
)


@pytest.fixture
def temp_synthetic_dataset():
    """Fixture generating a temporary synthetic BigEarthNet dataset directory."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        synth_dir = BigEarthNetDataset.create_synthetic_fixture(tmp_path, num_samples=5, seed=42)
        yield synth_dir


def test_synthetic_dataset_initialization_and_length(temp_synthetic_dataset):
    dataset = BigEarthNetDataset(temp_synthetic_dataset)
    assert len(dataset) == 5
    assert dataset.include_s2 is True
    assert dataset.include_s1 is True


def test_sample_tensor_shapes_and_labels(temp_synthetic_dataset):
    dataset = BigEarthNetDataset(temp_synthetic_dataset)
    sample = dataset[0]

    assert isinstance(sample, BigEarthNetSample)
    assert sample.patch_id.startswith("Patch_S2_synthetic_")
    
    # Check Sentinel-2 optical tensor shape (12, 120, 120)
    assert sample.s2_bands is not None
    assert sample.s2_bands.shape == (12, 120, 120)
    assert sample.s2_bands.dtype == np.float32

    # Check Sentinel-1 SAR tensor shape (2, 120, 120)
    assert sample.s1_bands is not None
    assert sample.s1_bands.shape == (2, 120, 120)
    assert sample.s1_bands.dtype == np.float32

    # Check 19-class target vector shape (19,)
    assert sample.target_vector is not None
    assert sample.target_vector.shape == (19,)
    assert sample.target_vector.dtype == np.float32

    # Verify labels match target vector binary encoding
    assert sample.labels is not None
    assert len(sample.labels) > 0
    for label in sample.labels:
        if label in CORINE_19_CLASSES:
            idx = CORINE_19_CLASSES.index(label)
            assert sample.target_vector[idx] == 1.0


def test_class_distribution(temp_synthetic_dataset):
    dataset = BigEarthNetDataset(temp_synthetic_dataset)
    dist = dataset.get_class_distribution()

    assert isinstance(dist, dict)
    assert len(dist) == 19
    total_labels = sum(dist.values())
    assert total_labels > 0


def test_strict_validation_missing_file():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        patch_dir = tmp_path / "Patch_S2_corrupt"
        patch_dir.mkdir()
        
        meta = {"patch_id": "Patch_S2_corrupt", "labels": ["Pastures"]}
        with open(patch_dir / "Patch_S2_corrupt_labels_metadata.json", "w", encoding="utf-8") as f:
            json.dump(meta, f)

        # Non-strict mode should handle missing band files gracefully (returning zero tensors)
        non_strict_ds = BigEarthNetDataset(tmp_path, strict_validation=False)
        sample = non_strict_ds[0]
        assert sample.s2_bands is not None
        assert sample.s2_bands.shape == (12, 120, 120)

        # Strict mode should raise FileNotFoundError when band files are missing
        strict_ds = BigEarthNetDataset(tmp_path, strict_validation=True)
        with pytest.raises(FileNotFoundError):
            _ = strict_ds[0]


def test_corrupt_metadata_handling():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        patch_dir = tmp_path / "Patch_S2_invalid_meta"
        patch_dir.mkdir()
        
        # Write malformed JSON
        with open(patch_dir / "Patch_S2_invalid_meta_labels_metadata.json", "w", encoding="utf-8") as f:
            f.write("{ invalid_json: True ")

        ds = BigEarthNetDataset(tmp_path, strict_validation=False)
        sample = ds[0]
        assert sample.labels == []
        assert sample.target_vector is not None
        assert (sample.target_vector == 0).all()

        strict_ds = BigEarthNetDataset(tmp_path, strict_validation=True)
        with pytest.raises(ValueError, match="Invalid JSON metadata"):
            _ = strict_ds[0]
