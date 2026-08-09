# M₁ — Scarcity Persistence Scalar

> **Document Status:** Draft — SPREMNO ZA GEJT (not frozen, not ratified)
> **Version:** v0.6.0 · supersedes v0.5.0, v0.4.0, v0.3.0, v0.2.0 (complete history preserved — see §9)
> **Author:** Nestorov, Ivan / VolMax Studio Lab / ORCID 0009-0006-7940-9539
> **Role:** Measurement Domain Specification **M₁** for event class *scarcity persistence*, under
> `INSTRUMENT_SPEC — Measurement Domain and Visibility Boundaries` (v0.3.0).

---

## 1. Event Class & Scalar Definition

**Event Class:** *Scarcity Persistence* (persistent elevated imbalance settlement price).

**Scalar Definition:** $M_1(m, W)$ is defined as the time-weighted proportion of admitted time in window $W$ during which the market imbalance shortage price $P_m(t)$ equals or exceeds the market-local reference level $R(m)$:

$$M_1(m, W) = \frac{\int_{t \in W_{\text{admitted}}} \mathbb{I}\left(P_m(t) \ge R(m)\right) \, dt}{\int_{t \in W_{\text{admitted}}} 1 \, dt}$$

Where:
- $m \in \mathcal{M}$ is a specific bidding zone / market jurisdiction.
- $W$ is a bounded observation window (e.g. one calendar month).
- $W_{\text{admitted}} \subseteq W$ is the subset of window $W$ satisfying telemetry completeness floors (§4).
- $R(m)$ is the local reference level derived from an uncontaminated baseline window $B(m)$.

---

## 2. Reference Level Derivation & Constraints

### 2.1 Disjointness Constraint:
The baseline window $B(m)$ and observation window $W$ **must be strictly disjoint**:

$$B(m) \cap W = \emptyset$$

No timestamp from window $W$ may be included in the calculation of $R(m)$.

### 2.2 Audit Contamination Clause:
If post-observation inspection reveals that $B(m) \cap W \neq \emptyset$, the computed scalar $M_1(m, W)$ is **void by construction**. It cannot be remediated by in-place adjustments; $R(m)$ must be recomputed over a strictly disjoint window $B^\prime(m)$.

### 2.3 Derivation Rule:
For a chosen reference quantile $q \in (0, 1)$ frozen in `PARAMS.md`, $R(m)$ is computed as the $q$-th percentile of $P_m(t)$ over baseline window $B(m)$:

$$R(m) = \text{Quantile}\left(\{P_m(t) \mid t \in B(m)\}, q\right)$$

The estimator method for percentiles is linear interpolation (`method='linear'`) over UTC-sorted timestamps.

### 2.4 Baseline Property Rule:
$R(m)$ is a structural property derived over baseline window $B(m)$ using quantile $q$ frozen in `PARAMS.md`, **not a property of the observation run**. Once calculated and frozen in `PARAMS.md`, $R(m)$ remains fixed for all evaluations against window $W$.

### 2.5 Stability Property Rule:
This specification imposes no guarantee that $R(m)$ is statistically stable across choice of baseline window $B(m)$ or quantile $q$. Stability is a property of the parameter set frozen in `PARAMS.md`, not of the measurement definition. The sensitivity of $R(m)$ to parameter choice must be evaluated and recorded prior to pre-registration freeze.

---

## 3. Single Scalar Dimension Constraint

$M_1(m, W)$ emits **exactly one dimensionless scalar in $[0, 1]$**. 
- Absolute duration of scarcity episodes (e.g. total minutes) is a descriptive companion statistic outside $M_1$.
- Ratio calculations based purely on interval counts are **non-conforming**, even when all intervals happen to have equal nominal duration. Ratios must be computed as explicit time-weighted duration ratios in seconds.

---

## 4. Telemetry Admissibility & Completeness Floor

1. **Completeness Floor:** $M_1(m, W)$ is valid if and only if admitted time covers at least the frozen completeness floor threshold $\text{Floor}_{\text{completeness}}$ (defined in `PARAMS.md`) and no contiguous gap exceeds $\Delta t_{\text{max}}$:
   $$\text{Completeness}(m, W) = \frac{N_{\text{admitted}}}{N_{\text{nominal}}} \ge \text{Floor}_{\text{completeness}}, \quad \max(\Delta t_i) \le \Delta t_{\text{max}}$$
   If telemetry violates either condition, evaluation aborts immediately (`MANDATE 8 ABORT`).
2. **Missing Telemetry Rule:** For admissible datasets, unobserved, missing, or NaN telemetry intervals are excluded from both numerator and denominator by evaluating time-weighted ratios strictly over admitted timestamps. No synthetic gap-filling or zero-imputation is permitted.

---

## 5. Algorithmic Pre-Conditions & Boundary Interval Rule

1. **UTC Sorting Pre-Condition:** Datasets must be sorted ascending by UTC timestamp (`df.sort_index()`) before any slicing, interval difference calculation, or quantile operation.
2. **Boundary Interval Rule:** For the first (boundary) interval $i=0$ of an admitted observation window $W$, if no preceding timestamp $i=-1$ exists in dataset, its duration $\Delta t_0$ is set equal to the median duration of all subsequent admitted intervals in $W$:
   $$\Delta t_0 = \text{Median}\left(\{\Delta t_i \mid i \ge 1\}\right)$$

---

## 6. Determinism Constraints & Execution Specifications

To guarantee bit-identical reproducibility across independent execution environments, $M_1$ mandates the following deterministic execution rules:

| Aspect | Deterministic Requirement | Failure Action |
|---|---|---|
| **Timestamp Indexing** | Convert to UTC-aware DatetimeIndex and sort ascending strictly before slicing. | ABORT if unparseable or unsorted. |
| **Duplicate Timestamps** | Datasets containing duplicate timestamps within $B(m)$ or $W$ are non-conforming. | ABORT immediately. |
| **NaN / Null Handling** | Filter NaN values from both value series and timestamp delta series prior to summation. | ABORT if unhandled NaN enters calculation. |
| **Inclusive Threshold** | Evaluation uses inclusive inequality: $\mathbb{I}(P_m(t) \ge R(m))$. | Reject exclusive threshold $>$. |
| **Floating Point Precision** | Quantile computation uses IEEE 754 double-precision float (64-bit). | Non-conforming if 32-bit float used. |
| **Rounding Rule** | Intermediate scalars are stored at full 64-bit precision; published values round to 4 decimals (`round(val, 4)`). | Do not round intermediate products. |

---

## 7. Parameters Frozen in `PARAMS.md`

The definition of $M_1$ is parameter-free. All specific numeric parameters and series bindings are frozen in `PARAMS.md` prior to execution:

- Reference Quantile $q \in (0, 1)$
- Reference Baseline Window $B(m)$ (start UTC, end UTC)
- Completeness Floor $\text{Floor}_{\text{completeness}} \in (0, 1]$
- Maximum Allowed Telemetry Gap $\Delta t_{\text{max}}$
- Designated Series Bindings per Market $m \in \mathcal{M}$ (`series_bindings`)

---

## 8. What $M_1$ Is Not

1. **$M_1$ is NOT a financial profitability index:** It measures time exposure to elevated price regimes, not revenue, battery dispatch efficiency, or arbitrage spread.
2. **$M_1$ is NOT a market ranking tool:** $M_1$ values across different jurisdictions compare local exposure to local expectations, not absolute price levels across borders.
3. **$M_1$ is NOT a predictive signal:** $M_1$ is an ex-post empirical measurement over a closed window $W$.

---

## 9. Amendment Record

**v0.6.0.** Fixed §2.4 phrasing regarding $R(m)$ derivation from $q$, clarified §4.2 missing telemetry exclusion for admissible datasets, and restored full historical amendment records.

**v0.5.0.** Restored original §2.5 wording regarding stability as a property of the parameter set, removing the unratified 12M mandate to maintain consistency with published 11M baselines. Updated §6 rounding rule to explicit 4 decimals.

**v0.4.0.** Restored all sections omitted in v0.3.0: §2.2 Audit Contamination Clause, §2.4 Baseline Property Rule, §6 Determinism Constraints table, §7 Parameters Frozen in `PARAMS.md`, §8 "What $M_1$ Is Not". Replaced hardcoded numbers with abstract parameter symbols.

**v0.3.0.** Added UTC sorting pre-condition and boundary interval duration rule ($\Delta t_0 = \text{Median}(\Delta t_{i \ge 1})$).

**v0.2.0.** Renamed document to `M1_SCARCITY_PERSISTENCE.md`. Updated references to `INSTRUMENT_SPEC.md` v0.3.0. Added Telemetry Admissibility & Completeness Floor.

*VolMax Studio Lab · P10 Verification Protocol*
