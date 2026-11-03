---
name: feedback-drawing-lessons
description: Drawing lessons from the first TypeRig Icons proofs (trash, bell, 2026-10-29) — counters, small details, construction tricks that work
metadata:
  type: feedback
---

From the first proof (trash, bell) — the user approved the approach; these are Claude's own observations:

- **Leave room between parallel strokes.** Trash bars at x 416 / 544 with 64 strokes leave 64-unit gaps and read
  dense. Aim for ≥ 96 clear between strokes inside a shape, or use fewer bars.
- **Small details vanish.** The bell clapper (r 64 → 32 counter) reads as a blob. Keep closed counters ≥ 64 clear
  or draw the detail as a single stroke (dot = filled element, not a tiny ring).
- **Build curves from quarter arcs.** `arc_to(p0, p1, center)` with handle 0.552 × r gives the same curves as the
  font; keep arc ends on the 32 grid and the radius a multiple of 32.
- **One element per stroke style.** All 64 centred butt strokes of an icon go in one `stroke()` element with many
  contours; a second element only for a different weight, cap, side or fill.
- **Check against neighbours.** Render the new icon next to related existing ones (same family / badge) before
  judging weight and size.

From the P1 batch (67 glyphs, 2026-11-02, not yet reviewed by the user):

- **Acute apexes spike.** A 60° triangle apex with a miter join runs ~64 past the node (warning). Cut the apex
  flat (two nodes 64 apart) instead of relying on FontLab's miter limit, which the renderer does not show.
- **Short cross strokes read as +.** A short line with a centred knob became a plus sign (config slider).
  Sliders need a long rail and an off-centre knob.
- **Arrow clusters crowd the centre.** Four arrowheads of leg 128 nearly meet in arrows_move; use leg 96
  with the tips out on 160 / 800.
- **A second name is a component glyph.** chevron_up = `component('fold_up')`; same for any alias, so the
  drawing stays in one place.
- **Badges cost legibility.** The top-left badge zone (≈ 96–384) fits a plus, minus, check or X; a circular
  arrow there (axis_reset) is at the limit of what reads.

**Why:** the font is read at small UI sizes in the TypeRig panels; density and tiny counters fill in first.
**How to apply:** check these points on every render; add new lessons here as the user gives feedback.
Related: [[project-icon-style]], [[project-drawing-workflow]]
