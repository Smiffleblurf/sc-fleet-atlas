#!/usr/bin/env python3
"""Check RSI ship additions and generate silhouette thumbnails from approved model links.

Usage:
  python scripts/update_holoviewer.py --check
  python scripts/update_holoviewer.py --generate --limit 12

The checked-in link index comes from public RSI asset URLs; no 3D meshes are
committed. The site bundles derived PNG thumbnails only. Before publishing,
confirm the intended use complies with RSI's current fan-content terms.

Extra dependencies for --generate: numpy, pillow, openctm.
"""

import argparse
import base64
import concurrent.futures
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'catalog' / 'holoviewer-models.json'
THUMBS = ROOT / 'assets' / 'ship-silhouettes'
PACK = ROOT / 'assets' / 'ship-silhouettes.json'
SHIP_MATRIX = 'https://robertsspaceindustries.com/ship-matrix/index'
MAX_MODEL_BYTES = 64 * 1024 * 1024
HEADERS = {'User-Agent': 'FleetAtlasSilhouetteUpdater/0.1 (+https://smiffleblurf.github.io/sc-fleet-atlas/)'}


def key(value: str) -> str:
    normalized = value.lower().strip()
    normalized = re.sub(r'^constellation mk iv ', 'constellation ', normalized)
    normalized = re.sub(r'^nova tank$', 'nova', normalized)
    normalized = re.sub(r'^ursa rover$', 'ursa', normalized)
    return re.sub('[^a-z0-9]', '', normalized)


def asset_key(url: str) -> str:
    return hashlib.sha256(url.encode('utf-8')).hexdigest()[:20]


def packed_images() -> dict[str, str]:
    if not PACK.exists():
        return {}
    data = json.loads(PACK.read_text(encoding='utf-8'))
    return data.get('images', {})


def pack_assets(index: dict, previous: dict[str, str]) -> int:
    """Persist the thumbnails as one reviewable asset manifest in Git.

    Individual PNGs remain available locally for visual QA, while the small
    Base64 bundle is easier to commit and refresh in GitHub Actions.
    """
    images = dict(previous)
    for url in {model['url'] for model in index['models']}:
        aid = asset_key(url)
        if aid in images:
            continue
        path = THUMBS / (aid + '.png')
        if path.exists():
            raw = path.read_bytes()
            if raw.startswith(b'\x89PNG\r\n\x1a\n'):
                images[aid] = base64.b64encode(raw).decode('ascii')
    if images != previous:
        PACK.parent.mkdir(parents=True, exist_ok=True)
        PACK.write_text(json.dumps({'schema_version': 1, 'encoding': 'base64-png',
                                    'images': dict(sorted(images.items()))}, indent=2) + '\n',
                        encoding='utf-8')
    return len(images)


def fetch(url: str, size_limit: int = MAX_MODEL_BYTES, require_ctm: bool = True) -> bytes:
    parsed = urlparse(url)
    if parsed.scheme != 'https' or parsed.hostname not in {
        'robertsspaceindustries.com', 'media.robertsspaceindustries.com'
    }:
        raise ValueError('Only official RSI HTTPS models may be downloaded')
    with urlopen(Request(url, headers=HEADERS), timeout=35) as response:
        length = response.headers.get('Content-Length')
        if length and int(length) > size_limit:
            raise ValueError('Model exceeds the size limit')
        raw = response.read(size_limit + 1)
    if len(raw) > size_limit:
        raise ValueError('Model exceeds the size limit')
    if require_ctm and not raw.startswith(b'OCTM'):
        raise ValueError('The response was not an OpenCTM model')
    return raw


def collect_status(index: dict) -> dict:
    packed = packed_images()
    refs = {key(row['name']) for row in index['models']}
    data = json.loads(fetch(SHIP_MATRIX, size_limit=12 * 1024 * 1024, require_ctm=False))
    official = [row['name'] for row in data['data']]
    missing = [name for name in official if key(name) not in refs]
    available = sum(1 for row in index['models'] if
                    asset_key(row['url']) in packed or
                    (THUMBS / (asset_key(row['url']) + '.png')).is_file())
    missing_images = sum(1 for url in {row['url'] for row in index['models']} if
                         asset_key(url) not in packed and
                         not (THUMBS / (asset_key(url) + '.png')).is_file())
    return {
        'official_ship_matrix_entries': len(official),
        'indexed_model_names': len(index['models']),
        'generated_model_names': available,
        'indexed_models_waiting_for_a_thumbnail': missing_images,
        'not_in_model_index': missing,
        'note': 'Unknown model URLs are queued for future discovery, not treated as unavailable.'
    }


def generate(entry: tuple[str, str, int]) -> tuple[str, str]:
    name, url, rotation = entry
    dest = THUMBS / (asset_key(url) + '.png')
    if dest.exists():
        return name, 'cached'
    try:
        source = fetch(url)
        with tempfile.TemporaryDirectory(prefix='scfa-model-') as directory:
            mesh = Path(directory) / 'model.ctm'
            preview = Path(directory) / 'silhouette.png'
            mesh.write_bytes(source)
            # OpenCTM decodes native mesh data and some upstream models are
            # malformed. Isolate each render: a native crash must not take
            # down the whole refresh or poison the other workers.
            subprocess.run([
                sys.executable, str(ROOT / 'scripts' / 'render_silhouette.py'),
                str(mesh), str(preview), '--size', '192', '--padding', '10',
                '--rotation', str(rotation),
            ], check=True, capture_output=True, text=True, timeout=90)
            dest.write_bytes(preview.read_bytes())
        return name, 'generated'
    except Exception as exc:
        return name, f'ERROR {exc}'


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check', action='store_true', help='Compare against the live RSI ship list')
    p.add_argument('--generate', action='store_true', help='Download and render indexed missing models')
    p.add_argument('--limit', type=int, default=12, help='Max new models per run; 0 for all')
    p.add_argument('--workers', type=int, default=2, help='Concurrent fetch/render jobs, maximum 4')
    p.add_argument('--only', type=str, default='', help='Only ship names containing this text')
    args = p.parse_args()
    if not (args.check or args.generate):
        p.error('Specify --check and/or --generate')
    if not 1 <= args.workers <= 4 or args.limit < 0:
        p.error('--workers must be 1–4 and --limit must be nonnegative')
    index = json.loads(INDEX.read_text(encoding='utf-8'))
    if args.check:
        # Do not fail the whole regeneration when a public lookup is temporarily down.
        try:
            print(json.dumps(collect_status(index), indent=2))
        except Exception as exc:
            print('Official ship-matrix availability check failed:', exc)
    if args.generate:
        THUMBS.mkdir(parents=True, exist_ok=True)
        packed = packed_images()
        distinct = {}
        for row in index['models']:
            if args.only and args.only.lower() not in row['name'].lower():
                continue
            distinct.setdefault(row['url'], (row['name'], row['url'], row.get('rotation', 180)))
        tasks = [entry for entry in distinct.values() if
                 asset_key(entry[1]) not in packed and
                 not (THUMBS / (asset_key(entry[1]) + '.png')).exists()]
        if args.limit:
            tasks = tasks[:args.limit]
        print(f'Checking {len(tasks)} missing Holoviewer model(s).', flush=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            for name, outcome in pool.map(generate, tasks):
                print(f'  {name}: {outcome}', flush=True)
        print(f'Bundled {pack_assets(index, packed)} distinct silhouettes in {PACK.relative_to(ROOT)}.')


if __name__ == '__main__':
    main()
