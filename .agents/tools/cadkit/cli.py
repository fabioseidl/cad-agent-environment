"""cadkit command line - the agent-facing interface to the CAD environment.

Run via ``.agents/tools/cad <command>`` (which handles the container), or
directly with ``python -m cadkit.cli <command>`` inside an environment that
already has build123d.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from pathlib import Path
from typing import Any

from . import __version__
from .project import Project, ProjectError, projects_dir, repo_root


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def _csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _emit(payload: dict[str, Any], as_json: bool, lines: list[str]) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=False))
    else:
        print("\n".join(lines))


def _fmt_report(name: str, report: dict[str, Any]) -> list[str]:
    size = report["bbox"]["size"]
    lines = [
        f"  {name}:",
        f"    bbox      {size['x']:g} x {size['y']:g} x {size['z']:g} mm",
        f"    volume    {report['volume_mm3']:g} mm^3"
        + (f"   mass {report['mass_g']:g} g" if "mass_g" in report else ""),
        f"    area      {report['area_mm2']:g} mm^2",
        "    topology  "
        + ", ".join(f"{k}={v}" for k, v in report["topology"].items()),
        f"    valid={report['valid']} manifold={report['manifold']}",
    ]
    com = report.get("center_of_mass")
    if com:
        lines.insert(
            4, f"    com       ({com['x']:g}, {com['y']:g}, {com['z']:g}) mm"
        )
    return lines


def _measure_all(parts: dict[str, Any], spec: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    from .metrics import density_for, measure, warnings_for

    density, material = density_for(spec)
    reports: dict[str, Any] = {}
    warnings: list[str] = []
    for name, shape in parts.items():
        report = measure(shape, density_g_cm3=density)
        if material:
            report["material"] = material
        reports[name] = report
        warnings.extend(f"{name}: {w}" for w in warnings_for(report))
    return reports, warnings


# --------------------------------------------------------------------------
# commands
# --------------------------------------------------------------------------
def cmd_new(args: argparse.Namespace) -> int:
    from .scaffold import create

    path = create(args.name, force=args.force)
    rel = path.relative_to(repo_root())
    print(f"created {rel}/")
    for item in ("README.md", "spec.yaml", "model.py", "reference/"):
        print(f"  {rel}/{item}")
    print(
        "\nnext: record the brief and measurements in README.md, encode the\n"
        "acceptance checks in spec.yaml, edit model.py, then run:\n"
        f"  .agents/tools/cad build {args.name}"
    )
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    root = projects_dir()
    names = sorted(
        p.name
        for p in root.iterdir()
        if p.is_dir() and not p.name.startswith((".", "_"))
    ) if root.is_dir() else []
    if args.json:
        print(json.dumps({"projects": names}, indent=2))
        return 0
    if not names:
        print("no projects yet - create one with: cad new <name>")
        return 0
    for name in names:
        has_model = (root / name / "model.py").is_file()
        built = (root / name / "output" / "report.json").is_file()
        flags = []
        if not has_model:
            flags.append("no model.py")
        flags.append("built" if built else "not built")
        print(f"{name:<32} {', '.join(flags)}")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    from .exporters import export_shape

    project = Project.load(args.project)
    project.ensure_dirs()

    started = time.perf_counter()
    parts = project.load_parts()
    build_seconds = time.perf_counter() - started

    formats = args.formats or project.spec.get("exports") or ["step", "stl", "3mf"]
    if isinstance(formats, str):
        formats = _csv(formats)

    reports, warnings = _measure_all(parts, project.spec)
    artifacts: dict[str, dict[str, str]] = {}

    for name, shape in parts.items():
        basename = name if len(parts) > 1 else project.name
        written = export_shape(
            shape,
            project.output_dir,
            basename,
            formats,
            linear_tolerance=args.mesh_tolerance,
        )
        artifacts[name] = {k: project.rel(Path(v)) for k, v in written.items()}

        if not args.no_preview:
            from .preview import render

            images = render(
                shape,
                project.preview_dir,
                basename,
                views=args.views,
                tolerance=args.mesh_tolerance * 2,
            )
            artifacts[name].update(
                {f"preview:{k}": project.rel(Path(v)) for k, v in images.items()}
            )

        if args.drawings:
            from .views import export_views

            drawings = export_views(shape, project.preview_dir, basename, fmt="svg")
            artifacts[name].update(
                {f"drawing:{k}": project.rel(Path(v)) for k, v in drawings.items()}
            )

    if len(parts) > 1:
        # One combined file + render so the assembly can be seen as a whole.
        from build123d import Compound

        assembly = Compound(children=list(parts.values()))
        written = export_shape(
            assembly,
            project.output_dir,
            f"{project.name}-assembly",
            [f for f in formats if f in ("step", "brep", "gltf")] or ["step"],
            linear_tolerance=args.mesh_tolerance,
        )
        artifacts["(assembly)"] = {k: project.rel(Path(v)) for k, v in written.items()}
        if not args.no_preview:
            from .preview import render

            images = render(
                assembly,
                project.preview_dir,
                f"{project.name}-assembly",
                views=args.views,
                tolerance=args.mesh_tolerance * 2,
            )
            artifacts["(assembly)"].update(
                {f"preview:{k}": project.rel(Path(v)) for k, v in images.items()}
            )

    payload: dict[str, Any] = {
        "project": project.name,
        "build_seconds": round(build_seconds, 3),
        "parts": reports,
        "artifacts": artifacts,
        "warnings": warnings,
    }

    if project.spec.get("checks"):
        from .checks import check_project

        payload["checks"] = check_project(reports, project.spec)

    report_path = project.output_dir / "report.json"
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [f"built {project.name} in {payload['build_seconds']:g}s"]
    for name, report in reports.items():
        lines.extend(_fmt_report(name, report))
    lines.append("  files:")
    for name, files in artifacts.items():
        for kind, path in files.items():
            lines.append(f"    {kind:<18} {path}")
    for warning in warnings:
        lines.append(f"  WARNING: {warning}")
    if "checks" in payload:
        lines.extend(_check_lines(payload["checks"]))
    lines.append(f"  report: {project.rel(report_path)}")

    _emit(payload, args.json, lines)

    if payload.get("checks") and not payload["checks"]["passed"]:
        return 2
    return 0


def _check_lines(checks: dict[str, Any]) -> list[str]:
    if checks.get("skipped"):
        return [f"  checks: skipped ({checks['skipped']})"]
    verdict = "PASS" if checks["passed"] else "FAIL"
    lines = [f"  checks: {verdict} ({checks['total'] - checks['failed']}/{checks['total']})"]
    for part, results in checks["parts"].items():
        for result in results:
            if result["status"] == "pass":
                continue
            lines.append(
                f"    FAIL {part}.{result['check']}: "
                f"expected {result['expected']}, got {result['actual']}"
            )
    return lines


def cmd_measure(args: argparse.Namespace) -> int:
    project = Project.load(args.project)
    parts = project.load_parts()
    reports, warnings = _measure_all(parts, project.spec)
    payload = {"project": project.name, "parts": reports, "warnings": warnings}
    lines = [f"{project.name}:"]
    for name, report in reports.items():
        lines.extend(_fmt_report(name, report))
    lines.extend(f"  WARNING: {w}" for w in warnings)
    _emit(payload, args.json, lines)
    return 0


def cmd_preview(args: argparse.Namespace) -> int:
    from .preview import render

    project = Project.load(args.project)
    project.ensure_dirs()
    parts = project.load_parts()
    written: dict[str, dict[str, str]] = {}
    for name, shape in parts.items():
        basename = name if len(parts) > 1 else project.name
        images = render(
            shape,
            project.preview_dir,
            basename,
            views=args.views,
            tolerance=args.mesh_tolerance,
            axes=not args.no_axes,
        )
        written[name] = {k: project.rel(Path(v)) for k, v in images.items()}
    lines = []
    for name, images in written.items():
        for view, path in images.items():
            lines.append(f"{view:<14} {path}")
    _emit({"project": project.name, "previews": written}, args.json, lines)
    return 0


def cmd_views(args: argparse.Namespace) -> int:
    from .views import export_views

    project = Project.load(args.project)
    project.ensure_dirs()
    parts = project.load_parts()
    written: dict[str, dict[str, str]] = {}
    for name, shape in parts.items():
        basename = name if len(parts) > 1 else project.name
        drawings = export_views(
            shape,
            project.preview_dir,
            basename,
            views=args.views,
            fmt=args.format,
            hidden_lines=not args.no_hidden,
        )
        written[name] = {k: project.rel(Path(v)) for k, v in drawings.items()}
    lines = [
        f"{view:<14} {path}"
        for images in written.values()
        for view, path in images.items()
    ]
    _emit({"project": project.name, "drawings": written}, args.json, lines)
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    from .checks import check_project

    project = Project.load(args.project)
    parts = project.load_parts()
    reports, warnings = _measure_all(parts, project.spec)
    checks = check_project(reports, project.spec)
    payload = {"project": project.name, "checks": checks, "warnings": warnings}
    lines = _check_lines(checks)
    lines.extend(f"  WARNING: {w}" for w in warnings)
    _emit(payload, args.json, lines)
    return 0 if checks.get("passed", True) else 2


def cmd_run(args: argparse.Namespace) -> int:
    """Execute an arbitrary build123d script inside the environment."""
    script = Path(args.script)
    if not script.is_file():
        raise ProjectError(f"script not found: {script}")
    source = script.read_text(encoding="utf-8")
    globals_dict: dict[str, Any] = {
        "__name__": "__main__",
        "__file__": str(script.resolve()),
    }
    sys.path.insert(0, str(script.resolve().parent))
    exec(compile(source, str(script), "exec"), globals_dict)  # noqa: S102
    return 0


def cmd_formats(args: argparse.Namespace) -> int:
    from .exporters import FORMATS
    from .preview import VIEWS
    from .views import ORTHO_VIEWS

    print("3D export formats (cad build --formats):")
    for name, description in FORMATS.items():
        print(f"  {name:<6} {description}")
    print("\nrendered preview views (cad preview --views):")
    print("  " + ", ".join(VIEWS))
    print("\n2D drawing views (cad views --views):")
    print("  " + ", ".join(ORTHO_VIEWS))
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    ok = True
    print(f"cadkit         {__version__}")
    print(f"python         {sys.version.split()[0]}")
    print(f"repo root      {repo_root()}")
    try:
        import build123d

        print(f"build123d      {build123d.__version__}")
    except Exception as exc:
        ok = False
        print(f"build123d      MISSING ({exc})")
    for module in ("matplotlib", "yaml", "numpy"):
        try:
            __import__(module)
            print(f"{module:<14} ok")
        except Exception as exc:
            ok = False
            print(f"{module:<14} MISSING ({exc})")
    if ok:
        from build123d import Box

        volume = Box(10, 10, 10).volume
        print(f"smoke test     Box(10,10,10).volume = {volume:g} (expected 1000)")
        ok = abs(volume - 1000) < 1e-6
    print("status         " + ("OK" if ok else "BROKEN"))
    return 0 if ok else 1


# --------------------------------------------------------------------------
# parser
# --------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    from .preview import DEFAULT_VIEWS as PREVIEW_DEFAULT
    from .views import DEFAULT_VIEWS as DRAWING_DEFAULT

    parser = argparse.ArgumentParser(
        prog="cad",
        description="build123d CAD environment for agents",
    )
    parser.add_argument("--version", action="version", version=f"cadkit {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_json(p: argparse.ArgumentParser) -> None:
        p.add_argument("--json", action="store_true", help="machine-readable output")

    p_new = sub.add_parser("new", help="scaffold a new project under projects/")
    p_new.add_argument("name")
    p_new.add_argument("--force", action="store_true", help="overwrite existing files")
    p_new.set_defaults(func=cmd_new)

    p_list = sub.add_parser("list", help="list projects")
    add_json(p_list)
    p_list.set_defaults(func=cmd_list)

    p_build = sub.add_parser(
        "build", help="build a project: export, measure, preview and check"
    )
    p_build.add_argument("project")
    p_build.add_argument(
        "--formats", type=_csv, help="comma-separated, e.g. step,stl (default: spec.yaml exports)"
    )
    p_build.add_argument("--views", type=_csv, default=list(PREVIEW_DEFAULT))
    p_build.add_argument("--no-preview", action="store_true", help="skip PNG rendering")
    p_build.add_argument(
        "--drawings", action="store_true", help="also write 2D SVG technical views"
    )
    p_build.add_argument(
        "--mesh-tolerance",
        type=float,
        default=0.05,
        help="chord deviation in mm for mesh exports (default 0.05)",
    )
    add_json(p_build)
    p_build.set_defaults(func=cmd_build)

    p_measure = sub.add_parser(
        "measure", aliases=["inspect"], help="measure the model without exporting"
    )
    p_measure.add_argument("project")
    add_json(p_measure)
    p_measure.set_defaults(func=cmd_measure)

    p_preview = sub.add_parser("preview", help="render shaded PNG views")
    p_preview.add_argument("project")
    p_preview.add_argument("--views", type=_csv, default=list(PREVIEW_DEFAULT))
    p_preview.add_argument("--mesh-tolerance", type=float, default=0.1)
    p_preview.add_argument("--no-axes", action="store_true")
    add_json(p_preview)
    p_preview.set_defaults(func=cmd_preview)

    p_views = sub.add_parser("views", help="export 2D orthographic drawings (SVG/DXF)")
    p_views.add_argument("project")
    p_views.add_argument("--views", type=_csv, default=list(DRAWING_DEFAULT))
    p_views.add_argument("--format", choices=["svg", "dxf"], default="svg")
    p_views.add_argument("--no-hidden", action="store_true", help="omit hidden lines")
    add_json(p_views)
    p_views.set_defaults(func=cmd_views)

    p_check = sub.add_parser("check", help="verify the model against spec.yaml")
    p_check.add_argument("project")
    add_json(p_check)
    p_check.set_defaults(func=cmd_check)

    p_run = sub.add_parser("run", help="execute a build123d script in the environment")
    p_run.add_argument("script")
    p_run.set_defaults(func=cmd_run)

    p_formats = sub.add_parser("formats", help="list export formats and view names")
    p_formats.set_defaults(func=cmd_formats)

    p_doctor = sub.add_parser("doctor", help="verify the toolchain works")
    p_doctor.set_defaults(func=cmd_doctor)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args) or 0)
    except ProjectError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # model scripts raise anything
        print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
        traceback.print_exc(limit=8)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
