# Star Citizen Fleet Atlas (SCFA)
A community profession map for Star Citizen

An **unofficial, free, non-commercial fan project** for mapping an imported Star Citizen fleet by career and approximate crew-operating tier. Inspired by the profession-planning approach of StarShip42 ProfessionMap, but not affiliated with its creator.

The loss of StarShip42's ProfessionMap was immense. Having a high level overview of what ships you have against what profession roles was useful to see what gaps existed in your fleet, but what this does even better is help articulate those role gaps in your fleet!

We hope by starting this project it will encourage better profession mapping tools for players in the Star Citizen community.

## Features

- Import HangarXPLOR-style `shiplist.json` (JSON array) or an exported Fleet Atlas mapped JSON (`{ "ships": [...] }`).
- Explore profession lanes, secondary capabilities, crew-scale matrix, fleet roster, and generalized coverage observations.
- **Show ships not in my fleet** is enabled by default: unowned catalog ships appear greyed out but do not influence counts or gaps. Turn it off for an owned-only view.
- Checks the **Star Citizen Wiki API** (ship matrix and ground vehicles) for new public entries on launch, with a local 12-hour public-data cache and a Check ship updates button. The status shows the time of each successful check in the visitor’s local time zone, including seconds; offline failures are distinguished from successful refreshes. Falls back to bundled public catalog entries; a secondary public community snapshot is available if the Wiki API is blocked.
- Edit primary role and planning tier in the fleet roster, then export your mapped fleet as JSON or CSV.
- Works as a standalone HTML file, including offline using the bundled reference. **No accounts, analytics, backend, or hangar uploads.** Imports are processed inside your browser only. The app stores a cache of **public ship-catalog data** in local browser storage; it does **not** store your hangar file or send your private fleet over the network.
- Ships with no confident mapping appear as **Needs classification**. Public data can automatically refresh from the Star Citizen Wiki API as that community source updates; the editorial profession taxonomy is not automatically maintained, and upstream/API/CORS outages may temporarily prevent a live check.

**Important:** All ship role assignments and crew tiers are unofficial editorial planning estimates, not current game statistics or gameplay guarantees. Empty lanes are information—not recommendations to spend money.

## Try it

Open `index.html` in a modern browser, or use GitHub Pages. Click **Import fleet JSON** and choose your local `shiplist.json`. No hangar file is sent to a server. Online reference refreshes depend on browser cross-origin permissions (CORS), source uptime, and network access; the bundled snapshot works offline. The primary public ship data source is [Star Citizen Wiki API](https://docs.star-citizen.wiki/) (community-maintained, **not** an official CIG API). The bundled offline reference and optional secondary live fallback are based on public ship names and roles from the community-maintained [RSI Ship Matrix project](https://github.com/meoiswa/rsi-ship-matrix), which draws on FleetYards data. These secondary entries may be older or classified differently from the Wiki.

### Publish on GitHub Pages

The current live repository publishes **Deploy from a branch → `main` → `/(root)`**. After your pull request is merged, GitHub Pages serves the committed root `index.html` file. A deployment does **not** automatically rebuild it from sources.

For any changes to `src/template.html`, `catalog/ship-roles.json`, or `catalog/reference-ships.txt`, run `python scripts/build.py`, commit the regenerated `index.html` **together with the sources**, and run `python -m unittest discover -s tests -v`. This prevents the website and its source from drifting apart.

An optional `.github/workflows/pages.yml` is included in the release package for repositories that intentionally switch their GitHub Pages Source setting to **GitHub Actions**. Do not enable both publishing approaches as separate release workflows without first coordinating the change.

## Contribute a new ship or change a role

Edit `catalog/ship-roles.json`. `rulebook` keys are ship display names and `codeRules` keys are HangarXPLOR `ship_code` values. To add support for a new ship, add a `role`, `tier`, and `secondary` list. Please explain role/crew evidence in your pull request. Run `python scripts/build.py` to update the single-file release locally. The current branch-based Pages setup serves the checked-in `index.html` on merging to `main`.

See [CONTRIBUTING.md](CONTRIBUTING.md) and [the publishing checklist](PUBLISHING.md).

## Project and IP notices

This is an unofficial Star Citizen fan site, not affiliated with the Cloud Imperium group of companies. All content on this site not authored by its host or users are property of their respective owners.

Star Citizen and related game terms are owned by their respective owners. The website links to [the official Star Citizen website](https://robertsspaceindustries.com/). See [CIG fan-site rules](https://support.robertsspaceindustries.com/hc/en-us/articles/360006895793-Star-Citizen-Fankit-and-Fandom-FAQ).

This project intentionally includes **no official CIG art assets** and does not accept donations, advertising, or subscriptions. The MIT license applies to original project code and original project content only; it does not license third-party game IP.