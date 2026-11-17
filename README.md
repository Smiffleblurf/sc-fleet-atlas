# Star Citizen Fleet Atlas (SCFA)
A community profession map for Star Citizen

**[Launch SC Fleet Atlas](https://smiffleblurf.github.io/sc-fleet-atlas/)** — free, browser-based profession matrix and fleet coverage tool.

An **unofficial, free, non-commercial fan project** for mapping an imported Star Citizen fleet by career and approximate crew-operating tier. Inspired by the profession-planning approach of StarShip42 ProfessionMap, but not affiliated with its creator.

The loss of StarShip42's ProfessionMap was immense. Having a high level overview of what ships you have against what profession roles was useful to see what gaps existed in your fleet, but what this does even better is help articulate those role gaps in your fleet!

We hope by starting this project it will encourage better profession mapping tools for players in the Star Citizen community.

## Features

- Import HangarXPLOR-style `shiplist.json` (JSON array) or an exported Fleet Atlas mapped JSON (`{ "ships": [...] }`).
- Explore profession lanes, built-in secondary capabilities, configurable module roles, crew-scale matrix, fleet roster, and generalized coverage observations.
- **Include secondary & module roles** is enabled by default and remembers your choice on that device (only this UI preference is stored, never your fleet). Built-in secondary capabilities count as coverage; optional module configurations appear as dotted chips and are **not counted as confirmed owned coverage**. Planned modules are distinctly marked.
- **Show ships not in my fleet** is enabled by default: unowned catalog ships appear greyed out but do not influence counts or gaps. Turn it off for an owned-only view.
- Checks the **Star Citizen Wiki API** (ship matrix and ground vehicles) for new public entries on launch, with a local 12-hour public-data cache and a Check ship updates button. The status shows the time of each successful check in the visitor’s local time zone, including seconds; offline failures are distinguished from successful refreshes. Falls back to bundled public catalog entries; a secondary public community snapshot is available if the Wiki API is blocked.
- Edit primary role and planning tier in the fleet roster, then export your mapped fleet as JSON or CSV.
- Works as a standalone HTML file, including offline using the bundled reference. **No accounts, analytics, backend, or hangar uploads.** Imports are processed inside your browser only. The app stores a cache of **public ship-catalog data** in local browser storage; it does **not** store your hangar file or send your private fleet over the network.
- Ships with no confident mapping appear as **Needs classification**. Public data can automatically refresh from the Star Citizen Wiki API as that community source updates; the editorial profession taxonomy is not automatically maintained, and upstream/API/CORS outages may temporarily prevent a live check.

**Important:** All ship role assignments and crew tiers are unofficial editorial planning estimates, not current game statistics or gameplay guarantees. Empty lanes are information—not recommendations to spend money.

### Modular ships and current gameplay

The editorial catalog distinguishes always-available secondary functions from roles requiring a specific interchangeable module. Ownership of a ship hull alone does not establish which module is installed or owned. For example:

- **RSI Galaxy:** Cargo and Med Bay modules are available in Alpha 4.10.3; the Refinery module is planned. These are mutually exclusive central-bay configurations.
- **Aegis Retaliator:** Torpedo and Cargo modules are available for its two bays; Dropship is a planned module. The ship may mix cargo and torpedo modules. Its unmodified hull is classified as a gunship for the profession map.
- **MISC Endeavor:** Research-oriented primary role with planned pod configurations for medical, agriculture, scouting, and landing support. The ship is still a concept; these are not playable modules.
- **Anvil Liberator:** Carrier with limited built-in repair, refuel and rearm support. In Alpha 4.10.3 the services work in its internal garages; expansion to exterior pads is planned. This is not the equivalent of a dedicated refueling or repair ship.

For background, see the [Galaxy specifications](https://robertsspaceindustries.com/en/comm-link/transmission/21346-RSI-Galaxy), [Retaliator module introduction](https://robertsspaceindustries.com/en/comm-link/transmission/19933-Aegis-Retaliator), [Endeavor concept](https://robertsspaceindustries.com/en/comm-link/transmission/14972-Research-Unbound-The-MISC-Endeavor), and [Liberator introduction](https://robertsspaceindustries.com/en/comm-link/transmission/21348-Anvil-Liberator). These classifications should be revisited as CIG changes gameplay or launches modules.

## Try it

Open `index.html` in a modern browser, or use GitHub Pages. Click **Import fleet JSON** and choose your local `shiplist.json`. No hangar file is sent to a server. Online reference refreshes depend on browser cross-origin permissions (CORS), source uptime, and network access; the bundled snapshot works offline. The primary public ship data source is [Star Citizen Wiki API](https://docs.star-citizen.wiki/) (community-maintained, **not** an official CIG API). The bundled offline reference and optional secondary live fallback are based on public ship names and roles from the community-maintained [RSI Ship Matrix project](https://github.com/meoiswa/rsi-ship-matrix), which draws on FleetYards data. These secondary entries may be older or classified differently from the Wiki.

### Share a fleet career graphic

After importing a fleet, choose **Fleet graphic** to preview a wide, three-panel, profession-by-crew-tier map inspired by the visual economy of StarShip42's classic ProfessionMap. Download a **3840-pixel PNG** for Discord or an **SVG** for lossless resizing. The chart shows the public catalog as top-down ship silhouettes: **bright = owned** and **faded = not in your imported fleet**. This makes career gaps visible without long ship-name lists or crowded `+N` labels. Hover descriptions in the SVG identify individual ships and capabilities; a diamond with a question mark means no verified model silhouette is available yet.

The **Include secondary & module roles** checkbox controls whether the chart also displays built-in secondary functions and conditional modules. Available and planned module options have distinct markings and never count as confirmed functions. Import and graphic generation are completely local: no RSI account IDs, pledge data, prices, or hangar JSON leave your browser. The SVG and PNG contain no private hangar fields, only names and owned/unowned visual status.

For a synthetic visual test, run `node tests/test_export_map.cjs`. Image export runs without third-party libraries in visitors' browsers.

### Ship silhouette sources and update checks

The silhouettes are rendered from publicly available [RSI Holoviewer](https://robertsspaceindustries.com/en/ship-matrix) 3D meshes into small transparent, top-down PNGs. **Original 3D models are never distributed with the site.** The starting list of official model URLs was gathered by [DragonAceNL](https://www.reddit.com/r/starcitizen/comments/1tmimsy/rsi_3d_model_download_links_odin_model_added/); we credit that index, while model artwork remains the property of its respective owners. The silhouette assets themselves are not covered by the project's MIT code license. This is a free, non-commercial fan site governed by [RSI's fan-content guidance](https://support.robertsspaceindustries.com/hc/en-us/articles/360006895793-Star-Citizen-Fankit-and-Fandom-FAQ).

`catalog/holoviewer-models.json` records indexed official model URLs. `scripts/update_holoviewer.py --check` compares them against RSI's public ship matrix and flags names without known models. `scripts/update_holoviewer.py --generate --limit 12` downloads missing **indexed** meshes temporarily, renders their silhouettes locally, and packs the tiny Base64 PNGs into `assets/ship-silhouettes.json` for version control. Individual PNGs are ignored as reproducible build products. Dependencies for artwork generation: `numpy`, `pillow`, and `openctm`; run `python scripts/build.py` afterward to embed the bundle into the offline HTML. A weekly GitHub Actions check reruns this pipeline and proposes a review PR when additional indexed silhouettes are generated. **It does not yet discover arbitrary new `.ctm` URLs automatically**; a newly listed ship with no indexed model is flagged for investigation, not presented as a confirmed missing model. Reviewers should verify source permission and visually check new silhouettes before merging.

### Get your hangar JSON

1. Install [HangarXPLOR](https://hangarxplor.space/) from the [Chrome Web Store](https://chromewebstore.google.com/detail/hangarxplor/bhkgemjdepodofcnmekdobmmbifemhkc/), [Firefox Add-ons](https://addons.mozilla.org/en-US/firefox/addon/star-citizen-hangar-xplorer/), or [Opera Add-ons](https://addons.opera.com/en/extensions/details/star-citizen-hangar-xplorer/).
2. Sign in and visit your [RSI My Hangar](https://robertsspaceindustries.com/account/pledges). Let HangarXPLOR finish loading the hangar pages.
3. Use HangarXPLOR's ship export in **Hangar Transfer Format (JSON)**, rather than CSV, and save the downloaded file.
4. Open Fleet Atlas and select **Import fleet JSON**. The file is parsed locally and is never uploaded.

**Chrome is not required.** HangarXPLOR provides extensions for Chrome, Firefox, and Opera. Fleet Atlas itself runs in modern browsers, independent of where the JSON was exported. The official HangarXPLOR project lists Edge support as on hold and Safari as requiring a manual extension build.

### Publish on GitHub Pages

The current live repository publishes **Deploy from a branch → `main` → `/(root)`**. After your pull request is merged, GitHub Pages serves the committed root `index.html` file. A deployment does **not** automatically rebuild it from sources.

For any changes to `src/template.html`, `catalog/ship-roles.json`, or `catalog/reference-ships.txt`, run `python scripts/build.py`, commit the regenerated `index.html` **together with the sources**, and run `python -m unittest discover -s tests -v`. This prevents the website and its source from drifting apart.

An optional `.github/workflows/pages.yml` is included in the release package for repositories that intentionally switch their GitHub Pages Source setting to **GitHub Actions**. Do not enable both publishing approaches as separate release workflows without first coordinating the change.

## Contribute a new ship or change a role

Edit `catalog/ship-roles.json`. `rulebook` keys are ship display names and `codeRules` keys are HangarXPLOR `ship_code` values. To add support for a new ship, add a `role`, `tier`, and `secondary` list. For conditional configurations, use `moduleRoles` entries with `role`, `module` name, and `status` (`available` or `planned`). A plain `secondary` capability means the hull has that function without swapping modules. Please explain role/crew and module evidence in your pull request. Run `python scripts/build.py` to update the single-file release locally. The current branch-based Pages setup serves the checked-in `index.html` on merging to `main`.

See [CONTRIBUTING.md](CONTRIBUTING.md) and [the publishing checklist](PUBLISHING.md).

## Project and IP notices

This is an unofficial Star Citizen fan site, not affiliated with the Cloud Imperium group of companies. All content on this site not authored by its host or users are property of their respective owners.

Star Citizen and related game terms are owned by their respective owners. The website links to [the official Star Citizen website](https://robertsspaceindustries.com/). See [CIG fan-site rules](https://support.robertsspaceindustries.com/hc/en-us/articles/360006895793-Star-Citizen-Fankit-and-Fandom-FAQ).

The site includes small, derived top-down silhouettes from publicly accessible RSI Holoviewer model assets, used solely as illustrative fan material. It does not distribute original 3D files, accept donations, serve advertising, or charge subscriptions. The MIT license applies to original project code and authored content only; it does **not** license CIG/RSI ship designs, silhouettes derived from them, or other third-party IP.
