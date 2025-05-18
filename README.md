# 🛰️ POI GeoValidation 
This repository contains a **modular AI-based pipeline** that validates **Points of Interest (POIs)** using satellite imagery and geospatial metadata. The system combines rule-based geometry validation with satellite-based deep learning to identify possible misplacements or mismatches in POI data.

---

## 🛠️ Requirements

Make sure you have Python ≥ 3.8 and the following packages installed:

- pandas
- geopandas
- shapely
- open_clip_pytorch
- torch
- ultralytics (for YOLOv8)
- opencv-python
- geopy
- Pillow
- tqdm
- rasterio

### 1. Extract POIs

Run `findPOI.py` to extract POIs from your input trail dataset:

```bash python findPOI.py ```

### 2. Refine POI Coordinates
geo_utils.py is used internally by other scripts to calculate precise POI coordinates along the trail geometry. No manual execution needed.

### 3. Get POI images
```bash python SATELITAL_IMAGES_FILE.py ```

### 4. Run the notebook in this Github, changing configuration and adjusting paths as needed
It requires certain folders with your data to be named specifically, so make sure of it before running

## Output
Two Excel files with the reports

