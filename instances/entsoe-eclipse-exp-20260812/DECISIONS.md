# DECISIONS — Instance entsoe-eclipse-exp-20260812 Append-Only Decision Log

> **Instance ID:** `entsoe-eclipse-exp-20260812`
> **Selection Mode:** `exploratory`
> **Governance Protocol:** Instance Isolation Protocol (v0.1.0) & P10 Verification Protocol

---

## Decision 001 — Pre-Registration Specification Freeze (2026-08-12)

- **Context:** Western European Total Solar Eclipse on 2026-08-12 (~17:15 to 19:30 UTC).
- **Gate Audit Corrections (Blockers B1–B8 Resolved):**
  1. **Container Isolation:** Exploratory instance (`instances/entsoe-eclipse-exp-20260812/`) chosen to preserve Handover §5 Rule 7 (Note #006 un-instantiated).
  2. **Uncontaminated Metric:** Imbalance settlement prices chosen as primary signal ($M_1$ v0.7.4). Day-Ahead clearing price premiums flagged as pre-exposed (secondary descriptive evidence only).
  3. **UTC Window Alignment:** Adjusted to **17:00 to 19:30 UTC** (150 minutes = 10 MTU intervals of 15-min resolution) to align cleanly on 15-min and 30-min MTU boundaries across all target zones (`ES`, `PT`, `FR`, `DE_LU`, `NL`).
  4. **Discrete Threshold Definition:** For 10 intervals of 15-min MTU, $S_{\text{thresh}} = 20.0\%$ (exactly $\ge 2$ out of 10 intervals above baseline $R_z$).
  5. **Diurnal Control & Net Metric:** Primary event elevation is evaluated against both $R_z$ ($B=12\text{M}$ rolling $P_{90}$) and the 7-day control window baseline ($17:00\text{--}19:30 \text{ UTC}$, August 5–11, 2026).
  6. **Per-Zone Falsification Rule:** A zone $z$ is classified as `ELEVATED_BY_EVENT` iff $M_{1, z}(\text{event}) \ge 20.0\%$ AND $N_{\text{control\_crossings}, z} \le 2$ out of 7 control days.
  7. **Publication Guarantee:** `NULL` verdicts (zero zones elevated by event) will be published unconditionally.
  8. **Document Status:** Set strictly to `Draft — SPREMNO ZA GEJT`.

*VolMax Studio Lab · Append-Only Decision Record*
