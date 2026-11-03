# SCRIPT: TypeRig Icons / Draw P1 glyphs
# -----------------------------------------------------------
# P1 "new glyph" and "alias" rows of lists/glyph_todo.csv, drawn with icon_draw.py.
#	python scripts/draw_p1.py [proof.vfj]
# Writes a proof VFJ (default: scratchpad of the caller, pass a path) and prints off-grid nodes.
# Render beside neighbours: merge into a copy of the font VFJ, then render_vfj.py.
# -----------------------------------------------------------

import math
import sys

from icon_draw import *

# - Helpers -----------------------------------------------
def arc(center, r, a0, a1, smooth=True):
	'''Circular arc from angle a0 to a1 (degrees, counter-clockwise positive) as cubic node strings,
	split into pieces of at most 90 degrees. The start point is not included.'''
	cx, cy = center
	steps = max(1, int(math.ceil(abs(a1 - a0) / 90. - 1e-9)))
	da = (a1 - a0) / steps
	out = []
	for i in range(steps):
		t0, t1 = math.radians(a0 + i * da), math.radians(a0 + (i + 1) * da)
		k = 4. / 3 * math.tan((t1 - t0) / 4) * r
		p0 = (cx + r * math.cos(t0), cy + r * math.sin(t0))
		p1 = (cx + r * math.cos(t1), cy + r * math.sin(t1))
		c1 = (p0[0] - k * math.sin(t0), p0[1] + k * math.cos(t0))
		c2 = (p1[0] + k * math.sin(t1), p1[1] - k * math.cos(t1))
		out.append(cubic(c1, c2, p1, smooth))
	return out

def at(center, r, a):
	return (center[0] + r * math.cos(math.radians(a)), center[1] + r * math.sin(math.radians(a)))

def rect(x0, y0, x1, y1):
	return line((x0, y0), (x1, y0), (x1, y1), (x0, y1), closed=True)

def dot(cx, cy, r):
	'''Filled dot as a plain shape'''
	return shape(circle(cx, cy, r))

def rounded(x0, y0, x1, y1, r):
	'''Closed rectangle with quarter-arc corners of radius r'''
	return path((x0 + r, y1),
		pt(x1 - r, y1), arc_to((x1 - r, y1), (x1, y1 - r), (x1 - r, y1 - r)),
		pt(x1, y0 + r), arc_to((x1, y0 + r), (x1 - r, y0), (x1 - r, y0 + r)),
		pt(x0 + r, y0), arc_to((x0 + r, y0), (x0, y0 + r), (x0 + r, y0 + r)),
		pt(x0, y1 - r), close_cubic(*_arc_handles((x0, y1 - r), (x0 + r, y1), (x0 + r, y1 - r))), closed=True)

def _arc_handles(p0, p1, center):
	d0 = (p0[0] - center[0], p0[1] - center[1])
	d1 = (p1[0] - center[0], p1[1] - center[1])
	return (p0[0] + d1[0] * KAPPA, p0[1] + d1[1] * KAPPA), (p1[0] + d0[0] * KAPPA, p1[1] + d0[1] * KAPPA)

def mirror_x(contour, axis=480):
	'''Mirror a contour left-right around x = axis (node strings keep their flags)'''
	out = dict(contour)
	nodes = []
	for n in contour['nodes']:
		flag = ' s' if n.endswith(' s') else (' c' if n.endswith(' c') else '')
		nums = [float(v) for v in n.replace(' s', '').replace(' c', '').split()]
		nums = [2 * axis - v if i % 2 == 0 else v for i, v in enumerate(nums)]
		pairs = [nums[i:i + 2] for i in range(0, len(nums), 2)]
		nodes.append('  '.join('{} {}'.format(*map(lambda v: str(int(round(v))), p)) for p in pairs) + flag)
	out['nodes'] = nodes
	return out

def rotate_contour(contour, quarter_turns, center=(480, 480)):
	'''Rotate a contour by 90 degree steps counter-clockwise around center'''
	out = dict(contour)
	nodes = []
	for n in contour['nodes']:
		flag = ' s' if n.endswith(' s') else (' c' if n.endswith(' c') else '')
		nums = [float(v) for v in n.replace(' s', '').replace(' c', '').split()]
		pairs = []
		for i in range(0, len(nums), 2):
			x, y = nums[i] - center[0], nums[i + 1] - center[1]
			for _ in range(quarter_turns % 4): x, y = -y, x
			pairs.append((x + center[0], y + center[1]))
		nodes.append('  '.join('{} {}'.format(int(round(x)), int(round(y))) for x, y in pairs) + flag)
	out['nodes'] = nodes
	return out

# Shared parts -------------------------------------------
LENS_C, LENS_R = (384, 576), 224		# glyph 'search'

def lens():
	'''The search lens ring and its 96 handle, as in glyph "search"'''
	return [stroke(circle(*LENS_C, LENS_R)), stroke(line((544, 416), (799, 160)), thickness=96)]

def glyph_a(dx=0, dy=0):
	'''Two-storey a of glyph "glyph_stack" (x 304-560, y 352-704), moved by dx, dy'''
	mv = lambda pts: [(x + dx, y + dy) for x, y in pts]
	return [line(*mv([(560, 448), (336, 384), (304, 416), (304, 544), (560, 544)])),
		line(*mv([(304, 672), (528, 704), (560, 672), (560, 352)]))]

# - Glyphs ------------------------------------------------
G = []

# -- Arrows & swap ------------------------------------------
G.append(glyph('arrows_left_right', [stroke(
	line((192, 480), (768, 480)),
	line((384, 672), (192, 480), (384, 288)),
	line((576, 672), (768, 480), (576, 288)))]))

G.append(glyph('arrows_up_down', [stroke(*[rotate_contour(c, 1) for c in G[-1]['layers'][0]['elements'][0]['elementData']['contours']])]))

G.append(glyph('arrows_move', [stroke(
	line((160, 480), (800, 480)), line((480, 160), (480, 800)),
	line((256, 576), (160, 480), (256, 384)), line((704, 576), (800, 480), (704, 384)),
	line((384, 704), (480, 800), (576, 704)), line((384, 256), (480, 160), (576, 256)))]))

G.append(glyph('arrows_swap_h', [stroke(
	line((160, 672), (800, 672)), line((672, 800), (800, 672), (672, 544)),
	line((800, 288), (160, 288)), line((288, 416), (160, 288), (288, 160)))]))

G.append(glyph('arrows_swap_v', [stroke(*[rotate_contour(c, 1) for c in G[-1]['layers'][0]['elements'][0]['elementData']['contours']])]))

# -- Window & layout ---------------------------------------
G.append(glyph('menu', [stroke(
	line((192, 672), (768, 672)), line((192, 480), (768, 480)), line((192, 288), (768, 288)))]))

G.append(glyph('menu_more', [shape(circle(224, 480, 64), circle(480, 480, 64), circle(736, 480, 64))]))

def toggle(on):
	pill = stroke(rounded(128, 320, 832, 640, 160))
	if on: return [pill, dot(640, 480, 96)]
	return [pill, stroke(circle(320, 480, 64))]

G.append(glyph('toggle_on', toggle(True)))
G.append(glyph('toggle_off', toggle(False)))

G.append(glyph('zoom_in', lens() + [stroke(line((288, 576), (480, 576)), line((384, 480), (384, 672)))]))
G.append(glyph('zoom_out', lens() + [stroke(line((288, 576), (480, 576)))]))
G.append(glyph('zoom_fit', [stroke(
	line((160, 352), (160, 160), (352, 160)), line((608, 160), (800, 160), (800, 352)),
	line((800, 608), (800, 800), (608, 800)), line((352, 800), (160, 800), (160, 608)),
	circle(448, 512, 128), line((544, 416), (640, 320)))]))

def padlock(open_):
	start, lead = ((320, 640), []) if open_ else ((320, 480), [pt(320, 640)])
	return [stroke(rect(224, 160, 736, 480), line((480, 288), (480, 352)),
		path(start, *lead, arc_to((320, 640), (480, 800), (480, 640)),
			arc_to((480, 800), (640, 640), (480, 640)), pt(640, 480)))]

G.append(glyph('lock', padlock(False)))
G.append(glyph('lock_off', padlock(True)))

# -- Dialog & status ---------------------------------------
G.append(glyph('search_clear', lens() + [stroke(line((320, 512), (448, 640)), line((320, 640), (448, 512)))]))

G.append(glyph('delete', [stroke(
	line((160, 704), (800, 704)),
	line((384, 704), (384, 800), (576, 800), (576, 704)),
	line((224, 704), (256, 160), (704, 160), (736, 704)),
	line((384, 576), (384, 288)), line((576, 576), (576, 288)))]))

G.append(glyph('clear', [stroke(
	line((160, 480), (352, 736), (800, 736), (800, 224), (352, 224), closed=True),
	line((480, 384), (672, 576)), line((480, 576), (672, 384)))]))

G.append(glyph('warning', [stroke(
	line((160, 192), (800, 192), (512, 768), (448, 768), closed=True),
	line((480, 384), (480, 576)), line((480, 256), (480, 320)))]))

G.append(glyph('error', [stroke(
	circle(480, 480, 320),
	line((352, 352), (608, 608)), line((352, 608), (608, 352)))]))

G.append(glyph('value_reset', [stroke(
	path((736, 448), *arc((480, 448), 256, 0, -270), pt(576, 704)),
	line((448, 576), (576, 704), (448, 832))), dot(480, 448, 64)]))

G.append(glyph('history', [stroke(
	path((480, 768), *arc((480, 480), 288, 90, -180)),
	line((96, 384), (192, 480), (288, 384)),
	line((480, 640), (480, 480), (608, 384)))]))

# -- Edit --------------------------------------------------
G.append(glyph('rename', [stroke(
	rect(160, 320, 800, 640),
	line((256, 480), (512, 480)),
	line((640, 192), (640, 768)), line((576, 768), (704, 768)), line((576, 192), (704, 192)))]))

G.append(glyph('edit', [stroke(
	line((224, 288), (224, 480), (544, 800), (736, 608), (416, 288), closed=True),
	line((448, 704), (640, 512)),
	line((480, 160), (800, 160)))]))

G.append(glyph('duplicate', [stroke(
	rect(160, 160, 608, 608),
	line((352, 704), (352, 800), (800, 800), (800, 352), (704, 352)))]))

G.append(glyph('filter', [stroke(
	line((160, 768), (800, 768), (544, 448), (544, 160), (416, 224), (416, 448), closed=True))]))

# -- Run ---------------------------------------------------
G.append(glyph('script_run', [stroke(
	line((288, 640), (128, 480), (288, 320)), line((672, 640), (832, 480), (672, 320))),
	stroke(line((416, 640), (608, 480), (416, 320), closed=True), fill=True)]))

# -- Glyphs ------------------------------------------------
G.append(glyph('glyph_unicode', [stroke(
	path((160, 768), pt(160, 384), arc_to((160, 384), (288, 256), (288, 384)),
		arc_to((288, 256), (416, 384), (288, 384)), pt(416, 768)),
	line((512, 512), (768, 512)), line((640, 384), (640, 640)))]))

G.append(glyph('glyph_next', [stroke(*glyph_a(-144, -64),
	line((608, 672), (800, 480), (608, 288)))]))
G.append(glyph('glyph_previous', [stroke(*glyph_a(240, -64),
	line((352, 672), (160, 480), (352, 288)))]))

G.append(glyph('glyph_capture', [stroke(
	line((160, 352), (160, 160), (352, 160)), line((608, 160), (800, 160), (800, 352)),
	line((800, 608), (800, 800), (608, 800)), line((352, 800), (160, 800), (160, 608)),
	*glyph_a(48, -64))]))

G.append(glyph('glyph_duplicate', [stroke(
	rect(128, 128, 576, 672), *glyph_a(-80, -128),
	line((256, 768), (256, 832), (832, 832), (832, 256), (672, 256)))]))

# -- Guides & measurement -----------------------------------
G.append(glyph('grid', [stroke(
	*[line((x, 192), (x, 768)) for x in (192, 384, 576, 768)],
	*[line((192, y), (768, y)) for y in (192, 384, 576, 768)])]))

G.append(glyph('snap', [stroke(
	path((192, 800), pt(192, 448), *arc((480, 448), 288, 180, 360), pt(768, 800), pt(640, 800), pt(640, 448),
		*arc((480, 448), 160, 0, -180), pt(320, 800), closed=True),
	line((192, 672), (320, 672)), line((640, 672), (768, 672)))]))

# -- Tools -------------------------------------------------
G.append(glyph('tool_text', [stroke(
	line((192, 672), (192, 768), (768, 768), (768, 672)),
	line((480, 768), (480, 192)), line((352, 192), (608, 192)))]))

# -- Aliases: a second ligature name for an existing drawing (component glyph) --
for alias, base in (('chevron_up', 'fold_up'), ('chevron_down', 'fold_down'), ('panel_delta', 'delta_machine'),
		('tool_zoom', 'zoom_in'), ('file_export', 'file_upload'), ('file_import', 'file_download')):
	G.append(glyph(alias, [component(base)]))

# -- Run & dialog --------------------------------------------
G.append(glyph('action_apply', [stroke(line((128, 544), (288, 352), (608, 736))),
	stroke(line((608, 416), (608, 160), (800, 288), closed=True), fill=True)]))

G.append(glyph('panel_sound', [stroke(
	line((160, 384), (288, 384), (448, 224), (448, 736), (288, 576), (160, 576), closed=True),
	path(at((448, 480), 160, -45), *arc((448, 480), 160, -45, 45)),
	path(at((448, 480), 320, -45), *arc((448, 480), 320, -45, 45)))]))

# -- Nodes ---------------------------------------------------
G.append(glyph('stroke_fake', [stroke(rounded(320, 160, 640, 800, 160), line((480, 320), (480, 640))),
	shape(rect(432, 272, 528, 368), rect(432, 592, 528, 688))]))

G.append(glyph('corner_radius', [stroke(
	path((800, 224), pt(480, 224), arc_to((480, 224), (224, 480), (480, 480)), pt(224, 800)),
	line((480, 480), (320, 320)), line((320, 448), (320, 320), (448, 320))), dot(480, 480, 48)]))

G.append(glyph('node_merge', [stroke(
	rect(192, 608, 320, 736), rect(640, 608, 768, 736),
	line((256, 608), (480, 384), (704, 608)), line((480, 384), (480, 320))),
	stroke(rect(416, 160, 544, 288), fill=True)]))

# -- Contours ------------------------------------------------
def node_marks(*corners, size=128):
	h = size // 2
	return shape(*[rect(x - h, y - h, x + h, y + h) for x, y in corners])

G.append(glyph('contour_match', [stroke(
	rect(128, 384, 320, 576), rect(640, 384, 832, 576),
	line((416, 416), (544, 416)), line((416, 544), (544, 544)))]))

G.append(glyph('contour_remove', [stroke(rect(384, 192, 768, 576), line((96, 736), (416, 736))),
	node_marks((384, 192), (768, 192), (768, 576), (384, 576))]))

G.append(glyph('contour_duplicate', [stroke(rect(160, 160, 576, 576),
	line((352, 704), (352, 800), (800, 800), (800, 352), (704, 352))),
	node_marks((160, 160), (576, 160), (576, 576), (160, 576))]))

# -- Elements ------------------------------------------------
G.append(glyph('component_decompose', [shape(rect(128, 352, 320, 608)),
	stroke(rect(640, 384, 800, 576), line((384, 480), (512, 480)), line((448, 544), (512, 480), (448, 416)))]))

# -- Guides --------------------------------------------------
G.append(glyph('guide_remove', [stroke(
	line((832, 704), (704, 704)), line((640, 704), (512, 704)), line((448, 704), (320, 704)), line((256, 704), (128, 704)),
	line((352, 224), (608, 480)), line((352, 480), (608, 224)))]))

# -- Tools ---------------------------------------------------
def finger(x, top):
	'''Up-stroke at x, round tip of radius 64 at top, back down at x + 128'''
	return [pt(x, top), arc_to((x, top), (x + 64, top + 64), (x + 64, top)), arc_to((x + 64, top + 64), (x + 128, top), (x + 64, top))]

G.append(glyph('tool_hand', [stroke(path((320, 448),
	*finger(320, 640), pt(448, 512), *finger(448, 704), pt(576, 512), *finger(576, 672), pt(704, 480), *finger(704, 576),
	pt(832, 384), arc_to((832, 384), (576, 128), (576, 384)), pt(448, 128), pt(160, 416),
	arc_to((160, 416), (224, 480), (224, 416)), pt(320, 448)))]))

# -- Delta & axes --------------------------------------------
def axis_base(slider=True, filled_ends=True):
	el = [stroke(line((480, 448), (192, 160)), line((832, 800), (640, 608)),
		rect(448, 416, 640, 608) if slider else line((448, 416), (640, 608)))]
	el.append(stroke(rect(704, 672, 832, 800), rect(191, 159, 319, 287), fill=filled_ends))
	return el

def badge_reset():
	return [stroke(path((256, 832), *arc((256, 736), 96, 90, -180)), line((96, 672), (160, 736), (224, 672)))]

G.append(glyph('axis_add', axis_base() + [stroke(line((128, 736), (384, 736)), line((256, 608), (256, 864)))]))
G.append(glyph('axis_reset', axis_base() + badge_reset()))
G.append(glyph('axis_reset_all', axis_base(slider=False, filled_ends=False) + badge_reset()))
G.append(glyph('axis_swap', axis_base() + [stroke(
	line((128, 800), (384, 800), (320, 864)), line((384, 672), (128, 672), (192, 608)))]))

def layer_base():
	'''Layer diamond and the edge under it, as in glyph "layer_add" (one-sided, vertical caps)'''
	e = stroke(line((544, 224), (860, 451), (544, 677), (227, 451), closed=True), line((228, 290), (544, 64), (861, 290)), proportion=100)
	e['stroke'].update({'cap0': 'vertical', 'cap1': 'vertical'})
	return e

G.append(glyph('axis_reseed', [layer_base()] + badge_reset()))

def delta(dy=0):
	'''Glyph "delta_machine" moved by dy'''
	return [stroke(line((832, 256 + dy), (608, 640 + dy), (482, 416 + dy), (576, 256 + dy), closed=True), fill=True),
		stroke(line((544, 256 + dy), (320, 640 + dy), (128, 256 + dy), closed=True))]

G.append(glyph('delta_bake', [stroke(line((128, 256), (512, 256), (320, 640), closed=True)),
	stroke(line((608, 640), (608, 320), (800, 480), closed=True), fill=True)]))
G.append(glyph('delta_live', delta(-64) + [dot(736, 768, 64)]))
G.append(glyph('delta_commit', delta(-64) + [stroke(line((576, 736), (640, 672), (800, 832)))]))

# -- Files & fonts --------------------------------------------
FOLD = line((640, 800), (640, 640), (768, 640))
FILE_SAVE = [line((640, 160), (800, 160), (800, 672), (677, 800), (320, 800), (320, 448)), line((608, 320), (160, 320)),
	line((448, 480), (608, 320), (448, 160)), FOLD]
FILE_OPEN = [line((480, 800), (480, 640), (640, 640), (640, 672), (512, 800), (160, 800), (160, 160), (480, 160)),
	line((768, 320), (288, 320)), line((608, 480), (768, 320), (608, 160))]

def slider_row(x0, x1, y, knob):
	return [line((x0, y), (x1, y)), line((knob, y - 64), (knob, y + 64))]

def axis_mark(x0, y0, x1, y1):
	'''Small axis: a line with filled square ends, as in the axis_* glyphs'''
	return [stroke(line((x0, y0), (x1, y1))), shape(rect(x0 - 48, y0 - 48, x0 + 48, y0 + 48), rect(x1 - 48, y1 - 48, x1 + 48, y1 + 48))]

G.append(glyph('file_new', [stroke(
	line((320, 512), (320, 160), (800, 160), (800, 672), (677, 800), (480, 800)), FOLD,
	line((96, 736), (416, 736)), line((256, 896), (256, 576)))]))

G.append(glyph('config_save', [stroke(*FILE_SAVE, *slider_row(416, 736, 544, 512))]))
G.append(glyph('config_open', [stroke(*FILE_OPEN, *slider_row(224, 576, 544, 320))]))
G.append(glyph('designspace_save', [stroke(*FILE_SAVE)] + axis_mark(416, 544, 544, 672)))
G.append(glyph('designspace_open', [stroke(*FILE_OPEN)] + axis_mark(256, 512, 384, 640)))

G.append(glyph('font_new', [stroke(
	line((288, 416), (288, 288), (224, 160), (192, 160), (128, 288), (128, 416)),
	line((576, 384), (416, 384), (416, 128)), line((560, 256), (416, 256)),
	line((832, 384), (672, 384), (672, 160), (832, 160)),
	line((352, 672), (608, 672)), line((480, 544), (480, 800)))]))

G.append(glyph('font_export', [stroke(
	rect(128, 160, 288, 384),
	line((384, 384), (576, 384)), line((480, 384), (480, 128)),
	line((832, 384), (672, 384), (672, 128)), line((800, 256), (672, 256)),
	line((480, 864), (480, 544)), line((640, 704), (480, 544), (320, 704)))]))

def glyph_A(dx=0):
	'''Letter A of glyph "glyph_active" (fixed caps, bevel join) moved by dx'''
	e = stroke(line((736 + dx, 192), (736 + dx, 288), (544 + dx, 736), (416 + dx, 736), (224 + dx, 288), (224 + dx, 192)),
		line((256 + dx, 352), (704 + dx, 352)))
	e['stroke'].update({'cap0': 'fixed', 'cap1': 'fixed', 'join': 'bevel', 'miter_limit': 2})
	return e

G.append(glyph('font_info', [glyph_A(-96), stroke(line((768, 192), (768, 512)), line((768, 576), (768, 640)))]))

# - Run ---------------------------------------------------
if __name__ == '__main__':
	out = sys.argv[1] if len(sys.argv) > 1 else 'proof_p1.vfj'
	for g in G:
		bad = off_grid(g)
		if bad: print('off grid {}: {}'.format(g['name'], bad[:6]))
	save_proof(G, out)
	print('-- {} glyphs -> {}'.format(len(G), out))
