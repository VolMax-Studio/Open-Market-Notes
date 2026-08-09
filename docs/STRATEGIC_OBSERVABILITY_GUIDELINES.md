# Strategic Observability Guidelines & Methodological Principles

> **Document Status:** RATIFIED STRATEGIC GUIDELINE
> **Author:** VolMax Studio Lab / Nestorov, Ivan
> **Target Scope:** All VolMax Observatory Instruments ($M_1$, $C$, $S_1$), Open Market Notes (#001–#010+), and External Strategic Communications.

---

## 1. Executive Summary & Foundational Shift

The VolMax Observatory does not build commercial algorithms, price forecasts, or trading signals. 

**The Observatory defines and measures a new physical observable in energy economics: *Extreme-State Occupancy*.**

---

## 2. Core Methodological Principles

### Principle A: The Denominator & The Value of Silence
- Industry participants focus almost exclusively on price spikes (numerators). Virtually no market provider publishes or tracks the prevalence of quiet, baseline periods.
- **Rule:** Every series published by the Observatory MUST track and report unskipped calendar windows, including quiet months (`NULL` classifications).
- **Rationale:** The classification label `REGIONAL` derives its scientific contrast and diagnostic value solely because `NULL` (quiet) months are measured and published with equal rigor.

### Principle B: Baseline Climate Binding ($B$)
- **Empirical Discovery:** July 2026 evaluates as `ISOLATED` under a 6-month baseline ($B=6\text{M}$), but as `REGIONAL` under a 12-month baseline ($B=12\text{M}$).
- **Rule:** A classification label MUST NEVER be stated in isolation. The baseline horizon $B$ is an integral component of the physical claim.
- **Syntax standard:** Always state `REGIONAL (B=12M)` or `ISOLATED (B=6M)`, treating $B$ as a mandatory binding parameter rather than a footnote.

### Principle C: Extreme-State Occupancy vs. Nominal Price Level
- Cross-zonal analysis does NOT compare nominal EUR/MWh price levels across different countries (e.g. Serbia vs France).
- **Definition:** The instrument measures how long each market spent occupied in **its own local tail regime** ($R_z = P_{90}$).
- **Application:** This measures true multi-zonal simultaneity and tests whether portfolio geographical diversification actually mitigates extreme-state risks for multi-asset operators (e.g., BESS operators).

### Principle D: The Epistemic Power of "I Don't Know" (`INDETERMINATE` / `NOT_EVALUATED`)
- Commercial index providers force numerical outputs even when data is incomplete or ambiguous.
- **Principle:** In physical measurement, the capacity to output `INDETERMINATE` or `NOT_EVALUATED` when exposure bounds cross decision thresholds or completeness floors fail is a hallmark of scientific maturity and un-falsifiable integrity.

---

## 3. Communication Doctrine: Framing the Instrument

When presenting VolMax Observatory work to external energy market stakeholders:

| ❌ DO NOT SAY (Internal Mechanics) | ✅ SAY INSTEAD (Physical Observable) |
|---|---|
| *"We developed $M_1$, $C$, $S_1$, Exposure_lower, $q_{\text{ref}}$, and $\delta t$ algorithms..."* | *"There is a fundamental dimension the energy market does not measure today: **how often a system was actually occupied in its own scarcity regime, using a local reference and explicit uncertainty bounds**. We built a physical instrument to measure that observable."* |
| *"Our algorithm classifies July 2026 as Regional."* | *"Under a 12-month reference climate, 5 of 6 Central-European imbalance markets were simultaneously occupied in their top-10% extreme price regimes during July 2026 (`REGIONAL, B=12M`)."* |

---

## 4. Product Progression Doctrine

1. **Phase 1 (Achieved):** Proving instrument rigor, determinism, and logical consistency.
2. **Phase 2 (Current Focus):** Demonstrating empirical contrast across historical calendar windows and establishing stable, reproducible market observables (e.g. $B=12\text{M}$ vs $B=6\text{M}$ baseline climate sensitivity).
3. **Phase 3 (Future):** Publishing continuous, unskipped series with documented denominators to create institutional market intelligence.

*VolMax Studio Lab · Strategic Guidelines*
