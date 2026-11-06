"""Export built shapes to the file formats a CAD project is expected to ship."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

# format -> short description, shown by `cad formats`
FORMATS: dict[str, str] = {
    "step": "STEP AP214 B-Rep. The interchange/archival master. Always export this.",
    "stl":  "Triangle mesh for 3D printing/slicing. Lossy, tolerance-dependent.",
    "3mf":  "Mesh + units + metadata. Preferred over STL by modern slicers.",
    "brep": "Native OpenCASCADE B-Rep. Lossless, but only OCCT tools read it.",
    "gltf": "Mesh for web/3D viewers.",
    "obj":  "Mesh for rendering/DCC tools.",
}

DEFAULT_FORMATS = ("step", "stl", "3mf")


def export_shape(
    shape: Any,
    out_dir: Path,
    basename: str,
    formats: Iterable[str] = DEFAULT_FORMATS,
    *,
    linear_tolerance: float = 0.05,
    angular_tolerance: float = 0.2,
) -> dict[str, str]:
    """Write ``shape`` in each requested format. Returns {format: file path}.

    The mesh tolerances apply to STL/3MF/glTF/OBJ only; 0.05 mm chord deviation
    is a good default for printed parts. Tighten it for small, curved parts.
    """
    from build123d import (
        Mesher,
        Unit,
        export_brep,
        export_gltf,
        export_obj,
        export_step,
        export_stl,
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, str] = {}

    for fmt in formats:
        fmt = fmt.lower().strip()
        if fmt not in FORMATS:
            raise ValueError(f"unknown export format {fmt!r}; known: {', '.join(FORMATS)}")
        target = out_dir / f"{basename}.{fmt}"

        if fmt == "step":
            export_step(shape, target)
        elif fmt == "stl":
            export_stl(
                shape,
                target,
                tolerance=linear_tolerance,
                angular_tolerance=angular_tolerance,
            )
        elif fmt == "3mf":
            mesher = Mesher(unit=Unit.MM)
            mesher.add_shape(
                shape,
                linear_deflection=linear_tolerance,
                angular_deflection=angular_tolerance,
                part_number=basename,
            )
            mesher.write(target)
        elif fmt == "brep":
            export_brep(shape, target)
        elif fmt == "gltf":
            export_gltf(
                shape,
                target,
                unit=Unit.MM,
                binary=False,
                linear_deflection=linear_tolerance,
                angular_deflection=angular_tolerance,
            )
        elif fmt == "obj":
            export_obj(shape, target)

        written[fmt] = str(target)

    return written
