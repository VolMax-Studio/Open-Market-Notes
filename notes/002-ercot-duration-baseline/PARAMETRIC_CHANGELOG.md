# Open Market Note #002 — Parametric Changelog

*(Governance Note: All entries marked `Pending Ratification (Pre-Merge)` transition to `Ratified` upon PR merge to `main`).*

---

## Entry #001: Pre-Registration Parameter Clarification & Code Alignment (2026-07-30)

- **Scope:** Note #002 ERCOT Duration Baseline
- **Audit Findings:**
  1. **Separation Rule (Metric 1):** `PARAMS.md` states: *"Events separated by <30 minutes (less than 2 intervals of 15 minutes)... are counted as separate events."* The frozen text is under-specified (defining behavior for gaps under 30 minutes while remaining silent on longer breaks). The executed code (`reproduce.py`) evaluates continuous sequences of $\ge \$100/\text{MWh}$ or $\ge \$250/\text{MWh}$ intervals and splits on any single interval below threshold without gap-bridging.
- **Rule of Precedence:** *Where the frozen text and the executed code differ, the executed code governs the published numbers; the frozen text governs what was pre-registered.*
- **Status:** Ratified (Merged to main)

---

## Entry #002: Reclassification of $25/MWh Cheap Charging Threshold Citation (2026-07-31)

- **Scope:** Note #002 ERCOT Duration Baseline (`PARAMS.md`)
- **Audit Findings:**
  1. **Citation Correction:** In pre-execution commit `7cf9c03`, Section 3 attributed the $25/\text{MWh}$ cheap charging threshold to *"ERCOT Nodal Protocols Section 4.4.11 System-Wide Offer Caps"*. Section 4.4.11 governs high offer cap ceilings (~$5,000/\text{MWh}$), not low-cost charging thresholds.
  2. **Reclassification:** In commit `a55af42` (Zenodo package release), the erroneous protocol citation was removed and the $25/\text{MWh}$ threshold was reclassified as an internal VolMax operational benchmark selected to capture low-cost wind and solar charging opportunities in West Hub (HB_WEST).
- **Rule of Precedence:** *The $25/\text{MWh}$ threshold operates as an internal VolMax operational benchmark without external protocol statutory citation.*
- **Status:** Ratified (Merged to main)
