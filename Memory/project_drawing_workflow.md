---
name: project-drawing-workflow
description: How Claude draws new TypeRig Icons — code the glyph with scripts/icon_draw.py, render PNG with scripts/render_vfj.py and look, write a proof VFJ, user opens it in FontLab and moves it into the binary .vfc
metadata:
  type: project
---

Agreed with the user 2026-10-29 ("Looking good" after the trash / bell proof):

1. Draw each icon in Python with `scripts/icon_draw.py` (house-style elements, `circle`, `arc_to`, `off_grid` check).
2. Write a proof VFJ with `save_proof()` (font header, UPM 960) — in the scratchpad unless the user wants it kept.
3. Render it with `scripts/render_vfj.py` and **look at the PNG before showing anything**; compare against
   neighbour icons rendered on the same sheet (`render_vfj.py … 'layer_*' newname`).
4. Iterate, then hand over: the user opens the proof in FontLab and copies glyphs into `sources/typerig-icons.vfc`,
   or `scripts/vfj_tool.py merge proof.vfj sources/typerig-icons.vfj` and the user re-saves as VFC.

Facts about the sources:
- `typerig-icons.vfc` is binary and the source of truth (committed with "[Build] vX [TTF] [VFC]" messages);
  `fonts/typerig-icons.ttf` is the build. Claude cannot edit the .vfc.
- `typerig-icons.vfj` is an untracked export (2026-10-29). If the .vfc changes, ask for a fresh export before merging.

**Why:** live strokes only exist inside FontLab; the PNG is the only visual check Claude has.
**How to apply:** never hand over an icon that was not rendered and checked; say what the renderer cannot show
(one-sided strokes, vertical/horizontal caps, named elements).
Related: [[project-icon-style]], [[reference-vfj-glyph-format]], [[feedback-drawing-lessons]]
