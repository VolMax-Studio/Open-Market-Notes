# M₁ — Scarcity Persistence Scalar

> **Document Status:** RATIFIED — FROZEN for Series Operation
> **Version:** v0.7.3 · supersedes v0.7.2, v0.6.0, v0.5.0, v0.4.0, v0.3.0, v0.2.0 (complete history preserved — see §9)
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
- Ratio calculations based purely on interval counts without explicit duration bindings are **non-conforming**. On fixed-resolution markets where interval duration $\Delta t$ is a parameter frozen in `PARAMS.md`, time-weighted duration ratios simplify to $(K \cdot \Delta t) / (N \cdot \Delta t) = K / N$; on mixed-resolution markets, explicit time-weighted duration ratios in seconds are mandatory.

---

## 4. Telemetry Admissibility, Completeness Floor, and Decision Bounds

### 4.1 Quantities

For a market $m$ and window $W$, over the designated series:

- `nominal_seconds` ($N$) — total duration of $W$, from the nominal interval count and interval duration frozen in `PARAMS.md`.
- `admitted_seconds` ($A$) — summed duration of intervals present and non-null.
- `missing_seconds` ($M$) = $N - A$.
- `qualifying_seconds` ($Q$) — summed duration of **admitted** intervals whose value equals or exceeds $R(m)$.

By construction $Q \le A \le N$.

The published scalar is unchanged from earlier versions:

$$M_1(m, W) = \frac{Q}{A} \qquad \text{(fraction of \textbf{observed} time at or above } R)$$

### 4.2 Completeness floor

`A / N` must be at least the frozen completeness floor ($\text{Floor}_{\text{completeness}}$ in `PARAMS.md`). Below the floor the zone yields no value and no bounds, and the window is unevaluated (`NOT_EVALUATED — INCOMPLETE_SET`). The floor is retained as a coarse guard: it caps the width of the decision interval in §4.3 before that interval is computed.

### 4.3 Exposure bounds — a second quantity, on a different denominator

Missing telemetry is never imputed. Its effect on the decision is instead **bounded**, by computing the two extremes of *nominal* exposure that the data permits:

$$\text{Exposure}_{\text{lower}} = \frac{Q}{N} \qquad \text{Exposure}_{\text{upper}} = \frac{Q + M}{N}$$

`Exposure_lower` assumes every missing interval was below $R$. `Exposure_upper` assumes every missing interval was at or above $R$. These are the two extremal nominal exposures consistent with the observed data **and with the instrument's model assumption that each missing interval is treated as either entirely qualifying or entirely non-qualifying.** They are extremes of the model, not a claim that the world admits no other configuration; a partially-qualifying interval lies strictly inside the interval and is therefore covered.

**These are not the extremes of $M_1$.** They are the extremes of the fraction of the *nominal* window at or above $R$. The denominator differs from $M_1$'s deliberately: the question they answer is "what could the whole window have looked like", not "what did the observed part look like". Naming them `M1_min` / `M1_max` would state the opposite and is prohibited.

Interval width is exactly the missing fraction:
$$\text{Exposure}_{\text{upper}} - \text{Exposure}_{\text{lower}} = \frac{M}{N} = 1 - \text{completeness}$$

**Containment (stated as a theorem, since the denominators differ):**

$$\text{Exposure}_{\text{lower}} \le M_1 \le \text{Exposure}_{\text{upper}}$$

*Proof.* Lower: $Q/N \le Q/A$ because $N \ge A$. Upper: $Q/A \le (Q+M)/N \iff QN \le A(Q + N - A) \iff Q(N-A) \le A(N-A) \iff (N-A)(Q-A) \le 0$, which holds because $N-A \ge 0$ and $Q-A \le 0$. ∎

The containment is a consequence of $Q \le A \le N$, not an assumption. It fails if any implementation ever counts a missing interval as qualifying.

### 4.4 Determinacy — and the elevation test

`S_thresh` is frozen in `PARAMS.md` as a multiple of the reference expectation $(1 - q)$. Under this section the elevation test operates on the **exposure bounds**, not on $M_1$:

| Condition | Zone state |
|---|---|
| `Exposure_lower ≥ S_thresh` | **Elevated** — determinate |
| `Exposure_upper < S_thresh` | **Not elevated** — determinate |
| `Exposure_lower < S_thresh ≤ Exposure_upper` | **INDETERMINATE** |

**Determinacy is evaluated before classification. Classification never receives an indeterminate elevation state.** $M_1$ emits one of three states per zone; **C** consumes only the first two and has no rule for the third, because the third never reaches it. This keeps the layer boundary intact: deciding whether a zone *has* an elevation state is a measurement question, and counting elevated zones is a classification question.

**This supersedes `Elevated(m) = 𝟙(M₁ ≥ S_thresh)`.** That earlier test is not merely rescaled here; it is replaced, and `C` §2 is amended in the same version bump so that only one definition of elevation exists across the specifications.

**Direction of the change, stated explicitly.** At 100% completeness the two tests coincide, because then $Q/N = Q/A = M_1$. Below 100% they differ, and the difference is one-sided: since $\text{Exposure}_{\text{lower}} \le M_1$, requiring $\text{Exposure}_{\text{lower}} \ge S_{\text{thresh}}$ is **strictly harder** than requiring $M_1 \ge S_{\text{thresh}}$. A zone can never be called determinately elevated under a weaker condition than before. A zone whose published $M_1$ exceeds $S_{\text{thresh}}$ while $\text{Exposure}_{\text{lower}}$ does not is INDETERMINATE — it is never silently downgraded to not-elevated, because $\text{Exposure}_{\text{upper}} \ge M_1 \ge S_{\text{thresh}}$ forbids that branch.

An INDETERMINATE zone has no elevation state. It is not counted as elevated, not counted as not-elevated, and not imputed in either direction. Its presence makes the comparison set incomplete for that window, and **C** emits no label — the same disposition as a zone that failed the completeness floor, under its own reason code (`INDETERMINATE_SET`).

Every published record carries $M_1$, `Exposure_lower`, `Exposure_upper`, `missing_fraction`, and the determinacy state, per zone. Below 100% completeness, $M_1$ is not quotable without the bounds, because the decision was not made on $M_1$.

### 4.5 Missing telemetry rule

Unobserved, missing, or NaN intervals are excluded from both numerator and denominator of $M_1$. No synthetic gap-filling, forward-fill, or zero-imputation is permitted anywhere. Their effect enters the instrument only through §4.3.

### 4.6 Baseline — uncertainty accepted, not bounded

The completeness floor of §4.2 applies to the baseline window $B(m)$. **The exposure bounds of §4.3 do not, and no equivalent bound is available.** $R$ is a quantile of a distribution rather than a comparison against a threshold, and the missing fraction alone implies nothing about how far the quantile moved: the same 1% of missing baseline time shifts $R$ negligibly if it fell in the body of the distribution and materially if it fell in the tail, and which of those occurred is exactly what is not observed.

Required in every artefact, in these terms:

> **The uncertainty R carries from missing baseline telemetry is accepted, not bounded.**
> The instrument bounds the effect of missing data in W and offers no equivalent guarantee for B. Its guarantees are therefore asymmetric between the two windows.

This is a limitation of the instrument as specified, not a defect of any run, and reducing it is open work. Any future bound on $R$ is a new version of this section, not a clarification of it.

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
- Designated Series Bindings per Market $m \in \mathcal{M}$ (`series_bindings`)

---

## 8. What $M_1$ Is Not

1. **$M_1$ is NOT a financial profitability index:** It measures time exposure to elevated price regimes, not revenue, battery dispatch efficiency, or arbitrage spread.
2. **$M_1$ is NOT a market ranking tool:** $M_1$ values across different jurisdictions compare local exposure to local expectations, not absolute price levels across borders.
3. **$M_1$ is NOT a predictive signal:** $M_1$ is an ex-post empirical measurement over a closed window $W$.

---

## 9. Amendment Record

**v0.7.3.** Added fixed-resolution parameter equivalence clause to §3 clarifying that on fixed-resolution markets where interval duration $\Delta t$ is a parameter frozen in `PARAMS.md`, time-weighted duration ratios simplify to $(K \cdot \Delta t) / (N \cdot \Delta t) = K / N$.

**v0.7.2.** Replaced §4 in full with Exposure Bounds ($\text{Exposure}_{\text{lower}}$, $\text{Exposure}_{\text{upper}}$) and the Determinacy Elevation Test (§4.4). Removed maximum gap rule $\Delta t_{\text{max}}$ for observation window $W$, replacing geometric gap rejection with uncertainty bounding over nominal window $N$. Added theorem proof for $M_1$ containment, §4.6 baseline uncertainty acceptance clause, and Parametric Changelog entry.

**v0.6.0.** Fixed §2.4 phrasing regarding $R(m)$ derivation from $q$, clarified §4.2 missing telemetry exclusion for admissible datasets, and restored full historical amendment records.

**v0.5.0.** Restored original §2.5 wording regarding stability as a property of the parameter set, removing the unratified 12M mandate to maintain consistency with published 11M baselines. Updated §6 rounding rule to explicit 4 decimals.

**v0.4.0.** Restored all sections omitted in v0.3.0: §2.2 Audit Contamination Clause, §2.4 Baseline Property Rule, §6 Determinism Constraints table, §7 Parameters Frozen in `PARAMS.md`, §8 "What $M_1$ Is Not". Replaced hardcoded numbers with abstract parameter symbols.

**v0.3.0.** Added UTC sorting pre-condition and boundary interval duration rule ($\Delta t_0 = \text{Median}(\Delta t_{i \ge 1})$).

**v0.2.0.** Renamed document to `M1_SCARCITY_PERSISTENCE.md`. Updated references to `INSTRUMENT_SPEC.md` v0.3.0. Added Telemetry Admissibility & Completeness Floor.

*VolMax Studio Lab · P10 Verification Protocol*
