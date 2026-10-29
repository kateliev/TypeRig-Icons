# Memory — TypeRig-Font

Agent memory kept in the repo so it follows the user between machines.
One fact per file (frontmatter: name / description / type). This file is the index: one line per memory.
Related tooling notes for icon import / live strokes live in `D:\Remote\GitHub\IconRig\Memory\`.

- [Icon house style](project_icon_style.md) — UPM 960, 32 grid, 64 centred butt/miter live stroke, centerlines ~160–800, circle handle 0.552
- [VFJ glyph format](reference_vfj_glyph_format.md) — node strings (s / c), stroke element keys, components + autoRecipe, named shared elements, layer flags
- [Drawing workflow](project_drawing_workflow.md) — icon_draw.py → proof VFJ → render_vfj.py PNG check → user moves glyphs into the binary .vfc (2026-10-29)
- [Drawing lessons](feedback_drawing_lessons.md) — gaps ≥ 96 between strokes, counters ≥ 64, quarter arcs on grid, one element per style, render beside neighbours
