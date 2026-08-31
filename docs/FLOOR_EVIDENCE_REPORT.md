# Phase 8: Floor Evidence Extraction Report

This report documents the extraction of 3D multi-storey floor entities linking physical structures to cadastral parcels in Bengaluru Urban.

## 1. Summary Statistics
- **Total Buildings Analyzed**: 2734
- **Total Discrete Floor Entities Extracted**: 0
- **Average Floors per Building**: 0.00

## 2. Floor Count Distribution
| Floor Count | Building Count | Percentage |
| :--- | :--- | :--- |

## 3. Data Provenance & Evidence Hierarchy (Rule 3)
| Source | Count | Confidence | Provenance Description |
| :--- | :--- | :--- | :--- |
| `NOT_DETERMINABLE` | 2734 | `MEDIUM` | Satellite ML height estimation (Google Open Buildings 2.5D) |

**Output Artefacts**:
- Floor Entities Database: `data/processed/floor_entities.json`
- Updated 3D Web UI Dataset: `frontend/data/buildings_3d.geojson`
