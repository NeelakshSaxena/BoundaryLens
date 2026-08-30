# 3D Reconstruction Skill

Input:
- parcel/building footprint
- ground elevation
- height evidence

MVP:
footprint + Z range → watertight extrusion.

Advanced:
point cloud/BIM → detailed mesh.

Validate:
- closed geometry
- no self-intersection
- correct containment
- valid Z range

Never convert uncertain height into a legal floor boundary without evidence.
