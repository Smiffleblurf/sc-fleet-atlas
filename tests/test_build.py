"""Regression and public-data privacy checks for the static Fleet Atlas build.

Never include a real hangar export or private fleet identifiers in fixtures.
"""
import json
import hashlib
import pathlib
import re
import subprocess
import sys
import unittest
from urllib.parse import urlparse

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

    def test_flexible_generalist_lane_first(self):
        # Matrix and career lane filter follow the source catalog ordering.
        self.assertEqual(self.catalog['lanes'][0]['id'], 'FLEX')
        self.assertEqual(self.bundle['lanes'][0]['id'], 'FLEX')
        self.assertEqual([lane['id'] for lane in self.bundle['lanes']],
                         [lane['id'] for lane in self.catalog['lanes']])

    def test_module_roles_are_distinct_from_inherent_secondary_capabilities(self):
        rules = self.bundle['rulebook']
        self.assertEqual(rules['Liberator']['role'], 'carrier')
        self.assertEqual(set(rules['Liberator']['secondary']), {'repair', 'fuel'})
        self.assertIn('rearm', rules['Liberator']['note'])
        self.assertEqual(rules['Galaxy']['secondary'], [])
        self.assertEqual({r['role']: r['status'] for r in rules['Galaxy']['moduleRoles']},
                         {'freight': 'available', 'medical': 'available', 'refining': 'planned'})
        self.assertEqual(rules['Retaliator']['role'], 'gunship')
        self.assertEqual({r['role']: r['status'] for r in rules['Retaliator']['moduleRoles']},
                         {'strike': 'available', 'freight': 'available', 'assault': 'planned'})
        self.assertTrue(all(m['status'] == 'planned' for m in rules['Endeavor']['moduleRoles']))
        for name, code in (('Liberator', 'ANVL_Liberator'), ('Galaxy', 'RSI_Galaxy'),
                           ('Retaliator', 'AEGS_Retaliator'), ('Endeavor', 'MISC_Endeavor')):
            self.assertEqual(self.bundle['rulebook'][name], self.bundle['codeRules'][code])
        self.assertIn('id="includeSecondary" checked', self.html)
        self.assertIn('SECONDARY_PREF_KEY', self.html)
        self.assertIn('moduleRoleFor=(s,r)', self.html)
        self.assertIn('const confirmed=relevant.filter(s=>hasRole(s,r.id,f.secondary))', self.html)
        self.assertIn('const conditional=relevant.filter(s=>!hasRole(s,r.id,f.secondary))', self.html)
        self.assertIn('module-dependent possibilities are shown in the matrix but excluded', self.html)
        self.assertIn('.shipchip.module.planned.not-owned', self.template)
        self.assertIn('.shipchip.module.not-owned:hover', self.template)

    def test_hyun_inherent_mining_salvage_mapping(self):
        hyun = self.bundle['rulebook']['Hyūn']
        self.assertEqual(hyun['role'], 'mining')
        self.assertEqual(hyun['tier'], 'solo')
        self.assertEqual(hyun['secondary'], ['salvage'])
        self.assertNotIn('moduleRoles', hyun)
        self.assertEqual(hyun, self.bundle['codeRules']['GAMA_Hyun'])
        self.assertTrue(any(s['name'] == 'Hyūn' and s['role'] == 'mining' for s in self.bundle['referenceShips']))
        self.assertIn('gatachyun', self.html)
        self.assertIn("const q=normalizeName(t);return [s.name", self.html)
        self.assertIn('const dualIndustry=!ground&&(focusDual||equippedDual)', self.html)
        self.assertIn('description:englishLabel(x.description).slice(0,800)', self.html)
        self.assertIn('only ships in your imported fleet JSON', self.html)
        self.assertIn('ship.secondary=[...(match.secondary||[])];ship.moduleRoles=', self.html)

    def test_live_multi_role_detection(self):
        subprocess.run(['node', str(ROOT / 'tests' / 'test_live_catalog.cjs')],
                       cwd=ROOT, check=True, capture_output=True)

    def test_search_discovery_metadata(self):
        # Public-facing SEO metadata is present in generated and source HTML.
        canonical = 'https://smiffleblurf.github.io/sc-fleet-atlas/'
        self.assertIn('<title>Star Citizen Fleet Atlas | Ship Profession Map & Fleet Coverage</title>', self.html)
        self.assertIn('name="description"', self.html)
        self.assertIn('rel="canonical" href="' + canonical + '"', self.html)
        self.assertIn('property="og:title"', self.html)
        self.assertIn('property="og:description"', self.html)
        self.assertIn('property="og:url"', self.html)
        self.assertIn('<title>Star Citizen Fleet Atlas | Ship Profession Map & Fleet Coverage</title>', self.template)
        sitemap = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
        self.assertIn('<loc>' + canonical + '</loc>', sitemap)

    def test_favicon_matches_site_branding(self):
        favicon = (ROOT / 'favicon.svg').read_text(encoding='utf-8')
        self.assertIn('<link rel="icon" type="image/svg+xml" href="favicon.svg" sizes="any">', self.html)
        self.assertIn('viewBox="0 0 64 64"', favicon)
        self.assertIn('#9a75fc', favicon)
        self.assertIn('#398cbb', favicon)

    def test_hangarxplor_import_guidance_and_browser_support(self):
        # Help is reachable from an empty fleet and remains available after import.
        for html in (self.template, self.html):
            self.assertIn('id="importGuide"', html)
            self.assertIn('id="openImportGuide"', html)
            self.assertIn('Hangar Transfer Format (JSON)', html)
            self.assertIn('Chrome is not required', html)
            self.assertIn('https://hangarxplor.space/', html)
            self.assertIn('https://addons.mozilla.org/en-US/firefox/addon/star-citizen-hangar-xplorer/', html)
            self.assertIn('https://chromewebstore.google.com/detail/hangarxplor/', html)
            self.assertIn('https://robertsspaceindustries.com/account/pledges', html)
            self.assertIn("el('importGuide').open=true", html)

    def test_import_guide_shimmer_finishes_and_respects_reduced_motion(self):
        for html in (self.template, self.html):
            self.assertIn('<summary><span class="import-guide-title">New here?', html)
            self.assertIn('animation:import-guide-shimmer 2.5s ease-in-out .6s 2 forwards,import-guide-glow 2.5s ease-in-out .6s 2 forwards', html)
            self.assertIn('@keyframes import-guide-shimmer', html)
            self.assertIn('@keyframes import-guide-glow', html)
            self.assertIn('@keyframes import-guide-border', html)
            self.assertIn('@media(prefers-reduced-motion:reduce)', html)
            self.assertIn('.import-guide,.import-guide-title{animation:none}', html)
            self.assertIn('.import-guide-title{background:none;-webkit-text-fill-color:currentColor}', html)

    def test_shareable_fleet_graphic_has_local_preview_and_safe_exports(self):
        for html in (self.template, self.html):
            self.assertIn('id="shareMap"', html)
            self.assertIn('id="shareDialog"', html)
            self.assertIn('id="shareImage"', html)
            self.assertIn('id="shareZoom"', html)
            self.assertIn('function downloadFleetPng()', html)
            self.assertIn('function downloadFleetSvg()', html)
            self.assertIn('canvas.toBlob(resolve,\'image/png\')', html)
            self.assertIn('el(\'shareMap\').disabled=!ships.length', html)
            self.assertIn('el(\'shareDialog\').showModal()', html)
        self.assertIn('__FLEET_SHARE_JS__', self.template)
        self.assertIn('function fleetMapSvg(fleet,showSecondary', self.html)
        self.assertIn('BRIGHT  =  OWNED', self.html)
        self.assertIn('silhouetteAssets', self.html)
        self.assertIn('silhouetteNames', self.html)
        self.assertGreaterEqual(len(self.bundle['silhouetteNames']), 1)
        self.assertLessEqual(len(self.bundle['silhouetteAssets']), 243)

    def test_silhouette_assets_use_official_holoviewer_links(self):
        model_index = json.loads((ROOT / 'catalog' / 'holoviewer-models.json').read_text())
        self.assertGreaterEqual(len(model_index['models']), 200)
        known_ids = set()
        for model in model_index['models']:
            url = urlparse(model['url'])
            self.assertEqual(url.scheme, 'https')
            self.assertIn(url.hostname, ('robertsspaceindustries.com',
                                         'media.robertsspaceindustries.com'))
            self.assertTrue(url.path.endswith('.ctm'))
            known_ids.add(hashlib.sha256(model['url'].encode()).hexdigest()[:20])
        self.assertGreaterEqual(len(self.bundle['silhouetteAssets']), 180)
        self.assertTrue(set(self.bundle['silhouetteAssets']).issubset(known_ids))
        self.assertIn('DragonAceNL', self.html)
        self.assertIn('MADE BY THE COMMUNITY', self.html)
        self.assertFalse(list(ROOT.rglob('*.ctm')), '3D model meshes must not be committed')

    def test_built_index_matches_current_sources(self):
        # Prevent a future source edit from silently undoing the previewed HTML.
        self.assertEqual(self.html, self.template.replace(
            '__EMBED_DATA__',
            json.dumps(self.bundle, ensure_ascii=False, separators=(',', ':'))
            .replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026'),
        ).replace('__FLEET_SHARE_JS__',
                  (ROOT / 'src' / 'share-map.js').read_text(encoding='utf-8')))


if __name__ == '__main__':
    unittest.main()
