"""Example Wall Bracket - build123d model.

A right-angle shelf bracket: a vertical wall plate that screws to a wall, a
horizontal shelf plate, and a triangular gusset stiffening the corner.

This project is the worked reference for the patterns described in
.agents/skills/build123d-modeling: every driving dimension in one block,
geometry built from sketches on named planes, holes placed with Locations,
and acceptance criteria encoded in spec.yaml.

Coordinate convention used here:
  * the wall surface is the plane y = 0, the bracket occupies y >= 0
  * the wall plate is y in [0, THICKNESS]; its front face is y = THICKNESS
  * the shelf plate is z in [0, THICKNESS] and extends to y = SHELF_DEPTH

Build with:  .agents/tools/cad build example-wall-bracket
"""

from build123d import *  # noqa: F403

# --- parameters (millimetres) -----------------------------------------------
WIDTH = 60.0           # common width of both plates (along X)
WALL_PLATE_H = 80.0    # vertical plate height (along Z)
SHELF_DEPTH = 70.0     # horizontal plate depth (along Y)
THICKNESS = 6.0        # plate thickness
GUSSET_T = 5.0         # thickness of the triangular rib

SCREW_D = 5.5          # clearance hole for an M5 screw
SCREW_HEAD_D = 10.0    # counterbore diameter
SCREW_HEAD_H = 3.0     # counterbore depth
WALL_HOLE_SPACING = 36.0    # between the two columns of wall holes (along X)
WALL_HOLE_Z = (22.0, 58.0)  # hole heights on the wall plate
SHELF_HOLE_Y = 50.0    # distance from the wall to the shelf holes
SHELF_HOLE_X = 15.0    # half-spacing of the shelf holes

EDGE_FILLET = 3.0      # rounding of the free outer corners
INNER_FILLET = 4.0     # rounding of the inside corner between the plates


def build():
    with BuildPart() as bracket:
        # Vertical wall plate. Plane.XZ points at -Y, so a negative extrusion
        # grows the plate into +Y, away from the wall at y = 0.
        with BuildSketch(Plane.XZ) as wall_sketch:
            Rectangle(WIDTH, WALL_PLATE_H, align=(Align.CENTER, Align.MIN))
            fillet(wall_sketch.vertices().sort_by(Axis.Y)[-2:], EDGE_FILLET)
        extrude(amount=-THICKNESS)

        # Horizontal shelf plate.
        with BuildSketch(Plane.XY) as shelf_sketch:
            Rectangle(WIDTH, SHELF_DEPTH, align=(Align.CENTER, Align.MIN))
            fillet(shelf_sketch.vertices().sort_by(Axis.Y)[-2:], EDGE_FILLET)
        extrude(amount=THICKNESS)

        # Triangular gusset, centred on the width. On Plane.YZ the sketch
        # coordinates are (y, z), so the right angle sits on the inside corner.
        with BuildSketch(Plane.YZ):
            with BuildLine():
                Polyline(
                    (THICKNESS, THICKNESS),
                    (SHELF_DEPTH - 2 * EDGE_FILLET, THICKNESS),
                    (THICKNESS, WALL_PLATE_H - 2 * EDGE_FILLET),
                    close=True,
                )
            make_face()
        extrude(amount=GUSSET_T / 2, both=True)

        # Round the inside corner where the two plates meet.
        inner_edges = (
            bracket.edges()
            .filter_by(Axis.X)
            .filter_by(
                lambda e: abs(e.center().Y - THICKNESS) < 1e-6
                and abs(e.center().Z - THICKNESS) < 1e-6
            )
        )
        if inner_edges:
            fillet(inner_edges, INNER_FILLET)

        # Counterbored screw holes through the wall plate. Holes are drilled
        # along the negative normal of their workplane, so the plane must be
        # the front face with its normal pointing away from the material:
        # Plane.back (normal +Y) offset to y = THICKNESS. Its local axes are
        # (-X, Z); the hole pattern is symmetric in X so the mirrored X axis
        # makes no difference here.
        front_face = Plane.back.offset(THICKNESS)
        with Locations(front_face):
            with Locations(
                *[
                    (x, z)
                    for x in (-WALL_HOLE_SPACING / 2, WALL_HOLE_SPACING / 2)
                    for z in WALL_HOLE_Z
                ]
            ):
                CounterBoreHole(
                    radius=SCREW_D / 2,
                    counter_bore_radius=SCREW_HEAD_D / 2,
                    counter_bore_depth=SCREW_HEAD_H,
                    depth=THICKNESS,
                )

        # Plain through holes in the shelf for fixing whatever sits on it.
        with Locations(Plane.XY.offset(THICKNESS)):
            with Locations((-SHELF_HOLE_X, SHELF_HOLE_Y), (SHELF_HOLE_X, SHELF_HOLE_Y)):
                Hole(radius=SCREW_D / 2)

    result = bracket.part
    result.label = "wall-bracket"
    return result


if __name__ == "__main__":
    part = build()
    print(part.bounding_box(), part.volume)
