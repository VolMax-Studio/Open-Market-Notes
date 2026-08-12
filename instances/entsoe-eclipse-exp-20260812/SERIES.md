# Pre-Registered Probe Specification — entsoe-eclipse-exp-20260812

> **Document Status:** Draft — SPREMNO ZA GEJT (Pre-Registration Proposal)
> **Instance Identifier:** `entsoe-eclipse-exp-20260812`
> **Version:** v1.0.0
> **Author:** VolMax Studio Lab / ORCID 0009-0006-7940-9539
> **Selection Mode:** `exploratory`
> **Measurement Standard:** M₁ (`M1_SCARCITY_PERSISTENCE.md` v0.7.4)
> **Classifier Standard:** C (`C_CLASSIFIER_SCARCITY_PERSISTENCE.md` v1.4.1)
> **Isolation Protocol:** `INSTANCE_ISOLATION_PROTOCOL.md` (v0.1.0)

---

## 1. Scope & Objective

This pre-registered exploratory probe measures whether the Total Solar Eclipse of **August 12, 2026** induced extreme imbalance scarcity persistence ($M_1 \ge 20.0\%$, corresponding to $\ge 2$ out of 10 15-minute MTUs) across Western European bidding zones (`ES`, `PT`, `FR`, `DE_LU`, `NL`) relative to:
1. Market-local 12-month rolling $P_{90}$ reference thresholds ($B = 12\text{M}$: August 1, 2025 to July 31, 2026).
2. The 7-day diurnal baseline control window (17:00 to 19:30 UTC, August 5–11, 2026).

---

## 2. Event Window & Resolution Alignment

- **Event Window ($W_{\text{event}}$):** `2026-08-12T17:00:00Z` to `2026-08-12T19:30:00Z` (150 minutes).
  - Aligns cleanly on 15-minute and 30-minute MTU boundaries across all target zones.
  - Nominal MTU Count: 10 intervals of 15-min resolution (or 5 intervals of 30-min resolution for 30-min markets).
- **Diurnal Control Window ($W_{\text{control}}$):** 17:00:00Z to 19:30:00Z for the preceding 7 days (`2026-08-05` through `2026-08-11`).
- **Solar Sunset Context (Spain `ES`):** In mid-August in Madrid/Spain, sunset occurs at ~21:00 CEST (~19:00 UTC). Solar generation naturally approaches zero during the final 30 minutes of the event window. This diurnal sunset effect is captured by the 7-day control window baseline.

---

## 3. P10 Exposure Disclosures & Metric Separation

1. **Primary Empirical Metric ($M_1$ v0.7.4):** Imbalance Settlement Price persistence during the event window (**17:00 to 19:30 UTC**). Imbalance telemetry has NOT been fetched or viewed prior to specification ratification.
2. **Secondary Disclosed Exposure (Day-Ahead Prices):** Day-Ahead clearing price premiums are acknowledged to have been traded prior to specification freeze. Per P10 Principle 2, DA data is degraded to **secondary descriptive evidence** and cannot serve as the primary metric.

---

## 4. Pre-Registered Per-Zone Falsification Criteria

> **Per-Zone Elevation Rule:** A bidding zone $z$ is classified as **`ELEVATED_BY_EVENT`** if and only if:
> $$M_{1, z}(W_{\text{event}}) \ge 20.0\% \quad \text{AND} \quad N_{\text{control\_crossings}, z} \le 2 \text{ out of } 7 \text{ control days}$$
>
> **Global Falsification Clause:** The hypothesis that the solar eclipse produced measurable extreme scarcity elevation is **FALSE** if zero target zones (`ES`, `PT`, `FR`, `DE_LU`, `NL`) satisfy `ELEVATED_BY_EVENT`.

### Unconditional Disclosure Commitment
Even if all zones return `NOT_ELEVATED` or `FALSE`, the **`NULL` result will be published without modification or cherry-picking**.

*VolMax Studio Lab · Pre-Registered Exploratory Probe*
