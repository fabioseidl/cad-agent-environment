# build123d 0.13 API cheat sheet

Every name below is verified against the installed package. Units are mm/degrees.

## Builders

| Builder | Produces | Typical contents |
| ------- | -------- | ---------------- |
| `BuildLine(workplane=Plane.XY)` | `.line` (`Curve`) | `Line`, `Polyline`, `Spline`, arcs |
| `BuildSketch(*workplanes)` | `.sketch` | `Rectangle`, `Circle`, `make_face()` |
| `BuildPart(*workplanes)` | `.part` | `Box`, `extrude`, `Hole`, `fillet` |

`BuildSketch` works in the local 2D coordinates of its workplane and projects
the result onto it. `BuildPart` operates in 3D.

## 3D objects (inside `BuildPart`, or standalone in algebra mode)

`Box(length, width, height)` · `Cylinder(radius, height)` ·
`Sphere(radius)` · `Cone(bottom_radius, top_radius, height)` ·
`Torus(major_radius, minor_radius)` · `Wedge(...)`

Holes (builder mode only): `Hole(radius, depth=None)` ·
`CounterBoreHole(radius, counter_bore_radius, counter_bore_depth, depth=None)` ·
`CounterSinkHole(radius, counter_sink_radius, depth=None, counter_sink_angle=82)`

## 2D objects (inside `BuildSketch`)

`Rectangle(width, height)` · `RectangleRounded(width, height, radius)` ·
`Circle(radius)` · `Ellipse(x_radius, y_radius)` · `Polygon(*pts)` ·
`RegularPolygon(radius, side_count)` · `Triangle(...)` · `Trapezoid(...)` ·
`SlotOverall(width, height)` · `SlotCenterToCenter(center_separation, height)` ·
`Text(txt, font_size)`

Most take `align=(Align.CENTER, Align.CENTER)`; `Align.MIN`/`MAX` place the
shape entirely on one side of the origin, which is usually what you want when
a datum matters.

## 1D objects (inside `BuildLine`)

`Line(pt1, pt2)` · `Polyline(*pts, close=False)` · `Spline(*pts)` ·
`CenterArc(center, radius, start_angle, arc_size)` ·
`RadiusArc(pt1, pt2, radius)` · `ThreePointArc(p1, p2, p3)` ·
`TangentArc(*pts, tangent=...)` · `JernArc(start, tangent, radius, arc_size)` ·
`Bezier(*cntl_pts)` · `FilletPolyline(*pts, radius=...)`

Close a profile and turn it into a face with `make_face()` inside `BuildSketch`.

## Operations

```python
extrude(to_extrude=None, amount=None, dir=None, until=None, target=None,
        both=False, taper=0.0, mode=Mode.ADD)
revolve(profiles=None, axis=Axis.Z, revolution_arc=360.0, mode=Mode.ADD)
loft(sections=None, ruled=False, mode=Mode.ADD)
sweep(sections=None, path=None, multisection=False, is_frenet=False, mode=Mode.ADD)
offset(objects=None, amount=0, openings=None, kind=Kind.ARC, mode=Mode.REPLACE)
fillet(objects, radius)
chamfer(objects, length, length2=None, angle=None, reference=None)
split(objects=None, bisect_by=Plane.YZ, keep=Keep.TOP)
mirror(objects=None, about=Plane.XZ, mode=Mode.ADD)
scale(objects=None, by=1, about=None, mode=Mode.REPLACE)
add(objects, mode=Mode.ADD)          # bring an external shape into a builder
make_face() / make_hull()            # close sketch geometry
project(...)                         # project geometry onto a plane/face
```

`mode=` is `Mode.ADD | SUBTRACT | INTERSECT | REPLACE | PRIVATE`.
`until=` is `Until.NEXT | LAST | FIRST | PREVIOUS` (needs `target=`).
`kind=` is `Kind.ARC | INTERSECTION | TANGENT`.

Hollowing a part: `offset(amount=-WALL, openings=<face or faces>)` inside
`BuildPart` — a negative amount shells inwards, `openings` names the faces to
leave open.

## Placement

```python
Locations((10, 0), (-10, 0))          # context: repeat the next object at each point
Locations(Plane.XY.offset(5))         # a plane as a location context
GridLocations(x_spacing, y_spacing, x_count, y_count)
PolarLocations(radius, count, start_angle=0)
HexLocations(radius, x_count, y_count)
Location((x, y, z), (rx, ry, rz))     # position + intrinsic XYZ rotation
Pos(x, y, z) * shape                  # algebra mode translation
Rot(rx, ry, rz) * shape               # algebra mode rotation
```

`Locations` nest: an outer plane context plus an inner point context is the
normal way to place holes on a face.

## Planes and axes

`Plane.XY`, `Plane.XZ`, `Plane.YZ`, `Plane.YX`, `Plane.ZX`, `Plane.ZY`,
`Plane.front`, `Plane.back`, `Plane.left`, `Plane.right`, `Plane.top`,
`Plane.bottom`, and `Plane(face)` to work on an existing face.

```python
Plane.XY.offset(10)        # move 10 mm along the plane normal
Plane.XZ.reverse()         # flip the normal (also flips the in-plane v axis)
Plane(origin=(0, 0, 5), x_dir=(1, 0, 0), z_dir=(0, 0, 1))
Axis.X / Axis.Y / Axis.Z / Axis((0, 0, 0), (1, 1, 0))
```

Normals of the named planes: `Plane.XY` -> +Z, `Plane.XZ` -> **-Y**,
`Plane.YZ` -> +X. On `Plane.XZ` the local axes are (X, Z); on `Plane.YZ` they
are (Y, Z).

## Selectors (`ShapeList`)

```python
.vertices() .edges() .wires() .faces() .shells() .solids()
.filter_by(Axis.Z | Plane.XY | GeomType.CIRCLE | callable)
.filter_by_position(Axis.Z, minimum, maximum)
.sort_by(Axis.Z | SortBy.LENGTH | SortBy.AREA | SortBy.VOLUME | SortBy.RADIUS)
.sort_by_distance(point)
.group_by(Axis.Z)      # list of lists, lowest group first
.first .last
```

`GeomType` includes `LINE`, `CIRCLE`, `ELLIPSE`, `BSPLINE`, `PLANE`,
`CYLINDER`, `CONE`, `SPHERE`, `TORUS`.

## Measuring a shape

```python
shape.bounding_box()        # BoundBox: .min .max .size .center() .diagonal
shape.volume                # mm^3   (property, not a method)
shape.area                  # mm^2
shape.center(CenterOf.MASS) # Vector; also CenterOf.BOUNDING_BOX
shape.is_valid              # property
shape.is_manifold           # property
tuple(vector)               # Vector -> (x, y, z); there is no .to_tuple() in 0.13
```

`.agents/tools/cad measure <project>` prints all of this already.

## Import / export

```python
export_step(shape, path)                     # B-Rep master
export_stl(shape, path, tolerance=0.001, angular_tolerance=0.1)
export_brep(shape, path)
export_gltf(shape, path, unit=Unit.MM, binary=False)
export_obj(shape, path)
Mesher(unit=Unit.MM).add_shape(shape); .write(path)     # 3MF
ExportSVG(...) / ExportDXF(...)   # 2D, with .add_layer() and .add_shape()
import_step(path) / import_stl(path) / import_svg(path) / import_dxf(path)
shape.project_to_viewport(viewport_origin, viewport_up, look_at)
    # -> (visible_edges, hidden_edges) for 2D drawings
```

Prefer `.agents/tools/cad build` and `cad views`, which wrap all of these.
