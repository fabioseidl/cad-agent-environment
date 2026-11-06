# build123d pitfalls

Behaviours verified against build123d 0.13. Each one has cost real debugging
time; check here before guessing.

## `Hole(radius, depth=d)` cuts `2*d`, centred on the workplane

With an explicit `depth`, `Hole` builds a cylinder of length `2*depth` aligned
on its centre, so it removes material `depth` in **both** directions from the
workplane. Omit `depth` for a true through hole:

```python
Hole(radius=2.75)                 # through the part - what you usually want
Hole(radius=2.75, depth=5)        # blind hole, but also cuts 5 mm backwards
```

`CounterBoreHole` and `CounterSinkHole` do not do this: their bore runs from
the workplane along the negative local Z for `depth`, and the recess occupies
the first `counter_bore_depth` of material.

## Holes are drilled along the negative plane normal

Pick the plane so that its normal points **out of** the material at the face
where the hole starts. Normals of the named planes:

| Plane | Normal | Local (u, v) axes |
| ----- | ------ | ----------------- |
| `Plane.XY` / `Plane.top` | +Z | (X, Y) |
| `Plane.XZ` / `Plane.front` | **-Y** | (X, Z) |
| `Plane.YZ` / `Plane.right` | +X | (Y, Z) |
| `Plane.back` | +Y | (-X, Z) |
| `Plane.bottom` | -Z | (X, -Y) |

`Plane.reverse()` flips the normal, and necessarily flips one in-plane axis
with it — coordinates on a reversed plane are mirrored. Prefer an already
named plane (`Plane.back` instead of `Plane.XZ.reverse()`) and state in a
comment which in-plane axis is mirrored.

`Plane.offset(d)` moves the plane `d` along its own normal, not along +Z.

## `extrude(amount=...)` follows the plane normal

On `Plane.XZ` a positive amount grows towards **-Y**. If a part ends up on the
wrong side of the origin, this is why. Use a negative amount, or `both=True`
for symmetric extrusion.

## Properties, not methods

`shape.volume`, `shape.area`, `shape.is_valid`, `shape.is_manifold` are
properties. `shape.is_valid()` raises `TypeError: 'bool' object is not
callable`. `shape.center(CenterOf.MASS)` and `shape.bounding_box()` *are*
methods.

## `Vector.to_tuple()` no longer exists

Removed in 0.13. Use `tuple(vector)`, or `vector.X / .Y / .Z`. Older examples
found online still use `to_tuple()`.

## Fillet and chamfer are the most fragile operations

```
ValueError: Failed creating a fillet with radius of 6, try a smaller value
or use max_fillet() to find the largest valid fillet radius
```

A fillet fails when the radius exceeds the available material, or when the
selected edges meet in a way OpenCASCADE cannot resolve. Remedies, in order:

1. Reduce the radius (`solid.max_fillet(edge_list)` reports the largest that
   works — it is iterative and slow, so use it while debugging, not in the
   final model).
2. Fillet fewer edges per call, grouping by region.
3. Fillet before cutting holes through the filleted region, not after.
4. Drop the fillet on the edges that genuinely have no room.

Never silently reduce a radius the user specified — report it instead.

## Index-based selection breaks under parameter changes

`part.faces()[3]` is meaningless after the geometry changes. Select by
property: `filter_by(Axis.Z)`, `group_by(Axis.Z)[0]`, `sort_by(SortBy.AREA)`,
or a lambda on position. Assert what you selected when it matters:

```python
top = part.faces().filter_by(Plane.XY).sort_by(Axis.Z)[-1]
assert abs(top.center().Z - HEIGHT) < 1e-6, "top face selector drifted"
```

## Several solids where one was intended

`cad build` warns when a part contains more than one solid. Usual causes: a
boolean that missed, two bodies that only touch (contact is not a fusion), or
a feature placed outside the body. A model with disjoint solids will not
slice; fix the geometry rather than exporting it.

Shapes that only touch at a face stay separate inside a `Compound`, but
`Part() + [a, b]` fuses them into one valid solid.

## Mesh export tolerance

STL/3MF/glTF are tessellations. `cad build --mesh-tolerance` sets the chord
deviation in mm (default 0.05). 0.05 is right for printed parts; use 0.01 for
small curved features and 0.1-0.2 for large, mostly flat parts where file size
matters. The STEP file is exact and unaffected.

## SVG colours

`ExportSVG` deprecated 0-255 RGB tuples; pass a colour name (`"black"`), a
normalized tuple or a hex integer. `cad views` already does this.

## Text needs fonts

`Text()` resolves fonts through fontconfig, whose default is `Arial`. The
container only installs `fonts-dejavu-core`, and fontconfig **substitutes a
different font silently** rather than failing - so text built with the default
has different glyph widths than intended, and engraved text can come out a
different size. Pass `font="DejaVu Sans"` (or an explicit `font_path=`) and
measure the resulting bounding box.

## The container has no network

`cad` runs with `--network none`. Model scripts cannot download anything; put
reference geometry in `projects/<project>/reference/` and import it from disk.
