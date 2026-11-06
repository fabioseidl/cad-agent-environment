# Agent instructions

See `CLAUDE.md` for the full brief; the two files are kept identical in
intent. Skills and tools live in `.agents/`, projects in `projects/`, the
container definition in `docker/`.

Quick start:

```bash
.agents/tools/cad doctor
.agents/tools/cad new my-part
.agents/tools/cad build my-part
```

Read `.agents/skills/cad-project-workflow/SKILL.md` before starting a new
modelling job.
