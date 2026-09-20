import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# Standard CORINE Land Cover 19-class re-mapped taxonomy for BigEarthNet
CORINE_19_CLASSES: List[str] = [
    "Continuous urban fabric",
    "Discontinuous urban fabric",
    "Industrial or commercial units",
    "Road and rail networks and associated land",
    "Port areas",
    "Airports",
    "Mineral extraction sites",
    "Dump sites",
    "Construction sites",
    "Green urban areas",
    "Sport and leisure facilities",
    "Non-irrigated arable land",
    "Permanently irrigated land",
    "Rice fields",
    "Vineyards",
    "Fruit trees and berry plantations",
    "Olive groves",
    "Pastures",
    "Annual crops associated with permanent crops",
]

# Mapping from class name to binary index
CLASS_TO_IDX: Dict[str, int] = {cls_name: i for i, cls_name in enumerate(CORINE_19_CLASSES)}

# Sentinel-2 band names (12 bands)
S2_BAND_NAMES: List[str] = [
    "B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B09", "B11", "B12"
]

# Sentinel-1 band names (2 dual-pol channels)
S1_BAND_NAMES: List[str] = ["VV", "VH"]


@dataclass
class BigEarthNetSample:
    """Dataclass representing a single BigEarthNet multi-modal sample patch."""
    patch_id: str
    s2_bands: Optional[np.ndarray] = None  # Shape: (12, H, W)
    s1_bands: Optional[np.ndarray] = None  # Shape: (2, H, W)
    target_vector: Optional[np.ndarray] = None  # Shape: (19,) binary float32
    labels: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class BigEarthNetDataset:
    """
    Modular, format-independent PyTorch/NumPy dataset loader for BigEarthNet.
    
    Supports Sentinel-2 (12 multispectral bands) and Sentinel-1 (2 SAR dual-pol channels),
    multi-label CORINE 19-class target vector generation, and synthetic test fixtures.
    """

    def __init__(
        self,
        root_dir: Union[str, Path],
        split_file: Optional[Union[str, Path]] = None,
        include_s2: bool = True,
        include_s1: bool = True,
        strict_validation: bool = False,
    ):
        self.root_dir = Path(root_dir)
        self.include_s2 = include_s2
        self.include_s1 = include_s1
        self.strict_validation = strict_validation
        self.samples: List[Path] = []

        if not self.root_dir.exists():
            raise FileNotFoundError(f"BigEarthNet root directory not found: {self.root_dir}")

        # Resolve sample paths
        if split_file:
            split_path = Path(split_file)
            if not split_path.exists():
                raise FileNotFoundError(f"Split file not found: {split_path}")
            with open(split_path, "r", encoding="utf-8") as f:
                patch_ids = json.load(f)
            for pid in patch_ids:
                patch_dir = self._find_patch_dir(pid)
                if patch_dir:
                    self.samples.append(patch_dir)
                elif self.strict_validation:
                    raise FileNotFoundError(f"Patch directory for ID '{pid}' not found under {self.root_dir}")
        else:
            # Discover patch directories containing labels_metadata.json
            s2_dir = self.root_dir / "Sentinel-2"
            search_dir = s2_dir if s2_dir.exists() else self.root_dir
            for p in search_dir.glob("**/*_labels_metadata.json"):
                self.samples.append(p.parent)

        self.samples.sort()

    def _find_patch_dir(self, patch_id: str) -> Optional[Path]:
        """Finds the directory corresponding to a patch_id."""
        s2_patch = self.root_dir / "Sentinel-2" / patch_id
        if s2_patch.is_dir():
            return s2_patch
        direct_patch = self.root_dir / patch_id
        if direct_patch.is_dir():
            return direct_patch
        # Search recursively
        for metadata_file in self.root_dir.glob(f"**/{patch_id}_labels_metadata.json"):
            return metadata_file.parent
        return None

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> BigEarthNetSample:
        if idx < 0 or idx >= len(self.samples):
            raise IndexError(f"Index {idx} out of range for dataset of size {len(self.samples)}")

        patch_dir = self.samples[idx]
        patch_id = patch_dir.name

        # 1. Parse Metadata & Labels
        metadata, labels, target_vec = self._load_metadata(patch_dir, patch_id)

        # 2. Load Sentinel-2 Optical Bands (12 bands)
        s2_tensor = None
        if self.include_s2:
            s2_tensor = self._load_s2_bands(patch_dir, patch_id)

        # 3. Load Sentinel-1 SAR Bands (2 bands)
        s1_tensor = None
        if self.include_s1:
            s1_tensor = self._load_s1_bands(patch_dir, patch_id)

        return BigEarthNetSample(
            patch_id=patch_id,
            s2_bands=s2_tensor,
            s1_bands=s1_tensor,
            target_vector=target_vec,
            labels=labels,
            metadata=metadata,
        )

    def _load_metadata(self, patch_dir: Path, patch_id: str) -> Tuple[Dict[str, Any], List[str], np.ndarray]:
        """Loads and parses metadata JSON, returning metadata dict, labels list, and 19-class target vector."""
        meta_file = patch_dir / f"{patch_id}_labels_metadata.json"
        if not meta_file.exists():
            # Search for any _labels_metadata.json in patch_dir
            candidates = list(patch_dir.glob("*_labels_metadata.json"))
            if candidates:
                meta_file = candidates[0]
            else:
                if self.strict_validation:
                    raise FileNotFoundError(f"Metadata file missing in patch: {patch_dir}")
                logger.warning(f"Metadata file missing for patch {patch_id}; returning empty target vector")
                return {}, [], np.zeros(19, dtype=np.float32)

        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                meta = json.load(f)
        except json.JSONDecodeError as e:
            if self.strict_validation:
                raise ValueError(f"Invalid JSON metadata in patch {patch_dir}: {e}")
            logger.warning(f"Corrupt metadata JSON in patch {patch_id}: {e}")
            return {}, [], np.zeros(19, dtype=np.float32)

        labels = meta.get("labels", [])
        target_vec = np.zeros(19, dtype=np.float32)
        for lbl in labels:
            if lbl in CLASS_TO_IDX:
                target_vec[CLASS_TO_IDX[lbl]] = 1.0

        return meta, labels, target_vec

    def _load_s2_bands(self, patch_dir: Path, patch_id: str) -> Optional[np.ndarray]:
        """Loads Sentinel-2 12 multispectral bands into shape (12, H, W)."""
        bands = []
        h, w = 120, 120  # Standard 10m grid shape

        for band_name in S2_BAND_NAMES:
            band_path = patch_dir / f"{patch_id}_{band_name}.tif"
            if not band_path.exists():
                # Check for .npy fallback for testing/fixtures
                npy_path = patch_dir / f"{patch_id}_{band_name}.npy"
                if npy_path.exists():
                    data = np.load(npy_path)
                    bands.append(data.astype(np.float32))
                    continue
                # If band file missing, fail in strict mode or fill zeros
                if self.strict_validation:
                    raise FileNotFoundError(f"Sentinel-2 band {band_name} missing: {band_path}")
                bands.append(np.zeros((h, w), dtype=np.float32))
                continue

            try:
                # Load GeoTIFF or Image
                with Image.open(band_path) as img:
                    arr = np.array(img, dtype=np.float32)
                    bands.append(arr)
            except Exception as e:
                if self.strict_validation:
                    raise ValueError(f"Failed reading band {band_name} from {band_path}: {e}")
                bands.append(np.zeros((h, w), dtype=np.float32))

        return np.stack(bands, axis=0) if bands else None

    def _load_s1_bands(self, patch_dir: Path, patch_id: str) -> Optional[np.ndarray]:
        """Loads Sentinel-1 2 dual-pol SAR channels (VV, VH) into shape (2, H, W)."""
        # Locate corresponding S1 directory if root is structured
        s1_patch_dir = patch_dir
        if "Sentinel-2" in str(patch_dir):
            s1_dir_name = patch_dir.name.replace("Patch_S2_", "Patch_S1_")
            s1_candidate = patch_dir.parent.parent / "Sentinel-1" / s1_dir_name
            if s1_candidate.is_dir():
                s1_patch_dir = s1_candidate

        s1_patch_id = s1_patch_dir.name
        bands = []
        h, w = 120, 120

        for bname in S1_BAND_NAMES:
            bpath = s1_patch_dir / f"{s1_patch_id}_{bname}.tif"
            if not bpath.exists():
                npy_path = s1_patch_dir / f"{s1_patch_id}_{bname}.npy"
                if npy_path.exists():
                    data = np.load(npy_path)
                    bands.append(data.astype(np.float32))
                    continue
                if self.strict_validation:
                    raise FileNotFoundError(f"Sentinel-1 band {bname} missing: {bpath}")
                bands.append(np.zeros((h, w), dtype=np.float32))
                continue

            try:
                with Image.open(bpath) as img:
                    bands.append(np.array(img, dtype=np.float32))
            except Exception as e:
                if self.strict_validation:
                    raise ValueError(f"Failed reading SAR band {bname} from {bpath}: {e}")
                bands.append(np.zeros((h, w), dtype=np.float32))

        return np.stack(bands, axis=0) if bands else None

    def get_class_distribution(self) -> Dict[str, int]:
        """Computes label frequency count across all samples in dataset."""
        counts = {cls_name: 0 for cls_name in CORINE_19_CLASSES}
        for i in range(len(self)):
            sample = self[i]
            if sample.labels:
                for lbl in sample.labels:
                    if lbl in counts:
                        counts[lbl] += 1
        return counts

    @classmethod
    def create_synthetic_fixture(
        cls, output_dir: Union[str, Path], num_samples: int = 5, seed: int = 42
    ) -> Path:
        """
        Creates a synthetic BigEarthNet dataset fixture directory for unit testing.
        Clearly labeled as synthetic test data.
        """
        out_dir = Path(output_dir)
        s2_dir = out_dir / "Sentinel-2"
        s1_dir = out_dir / "Sentinel-1"
        s2_dir.mkdir(parents=True, exist_ok=True)
        s1_dir.mkdir(parents=True, exist_ok=True)

        rng = np.random.default_rng(seed)

        for i in range(num_samples):
            pid_s2 = f"Patch_S2_synthetic_{i:03d}"
            pid_s1 = f"Patch_S1_synthetic_{i:03d}"

            patch_s2_dir = s2_dir / pid_s2
            patch_s1_dir = s1_dir / pid_s1
            patch_s2_dir.mkdir(exist_ok=True)
            patch_s1_dir.mkdir(exist_ok=True)

            # Sample 1-3 random CORINE classes
            sample_labels = list(rng.choice(CORINE_19_CLASSES, size=rng.integers(1, 4), replace=False))

            meta = {
                "patch_id": pid_s2,
                "labels": sample_labels,
                "coordinates": {"ulx": 400000.0, "uly": 5000000.0},
                "projection": "EPSG:32633",
                "is_synthetic": True,
            }

            with open(patch_s2_dir / f"{pid_s2}_labels_metadata.json", "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2)

            # Generate S2 bands (120x120 uint16 values)
            for bname in S2_BAND_NAMES:
                arr = rng.integers(100, 3000, size=(120, 120), dtype=np.uint16)
                img = Image.fromarray(arr)
                img.save(patch_s2_dir / f"{pid_s2}_{bname}.tif")

            # Generate S1 bands (120x120 float32 values)
            for bname in S1_BAND_NAMES:
                arr = rng.uniform(0.01, 0.5, size=(120, 120)).astype(np.float32)
                img = Image.fromarray((arr * 65535).astype(np.uint16))
                img.save(patch_s1_dir / f"{pid_s1}_{bname}.tif")

        return out_dir
