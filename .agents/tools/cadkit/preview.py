"""Headless shaded PNG previews, so the agent can actually look at the model.

Rendering goes through matplotlib's 3D axes on a tessellation of the B-Rep: no
GPU, no X server, no extra system packages beyond what OpenCASCADE already
needs. Quality is "good enough to spot a wrong feature", not photoreal.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Iterable, Sequence

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

# name -> (elevation, azimuth) for matplotlib's Z-up axes.
VIEWS: dict[str, tuple[float, float]] = {
    "iso": (24.0, -50.0),
    "front": (0.0, -90.0),   # looking along +Y, XZ plane
    "right": (0.0, 0.0),     # looking along -X, YZ plane
    "top": (89.9, -90.0),    # looking down -Z
    "back": (0.0, 90.0),
    "left": (0.0, 180.0),
    "bottom": (-89.9, -90.0),
}

DEFAULT_VIEWS = ("iso", "front", "right", "top")

_FACE_COLOR = (0.62, 0.70, 0.80)
_LIGHT_DIR = np.array([0.4, -0.7, 0.6])


def _triangles(shape: Any, tolerance: float) -> np.ndarray:
    """Tessellate a shape into an (n, 3, 3) array of triangle corner points."""
    vertices, faces = shape.tessellate(tolerance)
    if not faces:
        raise ValueError("tessellation produced no triangles (empty or degenerate shape)")
    points = np.array([tuple(v) for v in vertices], dtype=float)
    index = np.array(faces, dtype=int)
    return points[index]


def _shade(tris: np.ndarray) -> np.ndarray:
    """Flat Lambertian shading per triangle, returned as an RGB array."""
    normals = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    lengths = np.linalg.norm(normals, axis=1)
    lengths[lengths == 0] = 1.0
    normals /= lengths[:, None]
    light = _LIGHT_DIR / np.linalg.norm(_LIGHT_DIR)
    intensity = np.abs(normals @ light)
    # Ambient floor keeps faces turned away from the light readable.
    intensity = 0.45 + 0.55 * intensity
    return np.clip(np.array(_FACE_COLOR)[None, :] * intensity[:, None], 0, 1)


def _draw(ax, tris: np.ndarray, title: str, elev: float, azim: float, show_axes: bool) -> None:
    collection = Poly3DCollection(tris, facecolors=_shade(tris), linewidths=0)
    collection.set_edgecolor("none")
    ax.add_collection3d(collection)

    lo = tris.reshape(-1, 3).min(axis=0)
    hi = tris.reshape(-1, 3).max(axis=0)
    centre = (lo + hi) / 2.0
    radius = max(float(np.max(hi - lo)) / 2.0, 1e-6) * 1.08
    ax.set_xlim(centre[0] - radius, centre[0] + radius)
    ax.set_ylim(centre[1] - radius, centre[1] + radius)
    ax.set_zlim(centre[2] - radius, centre[2] + radius)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_title(title, fontsize=9)

    if show_axes:
        ax.set_xlabel("X", fontsize=7)
        ax.set_ylabel("Y", fontsize=7)
        ax.set_zlabel("Z", fontsize=7)
        ax.tick_params(labelsize=6)
    else:
        ax.set_axis_off()


def render(
    shape: Any,
    out_dir: Path,
    basename: str,
    views: Sequence[str] = DEFAULT_VIEWS,
    *,
    tolerance: float = 0.1,
    size: int = 900,
    dpi: int = 100,
    axes: bool = True,
    contact_sheet: bool = True,
) -> dict[str, str]:
    """Render ``shape`` from each named view. Returns {view name: png path}.

    When ``contact_sheet`` is set (default) an extra ``<basename>_views.png``
    with every view in one grid is written under the key ``"contact_sheet"``.
    Read that single file instead of four separate ones.
    """
    unknown = [v for v in views if v not in VIEWS]
    if unknown:
        raise ValueError(f"unknown view(s) {unknown}; known: {', '.join(VIEWS)}")

    out_dir.mkdir(parents=True, exist_ok=True)
    tris = _triangles(shape, tolerance)
    written: dict[str, str] = {}

    for view in views:
        elev, azim = VIEWS[view]
        fig = plt.figure(figsize=(size / dpi, size / dpi), dpi=dpi)
        ax = fig.add_subplot(111, projection="3d")
        _draw(ax, tris, f"{basename} - {view}", elev, azim, axes)
        target = out_dir / f"{basename}_{view}.png"
        fig.savefig(target, dpi=dpi, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        written[view] = str(target)

    if contact_sheet and len(views) > 1:
        columns = 2 if len(views) <= 4 else 3
        rows = math.ceil(len(views) / columns)
        fig = plt.figure(figsize=(columns * 4.2, rows * 4.2), dpi=dpi)
        for position, view in enumerate(views, start=1):
            elev, azim = VIEWS[view]
            ax = fig.add_subplot(rows, columns, position, projection="3d")
            _draw(ax, tris, view, elev, azim, axes)
        fig.suptitle(basename, fontsize=11)
        fig.tight_layout()
        target = out_dir / f"{basename}_views.png"
        fig.savefig(target, dpi=dpi, facecolor="white")
        plt.close(fig)
        written["contact_sheet"] = str(target)

    return written
