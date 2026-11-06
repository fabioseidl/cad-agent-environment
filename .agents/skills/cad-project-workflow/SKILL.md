---
name: cad-project-workflow
description: End-to-end procedure for turning a user's request for a physical object - with measurements, photos, sketches or a reference part - into a finished CAD project in this repository. Use at the start of any new modelling job, and when resuming or revising an existing project under projects/. Covers intake, the project folder layout, the build-review-check loop, revisions and what to hand back.
---

# Running a CAD project

A project is one directory under `projects/`. Everything about the object -
the brief, the source photos, the model, the acceptance checks and the
exported files - lives in it, so a later session (or a different agent) can
pick it up without re-asking the user anything.

```
projects/<name>/
  README.md     brief, dimension table with sources, assumptions, decisions, changelog
  spec.yaml     material, export formats, machine-checkable acceptance criteria
  model.py      the build123d model; build() returns the part(s)
  reference/    user-supplied photos, sketches, datasheets, scanned drawings
  output/       generated - STEP/STL/3MF, report.json, preview/*.png, *.svg
```

`output/` is generated and is not committed; everything else is.

## 1. Intake

Before writing geometry, write down what the object actually is. Capture, in
`README.md`:

* what it is for and what it has to fit, mate with or hold;
* every dimension the user gave, **in their words and units**, plus the
  converted value in mm;
* which dimensions are missing, and how you intend to obtain them;
* material and process (FDM print, resin, laser-cut sheet, machined), since
  that sets clearances and wall thickness.

Copy any photos, sketches or PDFs the user provided into `reference/` and
list them in the README table. For deriving numbers from images rather than
from stated measurements, use the `dimensions-from-media` skill.

**Ask before modelling, not after**, and only about things that change the
geometry: a missing mating dimension, which face mounts, whether a hole is
threaded or clearance. Bundle the questions into one message. For anything
secondary, choose a sensible default from
`.agents/skills/build123d-modeling/references/design-rules.md`, record it in
the README as an assumption, and continue.

## 2. Scaffold

```bash
.agents/tools/cad new <name>
```

Then fill in `README.md` and `spec.yaml` **before** `model.py`. Writing the
acceptance checks first is what makes the later loop cheap: the checks encode
the brief, so `cad check` answers "is this what was asked for?" without
re-reading the conversation.

## 3. Model

Follow the `build123d-modeling` skill. Keep every driving dimension in the
parameter block, named after the thing it describes, with a comment giving its
source where that is not obvious.

For an object with distinct pieces, return `dict[str, Shape]` from `build()`
and model mating parts against shared parameters (one `CLEARANCE` constant,
one `WALL` constant), never against duplicated literals.

## 4. Build, look, check

```bash
.agents/tools/cad build <name>
```

One command exports, measures, renders and runs the spec checks. Then:

1. **Read the contact sheet** at `output/preview/<name>_views.png`. The
   checks cannot see that a pocket is on the wrong face.
2. Read the warnings. "not manifold" or "N disjoint solids" means the model
   is broken even if every dimension is right.
3. Fix and rebuild. Exit code 2 means a spec check failed.

Use `cad views <name>` when a dimension is easier to confirm on a 2D
orthographic drawing, and `cad views <name> --format dxf` for laser cutting.

## 5. Revise

When the user changes a requirement:

1. Update `README.md` (dimension table and changelog) and `spec.yaml` first.
2. Change the parameter, not the geometry, whenever the parameter exists.
3. Rebuild and re-check.

Never weaken or delete a check to make a build pass. If a requirement has
genuinely changed, change the requirement and say so.

## 6. Hand back

Report:

* the headline dimensions and estimated mass from the build output;
* the files produced, by path (`projects/<name>/output/...`);
* assumptions that still need confirming;
* anything the user asked for that was not done, and why.

Attach or point at `output/preview/<name>_views.png` - the user will spot a
misread requirement in the picture faster than in a dimension table.

## Reviewing an existing project

`cad list` shows every project and whether it has been built. To pick one up:
read its `README.md` and `spec.yaml` (not the whole model), run
`cad build <name>`, and compare the render with the brief.
