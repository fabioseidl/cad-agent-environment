"""Smoke tests for the CAD environment.

Runs without pytest:  .agents/tools/cad run tests/test_cadkit.py
Runs under pytest too: pytest tests/

Everything here must pass inside the container, so it may not use the
network and must not depend on anything outside the repository.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / ".agents" / "tools"))

from cadkit.checks import check_project  # noqa: E402
from cadkit.exporters import export_shape  # noqa: E402
from cadkit.metrics import density_for, measure, warnings_for  # noqa: E402
from cadkit.preview import render  # noqa: E402
from cadkit.project import Project  # noqa: E402
from cadkit.views import export_views  # noqa: E402

EXAMPLE = "example-wall-bracket"


def _box():
    from build123d import Box, Part

    part = Part() + Box(10, 20, 30)
    part.label = "test-box"
    return part


def test_measure_box() -> None:
    report = measure(_box(), density_g_cm3=1.24)
    assert report["bbox"]["size"] == {"x": 10.0, "y": 20.0, "z": 30.0}
    assert report["volume_mm3"] == 6000.0
    assert report["area_mm2"] == 2200.0
    assert report["mass_g"] == 7.44
    assert report["topology"] == {
        "solids": 1,
        "shells": 1,
        "faces": 6,
        "edges": 12,
        "vertices": 8,
    }
    assert report["valid"] and report["manifold"]
    assert warnings_for(report) == []


def test_density_lookup() -> None:
    assert density_for({"material": "PLA"}) == (1.24, "PLA")
    assert density_for({"material": {"name": "x", "density_g_cm3": 2.0}}) == (2.0, "x")
    assert density_for({}) == (None, None)


def test_checks_pass_and_fail() -> None:
    report = measure(_box())
    reports = {"test-box": report}
    passing = check_project(reports, {"checks": {"bbox_mm": {"x": 10}, "solids": 1}})
    assert passing["passed"] and passing["failed"] == 0
    failing = check_project(reports, {"checks": {"bbox_mm": {"x": 11}}})
    assert not failing["passed"] and failing["failed"] == 1
    ranged = check_project(reports, {"checks": {"volume_mm3": [5000, 7000]}})
    assert ranged["passed"]


def test_exports_and_renders() -> None:
    shape = _box()
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        written = export_shape(shape, out, "box", ["step", "stl", "3mf"])
        for path in written.values():
            assert Path(path).stat().st_size > 0, path

        images = render(shape, out, "box", views=("iso", "front"))
        assert "contact_sheet" in images
        for path in images.values():
            assert Path(path).stat().st_size > 0, path

        drawings = export_views(shape, out, "box", views=("front", "iso"))
        for path in drawings.values():
            assert Path(path).read_text(encoding="utf-8").startswith("<?xml")


def test_example_project_builds_and_checks() -> None:
    project = Project.load(EXAMPLE)
    parts = project.load_parts()
    assert list(parts) == ["wall-bracket"]
    density, _ = density_for(project.spec)
    reports = {name: measure(shape, density) for name, shape in parts.items()}
    result = check_project(reports, project.spec)
    assert result["passed"], result


def test_model_contract_errors() -> None:
    from cadkit.project import ProjectError, _normalize

    for bad in (None, 42, "a shape"):
        try:
            _normalize(bad, "build()")
        except ProjectError:
            continue
        raise AssertionError(f"{bad!r} should have been rejected")


def main() -> int:
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    failures = 0
    for test in tests:
        try:
            test()
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"FAIL {test.__name__}: {type(exc).__name__}: {exc}")
        else:
            print(f"ok   {test.__name__}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
