# MODULE: TypeRig Icons / Glyph catalog
# -----------------------------------------------------------
# Planned glyphs for a complete font-editor UI - not tied to current call sites
# (those live in glyph_todo.py TODO). Read by glyph_todo.py and merged into lists/glyph_todo.csv.
# Entry: (priority, action, glyph, meaning, draw from, group)
#	action: 'new glyph' | 'alias' (extra ligature name for an existing glyph) |
#	        'exists' (glyph column lists what already covers the group)
# P1 = every sane app needs it; P2 = font / vector editor needs it; P3 = nice to have.
# -----------------------------------------------------------

NEW, ALIAS, EXISTS = 'new glyph', 'alias', 'exists'

ARROWS = 'Arrows & navigation'
RUN = 'Run & media'
HISTORY = 'History'
WINDOW = 'Window & layout'
DIALOG = 'Dialog & status'
EDIT = 'Edit & clipboard'
SELECT = 'Selection'
NODES = 'Nodes'
CONTOURS = 'Contours'
ELEMENTS = 'Elements & components'
GLYPHS = 'Glyphs'
SWAP = 'Swap & exchange'
TRANSFORM = 'Transform'
MEASURE = 'Guides & measurement'
TOOLS = 'Tools'
FILES = 'Files & fonts'

CATALOG = [
	# - Arrows & navigation -------------------------------------------
	('P1', EXISTS, 'arrow_left, arrow_right, arrow_up, arrow_down, chevron_left, chevron_right, fold_up, fold_down, arrows_expand, arrows_contract, node_next, node_previous',
		'Straight arrows, chevrons, expand / contract; arrows_2up_left draws two up-right arrows (check the name)', '', ARROWS),
	('P1', ALIAS, 'chevron_up', 'Chevron up - same drawing as fold_up, completes the chevron set', 'fold_up', ARROWS),
	('P1', ALIAS, 'chevron_down', 'Chevron down - same drawing as fold_down', 'fold_down', ARROWS),
	('P1', NEW, 'arrows_left_right', 'Double-headed horizontal arrow: resize width, horizontal extent', 'width (arrow only)', ARROWS),
	('P1', NEW, 'arrows_up_down', 'Double-headed vertical arrow: resize height, vertical extent', 'height (arrow only)', ARROWS),
	('P1', NEW, 'arrows_move', 'Four-way arrow: move / pan / drag', 'arrows_left_right + arrows_up_down', ARROWS),
	('P2', NEW, 'arrow_up_left', 'Diagonal arrow up-left', 'arrow_up rotated', ARROWS),
	('P2', NEW, 'arrow_up_right', 'Diagonal arrow up-right', 'arrow_up rotated', ARROWS),
	('P2', NEW, 'arrow_down_left', 'Diagonal arrow down-left', 'arrow_down rotated', ARROWS),
	('P2', NEW, 'arrow_down_right', 'Diagonal arrow down-right', 'arrow_down rotated', ARROWS),
	('P2', NEW, 'chevron_double_left', 'Double chevron left: collapse side panel, previous page', 'chevron_left x2', ARROWS),
	('P2', NEW, 'chevron_double_right', 'Double chevron right: expand side panel, next page', 'chevron_right x2', ARROWS),
	('P2', NEW, 'chevron_double_up', 'Double chevron up: collapse all sections', 'fold_up x2', ARROWS),
	('P2', NEW, 'chevron_double_down', 'Double chevron down: expand all sections', 'fold_down x2', ARROWS),
	('P2', NEW, 'arrow_first', 'Jump to first (glyph, node, master): arrow to bar', 'arrow_left + bar', ARROWS),
	('P2', NEW, 'arrow_last', 'Jump to last: arrow to bar', 'arrow_right + bar', ARROWS),
	('P2', NEW, 'menu_dropdown', 'Small caret: drop-down / combo indicator', 'fold_down, filled triangle', ARROWS),
	('P2', NEW, 'arrow_external', 'Open outside / external link: arrow out of a box', 'window + arrow_up_right', ARROWS),
	('P2', NEW, 'sort_ascending', 'Sort list ascending (glyph lists, tables)', 'select_list + arrow_down', ARROWS),
	('P2', NEW, 'sort_descending', 'Sort list descending', 'select_list + arrow_up', ARROWS),
	('P3', NEW, 'drag_handle', 'Grip dots: reorder rows, drag panels', 'six dots', ARROWS),

	# - Run & media ---------------------------------------------------
	('P1', EXISTS, 'action_play, action_play_reverse, action_stop, action_pause, action_rec', 'Transport basics', '', RUN),
	('P1', NEW, 'script_run', 'Run script / macro (not the same as play media or apply)', 'code_tag + action_play', RUN),
	('P2', NEW, 'script_stop', 'Stop running script', 'code_tag + action_stop', RUN),
	('P2', NEW, 'script_new', 'New script', 'code_tag + plus', RUN),
	('P2', NEW, 'action_batch', 'Run on all glyphs / batch process', 'action_play + glyph_stack', RUN),
	('P2', NEW, 'action_eject', 'Eject: pull out / detach (also element eject in Element panel)', 'triangle up + bar', RUN),
	('P2', NEW, 'action_step_forward', 'Step forward one item (play to bar)', 'action_play + bar', RUN),
	('P2', NEW, 'action_step_back', 'Step back one item', 'action_play_reverse + bar', RUN),
	('P3', NEW, 'action_skip_next', 'Skip to next (double triangle to bar)', 'value_increase_double + bar', RUN),
	('P3', NEW, 'action_skip_previous', 'Skip to previous', 'value_decrease_double + bar', RUN),
	('P3', NEW, 'action_loop', 'Repeat / loop', 'sync, single loop', RUN),

	# - History -------------------------------------------------------
	('P1', EXISTS, 'undo, redo, undo_snapshot', 'Undo, redo, make snapshot (to-do also adds undo_clear, undo_off, revert)', '', HISTORY),
	('P1', NEW, 'history', 'History panel / list of actions: clock with back arrow', 'circle + undo arrow + hands', HISTORY),
	('P2', NEW, 'snapshot_restore', 'Restore a snapshot', 'undo_snapshot, arrow reversed', HISTORY),
	('P3', NEW, 'snapshot_compare', 'Compare current state with a snapshot', 'undo_snapshot + compare', HISTORY),
	('P3', NEW, 'backup', 'Backups / versions of the font file', 'file + history', HISTORY),

	# - Window & layout ------------------------------------------------
	('P1', EXISTS, 'window, window_popup, panel_left, panel_right, panel_up, panel_down, panel_python, panel_code, panel_terminal, panel_node, panel_draw, panel_contour, panel_layer, widget, widget_add, widget_remove, widget_export, widget_import, viewport_single, viewport_double, viewport_quad, viewport_merge, view_icons, view_list, gui_mode_dark, gui_mode_light',
		'Windows, side panels, widgets, viewports, view modes, themes', '', WINDOW),
	('P1', NEW, 'menu', 'Hamburger menu', 'three bars', WINDOW),
	('P1', NEW, 'menu_more', 'More options: three dots horizontal', 'three dots', WINDOW),
	('P2', NEW, 'menu_more_vertical', 'More options: three dots vertical (row context menu)', 'menu_more rotated', WINDOW),
	('P1', NEW, 'toggle_on', 'Switch on', 'pill + filled knob right', WINDOW),
	('P1', NEW, 'toggle_off', 'Switch off', 'pill + knob left', WINDOW),
	('P1', NEW, 'zoom_in', 'Zoom in', 'search + plus', WINDOW),
	('P1', NEW, 'zoom_out', 'Zoom out', 'search + minus', WINDOW),
	('P1', NEW, 'zoom_fit', 'Fit to view (FontRig uses arrows_expand now)', 'search + frame corners', WINDOW),
	('P2', NEW, 'zoom_actual', 'Actual size / 100%', 'search + 1:1', WINDOW),
	('P2', NEW, 'zoom_selection', 'Zoom to selection', 'search + selection_basic', WINDOW),
	('P1', NEW, 'lock', 'Generic lock (layers and nodes have their own; this is for panels, guides, fields)', 'lock element used by layer_lock', WINDOW),
	('P1', NEW, 'lock_off', 'Generic unlock', 'lock, open shackle', WINDOW),
	('P2', NEW, 'panel_dock', 'Dock a floating panel', 'window_popup + arrow in', WINDOW),
	('P2', NEW, 'panel_undock', 'Float / detach a panel', 'window_popup + arrow out', WINDOW),
	('P2', NEW, 'tab_add', 'New tab (glyph tab, text tab)', 'window tab + plus', WINDOW),
	('P2', NEW, 'keyboard', 'Keyboard shortcuts', 'keyboard_arows, full keyboard', WINDOW),
	('P3', NEW, 'window_maximize', 'Maximize window', 'window, thick frame', WINDOW),
	('P3', NEW, 'window_minimize', 'Minimize window', 'bar at bottom', WINDOW),
	('P3', NEW, 'viewport_double_h', 'Two viewports stacked (rows)', 'viewport_double rotated', WINDOW),
	('P3', ALIAS, 'fullscreen', 'Full screen', 'arrows_expand', WINDOW),
	('P3', ALIAS, 'fullscreen_exit', 'Exit full screen', 'arrows_contract', WINDOW),

	# - Dialog & status ------------------------------------------------
	('P1', EXISTS, 'check, close, alert, info, help, question, refresh, sync, search', 'OK / apply, cancel / close, status, refresh', '', DIALOG),
	('P2', ALIAS, 'ok', 'OK button', 'check', DIALOG),
	('P2', ALIAS, 'cancel', 'Cancel button', 'close', DIALOG),
	('P1', NEW, 'delete', 'Delete permanently: trash can (remove = minus, clear = empty, delete = gone)', 'trash can', DIALOG),
	('P1', NEW, 'clear', 'Clear / empty a field or list: backspace', 'backspace key + close', DIALOG),
	('P1', NEW, 'warning', 'Warning: triangle with ! (FontRig already asks for this name)', 'alert inside a triangle', DIALOG),
	('P1', NEW, 'error', 'Error: X in a circle', 'alert circle + close', DIALOG),
	('P2', NEW, 'success', 'Done / passed: check in a circle', 'alert circle + check', DIALOG),
	('P2', NEW, 'busy', 'Working / please wait: hourglass', 'hourglass', DIALOG),
	('P3', NEW, 'disabled', 'Not allowed / disabled: circle with slash', 'circle + slash', DIALOG),
	('P3', NEW, 'notification', 'Notifications / messages: bell', 'bell', DIALOG),

	# - Edit & clipboard -----------------------------------------------
	('P1', EXISTS, 'clipboard, clipboard_alt, clipboard_copy, clipboard_paste, clipboard_paste_exact, clipboard_clear, clipboard_copy_nodes, clipboard_paste_nodes, label, flag',
		'Copy / paste, labels, flags', '', EDIT),
	('P1', NEW, 'edit', 'Edit: pencil (tool_line already looks like a pencil - keep them apart)', 'tool_line, simpler', EDIT),
	('P1', NEW, 'duplicate', 'Generic duplicate: two overlapping squares', 'align_contour_to_contour, filled back', EDIT),
	('P1', NEW, 'filter', 'Filter list: funnel', 'funnel', EDIT),
	('P2', NEW, 'clipboard_cut', 'Cut', 'scissors', EDIT),
	('P2', NEW, 'search_replace', 'Find and replace', 'search + swap arrows', EDIT),
	('P2', NEW, 'color_mark', 'Glyph / contour mark colour: swatch', 'flag swatch', EDIT),
	('P2', NEW, 'note', 'Note / comment on a glyph or layer', 'speech bubble', EDIT),
	('P2', NEW, 'tree_expand', 'Expand all tree rows', 'select_list + plus', EDIT),
	('P2', NEW, 'tree_collapse', 'Collapse all tree rows', 'select_list + minus', EDIT),

	# - Selection ----------------------------------------------------
	('P1', EXISTS, 'selection_basic, selection_lock, select_all, select_option, select_swap, select_list, select_glyph, select_window, tool_select, tool_select_alt, tool_pick, tool_pick_add, tool_pick_remove, tool_pick_set',
		'Select modes and pickers (select_swap = invert); to-do adds select_none', '', SELECT),
	('P2', NEW, 'tool_lasso', 'Lasso selection tool', 'selection_basic, free loop', SELECT),
	('P3', NEW, 'select_same', 'Select similar (same node type, same contour direction)', 'select_all + equals', SELECT),

	# - Nodes --------------------------------------------------------
	('P1', EXISTS, 'node_add (bgn, mid, end, extreme, single), node_remove, node_smooth, node_sharp, node_hobby, node_round, node_start, node_next, node_previous, node_copy, node_paste, node_clear, node_snap, node_target*, node_trace*, node_align_*, knot_add, knot_remove, nodes_lock, nodes_pull, nodes_push, line_to_curve, curve_to_line, curve_retract',
		'Node insert / remove / type / align / copy', '', NODES),
	('P1', NEW, 'node_merge', 'Merge selected nodes into one', 'two nodes -> one', NODES),
	('P2', NEW, 'node_swap', 'Swap two nodes (positions / order)', 'node x2 + arrows_swap_h', NODES),
	('P2', NEW, 'node_smooth_toggle', 'Toggle smooth / sharp (FontRig context menu)', 'node_smooth + node_sharp halves', NODES),
	('P2', NEW, 'node_tangent', 'Tangent node type (line-to-curve joint)', 'node_smooth, square + line', NODES),
	('P2', NEW, 'node_distribute_h', 'Distribute nodes horizontally', 'contour_distribute_h with nodes', NODES),
	('P2', NEW, 'node_distribute_v', 'Distribute nodes vertically', 'contour_distribute_v with nodes', NODES),
	('P2', NEW, 'node_simplify', 'Simplify: remove redundant nodes (Glyphs Cleanup panel)', 'node_remove + curve', NODES),
	('P2', NEW, 'node_add_intersection', 'Add nodes at intersections / overlaps', 'node_add on crossing lines', NODES),
	('P3', NEW, 'node_remove_smart', 'Remove node keeping the curve shape', 'node_remove + curve_tunni', NODES),

	# - Contours ------------------------------------------------------
	('P1', EXISTS, 'contour, contour_close, contour_open, contour_cut, contour_reverse, contour_cw, contour_ccw, contour_align_*, contour_distribute_h/v, contour_sort_*, contour_union, contour_intersect, contour_difference, contour_subtract',
		'Open / close / cut, direction, align, distribute, order, booleans (union = remove overlap)', '', CONTOURS),
	('P1', NEW, 'contour_remove', 'Delete selected contours', 'contour + minus', CONTOURS),
	('P1', NEW, 'contour_duplicate', 'Duplicate selected contours', 'contour x2', CONTOURS),
	('P2', NEW, 'contour_join', 'Join two open contours', 'contour_open x2 -> one', CONTOURS),
	('P2', NEW, 'contour_offset', 'Offset / inset outline', 'contour + parallel contour', CONTOURS),
	('P2', NEW, 'contour_stroke_expand', 'Expand stroke to outline (IconAssist Expand Stroke)', 'centerline -> contour', CONTOURS),
	('P2', NEW, 'contour_next', 'Select next contour', 'contour + chevron_right', CONTOURS),
	('P2', NEW, 'contour_previous', 'Select previous contour', 'contour + chevron_left', CONTOURS),
	('P3', NEW, 'contour_to_front', 'Contour to front of the order', 'contour_sort_y + fold_up', CONTOURS),
	('P3', NEW, 'contour_to_back', 'Contour to back of the order', 'contour_sort_y + fold_down', CONTOURS),

	# - Elements & components ---------------------------------------
	('P1', EXISTS, 'shape, align_group_to_group, layer_swap, layer_pull, layer_push, layer_clean', 'Element shape, align groups, layer element ops (to-do adds element_group/ungroup/forward/backward/front/back, component, link)', '', ELEMENTS),
	('P1', NEW, 'component_decompose', 'Decompose / flatten references into outlines', 'component -> contour', ELEMENTS),
	('P2', NEW, 'component_add', 'Add a component / reference', 'component + plus', ELEMENTS),
	('P2', NEW, 'element_add', 'New element', 'shape + plus', ELEMENTS),
	('P2', NEW, 'element_remove', 'Remove element', 'shape + minus', ELEMENTS),
	('P2', NEW, 'element_duplicate', 'Duplicate element', 'shape x2', ELEMENTS),
	('P2', NEW, 'element_eject', 'Eject element out of its group (Element panel "Eject")', 'shape + action_eject', ELEMENTS),
	('P2', NEW, 'element_split', 'Split element into islands / contours', 'shape cut in two', ELEMENTS),
	('P2', NEW, 'element_merge', 'Merge elements into one', 'two shapes -> one', ELEMENTS),

	# - Glyphs ------------------------------------------------------
	('P1', EXISTS, 'glyph, glyph_active, glyph_active_alt, glyph_add, glyph_stack, select_glyph, file_glyph',
		'Glyph, active glyph, add, stack (to-do adds glyph_duplicate, glyph_unicode, glyph_remove, glyph_search, glyph_capture, glyph_key, glyph_insert, rename, tag)', '', GLYPHS),
	('P1', NEW, 'glyph_next', 'Next glyph', 'glyph + chevron_right', GLYPHS),
	('P1', NEW, 'glyph_previous', 'Previous glyph', 'glyph + chevron_left', GLYPHS),
	('P2', NEW, 'glyph_open', 'Open glyph in a new tab / window', 'glyph + arrow_external', GLYPHS),
	('P2', NEW, 'glyph_clear', 'Clear the outline of a glyph (keep the glyph)', 'glyph, empty + close', GLYPHS),
	('P2', NEW, 'glyph_compose', 'Build composite / accented glyph from components', 'glyph + component', GLYPHS),
	('P2', NEW, 'charset', 'Character set / encoding coverage', 'grid of cells + U', GLYPHS),
	('P2', NEW, 'compare', 'Compare glyphs / layers / fonts side by side (TR-Comparator)', 'two glyphs + equals', GLYPHS),
	('P3', NEW, 'glyph_sort', 'Sort glyphs in the font', 'glyph_stack + sort_ascending', GLYPHS),

	# - Swap & exchange -----------------------------------------------
	('P1', EXISTS, 'select_swap, layer_swap, sync, flip_horizontal, flip_vertical', 'Invert selection, swap layer elements, sync, flip (to-do adds axis_swap)', '', SWAP),
	('P1', NEW, 'arrows_swap_h', 'Generic swap left <-> right: two opposite arrows', 'arrow_left + arrow_right offset', SWAP),
	('P1', NEW, 'arrows_swap_v', 'Generic swap up <-> down', 'arrow_up + arrow_down offset', SWAP),
	('P3', NEW, 'swap_xy', 'Exchange X and Y values', 'coordinates + arrows_swap_h', SWAP),

	# - Transform -------------------------------------------------------
	('P1', EXISTS, 'translate_x, translate_y, scale_x, scale_y, scale_lock, skew, rotate, flip_horizontal, flip_vertical', 'Move, scale, skew, rotate, flip (to-do adds transform, scale_fit)', '', TRANSFORM),
	('P2', NEW, 'rotate_cw_90', 'Rotate 90 degrees clockwise', 'rotate + quarter arc', TRANSFORM),
	('P2', NEW, 'rotate_ccw_90', 'Rotate 90 degrees counter-clockwise', 'rotate mirrored', TRANSFORM),
	('P2', NEW, 'transform_reset', 'Reset transformation (Element panel "Reset TX")', 'transform + refresh', TRANSFORM),
	('P2', NEW, 'transform_pivot', 'Pick transform origin / pivot', 'node_center + crosshair', TRANSFORM),
	('P3', NEW, 'transform_round', 'Round transformation values (Element panel "Round TX")', 'transform + node_round', TRANSFORM),

	# - Guides & measurement ------------------------------------------
	('P1', EXISTS, 'guide_horizontal, guide_vertical, guide_zone, guide_drop, guide_drop_flip_h, guide_drop_flip_v, dimension_*, tool_ruler, tool_calipers, distance, coordinates, width, width_x, width_y, height, bbox, bbox_percent, angle*, metrics_lsb, metrics_rsb, metrics_advance*, stem_*, kern_class*',
		'Guides, font dimensions, measuring, metrics, stems, kern classes', '', MEASURE),
	('P1', NEW, 'guide_remove', 'Remove guides', 'guide_horizontal + minus', MEASURE),
	('P1', NEW, 'grid', 'Show grid', 'grid of lines', MEASURE),
	('P1', NEW, 'snap', 'Snapping on / off: magnet (node_snap is node-specific)', 'magnet', MEASURE),
	('P2', NEW, 'guide_lock', 'Lock guides', 'guide_horizontal + lock', MEASURE),
	('P2', NEW, 'guide_angled', 'Angled guide (italic / slope guide)', 'guide_vertical slanted', MEASURE),
	('P2', NEW, 'ruler', 'Show rulers (tool_ruler is the measuring tool)', 'ruler edges of a frame', MEASURE),
	('P2', NEW, 'metrics_center', 'Center glyph / equalize side bearings', 'metrics_lsb + metrics_rsb, equal', MEASURE),
	('P2', NEW, 'kern_pair', 'Kerning pair (A V)', 'two letters + arrows', MEASURE),
	('P3', NEW, 'area', 'Measured / sampled area (AutoMetrics)', 'filled region + dimension', MEASURE),

	# - Tools ---------------------------------------------------------
	('P1', EXISTS, 'tool_select, tool_select_alt, tool_pick*, tool_line, tool_polyline, tool_bezier, tool_hobby, tool_ruler, tool_calipers, tool_pin, tool_cutter, tool_eraser, draw_*',
		'Pointer, pen, Hobby, ruler, calipers, pin, knife, eraser, shape drawing', '', TOOLS),
	('P1', NEW, 'tool_hand', 'Hand / pan tool', 'hand', TOOLS),
	('P1', NEW, 'tool_zoom', 'Zoom tool', 'zoom_in', TOOLS),
	('P1', NEW, 'tool_text', 'Text / string tool', 'T with serifs', TOOLS),
	('P2', NEW, 'tool_rotate', 'Rotate tool', 'rotate + pointer', TOOLS),
	('P2', NEW, 'tool_scale', 'Scale tool', 'scale_x + pointer', TOOLS),
	('P2', NEW, 'tool_metrics', 'Metrics / side-bearing tool', 'metrics_advance + pointer', TOOLS),
	('P2', NEW, 'tool_kern', 'Kerning tool', 'kern_pair + pointer', TOOLS),
	('P2', NEW, 'tool_anchor', 'Anchor tool', 'icon_anchor + pointer', TOOLS),
	('P3', NEW, 'tool_brush', 'Brush / calligraphic stroke tool', 'tool_line, broad nib', TOOLS),

	# - Files & fonts -------------------------------------------------
	('P1', EXISTS, 'file, file_open, file_save, file_glyph, file_meta, file_download, file_upload, font_open, font_save, kern_class_open, kern_class_save',
		'Files; font_open / font_save show VFC (to-do adds font_new, font_info, file_export/import, designspace_*, config_*, folder_open)', '', FILES),
	('P1', NEW, 'file_new', 'New file / document', 'file + plus', FILES),
	('P1', NEW, 'font_export', 'Generate / export font binaries (OTF, TTF, variable)', 'font_save with OTF', FILES),
	('P2', NEW, 'font', 'Generic font (fonts list, font window) without the VFC label', 'Aa in a frame', FILES),
	('P2', NEW, 'file_reload', 'Reload from disk (refresh is for UI state)', 'file + refresh', FILES),
	('P2', NEW, 'font_features', 'OpenType features', 'code_tag + fea', FILES),
	('P2', NEW, 'master_add', 'Add a master', 'layer_master + plus', FILES),
	('P2', NEW, 'instance', 'Instances / named styles to export', 'layer_master, outline + star', FILES),
	('P2', NEW, 'audit', 'Check / validate the font (problems report)', 'glyph + check in shield', FILES),
	('P2', NEW, 'image', 'Background image / tracing template', 'frame + mountain + sun', FILES),
	('P3', NEW, 'font_close', 'Close font', 'font + close', FILES),
	('P3', NEW, 'plugin', 'Plugins / extensions: puzzle piece', 'puzzle piece', FILES),
]
