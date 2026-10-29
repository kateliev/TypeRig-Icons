# TypeRig-Font

Home of TypeRig Icons, the icon font of the TypeRig GUI (FontLab).

- **Memory:** read `Memory/MEMORY.md` first. Shared agent memory kept in the repo; write durable facts there
  (one fact per file, indexed in `MEMORY.md`).
- **Sources:** `sources/typerig-icons.vfc` (binary, source of truth, edited only in FontLab);
  `sources/typerig-icons.vfj` is a JSON export Claude reads and writes. Build: `fonts/typerig-icons.ttf`.
- **Scripts:** `scripts/` — every script made for this project lives here (Python 3, tabs, needs matplotlib for rendering).
  - `icon_draw.py` — library: house-style stroke elements, `circle`, `arc_to`, `glyph`, `off_grid`, `save_proof`.
  - `render_vfj.py <vfj> <out.png> [names|patterns] [--cols N] [--mask]` — PNG contact sheet of glyphs (visual check).
  - `vfj_tool.py list|dump|stats|merge` — inspect the VFJ, profile its style, merge proof glyphs into it.
  - `icon_usage.py [out.csv]` — census of buttons / captions / icons in Typerig-Glyphs, TypeRig Scripts and FontRig
    editor → `lists/icon_usage.csv` (with heuristic mismatch flags).
  - `glyph_todo.py` — glyph backlog rules over the census + `glyph_catalog.py` (planned editor glyphs)
    → `lists/glyph_todo.csv` (grouped; new / alias / rename / use existing, P1–P3).
- **Drawing new icons:** follow `Memory/project_drawing_workflow.md`; temporary proofs and PNGs go to the scratchpad,
  not the repo.
- Related tooling (Figma → FontLab import, live-stroke research): `D:\Remote\GitHub\IconRig`.
