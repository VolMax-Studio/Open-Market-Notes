# ENTSO-E Scarcity Vintage-Stability Audit — Pre-registration

**Instance:** `entsoe-scarcity-s2`  
**Status:** DRAFT — NOT FROZEN (SPREMNO ZA PRE-EXECUTION GEJT)  
**Deadline:** 2026-09-12  
**Architecture:** Pinned-vintage ENTSO-E Transparency Platform / IEC 62325 raw-document architecture  
**Audit Class:** Internal self-reproduction and vintage-stability audit of published VolMax Open Market Note #003 findings.  
**Claimant:** VolMax Studio  

This instance is a new registered reproduction / vintage-stability audit.  
It is not a repair of `entsoe-scarcity-s1`.  
The team has prior exposure to the published July-2026 scarcity result. Therefore this instance is not outcome-naive and must not be described as first-pass confirmatory discovery.

---

## 1. Claim under test

The audit tests whether the previously published VolMax July-2026 six-zone European scarcity measurement can be reconstructed from a single post-freeze ENTSO-E Transparency Platform acquisition batch while preserving the exact expected MTU population and performing no silent data repair.

The six ENTSO-E zones are:
- NL
- BE
- FR
- DK-1
- DK-2
- AT

Great Britain is excluded from this instance because its evidence source is not the ENTSO-E Transparency Platform.  
The audit therefore does not test the complete earlier GB-versus-Europe narrative.

---

## 2. Primary public source & Request Contract

Source system:
`ENTSO-E Transparency Platform Web API` (`https://web-api.tp.entsoe.eu/api`).

Data class:
`Imbalance prices`.

Regulatory / document identity:
- TR art. 17.1.g / corresponding balancing publication;
- `documentType = A85`;
- realised process: `processType = A16`;
- raw ENTSO-E / IEC 62325 balancing-market documents (`Balancing_MarketDocument` XML).

Target Area EICs (`controlArea_Domain`):
- AT: `10YAT-APG------L`
- BE: `10YBE----------X`
- DK-1: `10YDK-1--------W`
- DK-2: `10YDK-2--------T`
- FR: `10YFR-RTE------C`
- NL: `10YNL----------L`

### Request Plan (Exactly 12 Requests)
The official acquisition executes exactly 12 HTTP GET requests (6 zones $\times$ 2 measurement windows):

Query selector template:
```text
GET https://web-api.tp.entsoe.eu/api
  ?documentType=A85
  &controlArea_Domain=<PINNED_EIC>
  &periodStart=<YYYYMMDDHHMM UTC>
  &periodEnd=<YYYYMMDDHHMM UTC>
  &securityToken=<SECRET — NEVER COMMITTED>
```

For each zone:
1. **Baseline Window (334 calendar days / 32,064 expected MTUs):**
   - `periodStart=202507312200`
   - `periodEnd=202606302200`
2. **Target Window (31 calendar days / 2,976 expected MTUs):**
   - `periodStart=202606302200`
   - `periodEnd=202607312200`

### Boundary & Chunking Invariants
- **Zero Chunking:** No monthly partitioning. No adaptive date sub-window retry.
- **Unsupported Request Rule:** If the baseline 334-day request is rejected because the API imposes a tighter A85 interval limit $\rightarrow$ `HALT: request contract unsupported`. A new preregistration version is required.

No `entsoe-py` dataframe is an evidentiary source.  
The authoritative input for this instance is the preserved raw response payload from the ENTSO-E API.

---

## 3. Vintage definition

ENTSO-E data may be revised after initial publication (e.g. intermediate values replaced by final values).  
Therefore the identity of the input is:

$$\text{source identity} + \text{exact 12 requests} + \text{acquisition batch timestamps} + \text{raw response bytes}$$

rather than merely:

$$\text{zone} + \text{historical delivery period}$$

### Acquisition Batch & Vintage Timestamps
The vintage is defined as a **single frozen acquisition batch**:
- $T_{\text{run\_start}}$: UTC timestamp recorded immediately before the first evidentiary ENTSO-E request of the official run.
- $T_{\text{run\_end}}$: UTC timestamp recorded immediately after the 12th response is received.
- For each request: request URL/parameters (credentials redacted), exact request timestamp $T_{\text{req}}$, response timestamp $T_{\text{resp}}$, HTTP status, and SHA-256 hash of the raw response payload.

All timestamps and hashes must be written to `run_metadata.json` before any response is parsed or interpreted.  
The raw responses captured in that batch become the immutable audit vintage.

### Multi-Document & Revision Handling
For every returned `MarketDocument`:
- Inventory and preserve every XML document raw byte-for-byte.
- Verify `documentType = A85` and `process.processType = A16`.
- For repeated `mRID` document revisions, identify the numerically latest `revisionNumber` as the current-state document while preserving all received revisions in the inventory.
- After source-defined revision handling, any remaining collision on the same registered UTC MTU is a duplicate and Target S fails. Zero analyst-discretion deduplication.

---

## 4. Measurement windows

### Baseline
Local-market interval:
`2025-08-01 00:00` inclusive through `2026-07-01 00:00` exclusive (11 calendar months / 334 calendar days).  
UTC equivalent: `2025-07-31 22:00:00Z` to `2026-06-30 22:00:00Z`.

### Target
Local-market interval:
`2026-07-01 00:00` inclusive through `2026-08-01 00:00` exclusive (31 calendar days).  
UTC equivalent: `2026-06-30 22:00:00Z` to `2026-07-31 22:00:00Z`.

All boundaries are converted exactly once to UTC before request construction.  
All internal interval identities after acquisition are UTC instants.  
No naive datetime is permitted.

---

## 5. Expected 15-minute population

The registered target resolution is:
`PT15M` (15 minutes).

For a continuous 15-minute UTC grid:

### Baseline
334 days $\times$ 96 intervals/day:
$$N_{\text{expected\_baseline}} = \mathbf{32,064}$$
per zone.

### July 2026 target
31 days $\times$ 96 intervals/day:
$$N_{\text{expected\_target}} = \mathbf{2,976}$$
per zone.

These values describe the expected interval grid after the registered local boundaries are converted to UTC.  
DST must never be handled by deleting or manufacturing rows.  
A DST transition changes the mapping between civil time and UTC; it does not license a missing or duplicated UTC interval.

---

## 6. Structural Target S

For each zone and each registered window construct the expected UTC grid independently of the received data.  
The raw document is then mapped to that grid.

Record, without repair:
- $N_{\text{expected}}$;
- $N_{\text{observed\_unique}}$;
- missing timestamps;
- duplicate timestamps;
- timestamps outside the requested interval;
- unexpected resolution changes;
- null-valued points;
- overlapping time-series segments.

### S-PASS
A zone/window passes the structural gate only when:
$$\text{missing} = 0 \quad \text{AND} \quad \text{duplicates} = 0 \quad \text{AND} \quad \text{unexpected timestamps} = 0$$
AND every populated series used by the estimator has the preregistered `PT15M` semantics.

### S-HALT
Any unexplained deviation from the exact interval population halts scarcity interpretation for the affected zone/window.  
Completeness percentages are not substitutes for this invariant.  
No rule such as "99.9% complete" is permitted.

---

## 7. No-repair rule

The confirmatory pipeline must not:
- interpolate;
- forward-fill;
- backward-fill;
- deduplicate by arbitrary first/last selection;
- infer missing prices;
- resample to manufacture absent MTUs;
- silently clip boundary rows;
- join neighbouring monthly chunks and then conceal overlap;
- substitute a national source for a missing ENTSO-E interval.

A missing interval remains missing evidence.  
Cross-source checks may be reported separately but cannot repair Target S.

---

## 8. Scarcity reproduction rule

This section reproduces an already exposed public rule; it is not presented as newly selected without knowledge of the outcome.

For each zone $z$:

### Baseline threshold
Let $B_z$ be all admissible 15-minute imbalance-price observations in the registered baseline after Target S has passed.

Define:
$$R_z = \text{90th percentile}(B_z)$$

**Single Executable Quantile Implementation (Pinned from historical Note #003):**
The quantile estimator is strictly and uniquely defined as:
```python
R_z = float(pd.Series(B_z).quantile(0.90, interpolation='linear'))
```
*(Mathematical equivalence note: This corresponds to Type 7 linear interpolation $Q(p) = (1-\gamma)x_j + \gamma x_{j+1}$ where index $j = \lfloor (n-1)p \rfloor + 1$ and $\gamma = (n-1)p - \lfloor (n-1)p \rfloor$. No alternative software method or default is permitted).*

Column mapping by zone (DocumentType `A85`):
- AT: `Short` (Single pricing)
- BE: `Short` (Single pricing)
- DK-1: `Short` (Single pricing)
- DK-2: `Short` (Single pricing)
- FR: `Short` (Dual pricing — shortage direction)
- NL: `Short` (Dual pricing — shortage direction)

### July occupancy
For the July target population:
$$M_z = \frac{\text{count}(\text{price} \ge R_z)}{N_{\text{expected\_target}}} = \frac{\text{count}(\text{price} \ge R_z)}{2,976}$$

A zone is:
$$\text{ELEVATED} \iff M_z \ge 0.15 \quad (15.0\%)$$
$$\text{NOT\_ELEVATED} \iff M_z < 0.15$$

The denominator is the registered exact population ($2,976$), not merely the number of rows returned by a parser.  
If Target S fails, no $M_z$ is issued for that zone.

---

## 9. Published reproduction target

Prior-exposed published reference:
- FR: approximately $31.8\%$
- NL: approximately $23.3\%$
- BE: approximately $18.8\%$
- AT: approximately $18.4\%$
- DK-1: approximately $17.5\%$
- DK-2: approximately $11.3\%$

Published qualitative result:
- Five of six ENTSO-E zones elevated ($\ge 15\%$);
- DK-2 not elevated ($< 15\%$).

These values are reference outputs, never estimator inputs.

### Primary reproduction comparison
Primary target is classification identity:
$$\text{FR, NL, BE, AT, DK-1} = \text{ELEVATED}$$
$$\text{DK-2} = \text{NOT\_ELEVATED}$$

### Numerical comparison
The recomputed occupancy for every zone is reported against the historical published value.  
A numerical difference is reported as a difference.  
It is not automatically treated as implementation failure, because the new frozen vintage may contain later ENTSO-E revisions.  
The audit must distinguish:
- pipeline disagreement;
- source-vintage revision;
- unresolved cause.

No cause is inferred without evidence.

---

## 10. Decision outcomes

The run produces separate outcomes:

### S — source-structure outcome
- `STRUCTURE_PASS`
- `STRUCTURE_FAIL`
- `HALT`

*(These are run findings, not P10 scientific verdicts.)*

### R — published-result reproduction
*(Only evaluated for structurally admissible zones)*
- `REPRODUCED`
- `NOT_REPRODUCED`
- `PARTIALLY_REPRODUCED`
- `NOT_EVALUATED`

*(These are reproduction outcomes for an internal self-reproduction audit; no controlled P10 independent verification verdict is automatically generated).*

---

## 11. Known prior exposure

Before this preregistration the team has already seen:
- the earlier ENTSO-E six-zone dataset;
- prior missing-interval and boundary defects;
- the published July-2026 six-zone occupancy values;
- the published five-of-six classification;
- alternative exploratory baseline constructions;
- cross-source investigations involving Danish intervals.

Therefore:
- this run is not epistemically blind;
- the old result is not treated as unseen confirmatory evidence;
- the contribution of s2 is the stricter source-vintage and exact-boundary test.

The exploratory six-month rolling-baseline analysis is not part of this target and must not be substituted for the published July-specific rule.

---

## 12. Evidentiary acquisition

The official run must preserve under:
`evidence/runs/<RUN_ID>/`
at minimum:
- `command.sh`
- `stdout.log`
- `stderr.log`
- `exit_code.txt`
- `env.txt`
- `git_commit.txt`
- `inputs.sha256`
- `outputs.sha256`
- `run_metadata.json`

Additionally required:
- exact request parameters with security credentials redacted;
- raw HTTP response bodies (`evidence/runs/<RUN_ID>/raw/`);
- response headers relevant to provenance;
- raw XML document inventory;
- parsed document metadata inventory;
- expected timestamp grid;
- missing/duplicate/extra timestamp listing per zone.

Derived counts do not replace raw listings.

---

## 13. Freeze and execution order

Required order:
1. complete L0 source/schema/licence identification and 12-request contract;
2. Claude pre-execution Gate review of draft specification;
3. Sol addresses any gate findings;
4. Ivan accepts specification;
5. commit frozen preregistration on `main`;
6. record preregistration SHA (`PREREG_SHA`);
7. no further semantic changes;
8. Ananke executes official run strictly on `PREREG_SHA` (capturing raw responses at $T_{\text{vintage}}$);
9. literal evidence packet produced under `evidence/runs/<RUN_ID>/`;
10. clean recreation from preserved raw vintage;
11. Claude final Gate;
12. Ivan ratification.

Any data execution before step 6 is:
`Exploratory (not pre-registered)`.

---

## 14. HALT conditions

HALT when any of the following occurs:
- executed git SHA differs from frozen SHA;
- exact ENTSO-E source identity is unresolved;
- expected A85 document identity cannot be established;
- requested period semantics are ambiguous;
- timezone conversion is ambiguous;
- API rejects 334-day or 31-day request (`HALT: request contract unsupported`);
- quantile implementation cannot be executed via pinned `pandas.Series.quantile(0.90, interpolation='linear')`;
- unexpected MTU resolution is present;
- raw artifact is unavailable;
- artifact hash changes inside the same run;
- parser modifies the raw interval population;
- duplicate resolution requires analyst discretion;
- later source data replaces the frozen vintage;
- authentication/request failure prevents complete acquisition.

No threshold or estimator is changed after HALT.

---

## 15. Scope exclusions

This instance does not establish:
- why ENTSO-E may contain a missing interval;
- whether the originating TSO submitted an interval correctly;
- whether ENTSO-E subsequently revised an interval;
- market causality;
- BESS revenue effects;
- independence among the six zones;
- a general European scarcity regime;
- a forecast of future scarcity;
- the Great Britain leg of the earlier regional comparison.

It tests only structural integrity and reproducibility of the stated measurement from the specified public acquisition vintage.
