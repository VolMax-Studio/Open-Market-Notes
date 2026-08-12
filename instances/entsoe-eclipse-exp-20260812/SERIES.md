# Pre-Registered Probe Specification — entsoe-eclipse-exp-20260812

> **Document Status:** RATIFIED & PRE-REGISTERED
> **Instance Identifier:** `entsoe-eclipse-exp-20260812`
> **Version:** v1.0.0
> **Author:** Nestorov, Ivan / VolMax Studio Lab / ORCID 0009-0006-7940-9539
> **Selection Mode:** `exploratory`
> **Measurement Standard:** M₁ (`M1_SCARCITY_PERSISTENCE.md` v0.7.3)
> **Classifier Standard:** C (`C_CLASSIFIER_SCARCITY_PERSISTENCE.md` v1.4.1)
> **Isolation Protocol:** `INSTANCE_ISOLATION_PROTOCOL.md` (v0.1.0)

---

## 1. Scope & Objective

This pre-registered exploratory probe measures whether the Total Solar Eclipse of **August 12, 2026** induced extreme imbalance scarcity elevation ($M_1 \ge 15.0\%$) across Western European bidding zones (`ES`, `PT`, `FR`, `DE_LU`, `NL`) relative to market-local 12-month rolling references ($B = 12\text{M}$: August 1, 2025 to July 31, 2026).

---

## 2. P10 Exposure Disclosures & Metric Separation

1. **Primary Empirical Metric ($M_1$):** Imbalance Settlement Price persistence during the event window (**17:15 to 19:30 UTC**). Imbalance telemetry has NOT been fetched or viewed prior to this specification freeze.
2. **Secondary Disclosed Exposure (Day-Ahead Prices):** Day-Ahead clearing price premiums are acknowledged to have been traded prior to specification freeze. Per P10 Principle 2, DA data is degraded to **secondary descriptive evidence** and cannot serve as the primary metric.

---

## 3. Pre-Registered Falsification Criteria

> **Falsification Clause:** The hypothesis that the solar eclipse caused extreme scarcity elevation is **FALSE** if:
> 1. No target zone (`ES`, `PT`, `FR`, `DE_LU`, `NL`) crosses $S_{\text{thresh}} = 15.0\%$ during the 135-minute event window (`17:15–19:30 UTC`), **OR**
> 2. The zone crossed $S_{\text{thresh}} \ge 15.0\%$ in $\ge 4$ of the 7 pre-registered control days (`2026-08-05` to `2026-08-11`).

### Unconditional Disclosure Commitment
Even if all zones return `NOT_ELEVATED` ($M_1 < 15.0\%$), the **`NULL` result will be published without modification or cherry-picking**.

*VolMax Studio Lab · Pre-Registered Exploratory Probe*
