---
name: project-glyph-todo
description: The glyph backlog is lists/glyph_todo.csv (P1-P3, 20 groups): census fixes for current plugins plus a planned catalog for a full font-editor UI
metadata:
  type: project
---

The icon backlog (2026-10-29) is `lists/glyph_todo.csv`, grouped (Arrows, Run, History, Window, Dialog, Edit, Nodes,
Contours, Elements, Glyphs, Swap, Transform, Guides & measurement, Tools, Files ...). Two origins:
- census: 82 new glyphs, 3 renames, 59 reuse of existing glyphs, each with its current call sites;
- catalog (`scripts/glyph_catalog.py`): 141 planned glyphs + 6 aliases a future font editor needs, plus one
  'exists' row per group listing the glyphs that already cover it.
Columns give group, priority, action, glyph name, meaning, a base glyph to derive it from, and call sites.

Pipeline: `scripts/icon_usage.py` scans the three projects → `lists/icon_usage.csv` (census);
`scripts/glyph_todo.py` holds the proposals as rules over the census and merges `glyph_catalog.py` → `lists/glyph_todo.csv`
(it warns when a planned name clashes with the font or a census proposal).
Rerun both after the plugins change; edit the TODO table in glyph_todo.py to add or rename proposals.

**Why:** many buttons reuse a generic icon (file_save 21 meanings, refresh 18, action_play 16) or a borrowed one
(heart = Matchmaker, contour_reverse = Swap axis masters); FontRig uses Material names missing from the font.

Aliases (chevron_up = fold_up, ok = check, cancel = close, fullscreen = arrows_expand) are extra ligature names, no drawing.

**How to apply:** draw P1 "new glyph" rows first, following [[project-drawing-workflow]] and [[project-icon-style]];
new names follow the existing families (axis_*, delta_*, file_*, config_*, panel_*, anchor_*, element_*).
After a glyph lands, the call sites in the Where column still need updating in the other repos.
