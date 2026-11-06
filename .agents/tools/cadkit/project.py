"""Project layout, model loading and the model contract."""

from __future__ import annotations

import importlib.util
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

MODEL_FILENAME = "model.py"
SPEC_FILENAME = "spec.yaml"


class ProjectError(RuntimeError):
    """Raised for user-fixable problems (missing project, bad model contract)."""


def repo_root(start: Path | None = None) -> Path:
    """Locate the repository root by walking up to the directory holding .agents."""
    env = os.environ.get("CAD_REPO_ROOT")
    if env:
        return Path(env).resolve()
    here = (start or Path(__file__)).resolve()
    for candidate in [here, *here.parents]:
        if (candidate / ".agents").is_dir() and (candidate / "projects").is_dir():
            return candidate
    # Fallback: .agents/tools/cadkit/project.py -> repo root is 3 levels up.
    return Path(__file__).resolve().parents[3]


def projects_dir() -> Path:
    return repo_root() / "projects"


@dataclass
class Project:
    """A single CAD project directory under ``projects/``."""

    name: str
    path: Path
    spec: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls, name: str) -> "Project":
        name = name.strip().strip("/")
        # Accept either a project name or a path to the project directory.
        path = Path(name)
        if not path.is_dir():
            path = projects_dir() / name
        if not path.is_dir():
            available = sorted(
                p.name
                for p in projects_dir().iterdir()
                if p.is_dir() and not p.name.startswith((".", "_"))
            ) if projects_dir().is_dir() else []
            raise ProjectError(
                f"project {name!r} not found in {projects_dir()}. "
                f"Existing projects: {', '.join(available) or '(none)'}. "
                f"Create one with: cad new {name}"
            )
        path = path.resolve()
        return cls(name=path.name, path=path, spec=_load_spec(path / SPEC_FILENAME))

    # --- layout -----------------------------------------------------------
    @property
    def model_file(self) -> Path:
        return self.path / MODEL_FILENAME

    @property
    def output_dir(self) -> Path:
        return self.path / "output"

    @property
    def preview_dir(self) -> Path:
        return self.path / "output" / "preview"

    def ensure_dirs(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.preview_dir.mkdir(parents=True, exist_ok=True)

    def rel(self, path: Path) -> str:
        """Path relative to the repo root, for compact log output."""
        try:
            return str(path.resolve().relative_to(repo_root()))
        except ValueError:
            return str(path)

    # --- model contract ---------------------------------------------------
    def load_parts(self) -> dict[str, Any]:
        """Execute ``model.py`` and return the produced parts.

        The model contract, in priority order:

        1. ``build()`` -> Shape, or dict[str, Shape], or list/tuple of Shapes
        2. module-level ``result``, same accepted types

        Returning a dict is how assemblies are expressed: each key becomes a
        separate exported file plus an entry in the metrics report.
        """
        if not self.model_file.is_file():
            raise ProjectError(f"missing {self.rel(self.model_file)}")

        module = _import_module(self.model_file, f"cad_model_{self.name}")

        if hasattr(module, "build") and callable(module.build):
            produced = module.build()
            source = "build()"
        elif hasattr(module, "result"):
            produced = module.result
            source = "result"
        else:
            raise ProjectError(
                f"{self.rel(self.model_file)} defines neither build() nor result; "
                "one of them must return the model (see .agents/skills/build123d-modeling)"
            )

        parts = _normalize(produced, source)
        if not parts:
            raise ProjectError(f"{source} in {self.rel(self.model_file)} produced no shapes")
        return parts


def _normalize(produced: Any, source: str) -> dict[str, Any]:
    from build123d import Shape

    if produced is None:
        raise ProjectError(f"{source} returned None")
    if isinstance(produced, Shape):
        label = getattr(produced, "label", "") or "part"
        return {label: produced}
    if isinstance(produced, dict):
        bad = [k for k, v in produced.items() if not isinstance(v, Shape)]
        if bad:
            raise ProjectError(f"{source} returned non-Shape values for keys: {bad}")
        return dict(produced)
    if isinstance(produced, (list, tuple)):
        out: dict[str, Any] = {}
        for index, item in enumerate(produced):
            if not isinstance(item, Shape):
                raise ProjectError(f"{source} returned a non-Shape at index {index}")
            label = getattr(item, "label", "") or f"part{index + 1}"
            while label in out:
                label = f"{label}_{index + 1}"
            out[label] = item
        return out
    raise ProjectError(
        f"{source} returned {type(produced).__name__}; expected a build123d Shape, "
        "a dict of name -> Shape, or a list of Shapes"
    )


def _load_spec(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    import yaml

    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ProjectError(f"{path} must contain a YAML mapping at the top level")
    return data


def _import_module(file_path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ProjectError(f"cannot import {file_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    # Let the model import sibling helper modules from its own directory.
    parent = str(file_path.parent)
    inserted = parent not in sys.path
    if inserted:
        sys.path.insert(0, parent)
    try:
        spec.loader.exec_module(module)
    finally:
        if inserted:
            sys.path.remove(parent)
    return module
