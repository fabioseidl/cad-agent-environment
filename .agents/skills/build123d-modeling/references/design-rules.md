# Design rules and standard dimensions

**How to read this file.** Each section is labelled either **[standard]** - the
value comes from a published standard or a manufacturer's own drawing, cited
inline - or **[rule of thumb]** - workshop practice with no standard behind
it, which varies by machine, material and operator.

A number from this file is never a substitute for a measurement. If the user
gave a dimension, the user's number wins. Anything taken from here must be
recorded in the project README as an assumption, with this file named as the
source.

## Fastener clearance holes - ISO 273 medium (H13) series **[standard]**

| Screw | Clearance hole |
| ----- | -------------- |
| M2    | 2.4 mm |
| M2.5  | 2.9 mm |
| M3    | 3.4 mm |
| M4    | 4.5 mm |
| M5    | 5.5 mm |
| M6    | 6.6 mm |
| M8    | 9.0 mm |

ISO 273 also defines a fine (H12) series - 2.2, 2.7, 3.2, 4.3, 5.3, 6.4,
8.4 mm - and a coarse (H14) series - 2.6, 3.1, 3.6, 4.8, 5.8, 7.0, 10.0 mm.
Note that M8 needs a 9.0 mm hole, not 8.0.

## Socket head cap screws - ISO 4762 / DIN 912 **[standard]**

| Screw | Head dia. (dk max) | Head height (k) | Hex key |
| ----- | ------------------ | --------------- | ------- |
| M2    | 3.8 mm | 2.0 mm | 1.5 mm |
| M2.5  | 4.5 mm | 2.5 mm | 2.0 mm |
| M3    | 5.5 mm | 3.0 mm | 2.5 mm |
| M4    | 7.0 mm | 4.0 mm | 3.0 mm |
| M5    | 8.5 mm | 5.0 mm | 4.0 mm |
| M6    | 10.0 mm | 6.0 mm | 5.0 mm |
| M8    | 13.0 mm | 8.0 mm | 6.0 mm |

Head height equals the nominal thread diameter for every size in this range.
These are maxima; minima are slightly smaller, which matters for a tight
counterbore.

## Hex nuts, width across flats - ISO 4032 **[standard]**

M2 4.0 · M2.5 5.0 · M3 5.5 · M4 7.0 · M5 8.0 · M6 10.0 · M8 13.0 mm (max;
minima are roughly 0.2 mm smaller).

## Tap drill, ISO metric coarse **[standard]**

Tap drill diameter = major diameter - pitch:

| Screw | Pitch | Tap drill |
| ----- | ----- | --------- |
| M2    | 0.40 | 1.60 mm |
| M2.5  | 0.45 | 2.05 mm |
| M3    | 0.50 | 2.50 mm |
| M4    | 0.70 | 3.30 mm |
| M5    | 0.80 | 4.20 mm |
| M6    | 1.00 | 5.00 mm |
| M8    | 1.25 | 6.75 mm |

These are the computed values; the nearest stocked drill is normally used
instead (6.8 mm for M8, for example). This is for cutting a thread in metal. Thread-forming screws into plastic
need a different hole - consult the screw manufacturer's data, which is
specific to the screw, not derivable from the thread size.

## Counterbores and nut pockets **[rule of thumb]**

* Counterbore diameter: head diameter + 0.5 mm.
* Counterbore depth: head height + 0.2 mm to sit flush, more to recess.
* Hex nut pocket: across-flats + 0.2 to 0.3 mm for a press fit, + 0.4 to
  0.5 mm to drop in.

## Fits and clearances, FDM printed parts **[rule of thumb]**

| Fit | Gap per side | Use |
| --- | ------------ | --- |
| Press / interference | 0 to -0.05 mm | assembled with force, permanent |
| Snug sliding | 0.1-0.15 mm | lids, drawers, parts that must not rattle |
| Free running | 0.2-0.3 mm | hinges, shafts, anything that rotates |
| Loose | 0.4-0.5 mm | printed threads, warped surfaces, long spans |

Holes print undersized on FDM machines. For a hole that must accept a 5 mm
shaft, model 5.2-5.4 mm, or plan to ream or drill it. The exact figure
depends on the printer, the material and the slicer, so print a test coupon
when the fit matters.

## Printing and sheet-work heuristics **[rule of thumb]**

* Minimum FDM wall: two extrusion widths, so about 0.8 mm with a 0.4 mm
  nozzle; 1.6-2.4 mm for anything structural.
* Smallest feature that prints reliably: about 1 mm. Engrave text 0.4-0.6 mm
  deep, emboss 0.4-0.8 mm, minimum stroke about 0.8 mm.
* Overhangs beyond roughly 45 degrees from vertical need support; a chamfer
  under an overhanging edge or hole usually avoids it.
* Chamfer the bottom edge 0.4-0.6 mm where an outside dimension must be
  accurate, to absorb first-layer squish.
* Fillet internal corners that carry load - a sharp internal corner is where
  the part cracks.
* Laser kerf: 0.1-0.2 mm per cut side on plywood or acrylic; subtract it from
  slot widths for a press fit. Measure it on your own machine.
* Finger joints: finger length equal to the material thickness.
* Export 2D geometry for cutting with `cad views --format dxf`.

## Reference dimensions **[standard, each cited]**

| Thing | Dimension | Source |
| ----- | --------- | ------ |
| ID-1 card (credit card) | 85.60 x 53.98 x 0.76 mm, corner radius 2.88-3.48 mm | ISO/IEC 7810 |
| DIN rail, top hat | 35 mm wide x 7.5 mm deep (a 35 x 15 mm version also exists) | EN/IEC 60715 |
| Raspberry Pi 5 board | 85 x 56 mm; four mounting holes ø2.7 mm on a 58 x 49 mm pattern, centres 3.5 mm from the edges | Raspberry Pi Ltd mechanical drawing RP-008347-DS |

The Raspberry Pi drawing carries its own warning: "All dimensions are
approximate and for reference purposes only. The dimensions shown should not
be used for producing production data." Treat the figures as a starting
point and check a physical board. The Pi 4 is widely reported to share the
58 x 49 mm pattern, but its official drawing was not readable when this file
was written, so that is unverified here.

Nothing else belongs in this table unless it has been checked against a
standard or a manufacturer drawing and cited. Measure the actual object
instead.

## Orientation convention for this repo **[convention]**

Unless the brief says otherwise:

* Z is up, and the part sits with its print or mounting face on `z = 0`.
* The largest flat face goes on the build plate.
* Keep the part in the positive octant when it has a natural datum corner, or
  centred on the origin when it is symmetric.

State the convention chosen in the project README so later edits do not
silently move the datum.
