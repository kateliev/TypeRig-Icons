# SCRIPT: TypeRig Icons / VFJ tool
# -----------------------------------------------------------
# Inspect and merge FontLab VFJ glyphs.
#	python scripts/vfj_tool.py list  [font.vfj] [pattern]          names (fnmatch pattern)
#	python scripts/vfj_tool.py dump  [font.vfj] name [name ...]     glyph JSON
#	python scripts/vfj_tool.py stats [font.vfj]                     style profile: stroke styles, grid, layers
#	python scripts/vfj_tool.py merge src.vfj dst.vfj [--replace]    copy glyphs of src into dst (by name)
# font.vfj defaults to sources/typerig-icons.vfj.
# -----------------------------------------------------------

import argparse
import collections
import fnmatch
import json
import os
import re
import sys

from icon_draw import save_vfj

# - Init --------------------------------------------------
FONT_VFJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sources', 'typerig-icons.vfj')

def load(path):
	with open(path, encoding='utf-8') as f:
		return json.load(f)

def split_font(args):
	'''First arg is a .vfj path if it ends with .vfj, else the default font'''
	if args and args[0].lower().endswith('.vfj'): return args[0], args[1:]
	return FONT_VFJ, args

# - Commands ----------------------------------------------
def cmd_list(args):
	path, rest = split_font(args)
	names = [g['name'] for g in load(path)['font']['glyphs']]
	if rest: names = fnmatch.filter(names, rest[0])
	print('\n'.join(names))
	print('-- {} glyphs'.format(len(names)), file=sys.stderr)

def cmd_dump(args):
	path, names = split_font(args)
	glyphs = {g['name']: g for g in load(path)['font']['glyphs']}
	for n in names:
		print(json.dumps(glyphs.get(n, {'missing': n}), indent=1, ensure_ascii=False))

def cmd_stats(args):
	path, _ = split_font(args)
	G = load(path)['font']['glyphs']
	styles, grid, layers, adv = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()

	for g in G:
		for L in g.get('layers', []):
			layers[(L.get('name'), L.get('flags'))] += 1
			adv[L.get('advanceWidth')] += 1
			for e in L.get('elements', []):
				ed = e.get('elementData')
				if not isinstance(ed, dict): continue
				styles[json.dumps({k: e[k] for k in ('pen', 'stroke', 'brush') if k in e}, sort_keys=True)] += 1
				for c in ed.get('contours', []):
					for n in c['nodes']:
						for v in re.findall(r'-?\d+(?:\.\d+)?', n)[-2:]:
							v = float(v)
							grid['32' if v % 32 == 0 else '16' if v % 16 == 0 else '8' if v % 8 == 0 else 'off'] += 1

	print('Glyphs:', len(G))
	print('Advance widths:', dict(adv))
	print('Layers (name, flags):', layers.most_common())
	print('On-curve grid:', dict(grid))
	print('Element styles:')
	for k, v in styles.most_common(15): print('  {:4d}  {}'.format(v, k))

def cmd_merge(args):
	ap = argparse.ArgumentParser(prog='vfj_tool.py merge')
	ap.add_argument('src'); ap.add_argument('dst')
	ap.add_argument('--replace', action='store_true', help='Replace glyphs that already exist in dst')
	a = ap.parse_args(args)

	src, dst = load(a.src), load(a.dst)
	if src['font'].get('upm') != dst['font'].get('upm'):
		sys.exit('UPM differs ({} vs {}): FontLab would rescale. Aborted.'.format(src['font'].get('upm'), dst['font'].get('upm')))

	index = {g['name']: i for i, g in enumerate(dst['font']['glyphs'])}
	added, replaced, kept = [], [], []
	for g in src['font']['glyphs']:
		if g['name'] in index:
			if a.replace:
				dst['font']['glyphs'][index[g['name']]] = g; replaced.append(g['name'])
			else:
				kept.append(g['name'])
		else:
			dst['font']['glyphs'].append(g); added.append(g['name'])

	dst['font']['glyphsCount'] = len(dst['font']['glyphs'])
	save_vfj(dst, a.dst)	# FontLab's own layout, so the diff shows only the glyph changes
	print('Added: {}\nReplaced: {}\nSkipped (exist, no --replace): {}'.format(added, replaced, kept))

# - Run ---------------------------------------------------
if __name__ == '__main__':
	commands = {'list': cmd_list, 'dump': cmd_dump, 'stats': cmd_stats, 'merge': cmd_merge}
	if len(sys.argv) < 2 or sys.argv[1] not in commands:
		sys.exit('Usage: vfj_tool.py {list|dump|stats|merge} ...')
	commands[sys.argv[1]](sys.argv[2:])
