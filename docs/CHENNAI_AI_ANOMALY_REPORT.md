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
- **Total Buildings Evaluated**: 8611
- **Normal Inliers**: 8394
- **AI Anomaly Flags Raised**: 217 (2.52%)

## 3. Sample Flagged Spatial/Vertical Conflicts
| Building ID | Linked Parcel | 2D Match Status | Height | Overlap | AI Anomaly Score |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `drdo_bldg_4` | `synthetic_parcel_4` | `CONTAINED` | 15.0m | 1.0 | `-0.1057` |
| `drdo_bldg_93` | `synthetic_parcel_93` | `CONTAINED` | 17.0m | 1.0 | `-0.159` |
| `drdo_bldg_140` | `synthetic_parcel_140` | `CONTAINED` | 14.0m | 1.0 | `-0.0423` |
| `drdo_bldg_160` | `synthetic_parcel_160` | `CONTAINED` | 14.0m | 1.0 | `-0.0423` |
| `drdo_bldg_171` | `synthetic_parcel_171` | `CONTAINED` | 14.0m | 1.0 | `-0.0423` |
| `drdo_bldg_181` | `synthetic_parcel_181` | `CONTAINED` | 18.0m | 1.0 | `-0.1637` |
| `drdo_bldg_184` | `synthetic_parcel_184` | `CONTAINED` | 14.0m | 1.0 | `-0.0423` |
| `drdo_bldg_198` | `synthetic_parcel_198` | `CONTAINED` | 14.0m | 1.0 | `-0.0423` |
| `drdo_bldg_281` | `synthetic_parcel_281` | `CONTAINED` | 18.0m | 1.0 | `-0.1637` |
| `drdo_bldg_285` | `synthetic_parcel_285` | `CONTAINED` | 14.0m | 1.0 | `-0.0423` |

**Output File**: `data/processed/buildings_ai_analyzed.geojson`
