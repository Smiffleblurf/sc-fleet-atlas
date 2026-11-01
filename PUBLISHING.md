# Launch checklist

- [ ] Create a **public** repository with an original, neutral name (e.g., `fleet-atlas`; no official CIG brand or in-game manufacturer in repository URL).
- [ ] Upload the complete contents of this ZIP, not the ZIP itself; keep `index.html` at repository root.
- [ ] Confirm your own `shiplist.json` and any personal fleet screenshots are **not** in the public repository.
- [ ] **Settings → Pages → Source: GitHub Actions**. Workflow `.github/workflows/pages.yml` builds and deploys.
- [ ] Confirm the page loads, begins with zero fleet entries, and shows the required unofficial fan-site notice prominently.
- [ ] Import a local JSON and verify the fleet matrix, gaps, and exports; make sure changes stay in the browser.
- [ ] Invite trusted contributors and enable pull-request reviews / branch protections if desired.
- [ ] Periodically check the official CIG fan-site policy and linked data sources.

**If the GitHub connector shows no accessible repositories**, install/configure the GitHub app on the destination repository. Repository creation and enabling Pages require account-side action when not exposed through the connection.
