# Design rules and standard dimensions

Engineering defaults for parts produced in this repo. They are starting
points, not laws: if the user gives a number, the user's number wins, and any
value taken from this file must be recorded in the project README as an
assumption.

## Fastener clearance holes (ISO metric, medium fit)

| Screw | Clearance hole | Tapping hole (into plastic/alu) | Head dia (socket cap) | Nut across flats |
| ----- | -------------- | ------------------------------- | --------------------- | ---------------- |
| M2    | 2.4 mm | 1.6 mm | 3.8 mm | 4.0 mm |
| M2.5  | 2.9 mm | 2.1 mm | 4.5 mm | 5.0 mm |
| M3    | 3.4 mm | 2.5 mm | 5.5 mm | 5.5 mm |
| M4    | 4.5 mm | 3.3 mm | 7.0 mm | 7.0 mm |
| M5    | 5.5 mm | 4.2 mm | 8.5 mm | 8.0 mm |
| M6    | 6.6 mm | 5.0 mm | 10.0 mm | 10.0 mm |
| M8    | 9.0 mm | 6.8 mm | 13.0 mm | 13.0 mm |

Counterbore for a socket cap head: diameter = head diameter + 0.5 mm,
depth = head height + 0.2 mm (head height is approximately the thread
diameter: 3 mm for M3, 5 mm for M5).

Hex nut pockets: add 0.2-0.3 mm to the across-flats dimension for a press
fit, 0.4-0.5 mm for a drop-in fit.

## Fits and clearances (FDM printed parts)

| Fit | Gap per side | Use |
| --- | ------------ | --- |
| Press / interference | 0.0 to -0.05 mm | parts assembled with force, permanent |
| Snug sliding | 0.1-0.15 mm | lids, drawers, parts that must not rattle |
| Free running | 0.2-0.3 mm | hinges, shafts, anything that rotates |
| Loose / tolerant | 0.4-0.5 mm | over printed threads, warped surfaces, large spans |

Holes print undersized on FDM printers. For a hole that must accept a 5 mm
shaft, model 5.2-5.4 mm, or plan to drill it.

## Wall thickness and features

* FDM minimum wall: 2 x nozzle diameter, so 0.8 mm with a 0.4 mm nozzle;
  1.6-2.4 mm for anything structural.
* Minimum feature that prints reliably: 1 mm. Text engraved 0.4-0.6 mm deep,
  embossed 0.4-0.8 mm, minimum stroke 0.8 mm.
* Overhangs steeper than 45 degrees from vertical need support; add a chamfer
  at the base of a hole or an overhanging edge instead.
* Bridge unsupported spans up to about 50 mm, shorter over curved features.
* First-layer elephant foot: chamfer the bottom edge 0.4-0.6 mm on parts
  whose outside dimension must be accurate.
* Keep a fillet at every internal corner that carries load; a sharp internal
  corner is where a part cracks.

## Sheet material and laser cutting

* Kerf allowance: 0.1-0.2 mm per cut side for a CO2 laser on plywood or
  acrylic; subtract it from slot widths for a press fit.
* Finger joints: finger length equal to material thickness.
* Export 2D geometry with `cad views --format dxf`.

## Common real-world dimensions

| Thing | Dimension |
| ----- | --------- |
| Credit card | 85.60 x 53.98 x 0.76 mm |
| AA battery | 14.5 dia x 50.5 mm |
| AAA battery | 10.5 dia x 44.5 mm |
| 18650 cell | 18.4 dia x 65.2 mm |
| USB-C receptacle opening | 9.0 x 3.2 mm |
| Raspberry Pi 4/5 board | 85 x 56 mm, holes 58 x 49 mm apart, 2.7 mm dia, 3.5 mm from edges |
| Arduino Uno board | 68.6 x 53.3 mm |
| 2020 aluminium extrusion | 20 x 20 mm, 6 mm slot, M5 fasteners |
| DIN rail (TS35) | 35 mm wide, 7.5 mm deep |
| Standard brick | 215 x 102.5 x 65 mm (UK), 194 x 92 x 57 mm (US modular) |

Verify any of these against the user's actual hardware before relying on it.

## Orientation convention for this repo

Unless the brief says otherwise:

* Z is up, and the part sits with its print/mounting face on `z = 0`.
* The largest flat face is the one on the build plate.
* Keep the part in the positive octant when it has a natural datum corner, or
  centred on the origin when it is symmetric.

State the convention chosen in the project README so later changes do not
silently move the datum.
