# Open Market Note #005 — Parametric Changelog

*(Governance Note: All entries marked `Ratified (Merged to main)` transition to `Ratified` upon PR merge to `main`).*

---

## Entry #001: Post-Execution Parameter Clarification & Registry Commit Alignment (2026-07-31)

- **Scope:** Note #005 ENTSO-E Cross-Border Flows (`PARAMS.md`, `notes_registry.json`)
- **Audit Findings:**
  1. **Parameter Lineage:** Pre-execution freeze commit was `afddbe9` (28 July 2026 22:59Z). Analysis execution commit producing output `60314bd2...` was `ce042d1` (28 July 2026 23:15Z).
  2. **Post-Execution Edit:** `PARAMS.md` in the published Zenodo package matches commit `afe7120` (29 July 2026 23:08Z), updated post-execution.
  3. **Registry Hash Discrepancy:** `notes_registry.json` records `params_commit_hash: afddbe9` (pre-execution freeze), whereas the published Zenodo v1.0.0 package contains `PARAMS.md` matching commit `afe7120`.
- **Rule of Precedence:** *The published Zenodo package is authoritative (`PARAMS.md` matches commit `afe7120`).*
- **Status:** Ratified (Merged to main)
