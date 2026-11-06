---
name: dimensions-from-media
description: Turn photos, hand sketches, screenshots, scanned drawings or a verbal description of an existing object into the dimension table that drives a CAD model. Use when the user supplies images of a part to reproduce, copy or make a fitting accessory for, or gives measurements that are incomplete, in mixed units, or ambiguous about what was measured. Covers scaling from a reference object, what to ask for, and how to record confidence.
---

# Getting dimensions out of photos and sketches

A photograph is evidence, not a measurement. The job of this step is to end
with a dimension table in `projects/<name>/README.md` where every number has a
stated source and confidence, so that later work does not treat a guess as a
fact.

## Record the source of every number

| Source | Confidence | How to treat it |
| ------ | ---------- | --------------- |
| Measured by the user with calipers | high (+/- 0.1 mm) | use directly |
| Measured by the user with a tape or ruler | medium (+/- 1 mm) | use, add clearance generously |
| From a datasheet or standard | high | cite the standard |
| Scaled from a photo with a reference object | low (+/- 5%) | use only for non-fitting dimensions |
| Inferred from proportion | very low | ask, or make the feature adjustable |
| Assumed from `design-rules.md` | by convention | state it as an assumption |

A low-confidence number on a **mating** dimension - anything that has to slot
into, screw onto or clamp around something - is not acceptable. Ask for that
one with calipers rather than modelling a part that will not fit.

## Reading a photo

1. Save the image into `projects/<name>/reference/` and look at it.
2. Describe the object back to the user in geometric terms: primitives,
   symmetry, how many distinct features. Getting this wrong is the expensive
   failure, and the user can correct it in one line.
3. Identify a scale reference in the frame. In descending order of
   usefulness: a ruler or caliper in the plane of the object; a coin or
   credit card lying flat on the object; a known fastener; a known part of
   the object itself.
4. Scale only within the plane of the reference. Perspective makes anything
   nearer or further from the camera a different scale; depth read off a
   single photo is a guess.
5. State the arithmetic in the README, e.g.
   `plate width = 3.1 x card width (85.6 mm) = 265 mm +/- 5%`.

Useful reference dimensions are in
`.agents/skills/build123d-modeling/references/design-rules.md`.

## What to ask the user for

Ask once, in a single message, naming the exact measurements:

* overall length, width and height;
* every dimension where the part meets something else (hole diameters and
  their centre-to-centre spacing, slot widths, shaft diameters, thread sizes);
* material thickness, measured somewhere flat;
* which face mounts, which side is visible, which way it is loaded.

Ask for better photos when it would settle the geometry: one straight-on shot
per face, with a ruler flat against the object in the same plane, taken from
far enough back that the lens does not bow the edges.

For a threaded feature, ask for the fastener rather than the hole: "M4
screw" is a usable answer; "about 4 mm hole" is not.

## Sketches and drawings

Hand sketches usually carry the right topology and unreliable proportions -
trust the annotated numbers, not the drawn lengths. On a scanned technical
drawing, check for a stated scale and a units note (mm vs inch) before using
any value, and watch for dimensions given to a centreline rather than an
edge.

## Units

Convert everything to millimetres in the model, but keep the user's original
figure in the README table. 1 in = 25.4 mm exactly. Fractional inches are
exact: 1/8" = 3.175 mm, 1/4" = 6.35 mm, 1/2" = 12.7 mm, 3/4" = 19.05 mm.
Nominal timber and pipe sizes are **not** their real dimensions - ask for the
measured value.

## Closing the loop

After the first build, send the user
`projects/<name>/output/preview/<name>_views.png` together with the dimension
table and ask them to confirm the numbers you were unsure about. A wrong
dimension caught at this point costs one parameter change.
