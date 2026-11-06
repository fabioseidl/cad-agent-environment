---
name: build123d-modeling
description: Write, debug and verify parametric 3D CAD models with build123d (Python/OpenCASCADE) in this repository. Use whenever a task involves creating or changing a part, a 3D-printable object, an STL/STEP/3MF file, a bracket, enclosure, adapter, jig or any physical object described by measurements, photos or sketches. Covers the builder and algebra APIs, selectors, the cad CLI, and the failure modes that cost the most time.
---

# Modelling with build123d

build123d 0.13 on OpenCASCADE, running in the container defined by
`docker/Dockerfile`. All geometry is in **millimetres** and degrees.

## Run everything through the CLI

Never hand-roll an export or measuring script; `.agents/tools/cad` already does
it and prints a compact summary.

```bash
.agents/tools/cad new <project>        # scaffold projects/<project>/
.agents/tools/cad build <project>      # export + measure + render + check
.agents/tools/cad measure <project>    # metrics only, no files written
.agents/tools/cad preview <project>    # shaded PNGs you can look at
.agents/tools/cad views <project>      # 2D orthographic SVG/DXF with hidden lines
.agents/tools/cad check <project>      # spec.yaml acceptance checks; exit 2 on failure
.agents/tools/cad run <script.py>      # one-off script in the CAD environment
.agents/tools/cad doctor               # verify the toolchain
```

`cad build` writes `projects/<project>/output/report.json` with every
measurement, so you never need to re-measure by hand.

**After any geometry change, look at the render.** Read
`projects/<project>/output/preview/<name>_views.png` — one image with four
views. Numbers passing `cad check` does not mean the shape is right.

## The model contract

`projects/<project>/model.py` defines `build()` returning:

* a single build123d `Shape` (the usual case), or
* `dict[str, Shape]` for an assembly — one exported file per key, plus a
  combined `<project>-assembly.step` and render.

Keep every driving dimension in one uppercase parameter block at the top. If a
value came from the user, it belongs there with a comment naming its source.

## Two APIs, one library

**Builder mode** (stateful context managers) — use it for parts with several
features, which is nearly always:

```python
from build123d import *

with BuildPart() as part:
    with BuildSketch(Plane.XY) as profile:
        Rectangle(60, 40)
        fillet(profile.vertices(), 5)
    extrude(amount=12)
    with Locations((-20, 0), (20, 0)):
        Hole(radius=2.5)                 # no depth -> through the part
    fillet(part.edges().filter_by(Axis.Z), 2)
result = part.part
```

**Algebra mode** (operators on objects) — use it for short, composable logic:

```python
body = Box(60, 40, 12) - Pos(20, 0, 0) * Cylinder(2.5, 12)
```

Mixing them in one file is fine; do not mix them inside one feature.

## Selectors

Feature selection is where models break when a dimension changes. Prefer
filters that stay true under parameter changes over index positions.

```python
part.faces().sort_by(Axis.Z)[-1]                 # topmost face
part.edges().filter_by(Axis.Z)                   # all vertical edges
part.edges().filter_by(GeomType.CIRCLE)          # circular edges
part.faces().filter_by(Plane.XY)                 # faces parallel to XY
part.edges().group_by(Axis.Z)[0]                 # all edges at the lowest Z
part.edges().filter_by(lambda e: e.length > 20)  # arbitrary predicate
```

`sort_by` also takes `SortBy.LENGTH | AREA | VOLUME | RADIUS | DISTANCE`.

## Working through a change

1. Edit the parameter block or geometry in `model.py`.
2. `.agents/tools/cad build <project>` — it fails loudly on invalid geometry.
3. Read the contact-sheet PNG.
4. Fix `spec.yaml` checks if the intended dimensions changed; never loosen a
   check just to make it pass.

## References

Load these only when you need them:

* `references/api-cheatsheet.md` — verified names and signatures for objects,
  operations, selectors, planes and locations.
* `references/pitfalls.md` — the failure modes that actually occur:
  `Hole(depth=...)` cutting both ways, plane orientation and `reverse()`,
  fillet radius failures, non-manifold results, tolerance choices.
* `references/design-rules.md` — clearances, wall thicknesses, thread and
  fastener sizes, 3D-printing constraints.

Worked example: `projects/example-wall-bracket/` (model, spec, README).

Upstream documentation: https://build123d.readthedocs.io/en/latest/ — the
container has no network access, so check the installed package instead:
`.agents/tools/cad run` a script that uses `help()` or `inspect.signature`.
