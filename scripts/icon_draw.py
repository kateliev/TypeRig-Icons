# MODULE: TypeRig Icons / Drawing helpers
# -----------------------------------------------------------
# Build TypeRig Icons glyphs as FontLab VFJ data (live strokes).
# Coordinates are font units (UPM 960), y up. See Memory/project_icon_style.md.
# -----------------------------------------------------------
# Example:
#	from icon_draw import *
#	g = glyph('trash', [stroke(
#		line((160, 704), (800, 704)),
#		line((256, 704), (288, 160), (672, 160), (704, 704)))])
#	save_proof([g], 'proof.vfj')
# -----------------------------------------------------------

import copy
import json
import os
import re

# - Init --------------------------------------------------
FONT_VFJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sources', 'typerig-icons.vfj')
UPM = 960
GRID = 32
STROKE = 64
KAPPA = 0.552	# Handle ratio used by the font's circles (circle: r 288 / handle 159)

# - Nodes -------------------------------------------------
def _fmt(v):
	v = round(v)
	return str(int(v))

def pt(x, y, smooth=False):
	'''On-curve node string'''
	return '{} {}{}'.format(_fmt(x), _fmt(y), ' s' if smooth else '')

def cubic(c1, c2, p, smooth=False):
	'''Cubic segment ending at p: "c1x c1y  c2x c2y  px py [s]"'''
	return '{} {}  {} {}  {} {}{}'.format(*map(_fmt, (c1[0], c1[1], c2[0], c2[1], p[0], p[1])), ' s' if smooth else '')

def close_cubic(c1, c2):
	'''Last cubic of a closed contour that ends back on the first node'''
	return '{} {}  {} {} c'.format(*map(_fmt, (c1[0], c1[1], c2[0], c2[1])))

# - Contours ----------------------------------------------
def line(*points, closed=False):
	'''Polyline contour; open unless closed=True'''
	c = {'nodes': [pt(*p) for p in points]}
	if not closed: c['open'] = True
	return c

def circle(cx, cy, r):
	'''Closed circle, same node layout as glyph "circle": starts at the left extreme'''
	k = r * KAPPA
	return {'nodes': [
		pt(cx - r, cy, True),
		cubic((cx - r, cy + k), (cx - k, cy + r), (cx, cy + r), True),
		cubic((cx + k, cy + r), (cx + r, cy + k), (cx + r, cy), True),
		cubic((cx + r, cy - k), (cx + k, cy - r), (cx, cy - r), True),
		close_cubic((cx - k, cy - r), (cx - r, cy - k))]}

def arc_to(p0, p1, center, smooth=True):
	'''Quarter arc from p0 to p1 around center (p0, p1 axis-aligned to center). Returns a cubic node string.'''
	d0 = (p0[0] - center[0], p0[1] - center[1])
	d1 = (p1[0] - center[0], p1[1] - center[1])
	c1 = (p0[0] + d1[0] * KAPPA, p0[1] + d1[1] * KAPPA)
	c2 = (p1[0] + d0[0] * KAPPA, p1[1] + d0[1] * KAPPA)
	return cubic(c1, c2, p1, smooth)

def path(start, *segments, closed=False):
	'''Free contour: start (x, y), then node strings from pt / cubic / arc_to'''
	c = {'nodes': [pt(*start)] + list(segments)}
	if not closed: c['open'] = True
	return c

# - Elements ----------------------------------------------
def stroke(*contours, thickness=STROKE, cap=None, join=None, proportion=None, fill=False):
	'''House live-stroke element. cap: None (butt) / 'round' / 'square'; join: None (miter) / 'round' / 'bevel';
	proportion: None = centred, 100 = one side (as in the font's "proportion": 100 elements).'''
	# Qt pen values; FontLab leaves out square cap (16) and bevel join (64) as Qt defaults
	pen = {'penCapStyle': {None: 0, 'round': 32}.get(cap), 'penJoinStyle': {None: 0, 'round': 128}.get(join),
		'penWidth': thickness, 'penMiterLimit': 3}
	pen = {k: v for k, v in pen.items() if v is not None}
	st = {'thickness': thickness}
	if cap: st['cap0'] = st['cap1'] = cap
	if join: st['join'] = join
	if proportion is not None: st['proportion'] = proportion
	e = {'elementData': {'contours': list(contours)}, 'pen': pen, 'stroke': st}
	if not fill: e['brush'] = {'style': 0}
	return e

def shape(*contours):
	'''Plain filled element (no stroke)'''
	return {'elementData': {'contours': list(contours)}}

def component(name, x_scale=1, y_scale=1, dx=0, dy=0):
	e = {'component': {'glyphName': name}}
	t = {k: v for k, v in (('xScale', x_scale), ('yScale', y_scale), ('xOffset', dx), ('yOffset', dy)) if v != (1 if 'Scale' in k else 0)}
	if t: e['transform'] = t
	return e

# - Glyphs ------------------------------------------------
def glyph(name, elements, width=UPM, unicode=None, layer='Regular'):
	g = {'name': name, 'openTypeGlyphClass': 1,
		'layers': [{'name': layer, 'advanceWidth': width, 'elements': list(elements)}]}
	if unicode: g['unicode'] = unicode if isinstance(unicode, str) else '{:04x}'.format(unicode)
	return g

def off_grid(g, grid=GRID):
	'''On-curve coordinates of a glyph that are off the grid (curve handles are not checked)'''
	bad = []
	for L in g['layers']:
		for e in L['elements']:
			for c in e.get('elementData', {}).get('contours', []) if isinstance(e.get('elementData'), dict) else []:
				for n in c['nodes']:
					nums = [float(v) for v in n.replace(' s', '').replace(' c', '').split()]
					if n.endswith(' c'): continue
					x, y = nums[-2], nums[-1]
					if x % grid or y % grid: bad.append((x, y))
	return bad

# - Files -------------------------------------------------
def load(vfj=FONT_VFJ):
	with open(vfj, encoding='utf-8') as f:
		return json.load(f)

def dumps_vfj(d):
	'''JSON text the way FontLab writes a VFJ (2-space indent, no space after ':', {"point":..} inline,
	empty {} / [] split over two lines), so a re-written source VFJ diffs only where glyphs changed'''
	out = json.dumps(d, indent=2, separators=(',', ':'), ensure_ascii=False) + '\n'
	out = re.sub(r'\{\n\s*("point":"[^"]*")\n\s*\}', r'{\1}', out)
	out = re.sub(r'(\n(\s*)[^\n]*)\{\}', lambda m: m.group(1) + '{\n' + m.group(2) + '}', out)
	out = re.sub(r'(\n(\s*)[^\n]*)\[\]', lambda m: m.group(1) + '[\n' + m.group(2) + ']', out)
	return out

def save_vfj(d, out):
	with open(out, 'w', encoding='utf-8', newline='') as f:
		f.write(dumps_vfj(d))
	return out

def save_proof(glyphs, out, header_from=FONT_VFJ):
	'''Write glyphs into a new VFJ that carries the font's header (UPM, master, guides) — open in FontLab and copy.'''
	d = load(header_from)
	d['font']['glyphs'] = copy.deepcopy(list(glyphs))
	d['font']['glyphsCount'] = len(glyphs)
	return save_vfj(d, out)
