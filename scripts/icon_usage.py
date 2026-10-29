# SCRIPT: TypeRig Icons / Icon usage census
# -----------------------------------------------------------
# Scan the projects that use the TypeRig Icons font and list every button / action,
# its caption (tooltip or visible text) and the icon ligature it renders.
#	python scripts/icon_usage.py [out.csv] [--font font.vfj]
# 'In font' checks the VFJ glyph names plus fonts/typerig-icons.ttf (needs fontTools for the TTF).
# Projects scanned (edit PROJECTS below):
#	Typerig-Glyphs/Plugins  - Glyphs plugins (vanilla IconButton / Button)
#	TypeRig/Scripts         - FontLab panels, toolbars, popups (CustomPushButton / QAction)
#	FontRig/editor          - web editor (FRWidget icon:'..', <span class="tri">..</span>)
# Flags are heuristics - they point at rows worth a human look, not verdicts.
# -----------------------------------------------------------

import argparse
import ast
import csv
import json
import os
import re
import sys
from collections import defaultdict

# - Init --------------------------------------------------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_VFJ = os.path.join(ROOT, 'sources', 'typerig-icons.vfj')
FONT_TTF = os.path.join(ROOT, 'fonts', 'typerig-icons.ttf')
GITHUB = os.path.dirname(ROOT)

PROJECTS = [
	('Typerig-Glyphs', os.path.join(GITHUB, 'Typerig-Glyphs', 'Plugins')),
	('TypeRig', os.path.join(GITHUB, 'TypeRig', 'Scripts')),
	('FontRig', os.path.join(GITHUB, 'FontRig', 'editor')),
]

SKIP_DIRS = {'__pycache__', 'node_modules', '.git', '.claude', 'test', 'Test', '_ideas'}

COLUMNS = ['Project', 'Plugin/Script', 'Panel/Toolbar/Section', 'Button/Action', 'Caption', 'Icon',
		'Flag', 'In font', 'Icon shared by', 'Callback', 'Widget', 'Source']

# Widget constructors -> index of the text/token positional argument
PY_CTORS = {
	'CustomPushButton': 0, 'QPushButton': 0, 'QAction': 0, 'QToolButton': 0, 'QCheckBox': 0,
	'QRadioButton': 0, 'CustomSpinButton': 0, 'CustomLabel': 0, 'QLabel': 0, 'FLIconButton': 0,
	'TRCustomSpinController': 0, 'CustomSpinLabel': 0,
	'IconButton': 1, 'GridIconButton': 1, 'Button': 1, 'CheckBox': 1, 'ActionButton': 1,
}
PY_ICON_CTORS = {'IconButton', 'GridIconButton'}
PY_LABELS = {'CustomLabel', 'QLabel', 'CustomSpinLabel', 'TRCustomSpinController'}
ICON_OBJ_NAMES = {'btn_panel', 'btn_panel_opt', 'btn_mast', 'lbl_panel', 'lbl_icon'}

# Words that mean the same thing when comparing icon names to button names / captions
SYNONYMS = {
	'add': {'insert', 'new', 'create', 'plus'}, 'remove': {'delete', 'del', 'clear', 'minus', 'rem'},
	'mitre': {'miter'}, 'prop': {'proportion', 'proportional', 'ratio'}, 'neigh': {'neighbor', 'neighbour', 'peer'},
	'xheight': {'x-height', 'x'}, 'caps': {'cap', 'capheight'}, 'cw': {'clockwise'}, 'ccw': {'counterclockwise', 'counter'},
	'bgn': {'begin', 'start', 'first'}, 'mid': {'middle', 'center', 'centre'}, 'end': {'last'},
	'h': {'horizontal', 'horizontally', 'x'}, 'v': {'vertical', 'vertically', 'y'}, 'x': {'horizontal', 'h'}, 'y': {'vertical', 'v'},
	'lsb': {'left', 'sidebearing'}, 'rsb': {'right', 'sidebearing'}, 'advance': {'width', 'adv'},
	'visible': {'show', 'hide', 'visibility', 'view'}, 'open': {'load', 'import'}, 'save': {'export', 'write'},
	'refresh': {'reload', 'update', 'reset'}, 'close': {'exit', 'quit', 'cancel'}, 'check': {'ok', 'apply', 'done'},
	'undo': {'revert'}, 'clipboard': {'copy', 'paste'}, 'rotate': {'rotation'}, 'skew': {'slant'},
	'scale': {'scaling', 'size'}, 'translate': {'move', 'shift', 'offset'}, 'dimension': {'metric', 'metrics'},
	'select': {'selection', 'selected'}, 'glyph': {'glyphs'}, 'layer': {'layers'}, 'master': {'masters'},
	'contour': {'contours', 'path', 'paths', 'shape'}, 'node': {'nodes', 'point', 'points'},
	'stem': {'stems'}, 'delta': {'machine'}, 'value': {'values'}, 'reverse': {'flip', 'direction'},
	'round': {'rounded', 'rounding'}, 'trap': {'ink'}, 'sync': {'synchronize', 'link'},
}

GENERIC_SECTIONS = re.compile(r'^(init|layout|signals?|actions? and (groups|dialogs)|widgets and tools|build|helpers?|procedures?|.*-+)$', re.I)

# - Font -----------------------------------------------------
def font_glyphs(path):
	'''Glyph names of the VFJ source plus the built TTF (they can drift apart)'''
	with open(path, encoding='utf-8') as f:
		vfj = json.load(f)
	names = {g['name'] for g in vfj['font']['glyphs']}
	try:
		from fontTools.ttLib import TTFont
		names |= set(TTFont(FONT_TTF).getGlyphOrder())
	except Exception as err:
		print('! TTF glyph names not read (%s): checking against the VFJ only' % err, file=sys.stderr)
	return names

# - Helpers --------------------------------------------------
def rel(path, base):
	return os.path.relpath(path, base).replace('\\', '/')

def walk_files(base, exts):
	for root, dirs, files in os.walk(base):
		dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
		for name in sorted(files):
			if os.path.splitext(name)[1].lower() in exts:
				yield os.path.join(root, name)

def words(text):
	text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text or '')
	return [w for w in re.split(r'[^A-Za-z0-9]+', text.lower()) if w]

def pretty_func(name):
	name = re.sub(r'^_*(build|make|create|setup|init)_?', '', name)
	name = re.sub(r'^_*ui$', '', name)
	return name.replace('_', ' ').strip().capitalize()

def plugin_name(project, path, base):
	parts = rel(path, base).split('/')
	if project == 'Typerig-Glyphs':
		return parts[0].rsplit('.', 1)[0]
	if project == 'FontRig':
		return 'FontRig editor'
	path = '/'.join(parts[1:] if parts[0] == 'TypeRig GUI' and len(parts) > 1 else parts)
	return os.path.splitext(path)[0]

# - Python extraction ----------------------------------------
class PyFile(object):
	def __init__(self, path, text):
		self.path = path
		self.text = text
		self.lines = text.splitlines()
		self.tree = ast.parse(text)
		self.parents = {}

		for node in ast.walk(self.tree):
			for child in ast.iter_child_nodes(node):
				self.parents[child] = node

		self.app_name = None
		m = re.search(r"app_name\s*,?.*?=\s*u?'([^']+)'", text)
		if m: self.app_name = m.group(1)

		# - Section comments: '# -- Name ----' (TypeRig) or '# Name ---' banners
		self.sections = []
		for i, line in enumerate(self.lines, 1):
			m = re.match(r"^\s*#\s*-{1,3}\s+([^-].*?)\s*-*\s*$", line)
			if m and len(m.group(1).strip()) <= 48 and not GENERIC_SECTIONS.match(m.group(1).strip()):
				self.sections.append((i, m.group(1).strip()))

		# - String assignments per scope: (lineno, name, node)
		self.assigns = defaultdict(list)
		for node in ast.walk(self.tree):
			if isinstance(node, ast.Assign):
				for tgt in node.targets:
					key = target_key(tgt)
					if key: self.assigns[(self.scope_of(node), key)].append((node.lineno, node.value))

		# - Post-construction tooltips and signal connections
		self.post_tips, self.post_cb = {}, {}
		for node in ast.walk(self.tree):
			if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute): continue
			attr = node.func.attr

			if attr in ('setToolTip', 'setToolTip_') and node.args:
				owner = node.func.value
				if isinstance(owner, ast.Call) and isinstance(owner.func, ast.Attribute) and owner.func.attr in ('getNSButton', 'getNSPopUpButton'):
					owner = owner.func.value
				key = target_key(owner)
				val = self.sval(node.args[0], node)
				if key and val: self.post_tips.setdefault(key, val)

			if attr == 'connect' and node.args and isinstance(node.func.value, ast.Attribute):
				key = target_key(node.func.value.value)
				cb = callback_name(node.args[0])
				if key and cb: self.post_cb.setdefault(key, cb)

	def scope_of(self, node):
		while node in self.parents:
			node = self.parents[node]
			if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)): return node
		return self.tree

	def enclosing(self, node, kind):
		while node in self.parents:
			node = self.parents[node]
			if isinstance(node, kind): return node
		return None

	def resolve_name(self, name, at_node, bind=None):
		if bind and name in bind: return bind[name]
		scope = self.scope_of(at_node)
		for sc in (scope, self.tree):
			found = [v for ln, v in self.assigns.get((sc, name), []) if ln <= at_node.lineno]
			if found: return found[-1]
		return None

	def sval(self, node, at, bind=None, depth=0):
		'''Best-effort static value of a string expression'''
		if node is None or depth > 6: return None
		if isinstance(node, ast.Constant) and isinstance(node.value, str): return node.value
		if isinstance(node, ast.Name):
			return self.sval(self.resolve_name(node.id, at, bind), at, bind, depth + 1)
		if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
			a, b = self.sval(node.left, at, bind, depth + 1), self.sval(node.right, at, bind, depth + 1)
			if a is None and b is None: return None
			return (a or '') + (b or '')
		if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
			return self.sval(node.left, at, bind, depth + 1)
		if isinstance(node, ast.JoinedStr):
			return ''.join(v.value if isinstance(v, ast.Constant) else '{..}' for v in node.values)
		if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'format':
			return self.sval(node.func.value, at, bind, depth + 1)
		if isinstance(node, (ast.Tuple, ast.List)) and node.elts:
			return self.sval(node.elts[-1], at, bind, depth + 1)
		return None

	def section_at(self, node):
		func = self.enclosing(node, (ast.FunctionDef, ast.AsyncFunctionDef))
		start = func.lineno if func is not None else 0
		cand = [name for ln, name in self.sections if start <= ln <= node.lineno]
		parts = []
		cls = self.enclosing(node, ast.ClassDef)
		if cls is not None: parts.append(cls.name)
		if func is not None and func.name not in ('__init__',) and re.match(r'^_*(build|make|create|setup|init)', func.name):
			parts.append(pretty_func(func.name))
		if cand: parts.append(cand[-1])
		return ' > '.join(p for p in parts if p)

def target_key(node):
	'''self.group.btn_x -> btn_x ; btn -> btn'''
	if isinstance(node, ast.Attribute): return node.attr
	if isinstance(node, ast.Name): return node.id
	return None

def call_name(func):
	if isinstance(func, ast.Attribute): return func.attr
	if isinstance(func, ast.Name): return func.id
	return None

GENERIC_CALLS = {'get_modifier', 'getattr', 'setattr', 'bool', 'int', 'float', 'str', 'len', '_run', 'run', '_c', 'cb', 'partial'}

def callback_name(node, pf=None, at=None, bind=None, depth=0):
	'''Name of the function a callback ends up calling; follows names bound by loops / lambda defaults'''
	if node is None or depth > 4: return None
	if isinstance(node, ast.Name) and pf is not None:
		if not (bind and node.id in bind) and len(pf.assigns.get((pf.scope_of(at), node.id), [])) > 1: return None	# branch-dependent
		value = pf.resolve_name(node.id, at, bind)
		if value is not None: return callback_name(value, pf, at, bind, depth + 1)
	if isinstance(node, (ast.Attribute, ast.Name)): return target_key(node)
	if isinstance(node, ast.Lambda):
		# lambda s, _c=cb: _c()  -> follow the default
		for arg, default in zip(node.args.args[-len(node.args.defaults):] if node.args.defaults else [], node.args.defaults):
			if isinstance(node.body, ast.Call) and call_name(node.body.func) == arg.arg:
				return callback_name(default, pf, at, bind, depth + 1)
		node = node.body
	for sub in ast.walk(node):
		if isinstance(sub, ast.Call):
			name = call_name(sub.func)
			if name and name not in GENERIC_CALLS: return name
	return None

GENERIC_LOCALS = {'btn', 'button', 'b', 'w', 'item', 'act', 'action', 'chk', 'box', 'widget', 'new_button'}

def kwarg(call, *names):
	for kw in call.keywords:
		if kw.arg in names: return kw.value
	return None

def bind_targets(target, value, bind):
	if isinstance(target, ast.Name):
		bind[target.id] = value
	elif isinstance(target, (ast.Tuple, ast.List)) and isinstance(value, (ast.Tuple, ast.List)):
		for t, v in zip(target.elts, value.elts):
			bind_targets(t, v, bind)

def find_wrappers(pyfiles):
	'''Functions that forward a parameter as the token of a widget ctor: name -> spec'''
	wrappers = {}
	for pf in pyfiles:
		for fn in ast.walk(pf.tree):
			if not isinstance(fn, ast.FunctionDef): continue
			params = [a.arg for a in fn.args.args]
			offset = 1 if params[:1] == ['self'] else 0
			for call in ast.walk(fn):
				if not isinstance(call, ast.Call): continue
				ctor = call_name(call.func)
				if ctor not in PY_CTORS or len(call.args) <= PY_CTORS[ctor]: continue
				tok = call.args[PY_CTORS[ctor]]
				if not (isinstance(tok, ast.Name) and tok.id in params): continue
				spec = {'ctor': ctor, 'params': params[offset:], 'token': tok.id}
				tip = kwarg(call, 'tooltip')
				if isinstance(tip, ast.Name) and tip.id in params: spec['tooltip'] = tip.id
				cb = kwarg(call, 'callback')
				if isinstance(cb, ast.Name) and cb.id in params: spec['callback'] = cb.id
				parent = pf.parents.get(call)
				if isinstance(parent, ast.Call) and call_name(parent.func) == 'setattr' and len(parent.args) == 3:
					if isinstance(parent.args[1], ast.Name) and parent.args[1].id in params: spec['attr'] = parent.args[1].id
				wrappers[fn.name] = spec
	return wrappers

def py_rows(project, base, glyphs):
	rows, pyfiles = [], []
	for path in walk_files(base, {'.py'}):
		try:
			with open(path, encoding='utf-8') as f:
				pyfiles.append(PyFile(path, f.read()))
		except (SyntaxError, UnicodeDecodeError) as err:
			print('! skip %s: %s' % (rel(path, base), err), file=sys.stderr)

	wrappers = find_wrappers(pyfiles)

	for pf in pyfiles:
		consumed = set()

		def emit(call, ctor, tok_node, tip_node, name, cb_node, bind=None, obj_name=None):
			token = pf.sval(tok_node, call, bind)
			if token is None: return False
			tip = pf.sval(tip_node, call, bind) if tip_node is not None else None
			if tip is None and name: tip = pf.post_tips.get(name)
			cb = callback_name(cb_node, pf, call, bind) if cb_node is not None else None
			if cb is None and name: cb = pf.post_cb.get(name)
			if name in GENERIC_LOCALS: name = None
			line = call.lineno
			if bind:
				line = min(getattr(v, 'lineno', line) for v in bind.values())

			if obj_name is None:
				obj = kwarg(call, 'obj_name')
				if ctor == 'CustomSpinButton' and len(call.args) > 3: obj = call.args[3]
				obj_name = pf.sval(obj, call, bind) if obj is not None else None
			icon_font = ctor in PY_ICON_CTORS or obj_name in ICON_OBJ_NAMES
			if ctor == 'QAction' and name and re.search(r'\b%s\.setFont\(' % re.escape(name), pf.text): icon_font = True

			is_icon = token in glyphs or (icon_font and re.match(r'^[a-z][a-z0-9]*(_[A-Za-z0-9]+)+$', token))
			if ctor in PY_LABELS and not is_icon: return True
			if ctor == 'QLabel': return True

			rows.append({
				'Project': project,
				'Plugin/Script': plugin_name(project, pf.path, base) + ((' (%s)' % pf.app_name) if pf.app_name else ''),
				'File': rel(pf.path, base),
				'Panel/Toolbar/Section': pf.section_at(call),
				'Button/Action': name or '',
				'Caption': (tip or ('' if is_icon else token)).strip(),
				'Icon': token if is_icon else '',
				'Text': '' if is_icon else token,
				'IconFontWidget': bool(icon_font),
				'Callback': cb or '',
				'Widget': ctor,
				'Source': '%s:%d' % (rel(pf.path, base), line),
			})
			for sub in ast.walk(call): consumed.add(id(sub))
			if bind:
				for v in bind.values():
					for sub in ast.walk(v): consumed.add(id(sub))
			return True

		def assigned_name(call, bind=None):
			parent = pf.parents.get(call)
			if isinstance(parent, ast.Call) and call_name(parent.func) == 'setattr' and len(parent.args) == 3:
				return pf.sval(parent.args[1], call, bind)
			if not isinstance(parent, ast.Assign): return None
			name = target_key(parent.targets[0])
			# btn = IconButton(..); setattr(self.group, 'nt_' + token, btn)
			block = pf.parents.get(parent)
			for sub in ast.walk(block) if block is not None else ():
				if isinstance(sub, ast.Call) and call_name(sub.func) == 'setattr' and len(sub.args) == 3 \
						and isinstance(sub.args[2], ast.Name) and sub.args[2].id == name and sub.lineno >= parent.lineno:
					return pf.sval(sub.args[1], call, bind) or name
			return name

		def handle_call(call, bind=None):
			ctor = call_name(call.func)
			if ctor in PY_CTORS and len(call.args) > PY_CTORS[ctor]:
				idx = PY_CTORS[ctor]
				tip = kwarg(call, 'tooltip', 'toolTip')
				if tip is None and ctor == 'CustomSpinButton' and len(call.args) > 2: tip = call.args[2]
				if tip is None and ctor == 'TRCustomSpinController' and len(call.args) > 3: tip = call.args[3]
				return emit(call, ctor, call.args[idx], tip, assigned_name(call, bind), kwarg(call, 'callback'), bind)

			if ctor in wrappers:
				spec = wrappers[ctor]
				args = dict(zip(spec['params'], call.args))
				args.update({kw.arg: kw.value for kw in call.keywords if kw.arg})
				name = pf.sval(args.get(spec.get('attr')), call, bind) if spec.get('attr') else assigned_name(call, bind)
				return emit(call, spec['ctor'], args.get(spec['token']), args.get(spec.get('tooltip')), name,
						args.get(spec.get('callback')), bind, obj_name=None)
			return False

		# - Loops over literal tables: for token, tip, cb in BUTTONS: IconButton(.., token, ..)
		for loop in ast.walk(pf.tree):
			if not isinstance(loop, ast.For): continue
			it = loop.iter
			if isinstance(it, ast.Call) and isinstance(it.func, ast.Attribute) and it.func.attr in ('items', 'enumerate'):
				it = it.func.value
			if isinstance(it, (ast.Name, ast.Attribute)):
				it = pf.resolve_name(target_key(it), loop) if target_key(it) else None
			if isinstance(it, ast.Dict):
				items = [ast.Tuple(elts=[k, v], ctx=ast.Load()) for k, v in zip(it.keys, it.values)]
			elif isinstance(it, (ast.List, ast.Tuple)):
				items = it.elts
			else:
				continue
			calls = [c for c in ast.walk(loop) if isinstance(c, ast.Call) and (call_name(c.func) in PY_CTORS or call_name(c.func) in wrappers)]
			for item in items:
				bind = {}
				bind_targets(loop.target, item, bind)
				if not bind: continue
				if any(handle_call(c, bind) for c in calls):
					for sub in ast.walk(item): consumed.add(id(sub))
			for c in calls: consumed.add(id(c))

		# - Direct calls
		for call in ast.walk(pf.tree):
			if isinstance(call, ast.Call) and id(call) not in consumed:
				handle_call(call)

		# - Fallback: literal tuples / dict entries carrying a glyph name and a caption
		for node in ast.walk(pf.tree):
			if id(node) in consumed: continue
			cand = []
			if isinstance(node, (ast.Tuple, ast.List)):
				cand.append((node, list(node.elts)))
			elif isinstance(node, ast.Dict):
				for k, v in zip(node.keys, node.values):
					if isinstance(v, (ast.Tuple, ast.List)): cand.append((k, [k] + list(v.elts)))
			for anchor, elts in cand:
				strs = [e.value for e in elts if isinstance(e, ast.Constant) and isinstance(e.value, str)]
				icons = [s for s in strs if s in glyphs and '_' in s]
				tips = [s for s in strs if ' ' in s.strip()] or [s for s in strs if s[:1].isupper() and not s.isupper() and s not in glyphs]
				if len(icons) == 1 and tips and len(elts) <= 6:
					# Table handed to a builder: self.flow('nd_', ((token, tip, cb), ...))
					widget, bname, cb = 'table entry', '', None
					holder = pf.parents.get(node)
					holder = pf.parents.get(holder) if isinstance(holder, (ast.Tuple, ast.List)) else holder
					if isinstance(holder, ast.Call) and call_name(holder.func) not in ('dict', 'OrderedDict'):
						widget = call_name(holder.func) + '()'
						prefix = [a.value for a in holder.args if isinstance(a, ast.Constant) and isinstance(a.value, str)]
						if prefix and prefix[0].endswith('_'): bname = prefix[0] + icons[0]
					for e in elts:
						if isinstance(e, (ast.Lambda, ast.Attribute)):
							cb = callback_name(e, pf, anchor)
							break
					rows.append({
						'Project': project,
						'Plugin/Script': plugin_name(project, pf.path, base) + ((' (%s)' % pf.app_name) if pf.app_name else ''),
						'File': rel(pf.path, base),
						'Panel/Toolbar/Section': pf.section_at(anchor),
						'Button/Action': bname, 'Caption': tips[0].strip(), 'Icon': icons[0], 'Text': '',
						'IconFontWidget': True, 'Callback': cb or '', 'Widget': widget,
						'Source': '%s:%d' % (rel(pf.path, base), anchor.lineno),
					})
					for e in elts:
						for sub in ast.walk(e): consumed.add(id(sub))
	return rows

# - JS / HTML extraction -------------------------------------
JS_STR = r"""(?:'((?:[^'\\]|\\.)*)'|"((?:[^"\\]|\\.)*)")"""

def js_unquote(m, a=1):
	return m.group(a) if m.group(a) is not None else m.group(a + 1)

def match_brace(text, start):
	'''Index of the brace closing the one at text[start]'''
	depth, i, quote = 0, start, None
	while i < len(text):
		ch = text[i]
		if quote:
			if ch == '\\': i += 1
			elif ch == quote: quote = None
		elif ch in '\'"`': quote = ch
		elif ch in '{(': depth += 1
		elif ch in '})':
			depth -= 1
			if depth == 0: return i
		i += 1
	return len(text) - 1

def open_brace(text, pos):
	'''Index of the unmatched { before pos'''
	depth = 0
	for i in range(pos - 1, -1, -1):
		ch = text[i]
		if ch == '}': depth += 1
		elif ch == '{':
			if depth == 0: return i
			depth -= 1
	return -1

def html_clean(s):
	s = re.sub(r'<[^>]+>', ' ', s or '')
	for a, b in (('&hellip;', '...'), ('&rarr;', '->'), ('&larr;', '<-'), ('&amp;', '&'), ('&nbsp;', ' '), ('&#9656;', '')):
		s = s.replace(a, b)
	return re.sub(r'\s+', ' ', s).strip()

def js_rows(project, base, glyphs):
	rows = []
	for path in walk_files(base, {'.js', '.html'}):
		with open(path, encoding='utf-8') as f:
			text = f.read()
		line_of = lambda pos: text.count('\n', 0, pos) + 1
		name = os.path.basename(path)
		consumed = []

		# - Section markers
		sections = []
		for m in re.finditer(r"FRWidget\.(?:GroupBox|CollapsibleBox)\(\s*" + JS_STR, text):
			sections.append((m.start(), js_unquote(m)))
		for m in re.finditer(r"^[ \t]*//\s*(?:\d+\.\s*|-{2,}\s*)([A-Z][A-Za-z0-9 &/,+()'-]{2,60}?)\s*-*\s*$", text, re.M):
			sections.append((m.start(), m.group(1).strip().title() if m.group(1).isupper() else m.group(1).strip()))
		for m in re.finditer(r"<!--\s*(.+?)\s*-->", text):
			sections.append((m.start(), m.group(1).strip()))
		for m in re.finditer(r"""class="tb-menu-label"[^>]*>([^<]+)<|id="(tb-[\w-]+-menu)\"""", text):
			sections.append((m.start(), html_clean(m.group(1) or m.group(2))))
		sections.sort()

		def section_at(pos):
			prev = [s for p, s in sections if p <= pos and not re.match(r'^(=+|-+)$', s)]
			return prev[-1] if prev else ''

		def add(pos, end, icon, caption, bname, cb, widget, text_label=''):
			consumed.append((pos, end))
			rows.append({
				'Project': project, 'Plugin/Script': plugin_name(project, path, base), 'File': rel(path, base),
				'Panel/Toolbar/Section': (re.sub(r'[-_.]', ' ', os.path.splitext(name)[0]) + ' > ' + section_at(pos)).rstrip(' >'),
				'Button/Action': bname or '', 'Caption': html_clean(caption or text_label), 'Icon': icon or '',
				'Text': html_clean(text_label), 'IconFontWidget': bool(icon), 'Callback': cb or '', 'Widget': widget,
				'Source': '%s:%d' % (rel(path, base), line_of(pos)),
			})

		def is_consumed(pos):
			return any(a <= pos <= b for a, b in consumed)

		def obj_fields(obj):
			out = {}
			for key in ('tooltip', 'title', 'label', 'id', 'text', 'name'):
				m = re.search(r"\b%s\s*:\s*%s" % (key, JS_STR), obj)
				if m: out[key] = js_unquote(m)
			m = re.search(r"""npa\(\s*\\?["']([\w]+)""", obj) or re.search(r"""\b_?run\w*\(\s*["']([\w.]+)""", obj)
			if m: out['cb'] = m.group(1)
			else:
				m = re.search(r"on(?:Click|Change|Toggle)\s*:\s*(?:function\s*\([^)]*\)\s*\{\s*)?(?:[\w.]+\s*=\s*)?([A-Za-z_$][\w.$]*)\s*\(", obj)
				if m and m.group(1) not in ('if', 'function', 'return', 'var'): out['cb'] = m.group(1).split('.')[-1]
				else:
					m = re.search(r"on(?:Click|Change|Toggle)\s*:\s*([A-Za-z_$][\w.$]*)\s*[,}\n]", obj)
					if m: out['cb'] = m.group(1).split('.')[-1]
			return out

		# - Option objects with an icon key: FRWidget.Button(null, { icon:'x', tooltip:'..' }), registerWidget({..})
		for m in re.finditer(r"\bicon\s*:\s*(?:" + JS_STR + r"|([A-Za-z_$][\w$.\[\]]*))", text):
			ob = open_brace(text, m.start())
			if ob < 0: continue
			cb_end = match_brace(text, ob)
			obj = text[ob:cb_end + 1]
			head = text[max(0, ob - 160):ob]
			hm = re.search(r"(FRWidget\.\w+|registerWidget|\w+)\(\s*(?:(null|undefined)|" + JS_STR + r")?\s*,?\s*$", head)
			widget = hm.group(1) if hm else 'object'
			label = ''
			if hm and (hm.group(3) is not None or hm.group(4) is not None): label = hm.group(3) if hm.group(3) is not None else hm.group(4)
			f = obj_fields(obj)
			literal = js_unquote(m) if (m.group(1) is not None or m.group(2) is not None) else None
			if literal is None: continue		# variable icon - resolved by the table scan below
			if literal == '': continue
			caption = f.get('tooltip') or f.get('title') or f.get('label') or label
			bname = f.get('id') or f.get('name') or ''
			add(ob, cb_end, literal, caption, bname, f.get('cb'), widget, label or f.get('label', ''))

		# - Array tables feeding a loop: ['node_align_left', 'L', 'Align left']
		for m in re.finditer(r"\[\s*" + JS_STR + r"\s*,([^\[\]]*)\]", text):
			icon = js_unquote(m)
			if icon not in glyphs or '_' not in icon or is_consumed(m.start()): continue
			rest = [js_unquote(x) for x in re.finditer(JS_STR, m.group(3))]
			tips = [s for s in rest if ' ' in s.strip()]
			key = rest[0] if rest and re.match(r'^[A-Za-z_]\w+$', rest[0]) and rest[0] not in ('true', 'false', 'null', 'True', 'False') else ''
			add(m.start(), m.end(), icon, tips[-1] if tips else '', key, '', 'table entry')

		# - Icon spans in markup: <div id="btn-x" title=".."><span class="tri">file</span>Caption</div>
		for m in re.finditer(r"""<span class=\\?["']tri[^"'\\]*\\?["'][^>]*>\s*([\w]+)\s*</span>([^<'"]*)""", text):
			if is_consumed(m.start()): continue
			line_text = text[text.rfind('\n', 0, m.start()) + 1:m.start()].lstrip()
			if line_text.startswith(('//', '*', '/*')): continue		# documentation comment
			tag_start = text.rfind('<', 0, m.start())
			tag = text[tag_start:m.start()]
			idm = re.search(r"""\bid=\\?["']([\w-]+)""", tag)
			ttm = re.search(r"""\btitle=\\?["']([^"'\\]+)""", tag)
			cap = html_clean(m.group(2))
			if not cap:		# caption in a sibling element
				after = text[m.end():m.end() + 200]
				cm = re.match(r"""\s*<span[^>]*class=\\?["'][^"']*(?:label|text)[^"']*["'][^>]*>([^<]+)""", after)
				if cm: cap = html_clean(cm.group(1))
			bname = idm.group(1) if idm else ''
			if not bname:
				back = text[max(0, m.start() - 400):m.start()]
				ids = re.findall(r"""\bid=\\?["']([\w-]+)""", back)
				if ids and back.rfind('id=') > back.rfind('</'): bname = ids[-1]
			add(m.start(), m.end(), m.group(1), (ttm.group(1) if ttm else '') or cap, bname, '', 'span.tri', cap)

		# - FRWidget.icon('x') calls
		for m in re.finditer(r"FRWidget\.icon\(\s*" + JS_STR, text):
			if is_consumed(m.start()): continue
			ctx = text[m.end():m.end() + 300]
			tm = re.search(r"\b(?:title|tooltip)\s*[:=]\s*" + JS_STR, ctx)
			add(m.start(), m.end(), js_unquote(m), js_unquote(tm) if tm else '', '', '', 'FRWidget.icon')

		# - Text-only buttons: FRWidget.Button('Apply', {..}) / ToggleButton / SpinButton without an icon
		for m in re.finditer(r"FRWidget\.(Button|ToggleButton|SpinButton)\(\s*" + JS_STR + r"\s*(,\s*\{)?", text):
			if is_consumed(m.start()): continue
			obj, end = '', m.end()
			if m.group(4):
				ob = m.end() - 1
				end = match_brace(text, ob)
				obj = text[ob:end + 1]
			f = obj_fields(obj)
			add(m.start(), end, '', f.get('tooltip') or f.get('title') or js_unquote(m, 2), f.get('id', ''), f.get('cb'), 'FRWidget.' + m.group(1), js_unquote(m, 2))

		# - Plain HTML buttons / menu items without an icon
		for m in re.finditer(r"""<(button|div)\b([^>]*\bclass=["'][^"']*(?:btn|tb-menu-item|tool-btn)[^"']*["'][^>]*)>(.*?)</\1>""", text, re.S):
			if is_consumed(m.start()) or 'class="tri' in m.group(3) or 'tb-submenu' in m.group(2): continue
			attrs = m.group(2)
			label = html_clean(m.group(3))
			if not label or len(label) > 60: continue
			idm = re.search(r"""\bid=["']([\w-]+)""", attrs)
			ttm = re.search(r"""\btitle=["']([^"']+)""", attrs)
			add(m.start(), m.end(), '', (ttm.group(1) if ttm else '') or label, idm.group(1) if idm else '', '', '<%s>' % m.group(1), label)
	return rows

# - Flags ----------------------------------------------------
def match_word(token, pool):
	alts = {token} | SYNONYMS.get(token, set())
	for a in alts:
		for w in pool:
			if a == w: return True
			if len(a) >= 3 and len(w) >= 3 and (w.startswith(a) or a.startswith(w)): return True
	return False

def flag_rows(rows, glyphs):
	shared = defaultdict(set)
	for r in rows:
		if r['Icon']: shared[r['Icon']].add((r['Caption'].lower() or r['Button/Action'].lower()))

	for r in rows:
		flags = []
		icon = r['Icon']
		r['In font'] = '' if not icon else ('yes' if icon in glyphs else 'NO')
		r['Icon shared by'] = len(shared[icon]) if icon else ''

		if icon and icon not in glyphs: flags.append('icon missing from font')
		if r['IconFontWidget'] and not icon and r['Text']: flags.append('text "%s" on icon-font button' % r['Text'])
		if not icon: flags.append('no icon')

		if icon:
			itoks = [w for w in words(icon) if w not in ('alt',) and not w.isdigit()]
			name_pool = [w for w in words(r['Button/Action']) if w not in ('btn', 'chk', 'opt', 'act', 'cv', 'obs', 'lbl', 'self', 'group')]
			cap_pool = words(r['Caption']) + words(r['Callback'])
			hit_name = [t for t in itoks if match_word(t, name_pool)]
			hit_cap = [t for t in itoks if match_word(t, cap_pool)]
			hit_any = [t for t in itoks if match_word(t, name_pool + cap_pool)]

			if itoks and not hit_any:
				flags.append('icon unrelated to name/caption')
			elif itoks and name_pool and not hit_name and r['Button/Action']:
				flags.append('icon differs from button name')
			elif itoks and r['Caption'] and not hit_cap and ' ' in r['Caption']:
				flags.append('caption does not mention icon concept')
			if r['Caption'] == '' and r['Widget'] != 'span.tri': flags.append('no caption/tooltip')

		r['Flag'] = '; '.join(flags)
	return rows

# - Main -----------------------------------------------------
def main():
	ap = argparse.ArgumentParser(description='List buttons, captions and icons used across TypeRig projects')
	ap.add_argument('out', nargs='?', default=os.path.join(ROOT, 'lists', 'icon_usage.csv'))
	ap.add_argument('--font', default=FONT_VFJ)
	args = ap.parse_args()

	glyphs = font_glyphs(args.font)
	rows = []
	for project, base in PROJECTS:
		if not os.path.isdir(base):
			print('! missing %s' % base, file=sys.stderr)
			continue
		rows += py_rows(project, base, glyphs)
		if project == 'FontRig': rows += js_rows(project, base, glyphs)

	rows = flag_rows(rows, glyphs)
	rows.sort(key=lambda r: (r['Project'], r['File'], int(r['Source'].rsplit(':', 1)[1])))

	os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
	with open(args.out, 'w', encoding='utf-8-sig', newline='') as f:
		w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction='ignore')
		w.writeheader()
		w.writerows(rows)

	used = {r['Icon'] for r in rows if r['Icon']}
	print('-- %d rows -> %s' % (len(rows), args.out))
	print('-- %d distinct icons used, %d missing from font, %d font glyphs unused' % (
		len(used), len(used - glyphs), len({g for g in glyphs if re.match(r'^[a-z]+(_[A-Za-z0-9]+)+$', g)} - used)))

if __name__ == '__main__':
	main()
