# SCRIPT: TypeRig Icons / Glyph to-do list
# -----------------------------------------------------------
# Turn the icon census (lists/icon_usage.csv, from icon_usage.py) into a glyph to-do list:
# new glyphs to draw, glyphs to rename, and places where an existing glyph should replace
# a wrong / overloaded / missing icon or a text-only button.
#	python scripts/glyph_todo.py [usage.csv] [out.csv]
# The proposals live in TODO below; each rule picks its census rows, so 'Where' stays current
# when the census is regenerated. A census row goes to the first rule that matches it.
# Planned glyphs without call sites (the rest of a font-editor UI) live in glyph_catalog.py.
# -----------------------------------------------------------

import csv
import json
import os
import re
import sys
from collections import OrderedDict

from glyph_catalog import *

# - Init --------------------------------------------------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USAGE_CSV = os.path.join(ROOT, 'lists', 'icon_usage.csv')
TODO_CSV = os.path.join(ROOT, 'lists', 'glyph_todo.csv')
FONT_VFJ = os.path.join(ROOT, 'sources', 'typerig-icons.vfj')

COLUMNS = ['Group', 'Priority', 'Action', 'Glyph', 'Meaning', 'Draw from', 'Replaces', 'Count', 'Captions', 'Where', 'Origin']
ACTION_ORDER = ['exists', 'rename glyph', 'new glyph', 'alias', 'use existing']

REN, USE = 'rename glyph', 'use existing'

VALUES, LAYERS, ANCHORS, DELTA = 'Values & controls', 'Layers', 'Anchors', 'Delta & axes'
GROUP_ORDER = [ARROWS, RUN, HISTORY, WINDOW, DIALOG, EDIT, VALUES, SELECT, NODES, CONTOURS, ELEMENTS, GLYPHS,
		LAYERS, ANCHORS, SWAP, TRANSFORM, MEASURE, DELTA, TOOLS, FILES]

# Group of a TODO glyph by name; first match wins
GROUP_RULES = [
	(r'^(arrow|chevron|keyboard)', ARROWS), (r'^(action_(?!apply)|script|python)', RUN),
	(r'^(undo|redo|revert|snapshot)', HISTORY), (r'^(panel|window|view|zoom|menu|toggle|settings)', WINDOW),
	(r'^(alert|warning|spark|check|close|search_clear|action_apply|value_reset)', DIALOG), (r'^value_', VALUES),
	(r'^(clipboard_(?!save|open)|tag|rename|add$|remove$|link)', EDIT), (r'^select', SELECT),
	(r'^(node|curve|corner|stem_center|stroke_fake)', NODES), (r'^(contour|hobby|pen_|cap_)', CONTOURS),
	(r'^(element|component)', ELEMENTS), (r'^glyph', GLYPHS), (r'^(layer|visible)', LAYERS), (r'^anchor', ANCHORS),
	(r'^(axis|delta|row_|gravity|centroid|stem_compensation)', DELTA), (r'swap', SWAP), (r'^(transform|scale|rotate|skew|translate|flip)', TRANSFORM),
	(r'^(guide|dimension|metrics|stem|kern|slope)', MEASURE),
	(r'^(tool|draw)', TOOLS),
	(r'^(file|font|config|designspace|folder|clipboard)', FILES),
]

def group_of(glyph):
	for pattern, group in GROUP_RULES:
		if re.search(pattern, glyph): return group
	return EDIT

# Rule keys (all given keys must match a census row):
#	icon - current icon (str or tuple), '' = text-only button
#	cap  - regex on the caption (case-insensitive)
#	name - regex on the button/action name
#	src  - regex on the source path
# (priority, action, glyph, meaning, draw from, [rules])
TODO = [
	# - P1: broken, missing or placeholder icons ----------------------
	('P1', REN, 'keyboard_arrows', 'Arrow-key nudge / keyboard capture (fix typo keyboard_arows; keep the old name as an alias until the 3 call sites move)', 'keyboard_arows', [
		dict(icon='keyboard_arows')]),
	('P1', REN, 'pen_cap_butt', 'Rename pen_capp_butt (typo); no code uses it yet', 'pen_capp_butt', []),
	('P1', REN, 'pen_cap_angle', 'Rename pen_capp_angle (typo); no code uses it yet', 'pen_capp_angle', []),
	('P1', USE, 'clipboard_copy', 'Copy message / error (FontRig uses the Material name content_copy, not in font)', '', [
		dict(icon='content_copy')]),
	('P1', USE, 'alert', 'Error header (FontRig uses Material name warning, not in font; or draw the planned warning glyph)', '', [
		dict(icon='warning')]),
	('P1', USE, 'spark', 'AI self-correcting header (FontRig uses Material name auto_fix_high, not in font)', '', [
		dict(icon='auto_fix_high')]),
	('P1', NEW, 'rename', 'Rename: layer, glyph name, anchors, elements (FontRig already asks for it)', 'label + text cursor', [
		dict(icon='rename'), dict(icon='glyph_active', name=r'btn_setName'),
		dict(icon='', name=r'btn_anchorRename'), dict(icon='', cap=r'^rename$', src=r'ElementNew')]),
	('P1', NEW, 'stroke_fake', 'Fake stroke: rebuild a clean stroke from two contours (button shows the letter S)', 'channel_process', [
		dict(icon='S')]),
	('P1', NEW, 'corner_radius', 'Corner value is a radius toggle (button shows the letter R)', 'corner_round + dimension line', [
		dict(icon='R')]),
	('P1', NEW, 'glyph_duplicate', 'Duplicate glyph(s) (now uses align_group_to_group)', 'layer_duplicate on glyph', [
		dict(icon='align_group_to_group', name=r'btn_duplicate')]),
	('P1', USE, 'view_list', 'List view toggle in the glyph widget (now align_group_to_group)', '', [
		dict(icon='align_group_to_group', cap=r'list view'), dict(icon='align_group_to_group', src=r'glyph-widget-panel')]),
	('P1', USE, 'glyph', 'Glyph menu (now align_group_to_group)', '', [
		dict(icon='align_group_to_group', name=r'menu-glyph')]),
	('P1', NEW, 'contour_match', 'Matchmaker: match contour order / start points between layers (now heart)', 'contour + two-way arrow', [
		dict(icon='heart')]),
	('P1', NEW, 'axis_swap', 'Swap axis masters (now contour_reverse)', 'axis_set + swap arrows', [
		dict(icon='contour_reverse', name=r'axis_swap')]),
	('P1', NEW, 'glyph_unicode', 'Set glyph unicode values (now select_glyph)', 'glyph + U+', [
		dict(icon='select_glyph', name=r'btn_setUnis')]),

	# - P1: FontRig sidebar tabs - panel_* glyphs exist but are unused --
	('P1', USE, 'panel_python', 'Python sidebar tab (now action_play)', '', [dict(name=r'^python$', icon='action_play')]),
	('P1', USE, 'panel_code', 'Scripts sidebar tab (now action_play)', '', [dict(name=r'^scripting$', icon='action_play')]),
	('P1', USE, 'panel_layer', 'Layer sidebar tab (now layer_actions)', '', [dict(name=r'^layer$', icon='layer_actions')]),
	('P1', USE, 'panel_node', 'Node sidebar tab (now node_add)', '', [dict(name=r'^node$', icon='node_add')]),
	('P1', USE, 'panel_draw', 'Draw sidebar tab (now draw_line)', '', [dict(name=r'^draw$', icon='draw_line')]),
	('P1', USE, 'panel_contour', 'Contour sidebar tab (now contour_close)', '', [dict(name=r'^contour$', icon='contour_close')]),
	('P1', NEW, 'panel_delta', 'Delta sidebar tab (now axis_set)', 'panel_* frame + delta', [dict(name=r'^delta$', icon='axis_set')]),
	('P1', NEW, 'panel_sound', 'Sonification sidebar tab (now wave)', 'panel_* frame + wave', [dict(name=r'^sonification$')]),
	('P1', NEW, 'font_info', 'Font info sidebar tab (now file)', 'file + info', [dict(name=r'^font-info$')]),
	('P1', NEW, 'font_new', 'New font (now file)', 'font_open + plus', [dict(icon='file', name=r'btn-new-font')]),
	('P1', USE, 'font_open', 'Open font (now file); read axes / masters from the font (now refresh)', '', [
		dict(icon='file', name=r'btn-open-font'), dict(icon='refresh', name=r'btn_ds_read')]),

	# - P1: split overloaded icons ------------------------------------
	('P1', NEW, 'delta_bake', 'Execute / bake delta targets (now action_play, shared with apply / run)', 'delta_machine + action_play', [
		dict(icon='action_play', cap=r'bake|execute|delta scale')]),
	('P1', NEW, 'delta_live', 'Live Edit: Live Axis controls on the glyph canvas (now delta_machine / selection_basic)', 'delta_machine + live dot', [
		dict(icon=('delta_machine', 'selection_basic'), cap=r'live edit')]),
	('P1', NEW, 'delta_commit', 'Commit delta results as real layers', 'delta_machine + layer_add', [
		dict(icon='delta_machine', cap=r'commit')]),
	('P1', NEW, 'action_apply', 'Apply current settings: transform, XML, warp update (now action_play)', 'check + action_play', [
		dict(icon='action_play', cap=r'apply|transform picked|update|refresh')]),
	('P1', NEW, 'value_reset', 'Reset fields / controls to defaults (now refresh)', 'refresh, reversed, with a zero dot', [
		dict(icon='refresh', cap=r'reset transform|defaults|^reset$')]),
	('P1', NEW, 'axis_reseed', 'Reset all data: re-seed masters from the font / glyph (now refresh)', 'layer_master + refresh', [
		dict(icon='refresh', cap=r'reset all')]),
	('P1', NEW, 'search_clear', 'Clear search / search results (now refresh or close)', 'search + close', [
		dict(icon=('refresh', 'close'), cap=r'clear search')]),
	('P1', NEW, 'glyph_capture', 'Capture / recapture the outline snapshot (now node_target / refresh / text)', 'glyph + capture corners', [
		dict(icon='node_target', cap=r'capture glyph'), dict(icon='refresh', cap=r'recapture'),
		dict(icon='', name=r'btn_capture$', src=r'trdl_window')]),
	('P1', NEW, 'file_export', 'Export to another format: SVG, UFO (now file_save); or adopt the unused file_upload', 'file_save + arrow out', [
		dict(icon='file_save', cap=r'^export$|svg|ufo')]),
	('P1', NEW, 'file_import', 'Import from another format: SVG, UFO (now file_open); or adopt the unused file_download', 'file_open + arrow in', [
		dict(icon='file_open', cap=r'^import$|ufo|not yet implemented')]),
	('P1', NEW, 'designspace_save', 'Save .designspace (now file_save)', 'file_save + axis mark', [
		dict(icon='file_save', cap=r'designspace')]),
	('P1', NEW, 'designspace_open', 'Open / read .designspace (now file_open)', 'file_open + axis mark', [
		dict(icon='file_open', cap=r'designspace')]),
	('P1', NEW, 'config_save', 'Save setup / configuration / layout / options (now file_save or text)', 'file_save + value_sliders', [
		dict(icon='file_save', cap=r'setup|configuration|layout|options|axis data'),
		dict(icon='', cap=r'save configuration', src=r'scripting-panel')]),
	('P1', NEW, 'config_open', 'Load setup / configuration / layout (now file_open or text)', 'file_open + value_sliders', [
		dict(icon='file_open', cap=r'setup|configuration|layout|axis data'),
		dict(icon='', cap=r'load configuration', src=r'scripting-panel')]),
	('P1', NEW, 'axis_reset', 'Reset axis: neutral controls for this layer (now axis_remove)', 'axis_set + refresh', [
		dict(icon='axis_remove', cap=r'reset axis|axis reset')]),
	('P1', NEW, 'axis_reset_all', 'Reset all axes / new setup / clear delta state (now axis_remove or text)', 'axis_reset doubled', [
		dict(icon='axis_remove', cap=r'reset all axes|new setup|clear delta'),
		dict(icon='', name=r'act_resetAxis|act_clear_all')]),
	('P1', NEW, 'axis_add', 'New axis (now axis_set or a text +)', 'axis_set + plus', [
		dict(icon='axis_set', name=r'btn_axis_add'), dict(icon='', name=r'btn_axis_add')]),

	# - P2: more splits and borrowed icons ----------------------------
	('P2', NEW, 'clipboard_save', 'Save clipboard / contour bank to file (now file_save)', 'clipboard + file_save', [
		dict(icon='file_save', cap=r'clipboard|bank')]),
	('P2', NEW, 'clipboard_open', 'Load clipboard / bank file (now file_open)', 'clipboard + file_open', [
		dict(icon='file_open', cap=r'clipboard|bank')]),
	('P2', NEW, 'folder_open', 'Browse for a file: tags, categories (now file_open)', 'folder', [
		dict(icon='file_open', cap=r'browse')]),
	('P2', USE, 'clipboard_clear', 'Reset / empty the contour bank (now close)', '', [
		dict(icon='close', cap=r'bank')]),
	('P2', NEW, 'glyph_remove', 'Remove glyphs from a group (now close)', 'glyph + minus (pair of glyph_add)', [
		dict(icon='close', name=r'btn_glyph_clear')]),
	('P2', NEW, 'view_zoom', 'Cycle zoom / thumbnail / cell size (now search)', 'search + plus/minus', [
		dict(icon='search', cap=r'zoom|size')]),
	('P2', USE, 'stem_detect_auto', 'Show stem detection settings (now search)', '', [
		dict(icon='search', name=r'chk_toggle_detect')]),
	('P2', NEW, 'glyph_search', 'Add the glyphs that match a pattern (now search)', 'glyph + search', [
		dict(icon='search', name=r'btn_pattern')]),
	('P2', NEW, 'view_padding', 'Cell padding (now view_icons)', 'view_icons + inset frame', [
		dict(icon='view_icons', cap=r'padding')]),
	('P2', NEW, 'tag', 'Glyph / node tags: set, copy, add (now label or text)', 'label', [
		dict(icon='label', cap=r'tags'), dict(icon='', name=r'btn_tag')]),
	('P2', NEW, 'link', 'Copy links / metric and element links (now guide_zone or text)', 'chain link', [
		dict(icon='guide_zone', name=r'chk_links'), dict(icon='', cap=r'^link$', src=r'ElementNew')]),
	('P2', NEW, 'link_off', 'Unlink metric expressions / elements (text now)', 'link + slash', [
		dict(icon='', name=r'btn_delMetrics'), dict(icon='', cap=r'^unlink$', src=r'ElementNew')]),
	('P2', NEW, 'transform', 'Transform controls / menu (now diagonal_bottom_up or arrows_expand)', 'translate + scale + rotate', [
		dict(icon='diagonal_bottom_up', cap=r'transform'), dict(icon='arrows_expand', cap=r'^transform$')]),
	('P2', NEW, 'component', 'Copy references / reference element (now shape or text)', 'shape + link', [
		dict(icon='shape', cap=r'references'), dict(icon='', name=r'btn_getShapeParent')]),
	('P2', NEW, 'stem_center', 'Stem-center snap (now node_middle_top)', 'stem_vertical + centre mark', [
		dict(icon='node_middle_top', cap=r'stem-center')]),
	('P2', NEW, 'row_inherit', 'Delta Machine: override rows inherit from the general row (now refresh)', 'select_list + arrow down', [
		dict(icon='refresh', name=r'btn_target_inherit')]),
	('P2', NEW, 'row_fold', 'Delta Machine: fold rows of one layer into a general row (now viewport_merge)', 'select_list + merge', [
		dict(icon='viewport_merge', name=r'btn_target_fold')]),
	('P2', NEW, 'contour_color', 'Colorize contours by index (now flag)', 'contour + colour fill', [
		dict(icon='flag', name=r'btn_colors')]),
	('P2', NEW, 'glyph_key', 'Group leader: the reference glyph of a group (now flag)', 'glyph + star / key', [
		dict(icon='flag', name=r'btn_glyph_ref')]),
	('P2', NEW, 'scale_fit', 'Scale / fit pasted contours into the selection (now node_target_expand)', 'bbox + arrows in', [
		dict(icon='node_target_expand', cap=r'fit')]),
	('P2', NEW, 'select_none', 'Select none / deselect all (now select_option)', 'select_option, empty', [
		dict(icon='select_option', cap=r'none|deselect')]),
	('P2', NEW, 'undo_off', 'Disable undo for speed (now alert)', 'undo + slash', [
		dict(icon='alert', cap=r'disable undo')]),
	('P2', NEW, 'revert', 'Revert to the captured outline (now undo or text)', 'undo + bar', [
		dict(icon='undo', cap=r'write the captured'), dict(icon='', name=r'btn_revert')]),
	('P2', NEW, 'settings', 'Settings / config / preferences (now view_list or text)', 'gear', [
		dict(icon='view_list', cap=r'^config$'), dict(icon='', cap=r'settings')]),

	# - P2: anchors, elements, metrics have no icons yet --------------
	('P2', NEW, 'anchor_add', 'Add anchor (Anchor panel, text now)', 'icon_anchor + plus', [dict(icon='', name=r'btn_anchorAdd')]),
	('P2', NEW, 'anchor_remove', 'Remove selected / all anchors (text now)', 'icon_anchor + minus', [dict(icon='', name=r'btn_clearSel|btn_clearAll')]),
	('P2', NEW, 'anchor_copy', 'Copy anchors from layers (text now)', 'icon_anchor + clipboard_copy', [dict(icon='', name=r'btn_anchorCopy')]),
	('P2', NEW, 'anchor_paste', 'Paste anchors to layers (text now)', 'icon_anchor + clipboard_paste', [dict(icon='', name=r'btn_anchorPaste')]),
	('P2', NEW, 'anchor_move', 'Move anchor (text now)', 'icon_anchor + translate', [dict(icon='', name=r'btn_anchorMov')]),
	('P2', NEW, 'element_group', 'Group elements (Element panel, text now)', 'shape x2 in frame', [dict(icon='', cap=r'^group$', src=r'ElementNew')]),
	('P2', NEW, 'element_ungroup', 'Ungroup / ungroup all elements (text now)', 'element_group, split', [dict(icon='', cap=r'^ungroup', src=r'ElementNew')]),
	('P2', NEW, 'element_forward', 'Move element forward one step (text now)', 'stack + arrow_up', [dict(icon='', cap=r'^forward$', src=r'ElementNew')]),
	('P2', NEW, 'element_backward', 'Move element backward one step (text now)', 'stack + arrow_down', [dict(icon='', cap=r'^backward$', src=r'ElementNew')]),
	('P2', NEW, 'element_front', 'Element to front (text now)', 'stack + fold_up', [dict(icon='', cap=r'^(to front|top)$', src=r'ElementNew')]),
	('P2', NEW, 'element_back', 'Element to back (text now)', 'stack + fold_down', [dict(icon='', cap=r'^(to back|bottom)$', src=r'ElementNew')]),
	('P2', NEW, 'metrics_copy', 'Copy metrics / bbox width / height (text now)', 'metrics_advance + clipboard_copy', [dict(icon='', name=r'btn_copyMetrics|btn_copyBBox')]),
	('P2', NEW, 'undo_clear', 'Clear undo history (text now)', 'undo + close', [dict(icon='', cap=r'clear undo history')]),

	# - P2: text-only buttons that have a glyph already ---------------
	('P2', USE, 'undo', 'Undo button (text now)', '', [dict(icon='', cap=r'^undo \(')]),
	('P2', USE, 'redo', 'Redo button (text now)', '', [dict(icon='', cap=r'^redo \(')]),
	('P2', USE, 'value_decrease_10', 'Value -10 step (text now)', '', [dict(icon='', cap=r'^-10$')]),
	('P2', USE, 'value_decrease_1', 'Value -1 step (text now)', '', [dict(icon='', cap=r'^-1$')]),
	('P2', USE, 'value_increase_1', 'Value +1 step (text now)', '', [dict(icon='', cap=r'^\+1$')]),
	('P2', USE, 'value_increase_10', 'Value +10 step (text now)', '', [dict(icon='', cap=r'^\+10$')]),
	('P2', USE, 'action_stop', 'Stop playback (text now)', '', [dict(icon='', cap=r'stop playback')]),
	('P2', USE, 'action_play', 'Sonify contours / segments (text now)', '', [dict(icon='', cap=r'^sonify')]),
	('P2', USE, 'guide_drop', 'Drop guideline between two nodes (text now)', '', [dict(icon='', name=r'btn_dropGuide$')]),
	('P2', USE, 'guide_drop_flip_h', 'Drop flipped guideline X (text now)', '', [dict(icon='', name=r'btn_dropFlipX')]),
	('P2', USE, 'guide_drop_flip_v', 'Drop flipped guideline Y (text now)', '', [dict(icon='', name=r'btn_dropFlipY')]),
	('P2', USE, 'guide_vertical', 'Drop vertical layer guide (text now)', '', [dict(icon='', name=r'btn_dropLayer_V')]),
	('P2', USE, 'guide_horizontal', 'Drop horizontal layer guide (text now)', '', [dict(icon='', name=r'btn_dropLayer_H')]),
	('P2', USE, 'dimension_ascender', 'Set font ascender (text now)', '', [dict(icon='', name=r'btn_setAscender')]),
	('P2', USE, 'dimension_caps', 'Set font caps height (text now)', '', [dict(icon='', name=r'btn_setCapsHeight')]),
	('P2', USE, 'dimension_xheight', 'Set font x-height (text now)', '', [dict(icon='', name=r'btn_setXHeight')]),
	('P2', USE, 'dimension_descender', 'Set font descender (text now)', '', [dict(icon='', name=r'btn_setDescender')]),
	('P2', USE, 'layer_push', 'IconAssist: push layer (text now)', '', [dict(icon='', name=r'^btn_push$')]),
	('P2', USE, 'layer_pull', 'IconAssist: pull layer (text now)', '', [dict(icon='', name=r'^btn_pull$')]),
	('P2', USE, 'stem_vertical_alt', 'Get / measure vertical stems menu action (text now)', '', [dict(icon='', name=r'act_get_?[vV]stem')]),
	('P2', USE, 'stem_horizontal_alt', 'Get / measure horizontal stems menu action (text now)', '', [dict(icon='', name=r'act_get_?[hH]stem')]),
	('P2', USE, 'node_snap', 'Snap captured stems to targets (text now)', '', [dict(icon='', name=r'btn_snap', src=r'StemSnap')]),
	('P2', USE, 'slope_italic', 'Take italic angle from the master (text now)', '', [dict(icon='', name=r'btn_italic', src=r'Cleanup')]),
	('P2', USE, 'font_save', 'Save Live Axis to font (text now)', '', [dict(icon='', name=r'btn_save', src=r'trdl_window')]),

	# - P3: Layer panel menu actions (text QActions with existing glyphs)
	('P3', USE, 'layer_add', 'Layer menu: New', '', [dict(icon='', name=r'act_layer_add$')]),
	('P3', USE, 'layer_duplicate', 'Layer menu: Duplicate', '', [dict(icon='', name=r'act_layer_duplicate$')]),
	('P3', USE, 'layer_mask_add', 'Layer menu: Duplicate to mask', '', [dict(icon='', name=r'act_layer_duplicate_mask')]),
	('P3', USE, 'layer_remove', 'Layer menu: Remove', '', [dict(icon='', name=r'act_layer_delete')]),
	('P3', USE, 'visible_toggle', 'Layer menu: Toggle visible', '', [dict(icon='', name=r'act_layer_visible$')]),
	('P3', USE, 'visible', 'Layer menu: Set visible', '', [dict(icon='', name=r'act_layer_visible_on')]),
	('P3', USE, 'visible_off', 'Layer menu: Set invisible', '', [dict(icon='', name=r'act_layer_visible_off')]),
	('P3', USE, 'layer_mask', 'Layer menu: Set as mask', '', [dict(icon='', name=r'act_layer_set_type_mask')]),
	('P3', USE, 'layer_service', 'Layer menu: Set as service', '', [dict(icon='', name=r'act_layer_set_type_service')]),
	('P3', NEW, 'layer_wireframe', 'Layer menu: Set as wireframe', 'layer_active, dashed', [dict(icon='', name=r'act_layer_set_type_wire')]),
	('P3', USE, 'layer_swap', 'Layer menu: Swap elements', '', [dict(icon='', name=r'act_layer_element_swap')]),
	('P3', USE, 'layer_pull', 'Layer menu: Pull elements', '', [dict(icon='', name=r'act_layer_element_pull')]),
	('P3', USE, 'layer_push', 'Layer menu: Push elements', '', [dict(icon='', name=r'act_layer_element_push')]),
	('P3', USE, 'layer_clean', 'Layer menu: Clean elements', '', [dict(icon='', name=r'act_layer_element_clean')]),
	('P3', USE, 'layer_lock', 'Layer menu: Lock elements', '', [dict(icon='', name=r'act_layer_lock')]),
	('P3', USE, 'layer_lock_off', 'Layer menu: Unlock elements', '', [dict(icon='', name=r'act_layer_unlock')]),
	('P3', USE, 'nodes_pull', 'Layer menu: Pull nodes', '', [dict(icon='', name=r'act_layer_contour_pull')]),
	('P3', USE, 'nodes_push', 'Layer menu: Push nodes', '', [dict(icon='', name=r'act_layer_contour_push')]),
	('P3', USE, 'clipboard_copy_nodes', 'Layer menu: Copy nodes', '', [dict(icon='', name=r'act_layer_contour_copy')]),
	('P3', USE, 'clipboard_paste_nodes', 'Layer menu: Paste nodes / paste by layer', '', [dict(icon='', name=r'act_layer_contour_paste')]),
	('P3', USE, 'visible_sbs', 'Layer menu: Side by side', '', [dict(icon='', name=r'act_layer_side_by_side')]),

	# - P3: nice to have --------------------------------------------
	('P3', NEW, 'draw_polygon', 'Insert a regular polygon (now gem)', 'draw_square, five sides', [dict(icon='gem', cap=r'pentagon')]),
	('P3', NEW, 'draw_squircle', 'Insert a squircle (now hyper)', 'draw_square + corner_smart', [dict(icon='hyper', cap=r'squircle')]),
	('P3', USE, 'draw_square', 'Insert a square (now quad)', '', [dict(icon='quad', cap=r'square')]),
	('P3', NEW, 'gravity_x', 'MagicScale: ink gravity X (now wave)', 'arrows_left_right + weight', [dict(icon='wave', cap=r'gravity x')]),
	('P3', NEW, 'gravity_y', 'MagicScale: ink gravity Y (now wave)', 'arrows_up_down + weight', [dict(icon='wave', cap=r'gravity y')]),
	('P3', NEW, 'centroid_x', 'MagicScale: centroid shift X (now delta_x)', 'delta_x + centre dot', [dict(icon='delta_x', cap=r'centroid')]),
	('P3', NEW, 'centroid_y', 'MagicScale: centroid shift Y (now delta_y)', 'delta_y + centre dot', [dict(icon='delta_y', cap=r'centroid')]),
	('P3', NEW, 'stem_compensation', 'Stem compensation intensity (now node_snap)', 'stem_vertical + value_sliders', [dict(icon='node_snap', cap=r'stem compensation')]),
	('P3', NEW, 'view_filled', 'View: filled preview (now shape)', 'circle, filled', [dict(icon='shape', name=r'btn-filled')]),
	('P3', NEW, 'view_outline', 'View: outline preview (now contour)', 'circle, outline', [dict(icon='contour', name=r'btn-outline')]),
	('P3', NEW, 'view_preview', 'Toggle black-and-white preview (now visible)', 'visible + filled glyph', [dict(icon='visible', cap=r'preview')]),
	('P3', NEW, 'metrics_view', 'Show baseline and side bearings (now visible)', 'metrics_advance + visible', [dict(icon='visible', cap=r'side bearings')]),
	('P3', NEW, 'window_new', 'Open a new workplane window (now select_window)', 'window + plus', [dict(icon='select_window', cap=r'new workplane')]),
	('P3', NEW, 'curve_quadratic', 'Convert to quadratic (now curve_set)', 'curve with one handle', [dict(icon='curve_set', cap=r'quadratic')]),
	('P3', NEW, 'hobby_to_bezier', 'Convert all Hobby splines to Beziers (now contour)', 'token_hobby -> token_bezier', [dict(icon='contour', cap=r'hobby')]),
	('P3', NEW, 'glyph_insert', 'Insert source glyph contents into the active layer (now layer_add)', 'glyph + clipboard_paste', [dict(icon='layer_add', name=r'btn_insert')]),
	# - Generic fallbacks: listed last so the specific rules above match first
	('P2', NEW, 'add', 'Generic list add (+) for presets, inputs, rows (text now)', 'plus in house stroke', [
		dict(icon='', cap=r'^(\+|add)$')]),
	('P2', NEW, 'remove', 'Generic list remove (-) for presets, inputs, targets (text now)', 'minus in house stroke', [
		dict(icon='', cap=r'^(-|−|remove)$'), dict(icon='', cap=r'^remove the selected')]),
	('P3', NEW, 'python_restart', 'Initialize / reset the Python runtime (now action_play)', 'panel_python + refresh', [dict(icon='action_play', cap=r'python runtime')]),
]

# - Helpers --------------------------------------------------
def matches(rule, row):
	if 'icon' in rule:
		want = rule['icon'] if isinstance(rule['icon'], tuple) else (rule['icon'],)
		if row['Icon'] not in want: return False
	if 'cap' in rule and not re.search(rule['cap'], row['Caption'].replace('&', '').strip(), re.I): return False	# & = Qt mnemonic
	if 'name' in rule and not re.search(rule['name'], row['Button/Action']): return False
	if 'src' in rule and not re.search(rule['src'], row['Source']): return False
	return True

def short_src(row):
	project = {'Typerig-Glyphs': 'Glyphs', 'TypeRig': 'TR', 'FontRig': 'FontRig'}.get(row['Project'], row['Project'])
	path = row['Source'].replace('.glyphsPlugin/Contents/Resources', '').replace('.glyphsPalette/Contents/Resources', '').replace('.glyphsTool/Contents/Resources', '')
	return '%s %s' % (project, path)

# - Main -----------------------------------------------------
def main():
	usage = sys.argv[1] if len(sys.argv) > 1 else USAGE_CSV
	out = sys.argv[2] if len(sys.argv) > 2 else TODO_CSV

	with open(usage, encoding='utf-8-sig') as f:
		rows = list(csv.DictReader(f))

	hits = OrderedDict((idx, []) for idx in range(len(TODO)))
	for row in rows:
		for idx, todo in enumerate(TODO):
			if any(matches(rule, row) for rule in todo[5]):
				hits[idx].append(row)
				break

	table = []
	for idx, (prio, action, glyph, meaning, base, rules) in enumerate(TODO):
		found = hits[idx]
		if rules and not found: print('! no census rows for %s' % glyph, file=sys.stderr)
		captions = OrderedDict((r['Caption'].split('\n')[0].strip(), 1) for r in found if r['Caption'].strip())
		table.append({
			'Priority': prio, 'Action': action, 'Glyph': glyph, 'Meaning': meaning, 'Draw from': base,
			'Replaces': ', '.join(OrderedDict((r['Icon'] or '(text)', 1) for r in found)),
			'Count': len(found),
			'Captions': ' | '.join(list(captions)[:4]),
			'Where': '; '.join(short_src(r) for r in found),
			'Group': group_of(glyph), 'Origin': 'census',
		})

	# - Planned glyphs: names must not clash with the font or the census proposals
	with open(FONT_VFJ, encoding='utf-8') as f:
		in_font = {g['name'] for g in json.load(f)['font']['glyphs']}
	proposed = {t['Glyph'] for t in table}

	for prio, action, glyph, meaning, base, group in CATALOG:
		if action != EXISTS and (glyph in in_font or glyph in proposed):
			print('! catalog glyph %s already %s' % (glyph, 'in font' if glyph in in_font else 'proposed'), file=sys.stderr)
		if action == ALIAS and base not in in_font:
			print('! alias %s points to missing %s' % (glyph, base), file=sys.stderr)
		proposed.add(glyph)
		table.append({
			'Group': group, 'Priority': prio, 'Action': action, 'Glyph': glyph, 'Meaning': meaning, 'Draw from': base,
			'Replaces': '', 'Count': 0, 'Captions': '', 'Where': '', 'Origin': 'catalog',
		})

	table.sort(key=lambda t: (GROUP_ORDER.index(t['Group']), t['Priority'], ACTION_ORDER.index(t['Action']), -t['Count']))

	with open(out, 'w', encoding='utf-8-sig', newline='') as f:
		w = csv.DictWriter(f, fieldnames=COLUMNS)
		w.writeheader()
		w.writerows(table)

	count = lambda action, origin=None: sum(t['Action'] == action and origin in (None, t['Origin']) for t in table)
	print('-- %d entries -> %s' % (len(table), out))
	print('-- new glyphs: %d from the census + %d planned; %d aliases, %d renames, %d use-existing; %d census rows covered' % (
		count(NEW, 'census'), count(NEW, 'catalog'), count(ALIAS), count(REN), count(USE), sum(t['Count'] for t in table)))

if __name__ == '__main__':
	main()
