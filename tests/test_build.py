"""Regression and public-data privacy checks for the static Fleet Atlas build.

Never include a real hangar export or private fleet identifiers in fixtures.
"""
import json
import pathlib
import re
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class BuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run(
            [sys.executable, str(ROOT / 'scripts' / 'build.py')],
            cwd=ROOT, check=True, capture_output=True,
        )
        cls.html = (ROOT / 'index.html').read_text(encoding='utf-8')
        cls.template = (ROOT / 'src' / 'template.html').read_text(encoding='utf-8')
        cls.catalog = json.loads((ROOT / 'catalog' / 'ship-roles.json').read_text(encoding='utf-8'))
        embedded = re.search(
            r'<script id="data" type="application/json">(.*?)</script>',
            cls.html, re.DOTALL,
        )
        assert embedded, 'Embedded public catalog is missing'
        cls.bundle = json.loads(embedded.group(1))

    def test_catalog_contains_no_hangar_records(self):
        self.assertNotIn('ships', self.catalog)
        self.assertGreater(len(self.catalog['rulebook']), 100)
        self.assertGreater(len(self.catalog['codeRules']), 100)
        for key in ('pledge_id', 'pledge_cost', 'pledge_date', 'pledge_name'):
            self.assertNotIn(key, json.dumps(self.catalog))

    def test_public_build_starts_with_empty_fleet(self):
        self.assertEqual(self.bundle['ships'], [])
        self.assertIn('let ships=[]', self.html)
        self.assertIn('This is an unofficial Star Citizen fan site', self.html)
        self.assertNotIn('pledge_id', self.html)
        self.assertNotIn('pledge_cost', self.html)
        self.assertNotIn('shiplist.json</script>', self.html)

    def test_reference_overlay_and_refresh_controls(self):
        reference = self.bundle['referenceShips']
        self.assertGreaterEqual(len(reference), 200)
        self.assertEqual(len(reference), len({re.sub('[^a-z0-9]', '', r['name'].lower()) for r in reference}))
        self.assertTrue(all(row['role'] and row['tier'] for row in reference))
        self.assertIn('id="showUnowned" checked', self.html)
        self.assertIn('id="checkUpdates"', self.html)
        self.assertIn('shipchip not-owned', self.template)
        self.assertIn('const LIVE_CATALOG_URL=', self.html)
        self.assertIn('https://api.star-citizen.wiki/api/shipmatrix/vehicles', self.html)
        self.assertIn('https://api.star-citizen.wiki/api/ground-vehicles', self.html)
        self.assertIn("credentials:'omit'", self.html)
        self.assertIn('if(!force && cached && Date.now()-cached.checked<CATALOG_CACHE_AGE)', self.html)

    def test_catalog_refresh_shows_local_timestamp(self):
        # A successful manual refresh must visibly update a local timestamp;
        # cached and failed refreshes must be labelled honestly.
        self.assertIn('function catalogCheckTime(value)', self.html)
        self.assertIn("timeZoneName:'short'", self.html)
        self.assertIn('storePublicCache(distilled,checkedAt)', self.html)
        self.assertIn('last checked ${catalogCheckTime(cached.checked)}', self.html)
        self.assertIn('updated from ${source} · checked ${catalogCheckTime(checkedAt)}', self.html)
        self.assertIn('live check unavailable at ${attemptedAt}', self.html)
        self.assertIn('last successful check ${catalogCheckTime(cached.checked)}', self.html)

    def test_built_index_matches_current_sources(self):
        # Prevent a future source edit from silently undoing the previewed HTML.
        self.assertEqual(self.html, self.template.replace(
            '__EMBED_DATA__',
            json.dumps(self.bundle, ensure_ascii=False, separators=(',', ':'))
            .replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026'),
        ))


if __name__ == '__main__':
    unittest.main()
