# Phase 2: BigEarthNet Dataset Preparation & Groundwork Plan

**Author**: Member 3 — AI/ML Lead (Remote Sensing VQA, VLMs, Pretrained Models, BigEarthNet, Grounding, Change-VQA, Evaluation)  
**Project**: SatQuery AI (SIH 2026, ISRO PS SIH26167)  
**Branch**: `feature/member3-ai-ml-training`  
**Date**: September 20, 2026  
**Status**: Phase 2 Dataset Groundwork Complete (Specification, Modular Loader & Synthetic Test Suite)  

---

## 1. Executive Summary & Dataset Version Decision

This document presents the verified dataset preparation plan, proposed directory layout, preprocessing audit, and modular loader architecture for integrating the **BigEarthNet** benchmark into the **SatQuery AI** Two-Lane Architecture.

### 1.1 Dataset Version Comparison

Four primary configurations of the BigEarthNet dataset family were evaluated:

| Feature / Metric | BigEarthNet-MM v1.0 | BigEarthNet-S2 (v1.0) | BigEarthNet-S1 (v1.0) | BigEarthNet v2.0 (reBEN) |
| --- | --- | --- | --- | --- |
| **Release Year** | 2021 (Sumbul et al.) | 2019 (Sumbul et al.) | 2021 (Sumbul et al.) | 2024 (Clasen et al., TU Berlin) |
| **Total Patches** | 590,326 patch pairs | 590,326 S2 patches | 590,326 S1 patches | 549,488 patch pairs |
| **Modalities** | 12-Band S2 + 2-Band S1 | 12-Band S2 Optical | 2-Band S1 SAR Dual-Pol | 12-Band S2 + 2-Band S1 |
| **S2 Tiles / S1 Scenes** | 125 tiles / 325 scenes | 125 tiles | 325 scenes | 115 tiles / 312 scenes |
| **Atmospheric Correction** | Sen2Cor (Original) | Sen2Cor (Original) | N/A | Sen2Cor v2.11 (Refined) |
| **Land Cover Labels** | CLC 2018 (v2018_u1) | CLC 2018 (v2018_u1) | CLC 2018 (v2018_u1) | CLC 2018 (v2020_u1, reduced noise) |
| **Label Hierarchy** | 43 original / 19 re-mapped | 43 original / 19 re-mapped | 43 original / 19 re-mapped | 19 CORINE land-cover classes |
| **Dataset License** | CDLA-Permissive-1.0 | CDLA-Permissive-1.0 | CDLA-Permissive-1.0 | CC BY 4.0 |

### 1.2 Version Selection Decision & Status

- **Proposed Target**: **BigEarthNet v2.0 (reBEN)** is the proposed primary target due to refined atmospheric correction (Sen2Cor v2.11) and updated CLC 2018 labels.
- **Selection Status**: **`PLANNED / PROPOSED TARGET — Pending real-dataset compatibility and subset evaluation.`**
- **Verification Note**: Neither v1.0 nor v2.0 has been downloaded, loaded, or benchmarked in this repository yet. Real-data compatibility remains an unverified assumption to be tested during Phase 3.

---

## 2. Official Dataset Sources & Attribution

1. **Official Website**: http://bigearth.net/
2. **BigEarthNet-MM v1.0 Repository**: Hosted by TU Berlin Remote Sensing Image Analysis (RSiM) Group & Zenodo ([doi:10.5281/zenodo.4893111](https://doi.org/10.5281/zenodo.4893111)).
3. **BigEarthNet v2.0 (reBEN) Paper & Code**: Clasen et al., *"reBEN: Refined BigEarthNet Dataset for Remote Sensing Image Analysis"*, TU Berlin (2024). GitHub: [rsim-tu-berlin/bigearthnet-pipeline](https://github.com/rsim-tu-berlin/bigearthnet-pipeline).

---

## 3. Dataset Modalities, Labels, and Metadata Structure

### 3.1 Sentinel-2 Multispectral Modality (`DESIGNED / UNVERIFIED ON REAL DATA`)
- **12 Bands**: B01 (60m), B02 (10m), B03 (10m), B04 (10m), B05 (20m), B06 (20m), B07 (20m), B08 (10m), B8A (20m), B09 (60m), B11 (20m), B12 (20m).
- **Assumed Spatial Resolution**: 10m grid (120x120 pixels per patch).

### 3.2 Sentinel-1 SAR Dual-Polarization Modality (`DESIGNED / UNVERIFIED ON REAL DATA`)
- **2 Channels**: Co-polarized VV and Cross-polarized VH backscatter intensity.
- **Assumed Spatial Resolution**: 10m spatial resolution (120x120 pixels per patch).

### 3.3 Label Hierarchy (19 CORINE Classes) (`IMPLEMENTED IN LOADER`)
Original 43 CORINE land-cover classes are mapped to 19 multi-label categories:
1. *Continuous urban fabric*
2. *Discontinuous urban fabric*
3. *Industrial or commercial units*
4. *Road and rail networks and associated land*
5. *Port areas*
6. *Airports*
7. *Mineral extraction sites*
8. *Dump sites*
9. *Construction sites*
10. *Green urban areas*
11. *Sport and leisure facilities*
12. *Non-irrigated arable land*
13. *Permanently irrigated land*
14. *Rice fields*
15. *Vineyards*
16. *Fruit trees and berry plantations*
17. *Olive groves*
18. *Pastures*
19. *Annual crops associated with permanent crops*

### 3.4 Metadata Format (`IMPLEMENTED IN LOADER / UNVERIFIED ON REAL DATA`)
The dataset loader expects a JSON metadata file (`*_labels_metadata.json`) containing a list of class strings under key `"labels"`.

---

## 4. Proposed Directory Structure (`PROPOSED / UNCREATED`)

The proposed data layout for future phases:

```text
data/
└── bigearthnet/
    ├── raw/                         # Downloaded GeoTIFF patch archives (uncreated)
    │   ├── sentinel-2/              # Sentinel-2 multispectral patch directories
    │   └── sentinel-1/              # Sentinel-1 dual-pol SAR patch directories
    ├── metadata/                    # Extracted class catalogs & CORINE 19-class mappings
    ├── processed/                   # Preprocessed tensors & synthesized VLM previews
    │   ├── rgb_previews/            # 3-channel RGB PNG composites
    │   └── normalized_tensors/      # Normalized numpy arrays
    ├── subsets/                     # Small reproducible experimental subsets
    │   └── subset_1k/               # 1,000-patch validation subset directory
    └── splits/                      # Train/Validation/Test split definition files
        ├── train.json
        ├── val.json
        └── test.json
```

---

## 5. Preprocessing Feature Audit & Verification

Every preprocessing capability is classified by its actual codebase implementation status:

| Feature / Capability | Actual Implementation Status | Module / Source Location | Notes |
| --- | --- | --- | --- |
| **Sentinel-1 Refined Lee Speckle Filtering** | `EXISTING IMPLEMENTATION` | `backend/scientific/sar/speckle_filter.py` | Existed prior to Phase 2; verified. |
| **SAR Intensity-to-Decibel Conversion ($\sigma^0\text{ dB}$)** | `EXISTING IMPLEMENTATION` | `backend/scientific/sar/calibration.py` | Existed prior to Phase 2 (`linear_to_db`). |
| **2%–98% Percentile Normalization** | `EXISTING IMPLEMENTATION` | `backend/scientific/preprocessing/normalization.py` | Existed prior to Phase 2 (`preview_png`). |
| **Sentinel-2 Band Resampling (20m/60m to 10m)** | `DESIGNED / PLANNED` | N/A | Not implemented in code; planned for Phase 3/4. |
| **RGB Preview Composite Generation** | `EXISTING IMPLEMENTATION` | `backend/scientific/preprocessing/normalization.py` | Existed prior to Phase 2 (`preview_png`). |
| **False-Color Composite Generation** | `EXISTING IMPLEMENTATION` | `backend/scientific/preprocessing/normalization.py` | Existed prior to Phase 2 (`preview_png`). |
| **Multi-Band Tensor Extraction** | `NEWLY IMPLEMENTED IN PHASE 2` | `backend/scientific/datasets/bigearthnet.py` | Implemented in `BigEarthNetDataset` (`_load_s2_bands`, `_load_s1_bands`). |

---

## 6. Small-Subset Experiment Plan

### 6.1 Planned Subset Status
- **Current Status**: **`PLANNED — NOT DOWNLOADED`**
  - *Local File Check*: `data/bigearthnet/subsets/subset_1k/` **does not exist locally**. 0 real BigEarthNet samples have been downloaded.
  - *Sampling & Label Distribution*: Has **not** been evaluated on real data.

### 6.2 Proposed Specifications
- **Target Size**: 1,000 Sentinel-2 + Sentinel-1 patch pairs (~250 MB total archive size).
- **Target Directory**: `data/bigearthnet/subsets/subset_1k/`.
- **Random Seed**: Fixed seed `42` for reproducible subset sampling.

---

## 7. Disambiguated Licensing Notes

- **BigEarthNet-MM v1.0 Dataset License**: **Community Data License Agreement - Permissive - Version 1.0 (CDLA-Permissive-1.0)**.
- **BigEarthNet v2.0 (reBEN) Dataset License**: **Creative Commons Attribution 4.0 International (CC BY 4.0)**.
- **Pretrained Checkpoint License**: **`Requires verification`** *(No specific checkpoint selected yet)*.
- **Codebase License**: **MIT License / Apache 2.0** (Official TU Berlin pipeline repository).

---

## 8. Hardware & Storage Requirements (`ESTIMATED`)

- **Full BigEarthNet-MM Storage Requirement**: ~150 GB compressed / ~250 GB uncompressed GeoTIFF rasters (`Estimated`).
- **1,000-Patch Subset Storage Requirement**: ~250 MB (`Estimated`).
- **RAM / Memory Footprint**: Single patch lazy loading requires <10 MB per sample (`Estimated`).

---

## 9. Dataset Loader Implementation & Test Verification

A modular dataset loader was implemented at [`backend/scientific/datasets/bigearthnet.py`](file:///e:/SatQuery%20AI/backend/scientific/datasets/bigearthnet.py).

### 9.1 Implementation Details
- **Supported Formats**: Reads `.tif` image files via PIL, `.npy` arrays via NumPy, and `_labels_metadata.json` metadata files via JSON parser.
- **Dual Mode**: Works as a standalone NumPy dataset iterable; compatible with PyTorch `Dataset` interface (`__len__`, `__getitem__`) if PyTorch is installed.
- **Error Handling**: Handles missing image files (filling zeros in non-strict mode, raising `FileNotFoundError` in strict mode) and corrupt JSON metadata (logging warnings in non-strict mode, raising `ValueError` in strict mode).
- **Synthetic Fixture Builder**: Includes `BigEarthNetDataset.create_synthetic_fixture()` to generate synthetic test directories.

### 9.2 Verification Status
- **Testing Scope**: **`TESTED WITH SYNTHETIC FIXTURES ONLY`**
- **Real-Data Verification**: **`NOT TESTED WITH REAL BIGEARTHNET DATA`** *(Real dataset compatibility remains an unverified assumption until real archives are inspected)*.

---

## 10. Automated Unit Test Results

Unit tests were executed via pytest:

```cmd
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD="1"; pytest backend/tests/test_bigearthnet_dataset.py -v
```
- **Dataset Loader Tests**: **5 passed in 1.07s**.
- **Full Backend Test Suite**: **46 passed, 4 warnings in 68.80s**.
- **Data Source**: **Synthetic Fixture Data Only** *(0 real BigEarthNet files used)*.

---

## 11. Known Risks & Limitations

1. **Real Dataset Format Unverified**: The loader assumes standard GeoTIFF/JSON directory layouts which have not been verified against live BigEarthNet v2.0 archives.
2. **Resampling Not Implemented**: On-the-fly band resampling for Sentinel-2 20m/60m bands is not implemented in the loader.
3. **Real Data Unavailable**: No real satellite rasters exist locally in the project workspace.

---

## 12. Next Steps & Phase 3 Scope (Gemini Baseline VQA Inference)

In accordance with official project protocols, Member 3 will begin **Phase 3 — Gemini Baseline VQA Inference and Evaluation**.

### 12.1 Immediate Phase 3 Priorities
1. **Gemini Baseline VQA Inference**: Execute baseline visual question answering using Google Gemini 1.5 Flash via `GeminiAdapter`.
2. **Standardized VQA Output Validation**: Enforce return payload contracts (`answer`, `evidence`, `confidence`, `is_error`).
3. **Baseline Prompt Testing**: Benchmark domain prompt templates on remote sensing single-image VQA and scene captioning tasks.
4. **Baseline Evaluation Design**: Establish qualitative and quantitative evaluation criteria for VQA responses.
5. **Model Version & Metadata Tracking**: Log active model version (`gemini-1.5-flash`), provider, and parameter settings.
6. **Runtime & Failure Logging**: Ensure robust exception handling, quota error handling, and latency logging.
7. **Evidence & Confidence Handling**: Integrate Lane C verification checks with VQA output confidence scores.
8. **Adapter Compatibility**: Maintain 100% compatibility with `BaseVLMAdapter` and `get_active_vlm_adapter()`.
9. **Zero Heavy Downloads**: Execute Phase 3 using the cloud Gemini API without downloading heavy model weights.

### 12.2 Explicit Exclusions for Phase 3 Start
- **No Qwen Fine-Tuning or Weight Downloads**
- **No LoRA / PEFT Implementation**
- **No Full BigEarthNet Training**
- **No Grounding Token Parser Implementation**
- **No Change-VQA Implementation**
- **Gemini remains the active default provider**
