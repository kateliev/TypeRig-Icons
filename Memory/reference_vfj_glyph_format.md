---
name: reference-vfj-glyph-format
description: How FontLab VFJ stores a TypeRig Icons glyph — node string syntax (s / c flags), stroke element keys, components, autoRecipe, named shared elements, layer flags
metadata:
  type: reference
---

Read from `sources/typerig-icons.vfj` on 2026-10-29 (FontLab 8 build 8950 save):

- **Glyph:** `{name, unicode?, openTypeGlyphClass, layers: [{name, advanceWidth, elements, flags?, color?, guidelines?}]}`.
  383 of 457 glyphs have no unicode: TypeRig calls icons by name. Layers `Regular` and sometimes `mask`.
- **Node strings** (inside `elementData.contours[].nodes`):
  - `"x y"` on-curve; `"x y s"` smooth.
  - `"c1x c1y  c2x c2y  x y [s]"` cubic segment ending at x y.
  - `"c1x c1y  c2x c2y c"` the closing cubic of a closed contour, ending on the first node.
  - Contour `"open": true` = open path; closed has no key.
- **Live stroke element:** `pen` (Qt QPen: penCapStyle 0 flat / 32 round, square left out; penJoinStyle 0 miter /
  128 round, bevel left out) + `stroke` {`thickness`, `cap0`/`cap1`, `join`, `proportion`, `miter_limit`,
  `remove_overlap`} + `brush {"style": 0}` = no fill. No `brush` = filled; `{}` element = plain fill shape.
  Full key study: `D:\Remote\GitHub\IconRig\Handouts\fontlab_live_strokes_handout.md` §7.
- **Components:** `{"component": {"glyphName": …}, "transform": {xScale, yScale, xOffset, yOffset}}`;
  layers built from recipes carry `autoRecipe` (`"=visible"`, `"=panel_down@~"`) and `flags` 16 / 17.
- **Named shared elements:** `"elementData": "lock:Regular"` + `transform` + `locked` references an element by name
  (the lock badge reused across *_lock glyphs). The renderer skips these.
- **Layer flags:** Regular 0 / 16 / 17 / absent, mask 12 / 13 — bit meanings unverified. IconRig found a written
  `"flags": 0` hides a layer, so new glyphs leave `flags` out.
- UPM must stay 960 in any VFJ we write; FontLab rescales pastes between fonts of different UPM.
- **File layout** (FontLab 8 save): 2-space indent, `"key":value` with no space, `{"point":"x y"}` kept on one line,
  empty `{}` / `[]` split over two lines, LF line ends, trailing newline. `icon_draw.dumps_vfj()` reproduces it byte for
  byte (checked 2026-11-02), so `vfj_tool.py merge` into the source VFJ diffs only the changed glyphs.

Related: [[project-icon-style]], [[project-drawing-workflow]]
