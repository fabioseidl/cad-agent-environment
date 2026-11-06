# Example Wall Bracket

Status: complete (reference example)

## Brief
A right-angle shelf bracket that screws to a wall with four M5 screws and
carries a 70 mm deep shelf, 60 mm wide. Screw heads must not stand proud of
the front face. 3D printed in PLA, laid on its back so no supports are
needed.

This project exists as a worked example of the repository's conventions. It
was not requested by a user, so the "source" column below says `example`
where a real project would name a measurement.

## Source material
No photos; the geometry is defined entirely by the brief.

| File | What it shows | Measurements taken from it |
| ---- | ------------- | -------------------------- |
| -    | -             | -                          |

## Dimensions

| Parameter | Value (mm) | Source | Confidence |
| --------- | ---------- | ------ | ---------- |
| `WIDTH` | 60 | example | - |
| `WALL_PLATE_H` | 80 | example | - |
| `SHELF_DEPTH` | 70 | example | - |
| `THICKNESS` | 6 | design-rules.md: structural FDM wall | assumption |
| `GUSSET_T` | 5 | design-rules.md | assumption |
| `SCREW_D` | 5.5 | M5 clearance hole, design-rules.md | standard |
| `SCREW_HEAD_D` | 10 | M5 socket cap head 8.5 mm + counterbore allowance | standard |
| `SCREW_HEAD_H` | 3 | counterbore depth, head sits below the surface | standard |
| `WALL_HOLE_SPACING` | 36 | example | - |
| `WALL_HOLE_Z` | 22, 58 | example | - |
| `EDGE_FILLET` | 3 | cosmetic | assumption |
| `INNER_FILLET` | 4 | stress relief at the internal corner | assumption |

## Assumptions and open questions
- PLA at 1.24 g/cm^3 for the mass estimate; the part is not load-rated.
- Screws are M5 socket cap. Countersunk heads would need `CounterSinkHole`.

## Design decisions
- Coordinate convention: the wall surface is the plane `y = 0`, the bracket
  occupies `y >= 0`, and the shelf underside is `z = 0`.
- The gusset is centred on the width rather than doubled at the edges: one
  rib prints without supports in this orientation.
- The inside corner is filleted (`INNER_FILLET`) because a sharp internal
  corner is where this part would crack under load.
- Counterbores are placed with `Plane.back.offset(THICKNESS)`: holes are
  drilled along a plane's negative normal, so the plane must sit on the face
  where the screw enters with its normal pointing outwards.

## Results
Built at 60 x 70 x 80 mm, 60 330 mm^3, approximately 74.8 g in PLA, one
watertight solid. All six spec checks pass.

## Changelog
- Initial example.
