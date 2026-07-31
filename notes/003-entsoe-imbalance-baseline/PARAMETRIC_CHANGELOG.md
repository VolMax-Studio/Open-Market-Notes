# Open Market Note #003 — Parametric Changelog

*(Governance Note: All entries marked `Pending Ratification (Pre-Merge)` transition to `Ratified` upon PR merge to `main`).*

---

## Entry #001: Pre-Registration Parameter Transition & Code Alignment (2026-07-31)

- **Scope:** Note #003 ENTSO-E Imbalance Baseline (`PARAMS.md`)
- **Audit Findings:**
  1. **Parameter Lineage:** Draft commit `99f87bb` (24 July 2026 22:19Z) proposed v3.0.0 rules featuring heuristic gap-bridging.
  2. **Transition to Strict Contiguous Rule:** On 27 July 2026 (commit `a2c0b3a`), `PARAMS.md` was updated to v3.1.0, replacing heuristic gap-bridging with Strict Contiguous Block Evaluation. Commit `a2c0b3a` served as the effective pre-execution parameter freeze (`params_commit_hash`) and simultaneously introduced the initial output dataset (`b1c71337...`).
  3. **Zero Output Under v3.0.0:** Git history inspection confirms zero output files (`.json`) were ever produced under the draft v3.0.0 bridging rule. The rule was revised prior to executing any calculation.
- **Rule of Precedence:** *No output was ever produced under the draft v3.0.0 bridging rule; the rule was revised before any result existed. The published Zenodo package is internally consistent (`PARAMS.md` v3.1.0 matches executed `run_imbalance_analysis.py` logic).*
- **Status:** Pending Ratification (Pre-Merge)
