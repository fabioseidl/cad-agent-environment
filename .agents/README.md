# `.agents/` - the agent-facing layer

Everything an agent needs to do CAD work in this repository.

`.agents/skills/` is an emerging cross-client convention for sharing skills
between coding agents, not a ratified standard, and discovery still differs
per tool: Claude Code reads `.claude/skills/` (hence the symlink at the
repository root), OpenAI Codex reads `.agents/skills/`, GitHub Copilot reads
`.github/skills/`. Check your own tool's documentation; where it does not
discover this directory, the SKILL.md files are still plain Markdown that can
be read by path.

The `cad` CLI below has no such caveat - it is a shell script and a Python
package, usable by any agent or human that can run a command.

```
.agents/
  skills/
    build123d-modeling/      how to write, debug and verify build123d models
      references/            api-cheatsheet.md, pitfalls.md, design-rules.md
    cad-project-workflow/    intake -> project -> build/review loop -> handover
    dimensions-from-media/   photos, sketches and measurements -> dimension table
  tools/
    cad                      the one entry point; runs cadkit in the container
    cadkit/                  Python package implementing the commands
```

## The `cad` command

```bash
.agents/tools/cad doctor               # verify the toolchain
.agents/tools/cad new <project>        # scaffold projects/<project>/
.agents/tools/cad list                 # projects and their build state
.agents/tools/cad build <project>      # export + measure + render + check
.agents/tools/cad measure <project>    # metrics only
.agents/tools/cad preview <project>    # shaded PNG views
.agents/tools/cad views <project>      # 2D orthographic SVG/DXF, hidden lines
.agents/tools/cad check <project>      # spec.yaml checks; exit code 2 on failure
.agents/tools/cad run <script.py>      # one-off script in the CAD environment
.agents/tools/cad formats              # available formats and view names
```

Add `--json` to any reporting command for machine-readable output.

The first invocation builds the Docker image. Afterwards each command starts
a throwaway container with the repo bind-mounted at `/work` and no network
access. The image build is untested - see the note in the root README.

Environment variables: `CAD_LOCAL=1` to use a host Python that already has
build123d instead of Docker, `CAD_PYTHON` to pick that interpreter,
`CAD_BUILD=1` to force an image rebuild, `CAD_IMAGE` to change the image tag.

## Why a CLI instead of ad-hoc scripts

Every project needs the same operations - export to three formats, measure
the result, render views, verify dimensions. Doing that with a fresh script
each time burns tokens and produces inconsistent output. `cad build` does all
of it in one call and writes `output/report.json`, so measurements can be read
back instead of recomputed.
