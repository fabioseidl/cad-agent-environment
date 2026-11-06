"""Declarative verification of a built model against its spec.yaml.

The point is to make "did I build what the user asked for?" a single command
with a pass/fail answer, instead of an ad-hoc measuring script each time.

Supported ``checks:`` keys in spec.yaml (all optional)::

    checks:
      part: main                 # which part to check (default: the only one)
      bbox_mm:                   # scalar = exact (within tolerance), [lo, hi] = range
        x: 80
        y: [39.5, 40.5]
        z: 12
      volume_mm3: [11000, 13000]
      mass_g: [13, 16]
      area_mm2: [4000, 7000]
      solids: 1
      faces: [10, 40]
      watertight: true           # valid AND manifold
      center_of_mass_mm:
        x: 0
        y: 0
      tolerance_mm: 0.2          # default tolerance for scalar comparisons
      relative_tolerance: 0.02   # default tolerance for scalar volume/mass/area

A check list may also be given per part::

    checks:
      parts:
        lid:  {bbox_mm: {x: 80, y: 40, z: 4}}
        base: {bbox_mm: {x: 80, y: 40, z: 20}}
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

DEFAULT_TOLERANCE_MM = 0.1
DEFAULT_RELATIVE_TOLERANCE = 0.02


@dataclass
class CheckResult:
    name: str
    passed: bool
    expected: str
    actual: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "check": self.name,
            "status": "pass" if self.passed else "FAIL",
            "expected": self.expected,
            "actual": self.actual,
        }


def _compare(
    name: str,
    actual: float | None,
    expected: Any,
    tolerance: float,
    relative: bool = False,
) -> CheckResult:
    if actual is None:
        return CheckResult(name, False, str(expected), "not measured")
    if isinstance(expected, (list, tuple)):
        if len(expected) != 2:
            raise ValueError(f"{name}: a range must be [low, high], got {expected!r}")
        low, high = float(expected[0]), float(expected[1])
        return CheckResult(
            name, low <= actual <= high, f"{low:g} .. {high:g}", f"{actual:g}"
        )
    target = float(expected)
    allowed = abs(target) * tolerance if relative else tolerance
    delta = abs(actual - target)
    return CheckResult(
        name,
        delta <= allowed,
        f"{target:g} +/- {allowed:g}",
        f"{actual:g} (off by {delta:g})",
    )


def run_checks(report: dict[str, Any], checks: dict[str, Any]) -> list[CheckResult]:
    """Apply one checks-mapping to one part's measurement report."""
    results: list[CheckResult] = []
    tolerance = float(checks.get("tolerance_mm", DEFAULT_TOLERANCE_MM))
    rel = float(checks.get("relative_tolerance", DEFAULT_RELATIVE_TOLERANCE))

    bbox = checks.get("bbox_mm") or checks.get("bbox")
    if bbox:
        for axis in "xyz":
            if axis in bbox:
                results.append(
                    _compare(
                        f"bbox.{axis}",
                        report["bbox"]["size"][axis],
                        bbox[axis],
                        tolerance,
                    )
                )

    com = checks.get("center_of_mass_mm") or checks.get("center_of_mass")
    if com:
        measured = report.get("center_of_mass") or {}
        for axis in "xyz":
            if axis in com:
                results.append(
                    _compare(
                        f"center_of_mass.{axis}",
                        measured.get(axis),
                        com[axis],
                        tolerance,
                    )
                )

    for key, path, relative in (
        ("volume_mm3", "volume_mm3", True),
        ("area_mm2", "area_mm2", True),
        ("mass_g", "mass_g", True),
    ):
        if key in checks:
            results.append(
                _compare(key, report.get(path), checks[key], rel, relative=relative)
            )

    for key, path in (
        ("solids", "solids"),
        ("shells", "shells"),
        ("faces", "faces"),
        ("edges", "edges"),
        ("vertices", "vertices"),
    ):
        if key in checks:
            results.append(
                _compare(key, report["topology"][path], checks[key], 0.0)
            )

    if checks.get("watertight"):
        ok = bool(report.get("valid")) and bool(report.get("manifold"))
        results.append(
            CheckResult(
                "watertight",
                ok,
                "valid and manifold",
                f"valid={report.get('valid')} manifold={report.get('manifold')}",
            )
        )

    return results


def check_project(reports: dict[str, dict[str, Any]], spec: dict[str, Any]) -> dict[str, Any]:
    """Run every check declared in ``spec`` against the per-part reports."""
    checks = spec.get("checks") or {}
    out: dict[str, Any] = {"parts": {}, "passed": True, "total": 0, "failed": 0}
    if not checks:
        out["skipped"] = "spec.yaml declares no checks: section"
        return out

    per_part: dict[str, dict[str, Any]] = {}
    if "parts" in checks and isinstance(checks["parts"], dict):
        per_part = dict(checks["parts"])
    else:
        target = checks.get("part")
        if target is None:
            if len(reports) != 1:
                raise ValueError(
                    "the model produced several parts; set checks.part or use "
                    "checks.parts: {name: {...}} in spec.yaml"
                )
            target = next(iter(reports))
        per_part = {target: checks}

    for part_name, part_checks in per_part.items():
        if part_name not in reports:
            out["parts"][part_name] = [
                CheckResult(
                    "part exists", False, part_name, f"model built: {', '.join(reports)}"
                ).as_dict()
            ]
            out["passed"] = False
            out["total"] += 1
            out["failed"] += 1
            continue
        results = run_checks(reports[part_name], part_checks)
        out["parts"][part_name] = [r.as_dict() for r in results]
        out["total"] += len(results)
        failed = sum(1 for r in results if not r.passed)
        out["failed"] += failed
        if failed:
            out["passed"] = False

    return out
