"""2D orthographic technical views (SVG / DXF) with hidden-line removal.

Uses build123d's ``project_to_viewport`` (OpenCASCADE HLR) so the output is
real projected geometry, not a raster of a 3D render - suitable for drawings,
laser cutting and dimensioning.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

# name -> (direction the camera sits in, viewport up vector)
# The camera is placed along `direction` from the shape centre.
ORTHO_VIEWS: dict[str, tuple[tuple[float, float, float], tuple[float, float, float]]] = {
    "front":  ((0, -1, 0), (0, 0, 1)),
    "back":   ((0, 1, 0),  (0, 0, 1)),
    "right":  ((1, 0, 0),  (0, 0, 1)),
    "left":   ((-1, 0, 0), (0, 0, 1)),
    "top":    ((0, 0, 1),  (0, 1, 0)),
    "bottom": ((0, 0, -1), (0, 1, 0)),
    "iso":    ((1, -1, 1), (0, 0, 1)),
}

DEFAULT_VIEWS = ("front", "top", "right", "iso")


def _projected_edges(shape: Any, view: str):
    from build123d import Vector

    direction, up = ORTHO_VIEWS[view]
    bbox = shape.bounding_box()
    centre = bbox.center()
    # Far enough away that the perspective term is negligible.
    distance = max(float(bbox.diagonal), 1.0) * 100.0
    origin = centre + Vector(direction).normalized() * distance
    return shape.project_to_viewport(
        viewport_origin=origin,
        viewport_up=up,
        look_at=centre,
    )


def export_views(
    shape: Any,
    out_dir: Path,
    basename: str,
    views: Sequence[str] = DEFAULT_VIEWS,
    *,
    fmt: str = "svg",
    hidden_lines: bool = True,
    line_weight: float = 0.25,
    margin: float = 5.0,
) -> dict[str, str]:
    """Write one 2D drawing file per view. Returns {view name: file path}.

    ``fmt`` is "svg" (viewable, good for documentation) or "dxf" (for CAM,
    laser cutters and other CAD packages).
    """
    unknown = [v for v in views if v not in ORTHO_VIEWS]
    if unknown:
        raise ValueError(f"unknown view(s) {unknown}; known: {', '.join(ORTHO_VIEWS)}")
    fmt = fmt.lower()
    if fmt not in ("svg", "dxf"):
        raise ValueError(f"unknown drawing format {fmt!r}; use 'svg' or 'dxf'")

    from build123d import ExportDXF, ExportSVG, LineType

    out_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, str] = {}

    for view in views:
        visible, hidden = _projected_edges(shape, view)
        target = out_dir / f"{basename}_{view}.{fmt}"

        if fmt == "svg":
            exporter = ExportSVG(margin=margin, line_weight=line_weight)
            exporter.add_layer("visible", line_color="black", line_weight=line_weight)
            exporter.add_shape(visible, layer="visible")
            if hidden_lines and hidden:
                exporter.add_layer(
                    "hidden",
                    line_color="gray",
                    line_weight=line_weight * 0.6,
                    line_type=LineType.ISO_DASH_SPACE,
                )
                exporter.add_shape(hidden, layer="hidden")
        else:
            exporter = ExportDXF(line_weight=line_weight)
            exporter.add_layer("visible")
            exporter.add_shape(visible, layer="visible")
            if hidden_lines and hidden:
                exporter.add_layer("hidden", line_type=LineType.ISO_DASH_SPACE)
                exporter.add_shape(hidden, layer="hidden")

        exporter.write(target)
        written[view] = str(target)

    return written
