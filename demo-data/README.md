# SatQuery AI - Demo Dataset Instructions

This directory contains sample remote-sensing imagery used for Quick Demo Mode in presentation and evaluation settings.

## 📁 Required Directory Layout & File Names

Place your satellite images (PNG, JPG, JPEG, TIFF, GeoTIFF) in the following directories:

```
demo-data/
├── single/
│   └── sample.png            # Single scene satellite image (Optical / Multispectral / SAR)
├── temporal/
│   ├── before/
│   │   └── sample.png        # Bi-temporal T1 (Before) scene
│   └── after/
│       └── sample.png        # Bi-temporal T2 (After) scene
└── optical-sar/
    ├── optical/
    │   └── sample.png        # Optical / Multispectral scene (e.g., Sentinel-2 L2A)
    └── sar/
        └── sample.png        # SAR scene (e.g., Sentinel-1 GRD IW)
```

## 🛰️ Recommended Satellite Data Sources

- **Sentinel-2 L2A (Optical)**: Copernicus Open Access Hub / AWS Sentinel-2
- **Sentinel-1 GRD (SAR)**: Copernicus Open Access Hub / ASF Data Search
- **Landsat 8/9**: USGS EarthExplorer
- **VRSBench / RSVQA / CDVQA**: Benchmark datasets for Remote Sensing VQA
