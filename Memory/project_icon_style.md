---
name: project-icon-style
description: House style of TypeRig Icons — UPM 960, 32-unit grid, 64-unit centred live stroke, butt caps, miter joins, centerlines ~160–800, circle handle ratio 0.552
metadata:
  type: project
---

Measured from `sources/typerig-icons.vfj` (v1.033, 457 glyphs) on 2026-10-29 (`python scripts/vfj_tool.py stats`):

- **Metrics:** UPM 960, one master `Regular`, advance 960 (11 glyphs 1024, `space` 240). Ascender 960, descender 0.
  Master guides at 64 / 128 / 832 / 896 both ways.
- **Live area:** stroke centerlines run about 160–800 (search, gem, heart, undo), so the stroke's outer edge lands on
  the 128 / 832 keylines. Small badges (+, −) and wide marks may go out to 96 / 864.
- **Grid:** ~85% of on-curve coordinates are on 32; the rest are diagonals, star points, curve stuff. Draw on 32.
- **Stroke:** one element per style, `thickness` 64, centred (no `proportion`), butt caps, miter joins, no fill
  (`"brush": {"style": 0}`). Most common element style in the font:
  `pen {penCapStyle 0, penJoinStyle 0, penWidth 64, penMiterLimit 3}`, `stroke {thickness 64}`, `brush {style 0}`.
- **Variants seen:** `proportion: 100` (one-sided, mostly squares in node_align_* / layer_* glyphs), caps
  `vertical`/`horizontal` (layer stacks), `join: bevel`, a 96 stroke for emphasis (search handle), filled
  elements (`{}`) for dots and solid shapes (eye pupil, panel bars).
- **Curves:** circles are 4 cubics, handle = 0.552 × r (circle r 288 → 159; undo r 224 → 124), start at the
  left extreme with a smooth node, close with a ` c` segment. `scripts/icon_draw.py circle()` reproduces glyph
  `circle` exactly.
- **Families:** related icons share a base and add a badge (layer_add = layer stack + plus at top-left), or are
  flipped components (`panel_up` = `panel_down` rotated via `autoRecipe "=panel_down@~"`).

**Why:** new icons must sit with the existing 450+ at small UI sizes in the TypeRig GUI.
**How to apply:** start every new icon with `icon_draw.stroke()` defaults; deviate only when a neighbour icon does.
Related: [[reference-vfj-glyph-format]], [[project-drawing-workflow]], [[feedback-drawing-lessons]]
