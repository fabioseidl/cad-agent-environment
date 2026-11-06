"""Geometric measurement and sanity checking of built shapes.

Everything an agent would otherwise have to write a throwaway script for:
bounding box, volume, surface area, centre of mass, estimated mass, topology
counts and validity flags.
"""

from __future__ import annotations

from typing import Any

# Densities in g/cm^3. Only used when the project spec names a material and
# does not give an explicit density.
MATERIAL_DENSITY_G_CM3: dict[str, float] = {
    "pla": 1.24,
    "petg": 1.27,
    "abs": 1.04,
    "asa": 1.07,
    "tpu": 1.21,
    "nylon": 1.14,
    "resin": 1.15,
    "aluminium": 2.70,
    "aluminum": 2.70,
    "steel": 7.85,
    "stainless-steel": 7.90,
    "brass": 8.50,
    "copper": 8.96,
    "titanium": 4.51,
    "abs-plate": 1.04,
    "acrylic": 1.18,
    "plywood": 0.60,
    "pine": 0.50,
}


def density_for(spec: dict[str, Any]) -> tuple[float | None, str | None]:
    """Resolve (density g/cm^3, material name) from a project spec."""
    material = spec.get("material")
    if material is None:
        return None, None
    if isinstance(material, (int, float)):
        return float(material), None
    if isinstance(material, str):
        return MATERIAL_DENSITY_G_CM3.get(material.strip().lower()), material
    if isinstance(material, dict):
        name = material.get("name")
        density = material.get("density_g_cm3", material.get("density"))
        if density is None and isinstance(name, str):
            density = MATERIAL_DENSITY_G_CM3.get(name.strip().lower())
        return (float(density) if density is not None else None), name
    return None, None


def _round(value: float, digits: int = 4) -> float:
    rounded = round(float(value), digits)
    # Avoid "-0.0" in reports.
    return 0.0 if rounded == 0 else rounded


def measure(shape: Any, density_g_cm3: float | None = None) -> dict[str, Any]:
    """Return a JSON-serialisable measurement report for one shape.

    Linear values are in millimetres (build123d's native unit), volume in mm^3,
    area in mm^2 and mass in grams.
    """
    from build123d import CenterOf

    bbox = shape.bounding_box()
    volume = float(shape.volume)
    report: dict[str, Any] = {
        "bbox": {
            "size": {k: _round(v) for k, v in zip("xyz", tuple(bbox.size))},
            "min": {k: _round(v) for k, v in zip("xyz", tuple(bbox.min))},
            "max": {k: _round(v) for k, v in zip("xyz", tuple(bbox.max))},
        },
        "volume_mm3": _round(volume),
        "area_mm2": _round(float(shape.area)),
        "topology": {
            "solids": len(shape.solids()),
            "shells": len(shape.shells()),
            "faces": len(shape.faces()),
            "edges": len(shape.edges()),
            "vertices": len(shape.vertices()),
        },
        "valid": bool(shape.is_valid),
        "manifold": bool(shape.is_manifold),
    }

    try:
        com = shape.center(CenterOf.MASS)
        report["center_of_mass"] = {k: _round(v) for k, v in zip("xyz", tuple(com))}
    except Exception as exc:  # pragma: no cover - degenerate geometry only
        report["center_of_mass"] = None
        report["center_of_mass_error"] = str(exc)

    if density_g_cm3:
        # 1 cm^3 == 1000 mm^3
        report["mass_g"] = _round(volume / 1000.0 * density_g_cm3, 3)
        report["density_g_cm3"] = density_g_cm3

    return report


def warnings_for(report: dict[str, Any]) -> list[str]:
    """Non-fatal problems worth surfacing to the agent without re-reading JSON."""
    issues: list[str] = []
    if not report.get("valid", True):
        issues.append("shape fails OCCT validity check (BRepCheck)")
    if not report.get("manifold", True):
        issues.append("shape is not manifold - it will not slice or 3D-print reliably")
    if report.get("volume_mm3", 0) <= 0:
        issues.append("volume is zero or negative - the model produced no solid material")
    if report.get("topology", {}).get("solids", 0) > 1:
        issues.append(
            f"{report['topology']['solids']} disjoint solids in one part - "
            "intended for an assembly, or a boolean that failed to fuse?"
        )
    return issues
