"""Create a new project directory from the built-in templates."""

from __future__ import annotations

import re
from pathlib import Path

from .project import ProjectError, projects_dir

TEMPLATE_DIR = Path(__file__).parent / "templates"
NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def _title(name: str) -> str:
    return name.replace("-", " ").replace("_", " ").strip().title()


def create(name: str, *, force: bool = False) -> Path:
    name = name.strip().strip("/")
    if not NAME_PATTERN.match(name):
        raise ProjectError(
            f"invalid project name {name!r}: use lowercase letters, digits, "
            "'-', '_' or '.', starting with a letter or digit (e.g. 'wall-bracket')"
        )

    target = projects_dir() / name
    if target.exists() and not force:
        raise ProjectError(f"projects/{name} already exists (pass --force to overwrite files)")

    (target / "reference").mkdir(parents=True, exist_ok=True)
    (target / "output").mkdir(parents=True, exist_ok=True)

    substitutions = {"__NAME__": name, "__TITLE__": _title(name)}
    for template in sorted(TEMPLATE_DIR.glob("*.tmpl")):
        destination = target / template.name[: -len(".tmpl")]
        if destination.exists() and not force:
            continue
        text = template.read_text(encoding="utf-8")
        for key, value in substitutions.items():
            text = text.replace(key, value)
        destination.write_text(text, encoding="utf-8")

    keep = target / "reference" / ".gitkeep"
    if not keep.exists():
        keep.write_text("", encoding="utf-8")

    return target
