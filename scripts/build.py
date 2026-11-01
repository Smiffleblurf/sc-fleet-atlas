#!/usr/bin/env python3
"""Build a fully self-contained Fleet Atlas HTML page from template + public catalog."""
from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[1]
CATALOG = json.loads((ROOT / 'catalog' / 'ship-roles.json').read_text(encoding='utf-8'))
role_ids={r['id'] for lane in CATALOG['lanes'] for r in lane['roles']}
valid_tiers={'solo','duo','small','multi','fleet','ground','unknown'}
for book in ('rulebook','codeRules'):
    for name,row in CATALOG[book].items():
        assert row['role'] in role_ids,(book,name,'invalid role')
        assert row['tier'] in valid_tiers,(book,name,'invalid tier')
        assert all(x in role_ids for x in row['secondary']),(book,name,'invalid secondary')
# IMPORTANT: no user-specific fleet should ever be embedded in this bundle.
bundle={key: CATALOG[key] for key in ('lanes','rulebook','codeRules')}
bundle['ships']=[]
json_in_script=json.dumps(bundle,ensure_ascii=False,separators=(',',':')).replace('<','\u003c').replace('>','\u003e').replace('&','\u0026')
template=(ROOT/'src'/'template.html').read_text(encoding='utf-8')
assert template.count('__EMBED_DATA__')==1
html=template.replace('__EMBED_DATA__',json_in_script)
(ROOT/'index.html').write_text(html,encoding='utf-8')
if '--dist' in __import__('sys').argv:
    d=ROOT/'dist';d.mkdir(exist_ok=True)
    (d/'index.html').write_text(html,encoding='utf-8')
print(f'Wrote index.html ({len(html.encode("utf-8")):,} bytes, {len(bundle["rulebook"])} classifications, zero embedded ships)')
