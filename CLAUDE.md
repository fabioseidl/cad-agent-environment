# CAD agent environment

This repository is a workspace for producing CAD models of physical objects
with [build123d](https://github.com/gumyr/build123d), running inside a Docker
container.

## Start here

* Skills live in `.agents/skills/` (exposed to Claude Code via the
  `.claude/skills` symlink):
  * **cad-project-workflow** - the end-to-end procedure for a modelling job.
  * **build123d-modeling** - the library, the CLI and the failure modes.
  * **dimensions-from-media** - photos and measurements into a dimension table.
* All CAD operations go through `.agents/tools/cad` - see `.agents/README.md`.
* Each object lives in its own directory under `projects/`.

## Rules for work in this repo

1. Never write a one-off export, measurement or render script. `cad build`
   does all three and writes `projects/<name>/output/report.json`.
2. After any geometry change, look at
   `projects/<name>/output/preview/<name>_views.png` before reporting success.
3. Keep every driving dimension in the parameter block at the top of
   `model.py`, with its source recorded in the project README.
4. Encode acceptance criteria in `spec.yaml` and never loosen a check to make
   a build pass; change the requirement explicitly instead.
5. Do not commit anything under `projects/*/output/` - it is generated.
6. The container runs with `--network none`; model scripts cannot fetch
   anything at build time.

## Worked example

`projects/example-wall-bracket/` - a parametric shelf bracket with
counterbored fixings, a gusset and passing spec checks. Build it with
`.agents/tools/cad build example-wall-bracket`.
