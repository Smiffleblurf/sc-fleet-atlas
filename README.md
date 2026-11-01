# Star Citizen Fleet Atlas (SCFA)
A community profession map for Star Citizen

An **unofficial, free, non-commercial fan project** for mapping an imported Star Citizen fleet by career and approximate crew-operating tier. Inspired by the profession-planning approach of StarShip42 ProfessionMap, but not affiliated with its creator.

The loss of StarShip42's ProfessionMap was immense. Having a high level overview of what ships you have against what profession roles was useful to see what gaps existed in your fleet, but what this does even better is help articulate those role gaps in your fleet!

We hope by starting this project it will encourage better profession mapping tools for players in the Star Citizen community.

## Features

- Import HangarXPLOR-style `shiplist.json` (JSON array) or an exported Fleet Atlas mapped JSON (`{ "ships": [...] }`).
- Explore profession lanes, secondary capabilities, crew-scale matrix, fleet roster, and generalized coverage observations.
- Edit primary role and planning tier in the fleet roster, then export your mapped fleet as JSON or CSV.
- Works as a standalone, offline HTML file. **No accounts, analytics, cookies, backend, or network upload.** Imports are processed inside your browser only.
- Ships that the manual catalog doesn't recognize appear as **Needs classification**. The catalog does **not** automatically sync with CIG.

**Important:** All ship role assignments and crew tiers are unofficial editorial planning estimates, not current game statistics or gameplay guarantees. Empty lanes are information—not recommendations to spend money.

## Try it

Open `index.html` in a modern browser, or upload the repository to GitHub Pages. Click **Import fleet JSON** and choose your local `shiplist.json`. No file is sent to a server.

### Publish on GitHub Pages

1. Create a **public** GitHub repository and upload these files (preserving folders). `index.html` must remain in the repository root.
2. In the repository, open **Settings → Pages → Build and deployment**.
3. Choose **GitHub Actions** as the source. The included workflow builds from `src/template.html` and `catalog/ship-roles.json`, then deploys to GitHub Pages on pushes to `main`.
4. Wait for the Pages workflow to succeed. The website address appears under **Settings → Pages**.

For simpler no-workflow hosting, choose **Deploy from a branch → main → /(root)**; however, editing the catalog then requires rebuilding `index.html` and committing it.

## Contribute a new ship or change a role

Edit `catalog/ship-roles.json`. `rulebook` keys are ship display names and `codeRules` keys are HangarXPLOR `ship_code` values. To add support for a new ship, add a `role`, `tier`, and `secondary` list. Please explain role/crew evidence in your pull request. Run `python scripts/build.py` to update the single-file release locally. GitHub Actions builds and deploys the current sources automatically on merging to `main`.

See [CONTRIBUTING.md](CONTRIBUTING.md) and [the publishing checklist](PUBLISHING.md).

## Project and IP notices

This is an unofficial Star Citizen fan site, not affiliated with the Cloud Imperium group of companies. All content on this site not authored by its host or users are property of their respective owners.

Star Citizen and related game terms are owned by their respective owners. The website links to [the official Star Citizen website](https://robertsspaceindustries.com/). See [CIG fan-site rules](https://support.robertsspaceindustries.com/hc/en-us/articles/360006895793-Star-Citizen-Fankit-and-Fandom-FAQ).

This project intentionally includes **no official CIG art assets** and does not accept donations, advertising, or subscriptions. The MIT license applies to original project code and original project content only; it does not license third-party game IP.
