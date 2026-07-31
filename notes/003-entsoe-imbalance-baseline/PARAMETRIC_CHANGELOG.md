# Open Market Note #003 — Parametric Changelog

*(Governance Note: All entries marked `Pending Ratification (Pre-Merge)` transition to `Ratified` upon PR merge to `main`).*

---

## Entry #001: Pre-Registration Parameter Transition & Code Alignment (2026-07-31)

- **Scope:** Note #003 ENTSO-E Imbalance Baseline (`PARAMS.md`)
- **Audit Findings:**
  1. **Parameter Lineage:** Pre-registration commit `99f87bb` (24 July 2026 22:19Z) specified v3.0.0 rules featuring heuristic gap-bridging.
  2. **Transition to Strict Contiguous Rule:** On 27 July 2026 (commit `a2c0b3a`), `PARAMS.md` was updated to v3.1.0, replacing heuristic gap-bridging with Strict Contiguous Block Evaluation. Commit `a2c0b3a` simultaneously introduced the published output dataset (`b1c71337...`).
  3. **Pre-Registration Precedence:** The strict-contiguous rule was committed simultaneously with the published output, not in advance of it.
- **Rule of Precedence:** *The published Zenodo package is internally consistent (`PARAMS.md` v3.1.0 matches executed `run_imbalance_analysis.py` logic).*
- **Status:** Pending Ratification (Pre-Merge)
