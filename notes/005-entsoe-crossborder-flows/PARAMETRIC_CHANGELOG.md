# Open Market Note #005 — Parametric Changelog

*(Governance Note: All entries marked `Pending Ratification (Pre-Merge)` transition to `Ratified` upon PR merge to `main`).*

---

## Entry #001: Post-Execution Parameter Clarification & Registry Commit Alignment (2026-07-31)

- **Scope:** Note #005 ENTSO-E Cross-Border Flows (`PARAMS.md`, `notes_registry.json`)
- **Audit Findings:**
  1. **Parameter Lineage:** Pre-execution freeze commit was `afddbe9` (28 July 2026 22:59Z). Analysis execution commit producing output `60314bd2...` was `ce042d1` (28 July 2026 23:15Z).
  2. **Post-Execution Edit:** `PARAMS.md` in the published Zenodo package matches commit `afe7120` (29 July 2026 23:08Z), updated post-execution.
  3. **Registry Hash Discrepancy:** `notes_registry.json` records `params_commit_hash: afddbe9` (pre-execution freeze), whereas the published Zenodo v1.0.0 package contains `PARAMS.md` matching commit `afe7120`.
- **Rule of Precedence:** *The published Zenodo package is authoritative (`PARAMS.md` matches commit `afe7120`).*
- **Status:** Ratified (Merged to main)

---

## Entry #002: Typographical Artifact Retention in Frozen PARAMS.md (2026-08-06)

- **Scope:** Note #005 ENTSO-E Cross-Border Flows (`PARAMS.md`)
- **Governance Finding:** Typographical artifact ('u' for 'in') in the Known Empirical Limitations block of Section 1 of the frozen `PARAMS.md`; not corrected, as the document is byte-frozen against the published Zenodo record (`6bdbb82853e9e5c3e29539f560ce22b40aefbcbaf26483727c5c4ad6a9222387`).
- **Status:** Pending Ratification (Pre-Merge)

---

## Entry #003: Licensing Attribution Errata & Published Document Freeze Preservation (2026-08-28)

- **Scope:** Note #005 ENTSO-E Cross-Border Flows (`PARAMS.md`, `PARAMETRIC_CHANGELOG.md`, `download_all_corridors.py`, `download_crossborder_data.py`)
- **Errata Findings:**
  1. **Physical Flow Attribution:** The frozen `PARAMS.md` and Zenodo v1.0.0 metadata cite `Item #27` (which legally applies to Imbalance prices under Article 17.1.g/17.2.f). The authoritative legal category in the pinned ENTSO-E Open Data List (`L-08`) is **`Item #18: Physical flows (Relevant Article of Transparency Regulation: 12.1.g)`**, authorised for free reuse and redistribution under **`Article 2.5 of the ENTSO-E Terms of Use (L-04)`** (CC BY 4.0).
  2. **Regulatory Citation Sanitation:** Article `12.1.d` does not exist in the pinned `L-08` List of Data available for reuse and is removed from all future references. `Item #28` covers Total imbalance volumes (Article 17.1.h / 17.2.g).
  3. **Byte-Frozen Integrity Rule:** In accordance with L3 governance rules, `notes/005-entsoe-crossborder-flows/PARAMS.md` remains strictly byte-frozen matching Zenodo v1.0.0 SHA-256 (`6bdbb82853e9e5c3e29539f560ce22b40aefbcbaf26483727c5c4ad6a9222387`). No retroactive in-place mutation of the published artifact is performed; this Errata entry serves as the authoritative audit discrepancy record.
  4. **Generator Sanitization:** Active executable generators (`download_all_corridors.py` and `download_crossborder_data.py`) are sanitized to output the corrected `Item #18 (12.1.g)` metadata on all future pipeline executions.
- **Status:** Pending Ratification (Pre-Merge)
