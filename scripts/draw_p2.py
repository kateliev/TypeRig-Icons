# SCRIPT: TypeRig Icons / Draw P2 glyphs
# -----------------------------------------------------------
# P2 "new glyph" and "alias" rows of lists/glyph_todo.csv, drawn with icon_draw.py.
#	python scripts/draw_p2.py [proof.vfj]        (run from scripts/)
# Follows the user's P1 polish (Memory/feedback_drawing_lessons.md): badge top-left / object bottom-right,
# hand-chamfered acute corners, shapes that fill the 160-800 box. Shared parts are read from the source VFJ,
# so glyphs the user polished (search lens, play triangle) carry over as they are now.
# -----------------------------------------------------------

import copy
import math
import sys

from icon_draw import *
from draw_p1 import arc, at, rect, dot, rounded, rotate_contour, mirror_x

# - Font parts --------------------------------------------
FONT = {g['name']: g for g in load()['font']['glyphs']}

def from_font(name, dx=0, dy=0):
	'''Elements of a font glyph (Regular layer), moved by dx, dy'''
	L = [L for L in FONT[name]['layers'] if L.get('name') == 'Regular'][0]
	els = copy.deepcopy(L['elements'])
	if dx or dy:
		for e in els:
			for c in e.get('elementData', {}).get('contours', []) if isinstance(e.get('elementData'), dict) else []:
				c['nodes'] = [move_node(n, dx, dy) for n in c['nodes']]
	return els

def move_node(n, dx, dy):
	flag = ' s' if n.endswith(' s') else (' c' if n.endswith(' c') else '')
	nums = [float(v) for v in n.replace(' s', '').replace(' c', '').split()]
	nums = [v + (dx if i % 2 == 0 else dy) for i, v in enumerate(nums)]
	pairs = ['{} {}'.format(*(str(int(round(v))) for v in nums[i:i + 2])) for i in range(0, len(nums), 2)]
	return '  '.join(pairs) + flag

def moved(contours, dx, dy):
	out = []
	for c in contours:
		c = dict(c); c['nodes'] = [move_node(n, dx, dy) for n in c['nodes']]; out.append(c)
	return out

def turned(contours, quarter_turns, center=(480, 480)):
	return [rotate_contour(c, quarter_turns, center) for c in contours]

def mirrored(contours, axis=480):
	return [mirror_x(c, axis) for c in contours]

def chamfer(points, d=32):
	'''Closed polygon with every corner cut by d along both edges (the user's hand bevel on acute corners)'''
	out = []
	n = len(points)
	for i, p in enumerate(points):
		a, b = points[i - 1], points[(i + 1) % n]
		ua = _unit(p, a); ub = _unit(p, b)
		out += [(p[0] + ua[0] * d, p[1] + ua[1] * d), (p[0] + ub[0] * d, p[1] + ub[1] * d)]
	return line(*out, closed=True)

def _unit(p, q):
	dx, dy = q[0] - p[0], q[1] - p[1]
	l = math.hypot(dx, dy)
	return dx / l, dy / l

def ellipse(cx, cy, rx, ry):
	kx, ky = rx * KAPPA, ry * KAPPA
	return {'nodes': [
		pt(cx - rx, cy, True),
		cubic((cx - rx, cy + ky), (cx - kx, cy + ry), (cx, cy + ry), True),
		cubic((cx + kx, cy + ry), (cx + rx, cy + ky), (cx + rx, cy), True),
		cubic((cx + rx, cy - ky), (cx + kx, cy - ry), (cx, cy - ry), True),
		close_cubic((cx - kx, cy - ry), (cx - rx, cy - ky))]}

def filled(*contours):
	return stroke(*contours, fill=True)

def head(tip, direction, leg=128):
	'''Open arrowhead (two legs at 45 degrees) at tip, pointing along direction: l / r / u / d / ur / ul / dr / dl'''
	x, y = tip
	v = {'l': [(leg, leg), (leg, -leg)], 'r': [(-leg, leg), (-leg, -leg)], 'u': [(-leg, -leg), (leg, -leg)],
		'd': [(-leg, leg), (leg, leg)], 'ur': [(-leg * 1.414, 0), (0, -leg * 1.414)], 'ul': [(leg * 1.414, 0), (0, -leg * 1.414)],
		'dr': [(-leg * 1.414, 0), (0, leg * 1.414)], 'dl': [(leg * 1.414, 0), (0, leg * 1.414)]}[direction]
	return line((x + v[0][0], y + v[0][1]), (x, y), (x + v[1][0], y + v[1][1]))

# - Badges (top-left), as in the user's delta_add / delta_remove / delta_clear / delta_commit
def badge_plus():
	return [line((128, 672), (448, 672)), line((288, 512), (288, 832))]

def badge_minus():
	return [line((128, 704), (416, 704))]

def badge_x():
	return [line((175, 785), (401, 559)), line((401, 785), (175, 559))]

def badge_arrow(up=True, bar=False):
	'''Small vertical arrow at x 288; bar = a stop bar at the arrow's tip'''
	if up:
		c = [line((288, 512), (288, 768 if bar else 832)), head((288, 768 if bar else 832), 'u', 96)]
		if bar: c.append(line((160, 832), (416, 832)))
	else:
		c = [line((288, 832), (288, 576 if bar else 512)), head((288, 576 if bar else 512), 'd', 96)]
		if bar: c.append(line((160, 512), (416, 512)))
	return c

def badge_copy():
	return [rect(128, 544, 320, 736), line((224, 832), (416, 832), (416, 640))]

def badge_reset():
	return [path((288, 832), *arc((288, 704), 128, 90, -180)), head((160, 704), 'u', 64)]

# - Glyphs ------------------------------------------------
G = []
add = lambda name, els: G.append(glyph(name, els))

# -- Arrows & navigation --------------------------------------
ARROW_UR = [line((224, 224), (736, 736)), line((416, 736), (736, 736), (736, 416))]
add('arrow_up_right', [stroke(*ARROW_UR)])
add('arrow_up_left', [stroke(*turned(ARROW_UR, 1))])
add('arrow_down_left', [stroke(*turned(ARROW_UR, 2))])
add('arrow_down_right', [stroke(*turned(ARROW_UR, 3))])

CHEV2_L = [line((480, 704), (256, 480), (480, 256)), line((736, 704), (512, 480), (736, 256))]
add('chevron_double_left', [stroke(*CHEV2_L)])
add('chevron_double_right', [stroke(*mirrored(CHEV2_L))])
add('chevron_double_up', [stroke(*turned(CHEV2_L, 3))])
add('chevron_double_down', [stroke(*turned(CHEV2_L, 1))])

FIRST = [line((192, 224), (192, 736)), line((320, 480), (800, 480)), head((320, 480), 'l', 192)]
add('arrow_first', [stroke(*FIRST)])
add('arrow_last', [stroke(*mirrored(FIRST))])

add('menu_dropdown', [filled(chamfer([(224, 640), (736, 640), (480, 320)]))])

add('arrow_external', [stroke(line((448, 768), (192, 768), (192, 192), (768, 192), (768, 448)),
	line((448, 512), (800, 864 - 64)), line((576, 800), (800, 800), (800, 576)))])

def sort_glyph(ascending):
	bars = [(736, 128), (480, 224), (224, 320)] if ascending else [(736, 320), (480, 224), (224, 128)]
	tip = 192 if ascending else 768
	return [stroke(line((256, 768 if ascending else 192), (256, tip)), head((256, tip), 'd' if ascending else 'u', 128),
		*[line((480, y), (480 + w + 32 * (w // 128), y)) for y, w in bars])]

add('sort_ascending', sort_glyph(True))
add('sort_descending', sort_glyph(False))

# -- Run & media --------------------------------------------
SCRIPT = from_font('script_run')
add('script_stop', [e for e in SCRIPT if 'brush' in e] + [filled(rect(400, 400, 560, 560))])
add('script_new', [stroke(*badge_plus(), line((512, 576), (384, 416), (512, 256)), line((672, 576), (800, 416), (672, 256)))])
add('action_batch', [filled(chamfer([(160, 160), (160, 576), (544, 368)])),
	stroke(line((288, 704), (704, 704), (704, 288)), line((416, 832), (832, 832), (832, 416)))])
add('action_eject', [filled(chamfer([(192, 448), (768, 448), (480, 768)])), filled(rect(192, 192, 768, 288))])
STEP = [filled(chamfer([(224, 192), (224, 768), (576, 480)])), stroke(line((704, 192), (704, 768)))]
add('action_step_forward', STEP)
add('action_step_back', [filled(*mirrored(STEP[0]['elementData']['contours'])), stroke(*mirrored(STEP[1]['elementData']['contours']))])

# -- History ------------------------------------------------
UNDO = from_font('undo')
add('revert', from_font('undo', 64) + [stroke(line((128, 512), (128, 832)))])
add('undo_off', UNDO + [stroke(line((160, 160), (800, 800)))])
add('undo_clear', UNDO + [stroke(line((320, 352), (512, 544)), line((320, 544), (512, 352)))])
add('snapshot_restore', [stroke(rect(160, 576, 384, 800)), filled(rect(160, 160, 384, 384)),
	stroke(path((512, 704), pt(608, 704), arc_to((608, 704), (832, 480), (608, 480)), arc_to((832, 480), (608, 256), (608, 480)), pt(512, 256)),
		head((512, 256), 'l', 96))])

# -- Window & layout ------------------------------------------
LENS = from_font('search')
LENS_C = (416, 544)
add('view_zoom', LENS + [stroke(rect(352, 480, 480, 608))])

def gear(cx, cy, teeth=8, r_out=320, r_base=240, w_out=10, w_base=16):
	pts = []
	for i in range(teeth):
		a = 360. / teeth * i + 90
		pts += [at((cx, cy), r_base, a - w_base), at((cx, cy), r_out, a - w_out), at((cx, cy), r_out, a + w_out), at((cx, cy), r_base, a + w_base)]
	return line(*pts, closed=True)

add('settings', [stroke(gear(480, 480), circle(480, 480, 96))])
add('view_padding', [stroke(rect(160, 160, 800, 800)), filled(rect(384, 384, 576, 576))])
add('menu_more_vertical', [shape(circle(480, 224, 64), circle(480, 480, 64), circle(480, 736, 64))])
add('zoom_actual', LENS + [stroke(line((320, 448), (320, 640)), line((512, 448), (512, 640))), shape(rect(392, 472, 440, 520), rect(392, 568, 440, 616))])
add('zoom_selection', from_font('selection_basic') + [stroke(circle(448, 512, 128), line((544, 416), (640, 320)))])
DOCK = [rect(160, 160, 800, 800), line((352, 160), (352, 800))]
add('panel_dock', [stroke(*DOCK, line((736, 480), (480, 480)), head((480, 480), 'l', 96))])
add('panel_undock', [stroke(*DOCK, line((480, 480), (736, 480)), head((736, 480), 'r', 96))])
add('tab_add', [stroke(line((160, 160), (800, 160), (800, 608), (480, 608), (480, 768), (160, 768), closed=True),
	line((352, 384), (608, 384)), line((480, 256), (480, 512)))])
add('keyboard', [stroke(rect(128, 224, 832, 736),
	*[line((x - 32, y), (x + 32, y)) for y in (608, 480) for x in (288, 416, 544, 672)],
	line((288, 352), (672, 352)))])

# -- Dialog & status ------------------------------------------
add('success', [stroke(circle(480, 480, 320), line((320, 480), (448, 352), (672, 608)))])
add('busy', [stroke(line((224, 800), (736, 800)), line((224, 160), (736, 160)),
	line((320, 800), (320, 704), (448, 480), (320, 256), (320, 160)), line((640, 800), (640, 704), (512, 480), (640, 256), (640, 160))),
	filled(chamfer([(400, 224), (560, 224), (480, 352)], 16))])
add('ok', [component('check')])
add('cancel', [component('close')])

# -- Edit & clipboard ----------------------------------------
add('add', [stroke(line((192, 480), (768, 480)), line((480, 192), (480, 768)))])
add('remove', [stroke(line((192, 480), (768, 480)))])
add('tag', [stroke(line((352, 160), (416, 800)), line((544, 160), (608, 800)), line((192, 352), (768, 352)), line((192, 608), (768, 608)))])
LINK = [path((448, 608), pt(288, 608), arc_to((288, 608), (160, 480), (288, 480)), arc_to((160, 480), (288, 352), (288, 480)), pt(448, 352)),
	path((512, 608), pt(672, 608), arc_to((672, 608), (800, 480), (672, 480)), arc_to((800, 480), (672, 352), (672, 480)), pt(512, 352))]
add('link', [stroke(*LINK, line((352, 480), (608, 480)))])
add('link_off', [stroke(*LINK, line((224, 224), (736, 736)))])
add('clipboard_cut', [stroke(circle(288, 288, 96), circle(672, 288, 96), line((356, 356), (640, 800)), line((604, 356), (320, 800)))])
add('search_replace', [stroke(circle(320, 640, 160), line((432, 528), (512, 448)),
	line((576, 416), (832, 416)), head((832, 416), 'r', 64), line((832, 192), (576, 192)), head((576, 192), 'l', 64))])

def drop(cx, cy, r, apex):
	'''Teardrop: circle at (cx, cy) with tangents to an apex straight above'''
	d = apex - cy
	a = math.degrees(math.asin(r / d))
	p_r, p_l = at((cx, cy), r, a), at((cx, cy), r, 180 - a)
	return path((cx, apex), pt(*p_l), *arc((cx, cy), r, 180 - a, 360 + a), pt(cx, apex), closed=True)

add('color_mark', [stroke(drop(480, 384, 224, 800))])
add('note', [stroke(line((160, 800), (800, 800), (800, 288), (416, 288), (256, 160), (256, 288), (160, 288), closed=True),
	line((288, 640), (672, 640)), line((288, 480), (544, 480)))])
add('tree_expand', [stroke(rect(224, 224, 736, 736), line((320, 480), (640, 480)), line((480, 320), (480, 640)))])
add('tree_collapse', [stroke(rect(224, 224, 736, 736), line((320, 480), (640, 480)))])

# -- Selection ----------------------------------------------
add('select_none', [stroke(*[c for y in (768, 512, 256) for c in (line((128, y - 64), (256, y + 64)), line((128, y + 64), (256, y - 64)))],
	line((352, 768), (832, 768)), line((352, 512), (704, 512)), line((352, 256), (576, 256)))])
add('tool_lasso', [stroke(ellipse(512, 576, 288, 192),
	path((352, 416), cubic((288, 352), (352, 288), (320, 224)), cubic((304, 192), (256, 160), (224, 160))))])

# -- Nodes ---------------------------------------------------
add('stem_center', [stroke(rect(320, 160, 640, 800), line((480, 224), (480, 352)), line((480, 416), (480, 544)), line((480, 608), (480, 736)))])
add('node_swap', [filled(rect(160, 576, 288, 704), rect(672, 256, 800, 384)),
	stroke(line((352, 640), (800, 640)), head((800, 640), 'r', 160), line((608, 320), (160, 320)), head((160, 320), 'l', 160))])
add('node_smooth_toggle', [stroke(path((480, 640), *arc((480, 480), 160, 90, 270), pt(640, 320), pt(640, 640), closed=True),
	line((128, 480), (256, 480)), line((704, 480), (832, 480)))])
add('node_tangent', [stroke(line((352, 480), (480, 608), (608, 480), (480, 352), closed=True), line((128, 480), (320, 480)),
	path((640, 480), cubic((768, 480), (832, 576), (832, 736))))])
DIST_H = [line((160, 160), (160, 800)), line((480, 160), (480, 800)), line((800, 160), (800, 800))]
DIST_H_NODES = [rect(96, 576, 224, 704), rect(416, 256, 544, 384), rect(736, 480, 864, 608)]
add('node_distribute_h', [stroke(*DIST_H), filled(*DIST_H_NODES)])
add('node_distribute_v', [stroke(*turned(DIST_H, 1)), filled(*turned(DIST_H_NODES, 1))])
add('node_simplify', [stroke(*badge_minus(), path((416, 192), cubic((416, 576), (800, 576), (800, 192)))),
	shape(rect(368, 144, 464, 240), rect(752, 144, 848, 240))])
add('node_add_intersection', [stroke(*badge_plus(), line((448, 192), (800, 544)), line((448, 544), (800, 192))),
	filled(rect(576, 320, 672, 416))])

# -- Contours ------------------------------------------------
add('contour_color', [filled(rect(160, 160, 544, 544)), stroke(rect(416, 416, 800, 800))])
add('contour_join', [stroke(line((448, 224), (192, 224), (192, 736), (448, 736)), line((512, 736), (768, 736), (768, 224), (512, 224))),
	shape(rect(432, 688, 528, 784), rect(432, 176, 528, 272))])
add('contour_offset', [stroke(rounded(160, 160, 800, 800, 160), rect(352, 352, 608, 608))])
add('contour_stroke_expand', [stroke(line((192, 800), (352, 800), (352, 352), (800, 352), (800, 192), (192, 192), closed=True))])

def contour_mini(dx=0):
	return [stroke(rect(160 + dx, 320, 448 + dx, 608)), shape(*[rect(x - 48, y - 48, x + 48, y + 48) for x in (160 + dx, 448 + dx) for y in (320, 608)])]

add('contour_next', contour_mini() + [stroke(line((608, 672), (800, 480), (608, 288)))])
add('contour_previous', contour_mini(352) + [stroke(line((352, 672), (160, 480), (352, 288)))])

# -- Elements & components -----------------------------------
SHAPE_OUT = from_font('shape')[0]['elementData']['contours'][0]
add('component', [stroke(SHAPE_OUT)])

def mini_shape(fill_=True, dx=0, dy=0):
	parts = moved([rect(384, 160, 608, 384), circle(640, 448, 160)], dx, dy)
	return [filled(*parts)] if fill_ else [stroke(*parts)]

add('element_add', [stroke(*badge_plus())] + mini_shape())
add('element_remove', [stroke(*badge_minus())] + mini_shape())
add('component_add', [stroke(*badge_plus())] + mini_shape(False))
add('element_duplicate', mini_shape(True, -224, 0) + [stroke(line((448, 736), (448, 832), (832, 832), (832, 448), (768, 448)))])
add('element_eject', mini_shape() + [filled(chamfer([(160, 640), (416, 640), (288, 800)], 24)), filled(rect(160, 512, 416, 560))])
HALF = path((448, 800), *arc((448, 480), 320, 90, 270), closed=True)
add('element_split', [filled(HALF, mirror_x(HALF, 480 + 32))])
add('element_merge', [filled(circle(256, 672, 64), circle(704, 672, 64)), stroke(line((256, 608), (480, 384), (704, 608)), line((480, 384), (480, 320))),
	filled(rect(416, 160, 544, 288))])

STACK = [filled(rect(384, 160, 640, 416)), stroke(line((672, 320), (800, 320), (800, 576), (544, 576), (544, 448)))]
add('element_group', [stroke(rect(160, 160, 800, 800)), filled(rect(320, 320, 448, 448), rect(512, 512, 640, 640))])
add('element_ungroup', [stroke(*[line(a, b) for a, b in (((160, 160), (352, 160)), ((608, 160), (800, 160)), ((800, 160), (800, 352)), ((800, 608), (800, 800)),
	((800, 800), (608, 800)), ((352, 800), (160, 800)), ((160, 800), (160, 608)), ((160, 352), (160, 160)))]), filled(rect(320, 320, 448, 448), rect(512, 512, 640, 640))])
add('element_forward', STACK + [stroke(*badge_arrow(True))])
add('element_backward', STACK + [stroke(*badge_arrow(False))])
add('element_front', STACK + [stroke(*badge_arrow(True, bar=True))])
add('element_back', STACK + [stroke(*badge_arrow(False, bar=True))])

# -- Glyphs --------------------------------------------------
A_BARE = from_font('glyph_add')
A_BARE = [dict(A_BARE[0], elementData={'contours': A_BARE[0]['elementData']['contours'][:2]})]	# the 'a' without the plus
add('glyph_search', A_BARE + [stroke(circle(224, 736, 96), line((292, 668), (352, 608)))])

def star(cx, cy, r_out, r_in, points=5):
	return line(*[at((cx, cy), r_out if i % 2 == 0 else r_in, 90 + 180. / points * i) for i in range(points * 2)], closed=True)

add('glyph_key', A_BARE + [shape(star(256, 704, 160, 72))])
add('glyph_open', [stroke(line((544, 800), (160, 800), (160, 160), (800, 160), (800, 416)), *from_font('glyph_stack', -64, -96)[0]['elementData']['contours'][:2],
	line((576, 576), (832, 832)), line((640, 832), (832, 832), (832, 640)))])
add('glyph_clear', [stroke(rect(160, 160, 800, 800), line((352, 352), (608, 608)), line((352, 608), (608, 352)))])
add('glyph_compose', [stroke(*moved(A_BARE[0]['elementData']['contours'], -80, 0), line((448, 672), (576, 832)))])
add('charset', [stroke(*from_font('view_icons')[0]['elementData']['contours']), filled(rect(192, 576, 384, 768), rect(192, 192, 384, 384), rect(576, 192, 768, 384))])
add('compare', [stroke(line((480, 160), (480, 768)), line((320, 160), (640, 160)), line((160, 704), (800, 704)),
	line((224, 704), (128, 448), (320, 448), closed=True), line((736, 704), (640, 448), (832, 448), closed=True))])

# -- Anchors -------------------------------------------------
ANCHOR = [circle(640, 576, 64), line((640, 512), (640, 128)), line((544, 448), (736, 448)),
	path((448, 320), *arc((640, 320), 192, 180, 360))]
add('anchor_add', [stroke(*badge_plus(), *ANCHOR)])
add('anchor_remove', [stroke(*badge_minus(), *ANCHOR)])
add('anchor_copy', [stroke(*badge_copy(), *ANCHOR)])
add('anchor_paste', [stroke(rect(160, 544, 384, 800), rect(224, 768, 320, 832), *ANCHOR)])
add('anchor_move', [stroke(line((128, 704), (448, 704)), line((288, 544), (288, 864)), head((128, 704), 'l', 48), head((448, 704), 'r', 48),
	head((288, 864), 'u', 48), head((288, 544), 'd', 48), *ANCHOR)])

# -- Transform -----------------------------------------------
CORNERS = [rect(128, 128, 256, 256), rect(704, 128, 832, 256), rect(704, 704, 832, 832), rect(128, 704, 256, 832)]
add('transform', [filled(*CORNERS), stroke(line((256, 480), (704, 480)), line((480, 256), (480, 704)),
	head((256, 480), 'l', 64), head((704, 480), 'r', 64), head((480, 704), 'u', 64), head((480, 256), 'd', 64))])
add('scale_fit', [stroke(rect(160, 160, 800, 800), line((256, 256), (416, 416)), line((416, 320), (416, 416), (320, 416)),
	line((704, 704), (544, 544)), line((544, 640), (544, 544), (640, 544)))])
ROT_CW = [rect(160, 160, 480, 480), path((288, 672), *arc((288, 288), 384, 90, 0)), head((672, 288), 'd', 96)]
add('rotate_cw_90', [stroke(*ROT_CW)])
add('rotate_ccw_90', [stroke(*mirrored(ROT_CW))])
add('transform_reset', [filled(*CORNERS), stroke(path((288, 480), *arc((480, 480), 192, 180, -90)), head((288, 480), 'u', 64))])
add('transform_pivot', [stroke(circle(480, 480, 192), line((480, 160), (480, 352)), line((480, 608), (480, 800)),
	line((160, 480), (352, 480)), line((608, 480), (800, 480))), dot(480, 480, 48)])

# -- Guides & measurement -------------------------------------
DASH_H = [line((832, 704), (704, 704)), line((640, 704), (512, 704)), line((448, 704), (320, 704)), line((256, 704), (128, 704))]
add('metrics_copy', [stroke(*badge_copy(), line((448, 160), (448, 480)), line((832, 160), (832, 480)), line((512, 320), (768, 320)),
	head((512, 320), 'l', 64), head((768, 320), 'r', 64))])
add('guide_lock', [stroke(*DASH_H, rect(320, 160, 640, 416),
	path((384, 416), pt(384, 512), arc_to((384, 512), (480, 608), (480, 512)), arc_to((480, 608), (576, 512), (480, 512)), pt(576, 416)))])
add('guide_angled', [stroke(line((160, 192), (800, 192)), line((352, 192), (416, 352)), line((448, 432), (512, 592)), line((544, 672), (608, 832)),
	path(at((352, 192), 224, 0), *arc((352, 192), 224, 0, 68)))])
add('ruler', [stroke(line((160, 160), (160, 800), (800, 800)),
	*[line((x, 800), (x, 704 if i % 2 else 736)) for i, x in enumerate((288, 416, 544, 672))],
	*[line((160, y), (256 if i % 2 else 224, y)) for i, y in enumerate((672, 544, 416, 288))])])
add('metrics_center', [stroke(line((160, 160), (160, 800)), line((800, 160), (800, 800)),
	line((224, 480), (320, 480)), head((320, 480), 'r', 64), line((736, 480), (640, 480)), head((640, 480), 'l', 64)), filled(rect(416, 288, 544, 672))])
add('kern_pair', [stroke(line((160, 192), (272, 768), (304, 768), (416, 192)), line((208, 384), (368, 384)),
	line((544, 768), (656, 192), (688, 192), (800, 768)))])

# -- Delta & axes --------------------------------------------
ROWS = [line((416, 768), (832, 768)), line((416, 512), (832, 512)), line((416, 256), (832, 256))]
add('row_inherit', [stroke(*ROWS, line((224, 768), (224, 256), (320, 256)), line((224, 512), (320, 512)),
	head((320, 512), 'r', 64), head((320, 256), 'r', 64))])
add('row_fold', [stroke(line((160, 736), (384, 736)), line((160, 480), (384, 480)), line((160, 224), (384, 224)),
	line((384, 736), (576, 480)), line((384, 224), (576, 480)), line((384, 480), (832, 480)))])

# -- Tools (symbol top-left, filled pointer bottom-right) -------
POINTER = shape(line((512, 544), (512, 192), (608, 288), (672, 160), (736, 192), (672, 320), (800, 320), closed=True))
add('tool_rotate', [stroke(path((288, 832), *arc((288, 672), 160, 90, -180)), head((128, 672), 'u', 64)), POINTER])
add('tool_scale', [stroke(line((160, 512), (416, 768)), line((160, 640), (160, 512), (288, 512)), line((288, 768), (416, 768), (416, 640))), POINTER])
add('tool_metrics', [stroke(line((128, 512), (128, 832)), line((448, 512), (448, 832)), line((192, 672), (384, 672)),
	head((192, 672), 'l', 48), head((384, 672), 'r', 48)), POINTER])
add('tool_kern', [stroke(line((128, 512), (208, 832), (240, 832), (320, 512)), line((160, 608), (288, 608)), line((256, 832), (336, 512), (368, 512), (448, 832))), POINTER])
add('tool_anchor', [stroke(line((288, 512), (288, 768)), line((224, 704), (352, 704)), path((160, 640), *arc((288, 640), 128, 180, 360))),
	dot(288, 816, 48), POINTER])

# -- Files & fonts -------------------------------------------
CLIP = from_font('clipboard')
add('clipboard_save', CLIP + [stroke(line((544, 640), (544, 320)), head((544, 320), 'd', 96))])
add('clipboard_open', CLIP + [stroke(line((544, 288), (544, 608)), head((544, 608), 'u', 96))])
add('folder_open', [stroke(line((736, 544), (736, 672), (448, 672), (384, 736), (160, 736), (160, 224)),
	line((160, 224), (288, 544), (864, 544), (736, 224), closed=True))])

def letter_A(x0, x1):
	e = stroke(line((x1, 192), (x1, 288), (x1 - 160, 736), (x0 + 160, 736), (x0, 288), (x0, 192)), line((x0 + 32, 352), (x1 - 32, 352)))
	e['stroke'].update({'cap0': 'fixed', 'cap1': 'fixed', 'join': 'round', 'miter_limit': 2})
	return e

add('font', [letter_A(128, 512), stroke(*moved(from_font('glyph_stack')[0]['elementData']['contours'][:2], 272, -160))])
FILE = [line((320, 160), (800, 160), (800, 672), (677, 800), (320, 800), closed=True), line((640, 800), (640, 640), (768, 640))]
add('file_reload', [stroke(*FILE, path((560, 576), *arc((560, 416), 160, 90, -180)), head((400, 416), 'u', 64))])
add('font_features', [stroke(*FILE, line((512, 544), (416, 448), (512, 352)), line((608, 544), (704, 448), (608, 352)))])
LAYERS3 = [line((608, 768), (832, 608), (608, 448), (384, 608), closed=True), line((384, 448), (608, 288), (832, 448)), line((384, 288), (608, 128), (832, 288))]
add('master_add', [stroke(*LAYERS3, line((96, 736), (352, 736)), line((224, 608), (224, 864)))])
add('instance', [stroke(*LAYERS3), shape(star(224, 736, 128, 56))])
add('audit', [stroke(line((480, 832), (192, 736), (192, 448), (480, 160), (768, 448), (768, 736), closed=True),
	line((352, 480), (448, 384), (608, 576)))])
add('image', [stroke(rect(160, 192, 800, 768), line((224, 256), (416, 512), (512, 416), (576, 480), (736, 256))), dot(608, 640, 64)])

# - Run ---------------------------------------------------
if __name__ == '__main__':
	out = sys.argv[1] if len(sys.argv) > 1 else 'proof_p2.vfj'
	names = [g['name'] for g in G]
	dupes = [n for n in names if names.count(n) > 1]
	clash = [n for n in names if n in FONT]
	if dupes: print('! duplicate names:', sorted(set(dupes)))
	if clash: print('! already in the font:', clash)
	save_proof(G, out)
	print('-- {} glyphs -> {}'.format(len(G), out))
