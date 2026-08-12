# Pre-Registered Probe Specification — entsoe-eclipse-exp-20260812

> **Document Status:** Draft — SPREMNO ZA GEJT (Pre-Registration Proposal)
> **Instance Identifier:** `entsoe-eclipse-exp-20260812`
> **Version:** v1.0.0
> **Author:** Nestorov, Ivan / VolMax Studio Lab / ORCID 0009-0006-7940-9539
> **Selection Mode:** `exploratory`
> **Measurement Standard:** M₁ (`M1_SCARCITY_PERSISTENCE.md` v0.7.4)
> **Classifier Standard:** C (`C_CLASSIFIER_SCARCITY_PERSISTENCE.md` v1.4.1)
> **Isolation Protocol:** `INSTANCE_ISOLATION_PROTOCOL.md` (v0.1.0)

---

## 1. Scope & Objective

This pre-registered exploratory probe measures whether the Total Solar Eclipse of **August 12, 2026** induced extreme imbalance scarcity persistence ($M_1 \ge 20.0\%$, corresponding to $\ge 2$ out of 10 15-minute MTUs) across Western European bidding zones (`ES`, `PT`, `FR`, `DE_LU`, `NL`) relative to:
1. Market-local 12-month fixed baseline reference thresholds ($B = 12\text{M}$: August 1, 2025 to July 31, 2026).
2. The 7-day diurnal baseline control window (17:00 to 19:30 UTC, August 5–11, 2026).

---

## 2. Event Window & Resolution Alignment

- **Event Window ($W_{\text{event}}$):** `2026-08-12T17:00:00Z` to `2026-08-12T19:30:00Z` (150 minutes).
  - Filtering uses half-open interval slicing `[17:00:00Z, 19:30:00Z)` on UTC timestamp index.
  - Timestamp convention: `PROVISIONAL_INTERVAL_START_UTC` (Pending L0 source session check).
  - Nominal MTU Count: Exactly 10 intervals of 15-min resolution per zone.
- **Diurnal Control Window ($W_{\text{control}}$):** 17:00:00Z to 19:30:00Z for the preceding 7 days (`2026-08-05` through `2026-08-11`). Note that control days include weekend days (`2026-08-08` Saturday and `2026-08-09` Sunday), capturing natural weekly diurnal profiles.
- **Solar Sunset Context (Spain `ES`):** In mid-August in Madrid/Spain, sunset occurs at ~21:00 CEST (~19:00 UTC). Solar generation naturally approaches zero during the final 30 minutes of the event window. This diurnal sunset effect is captured symmetrically by the 7-day control window baseline.
- **V-Component Blindspot Disclosure:** The 12-month all-hours $P_{90}$ reference $R_z$ measures overall annual scarcity and does not isolate evening net-load peak variance from solar eclipse variance. The 7-day diurnal control delta is mandatory to absorb evening peak artifacts.

---

## 3. P10 Exposure Disclosures & Comparability Discipline

1. **Primary Empirical Metric ($M_1$ v0.7.4):** Imbalance Settlement Price persistence during the event window (**17:00 to 19:30 UTC**). Imbalance telemetry has NOT been fetched or viewed prior to specification ratification.
2. **Secondary Disclosed Exposure (Day-Ahead Prices):** Day-Ahead clearing price premiums are acknowledged to have been traded prior to specification freeze. Per P10 Principle 2, DA data is degraded to **secondary descriptive evidence** and cannot serve as the primary metric.
3. **Comparability Discipline Disclosure:** Target zones differ in settlement mechanics (e.g. single-pricing in DE_LU/NL vs dual/single pricing rules in ES/FR). Imbalance persistence values are measured against zone-local 12-month fixed P90 baselines ($R_z$), which natively absorb zone-specific pricing structures, but cross-zone persistence values reflect distinct market settlement designs.

---

## 4. Pre-Registered Per-Zone & Global Verdict Rules

### 5-State Global Verdict Enum
The global probe verdict is chosen from a strict 5-state enum:
1. **`ELEVATED_BY_EVENT`**: At least one comparison zone returns `ELEVATED_BY_EVENT`.
2. **`INDETERMINATE`**: Zero zones are `ELEVATED_BY_EVENT`, and at least one zone returns `INDETERMINATE`.
3. **`INCOMPLETE`**: Zero zones are `ELEVATED_BY_EVENT`, zero zones are `INDETERMINATE`, and at least one zone returns `INCOMPLETE`.
4. **`DATA_PENDING`**: Zero zones are `ELEVATED_BY_EVENT`, `INDETERMINATE`, or `INCOMPLETE`, and at least one target zone has un-fetched telemetry (`DATA_PENDING`). An un-fetched zone can NEVER yield global `NULL`.
5. **`NULL`**: All target zones evaluated cleanly with completeness $\ge 80.0\%$ and zero target zones returned `ELEVATED_BY_EVENT`.

### Per-Zone Elevation Rule
A bidding zone $z$ is classified as **`ELEVATED_BY_EVENT`** if and only if:
$$\text{Event Status}_z == \mathtt{ELEVATED} \quad \text{AND} \quad N_{\text{control\_crossings}, z} \le 2 \quad \text{AND} \quad N_{\text{incomplete\_control\_days}, z} < 2$$
where each control day is evaluated under symmetric M1 v0.7.4 exposure bounds. A control day counts as a crossing if its status is `ELEVATED` or `INDETERMINATE` (conservative inclusion against false elevation claims). If $N_{\text{incomplete\_control\_days}, z} \ge 2$, zone $z$ status is `INCOMPLETE`.

### Unconditional Disclosure Commitment
Even if all zones return `NOT_ELEVATED`, `INDETERMINATE`, `INCOMPLETE`, `DATA_PENDING`, or `NULL`, the final result will be published without modification or cherry-picking.

*VolMax Studio Lab · Pre-Registered Exploratory Probe*
