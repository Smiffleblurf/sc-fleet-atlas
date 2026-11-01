# Contributing to Fleet Atlas

Thanks for improving an independent fan project. Pull requests and issue reports are welcome.

## Common contributions

- New ship: add a rule in `catalog/ship-roles.json`, ideally with a `ship_code` alias to support renamed hangar ships.
- Accuracy change: include a source and note whether a role is in-game, planned, or conjectural.
- Import bug: supply a **redacted/minimal** sample JSON only; never upload your pledge IDs, purchase prices, emails, or full personal hangar exports to public issues.
- Recommendation: explain why the finding applies to fleets generally, not just one person's collection.

## Run locally

Use Python 3.10+ (standard library only): `python scripts/build.py`. Open generated `index.html` in a browser. Run `python -m unittest discover -s tests -v` before submitting a PR.

Primary classifications and crew tiers are planning heuristics. Avoid presenting them as official CIG specifications. No new external analytics or tracking scripts should be added.

Use pull requests rather than pushing to the protected `main` branch if the maintainer enables branch protection. Maintainers have final review authority.
