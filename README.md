# CAD agent environment

A repository for building parametric 3D models with build123d (Python + OpenCASCADE). It provides a reproducible toolchain that scaffolds projects, exports to STEP/STL/3MF, measures geometry against acceptance criteria, and renders preview images.

## What it does

- **Scaffolding**: `cad new <name>` creates a project directory with a brief template, dimension table, spec.yaml (machine-checkable constraints), model.py stub, and output folder.
- **Building**: `cad build` compiles the model, exports STEP/STL/3MF, computes bbox/volume/mass/com, runs topology validation, renders views, and writes results to `projects/<name>/output/`.
- **Validation**: `spec.yaml` defines measurable properties (tolerances, bounding box, volume range, watertightness, solid count). `cad check` runs these checks and exits non-zero on failure.
- **Inspection**: `cad list`, `cad measure`, `cad preview`, `cad views` provide quick access to project metadata without rebuilding.

## Why use this repository

| Problem | Solution |
|----------|-----------|
| CAD models are hard to share (scripts get lost, tolerances drift between sessions) | All constraints live in `spec.yaml`; validation is automated and repeatable. |
| Parametric modeling requires writing boilerplate for export/format/validation every time | One scaffolded project file handles the full pipeline. |
| Desktop CAD tools are non-scriptable or awkward to version-control | Build123d + OpenCASCADE runs as pure Python; changes are diffs in text files. |
| "It works on my machine" is common in CAD workflows | Docker image pins build123d, OpenCASCADE, and all dependencies; same environment everywhere. |

## How it works (briefly)

The `cad` CLI script invokes a Docker container that contains Python 3.10+, build123d 0.13+, numpy, meshio, matplotlib, PyYAML, and the full OpenCASCADE runtime. The repository is bind-mounted at `/work`, so generated files appear directly on the host under `projects/<name>/output/`.

If Docker isn't available, set `CAD_LOCAL=1` to run against a local Python environment that has build123d installed (wheels exist for Linux x86_64/aarch64, macOS arm64/x86_64, Windows amd64 on Python 3.11–3.14).

## Quick start

```bash
# verify the toolchain works
.agents/tools/cad doctor

# scaffold a new project (creates projects/<name>/ with README.md, spec.yaml, model.py)
.agents/tools/cad new wall-bracket

# edit:
#   - projects/wall-bracket/README.md  (brief + dimensions)
#   - projects/wall-bracket/spec.yaml  (acceptance criteria)
#   - projects/wall-bracket/model.py   (parametric geometry)

# build and validate
.agents/tools/cad build wall-bracket
```

`cad build` output example:

```text
built example-wall-bracket in 1.7s
  wall-bracket:
    bbox      60 x 70 x 80 mm
    volume    75247.2 mm^3   mass 93.307 g
    com       (0, 20.3576, 24.6366) mm
    topology  solids=1, shells=1, faces=31, edges=75, vertices=50
    valid=True manifold=True
  checks: PASS (6/6)
```

## Example project

The repo includes `projects/example-wall-bracket/`, a parametric shelf bracket with counterbored M5 fixings and gusset plates. It demonstrates the full workflow: brief, dimensions, spec.yaml constraints, parametric model in build123d, export to STEP/STL/3MF, rendered preview images, and automated validation.

Rendered views of the example wall bracket:

![Example wall bracket — front](docs/example-wall-bracket.png)


## Project layout

```text
projects/<name>/
  README.md      # brief and dimension table
  spec.yaml       # machine-checkable acceptance criteria
  model.py        # parametric build123d model
  reference/      # photos or screenshots of the real object (optional)
  output/         # generated STEP, STL, 3MF, rendered views (not committed to VCS)
```

## Tests

```bash
make test   # smoke tests for the toolchain and all example projects
```

---

**Next step:** run `.agents/tools/cad doctor` to confirm your environment is ready, then create a new project with `.agents/tools/cad new <name>`.