# Phase 9: AI Anomaly Detection Report (Isolation Forest)

This report details the unsupervised Machine Learning analysis conducted on the 2,734 3D building entities in Bengaluru Urban, strictly following **Project Rule 5** (*AI assists; it does not adjudicate legal rights*).

## 1. Model Configuration
- **Algorithm**: `sklearn.ensemble.IsolationForest`
- **Contamination Parameter**: `0.03` (Top 3% spatial/vertical outliers)
- **Feature Matrix Inputs**:
  1. `parcel_overlap_ratio` (2D Spatial Boundary Intersection)
  2. `building_height_m` (Satellite Height)
  3. `ground_elevation_m` (Copernicus DEM Terrain)
  4. `derived_floors` (Multi-Storey Count)

## 2. Detection Results
- **Total Buildings Evaluated**: 2734
- **Normal Inliers**: 2652
- **AI Anomaly Flags Raised**: 82 (3.00%)

## 3. Sample Flagged Spatial/Vertical Conflicts
| Building ID | Linked Parcel | 2D Match Status | Height | Overlap | AI Anomaly Score |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `osm_way_130829155` | `cadastral_parcel_22068` | `CONTAINED` | 6.47m | 1.0 | `-0.0407` |
| `osm_way_147860504` | `cadastral_parcel_22460` | `CONTAINED` | 2.56m | 1.0 | `-0.0135` |
| `osm_way_147860505` | `cadastral_parcel_22459` | `BOUNDARY_OVERLAP` | Nonem | 0.4699 | `-0.0565` |
| `osm_way_347187488` | `cadastral_parcel_22276` | `BOUNDARY_OVERLAP` | Nonem | 0.4572 | `-0.0402` |
| `osm_way_347187505` | `cadastral_parcel_22074` | `MAJORITY` | Nonem | 0.5109 | `-0.0307` |
| `osm_way_347187537` | `cadastral_parcel_22072` | `BOUNDARY_OVERLAP` | Nonem | 0.49 | `-0.0207` |
| `osm_way_347187643` | `cadastral_parcel_22066` | `CONTAINED` | Nonem | 0.9872 | `-0.0334` |
| `osm_way_347187949` | `cadastral_parcel_22079` | `MAJORITY` | Nonem | 0.7118 | `-0.0011` |
| `osm_way_347187955` | `cadastral_parcel_22276` | `MAJORITY` | Nonem | 0.5254 | `-0.0031` |
| `osm_way_347188035` | `cadastral_parcel_22274` | `MAJORITY` | 2.69m | 0.6153 | `-0.0367` |

**Output File**: `data/processed/buildings_ai_analyzed.geojson`
