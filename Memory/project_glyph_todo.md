---
name: project-glyph-todo
description: The glyph backlog is lists/glyph_todo.csv (P1-P3), built from the icon usage census of Typerig-Glyphs, TypeRig Scripts and FontRig editor
metadata:
  type: project
---

The icon backlog (2026-10-29) is `lists/glyph_todo.csv`: 82 new glyphs, 3 renames, 59 places where an
existing glyph should replace a wrong icon or a text-only button. Columns give priority, the glyph name to draw,
its meaning, a base glyph to derive it from, the icon it replaces and every call site.

Pipeline: `scripts/icon_usage.py` scans the three projects → `lists/icon_usage.csv` (census);
`scripts/glyph_todo.py` holds the proposals as rules over the census → `lists/glyph_todo.csv`.
Rerun both after the plugins change; edit the TODO table in glyph_todo.py to add or rename proposals.

**Why:** many buttons reuse a generic icon (file_save 21 meanings, refresh 18, action_play 16) or a borrowed one
(heart = Matchmaker, contour_reverse = Swap axis masters); FontRig uses Material names missing from the font.

**How to apply:** draw P1 "new glyph" rows first, following [[project-drawing-workflow]] and [[project-icon-style]];
new names follow the existing families (axis_*, delta_*, file_*, config_*, panel_*, anchor_*, element_*).
After a glyph lands, the call sites in the Where column still need updating in the other repos.
