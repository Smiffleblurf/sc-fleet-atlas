#!/usr/bin/env python3
"""Build a standalone, no-network Fleet Atlas HTML page from public catalog data."""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CATALOG = json.loads((ROOT / 'catalog' / 'ship-roles.json').read_text(encoding='utf-8'))
ROLE_IDS = {r['id'] for lane in CATALOG['lanes'] for r in lane['roles']}
TIERS = {'solo', 'duo', 'small', 'multi', 'fleet', 'ground', 'unknown'}
for book in ('rulebook', 'codeRules'):
    for name, row in CATALOG[book].items():
        assert row['role'] in ROLE_IDS, (book, name, 'invalid role')
        assert row['tier'] in TIERS, (book, name, 'invalid tier')
        assert all(x in ROLE_IDS for x in row['secondary']), (book, name, 'invalid secondary')

# An offline reference snapshot, not a live API. Public classification/focus labels from
# the community FleetYards-derived meoiswa/rsi-ship-matrix ship list. The references
# are not a promise that a hull is currently pledgeable, released, or player-ownable.
# Only ship model names and broad profession information are incorporated; no
# individual hangar records are used in this catalog.
GROUND_WORDS = ('nox','dragonfly','hoverquad','g12','x1','ranger','cyclone','pulse',
                'roc','ptv','stv','utv','mule','ursa','nova','storm','atls','csv-sm',
                'lynx','mdc','mtc','spartan','ballista','centurion')

def key(name):
    return re.sub('[^a-z0-9]', '', name.lower())

def likely_ground(name, category):
    return category == 'Ground' or any(name.lower().startswith(w) for w in GROUND_WORDS)

def infer_role(category, focus, name):
    c, f = category.lower(), focus.lower()
    if likely_ground(name, category):
        if 'mine' in f or 'industrial' in f and name.lower().startswith('roc'):
            return 'surfacemining'
        if 'racing' in f or 'competition' in c:
            return 'groundracing'
        if any(w in f for w in ('combat', 'anti-', 'military', 'assault')):
            return 'groundcombat'
        if any(w in f for w in ('recon','explor','scout')):
            return 'groundscout'
        return 'groundutility'
    if 'science' in f or 'research' in f:
        return 'science'
    if 'refin' in f or 'processing' in f:
        return 'refining'
    if 'mining' in f or 'prospect' in f:
        return 'mining'
    if 'salvage' in f:
        return 'salvage'
    if 'construct' in f:
        return 'construction'
    if 'repair' in f:
        return 'repair'
    if 'refuel' in f:
        return 'fuel'
    if 'recovery' in f or 'tow' in f:
        return 'towing'
    if 'medical' in f or 'ambulance' in f:
        return 'medical'
    if 'report' in f or 'news' in f:
        return 'reporting'
    if 'racing' in f or c == 'competition':
        return 'racing'
    if 'bomber' in f or 'strike' in f:
        return 'strike'
    if 'mine' in f and c=='combat':
        return 'minelaying'
    if 'interdict' in f or 'electronic' in f or 'stealth' in f and 'fighter' not in f:
        return 'ew'
    if 'board' in f or 'dropship' in f or 'transport' in f and c=='combat':
        return 'assault'
    if 'heavy fighter' in f:
        return 'heavyfighter'
    if 'fighter' in f or 'snub' in f:
        return 'fighter'
    if any(w in f for w in ('destroyer','frigate','battlecruiser','corvette','capital')):
        return 'warship'
    if 'gunship' in f or 'gun ship' in f or 'patrol' in f:
        return 'gunship'
    if c == 'combat':
        return 'fighter'
    if 'passenger' in f:
        return 'passenger'
    if 'data' in f:
        return 'data'
    if 'carrier' in f:
        return 'carrier'
    if any(w in f for w in ('heavy freight','heavy hauler')):
        return 'heavyfreight'
    if any(w in f for w in ('medium freight','medium cargo','medium freighter','medium hauler')):
        return 'freight'
    if 'freight' in f or 'cargo' in f:
        return 'courier'
    if 'cargo loader' in f:
        return 'handling'
    if 'luxury' in f or 'touring' in f:
        return 'touring'
    if 'expedition' in f or 'deep space' in f:
        return 'expedition'
    if 'pathfind' in f or 'recon' in f or 'exploration' in f:
        return 'scout'
    return 'generalist'


def inferred_tier(name, category, crew_max):
    if likely_ground(name,category):
        return 'ground'
    n = int(crew_max)
    return 'solo' if n <= 1 else 'duo' if n == 2 else 'small' if n <= 4 else 'multi' if n <= 8 else 'fleet'


def reference_catalog():
    rows = []
    seen = set()
    for line in (ROOT / 'catalog' / 'reference-ships.txt').read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        name, category, focus, crew = line.split('|')
        k = key(name)
        assert k not in seen, ('duplicate reference model', name)
        seen.add(k)
        existing = CATALOG['rulebook'].get(name)
        role = existing['role'] if existing else infer_role(category, focus, name)
        tier = existing['tier'] if existing else inferred_tier(name, category, crew)
        assert role in ROLE_IDS and tier in TIERS, (name, role, tier)
        rows.append({'name': name, 'role': role, 'tier': tier, 'secondary': []})
    assert len(rows) >= 200, 'Reference dataset unexpectedly small'
    return rows

bundle = {k: CATALOG[k] for k in ('lanes', 'rulebook', 'codeRules')}
bundle['referenceShips'] = reference_catalog()
# Privacy boundary: never embed fleet entries, pledge metadata, or user-specific values.
bundle['ships'] = []
script_json = (json.dumps(bundle, ensure_ascii=False, separators=(',', ':'))
               .replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026'))
template = (ROOT / 'src' / 'template.html').read_text(encoding='utf-8')
assert template.count('__EMBED_DATA__') == 1
html = template.replace('__EMBED_DATA__', script_json)
(ROOT / 'index.html').write_text(html, encoding='utf-8')
if '--dist' in sys.argv:
    dest = ROOT / 'dist'
    dest.mkdir(exist_ok=True)
    (dest / 'index.html').write_text(html, encoding='utf-8')
print(f'Wrote index.html ({len(html.encode("utf-8")):,} bytes; '
      f'{len(bundle["referenceShips"])} reference models; no imported fleet)')