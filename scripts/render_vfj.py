# SCRIPT: TypeRig Icons / Render VFJ glyphs
# -----------------------------------------------------------
# Draw glyphs of a FontLab VFJ (live strokes) to a PNG contact sheet for a visual check.
# Usage:
#	python scripts/render_vfj.py <font.vfj> <out.png> <name|pattern> [...] [--cols N] [--layer Regular] [--mask]
# Patterns use fnmatch: 'node_*', 'layer_?dd'. With no names, every glyph is drawn.
# Limits: FontLab caps 'vertical'/'horizontal' draw as butt; one-sided strokes ("proportion") draw centred;
# named shared elements ("elementData": "lock:Regular") are skipped and listed on stdout.
# -----------------------------------------------------------

import argparse
import fnmatch
import json
import math
import re

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch

# - Init --------------------------------------------------
UPM = 960
CELL = 2.0		# Inches per glyph box
TITLE = 0.3		# Inches above each box for the name
DPI = 80
SCALE = CELL * 72 / UPM	# Points per font unit (line widths are in points)
KEYLINES = (64, 128, 832, 896)
CAPS = {'round': 'round', 'square': 'projecting'}
JOINS = {0: 'miter', 128: 'round', 64: 'bevel'}

# - Geometry ----------------------------------------------
def parse_node(s):
	nums = [float(v) for v in re.findall(r'-?\d+(?:\.\d+)?', s)]
	return [(nums[i], nums[i + 1]) for i in range(0, len(nums) - 1, 2)], s.strip().endswith(' c')

def contour_path(c, t):
	nodes = c['nodes']
	start = parse_node(nodes[0])[0][-1]
	verts, codes = [start], [Path.MOVETO]

	for n in nodes[1:]:
		p, closing = parse_node(n)
		if closing and len(p) == 2: p = p + [start]
		verts += p
		codes += {1: [Path.LINETO], 2: [Path.CURVE3] * 2, 3: [Path.CURVE4] * 3}[len(p)]

	if not c.get('open'):
		verts.append(start); codes.append(Path.CLOSEPOLY)

	xs, ys, dx, dy = t
	return Path([(x * xs + dx, y * ys + dy) for x, y in verts], codes)

def compose(outer, e):
	t = e.get('transform') or {}
	xs, ys, dx, dy = outer
	return (t.get('xScale', 1) * xs, t.get('yScale', 1) * ys, t.get('xOffset', 0) * xs + dx, t.get('yOffset', 0) * ys + dy)

# - Drawing -----------------------------------------------
def get_layer(g, name):
	for L in g.get('layers', []):
		if L.get('name') == name: return L
	return None

def draw_layer(ax, glyphs, layer, t, color, skipped, layer_name):
	for e in layer.get('elements', []):
		tt = compose(t, e)

		if 'component' in e:
			g = glyphs.get(e['component']['glyphName'])
			L = get_layer(g, layer_name) if g else None
			if L: draw_layer(ax, glyphs, L, tt, color, skipped, layer_name)
			continue

		ed = e.get('elementData')
		if not isinstance(ed, dict):
			skipped.append(str(ed)); continue

		st, pen = e.get('stroke') or {}, e.get('pen') or {}
		filled = 'brush' not in e

		for c in ed.get('contours', []):
			p = contour_path(c, tt)
			if 'thickness' in st:
				cap = CAPS.get(st.get('cap0'), 'butt')
				join = st.get('join') or JOINS.get(pen.get('penJoinStyle', 0), 'miter')
				ax.add_patch(PathPatch(p, fill=False, lw=st['thickness'] * SCALE, capstyle=cap, joinstyle=join, color=color))
				if filled and not c.get('open'):
					ax.add_patch(PathPatch(p, fill=True, lw=0, color=color))
			else:
				ax.add_patch(PathPatch(p, fill=True, lw=0, color=color))

def render(vfj, out, patterns, cols=6, layer='Regular', mask=False):
	with open(vfj, encoding='utf-8') as f:
		font_glyphs = json.load(f)['font']['glyphs']

	glyphs = {g['name']: g for g in font_glyphs}
	order = [g['name'] for g in font_glyphs]
	names = []
	for p in patterns or ['*']:
		for n in (fnmatch.filter(order, p) if any(ch in p for ch in '*?[') else [p]):
			if n not in names: names.append(n)

	cols = max(1, min(cols, len(names)))
	rows = math.ceil(len(names) / cols)
	w, h = cols * CELL, rows * (CELL + TITLE)
	fig = plt.figure(figsize=(w, h))
	skipped_all = {}

	for i, name in enumerate(names):
		r, c = divmod(i, cols)
		ax = fig.add_axes([c * CELL / w, 1 - (r + 1) * (CELL + TITLE) / h, CELL / w, CELL / h])
		ax.set_xlim(0, UPM); ax.set_ylim(0, UPM); ax.set_xticks([]); ax.set_yticks([])
		for k in KEYLINES:
			ax.axhline(k, color='#cde', lw=0.5); ax.axvline(k, color='#cde', lw=0.5)
		ax.set_title(name if name in glyphs else name + ' (missing)', fontsize=8)

		g = glyphs.get(name)
		if not g: continue
		skipped = []
		if mask:
			M = get_layer(g, 'mask')
			if M: draw_layer(ax, glyphs, M, (1, 1, 0, 0), '#e88', skipped, 'mask')
		L = get_layer(g, layer) or g['layers'][0]
		draw_layer(ax, glyphs, L, (1, 1, 0, 0), 'black', skipped, layer)
		if skipped: skipped_all[name] = skipped

	fig.savefig(out, dpi=DPI)
	for n, s in skipped_all.items():
		print('Skipped named elements in {}: {}'.format(n, ', '.join(s)))
	print('Rendered {} glyphs -> {}'.format(len(names), out))

# - Run ---------------------------------------------------
if __name__ == '__main__':
	ap = argparse.ArgumentParser(description=__doc__)
	ap.add_argument('vfj')
	ap.add_argument('out')
	ap.add_argument('names', nargs='*')
	ap.add_argument('--cols', type=int, default=6)
	ap.add_argument('--layer', default='Regular')
	ap.add_argument('--mask', action='store_true', help='Draw the mask layer under the glyph in red')
	a = ap.parse_args()
	render(a.vfj, a.out, a.names, a.cols, a.layer, a.mask)
