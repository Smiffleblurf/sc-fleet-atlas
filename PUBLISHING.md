# Launch checklist

- [ ] Create a **public** repository with an original, neutral name (e.g., `fleet-atlas`; no official CIG brand or in-game manufacturer in repository URL).
- [ ] Upload the complete contents of this ZIP, not the ZIP itself; keep `index.html` at repository root.
- [ ] Confirm your own `shiplist.json` and any personal fleet screenshots are **not** in the public repository.
- [ ] **Settings → Pages → Source: Deploy from a branch → main → /(root)** for the current setup, OR choose GitHub Actions if the `.github/workflows/pages.yml` workflow has been uploaded and you want auto-builds from curated catalog changes.
- [ ] Confirm the page loads, begins with zero fleet entries, and shows the required unofficial fan-site notice prominently.
- [ ] Confirm **Show ships not in my fleet** starts checked; unowned names are greyed out; importing your local JSON updates only owned ships.
- [ ] Click **Check ship updates** and inspect whether the label says Star Citizen Wiki API, secondary community snapshot, or offline cache; if live checks are blocked, the built-in reference should remain functional.
- [ ] Import a local JSON and verify the fleet matrix, gaps, and exports; make sure changes stay in the browser.
- [ ] Invite trusted contributors and enable pull-request reviews / branch protections if desired.
- [ ] Periodically check the official CIG fan-site policy and linked data sources.

**If the GitHub connector shows no accessible repositories**, install/configure the GitHub app on the destination repository. Repository creation and enabling Pages require account-side action when not exposed through the connection.