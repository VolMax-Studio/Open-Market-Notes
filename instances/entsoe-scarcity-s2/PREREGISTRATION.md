# ENTSO-E Scarcity Vintage-Stability Audit — Pre-registration

**Instance:** `entsoe-scarcity-s2`  
**Status:** DRAFT v4 — NOT FROZEN (FOR PRE-EXECUTION GATE REVIEW)  
**Deadline:** 2026-09-12  
**Architecture:** Pinned-vintage ENTSO-E Transparency Platform / IEC 62325 raw-document architecture with PKZip extraction and Multi-Period parsing  
**Audit Class:** Internal self-reproduction and vintage-stability audit of published VolMax Open Market Note #003 findings.  
**Claimant:** VolMax Studio  

This instance is a new registered reproduction / vintage-stability audit.  
It is not a repair of `entsoe-scarcity-s1`.  
The team has prior exposure to the published July-2026 scarcity result and empirical findings from `run-001`, `run-002`, and `run-003`. Therefore this instance is not outcome-naive and must not be described as first-pass confirmatory discovery.

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
- realised process: `processType = A16` (XML validation invariant);
- raw ENTSO-E / IEC 62325 balancing-market documents (`Balancing_MarketDocument` XML).

Target Area EICs (`controlArea_Domain`):
- AT (Austria): `10YAT-APG------L` (Austrian Power Grid CA/BZ per ENTSO-E Market Areas v2.0; confirmed HTTP 200 in runs 001, 002, 003)
- BE (Belgium): `10YBE----------2` (Belgian BZ/CA per ENTSO-E Market Areas v2.0; confirmed HTTP 200 in runs 002, 003)
- DK-1 (Denmark West): `10YDK-1--------W` (DK1 BZ per ENTSO-E Market Areas v2.0; confirmed HTTP 200 in runs 002, 003)
- DK-2 (Denmark East): `10YDK-2--------M` (DK2 BZ per ENTSO-E Market Areas v2.0; confirmed HTTP 200 in runs 002, 003)
- FR (France): `10YFR-RTE------C` (RTE CA/BZ per ENTSO-E Market Areas v2.0; confirmed HTTP 200 in runs 002, 003)
- NL (Netherlands): `10YNL----------L` (TenneT NL CA/BZ per ENTSO-E Market Areas v2.0; confirmed HTTP 200 in runs 002, 003)

### Shortage Price Category Selector (B-23 & B-24 Resolution)
For all six zones (`AT`, `BE`, `DK-1`, `DK-2`, `FR`, `NL`), the evaluation extracts shortage price observations matching:
```xml
<imbalance_Price.category>A04</imbalance_Price.category>
```
- In single pricing zones (`AT`, `BE`, `DK-1`, `DK-2`), `A04` (Shortage) and `A05` (Surplus) prices are equal.
- In dual pricing zones (`FR`, `NL`), `A04` represents the shortage direction.

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

---

## 3. Vintage definition & Multi-Period Extraction Architecture

ENTSO-E data may be revised after initial publication (e.g. intermediate values replaced by final values).  
Therefore the identity of the input is:

$$\text{source identity} + \text{exact 12 requests} + \text{acquisition batch timestamps} + \text{raw response bytes}$$

### Acquisition Batch & Raw Response Preservation
The vintage is defined as a **single frozen acquisition batch**:
- For each request: request URL/parameters (credentials redacted), exact request timestamp $T_{\text{req}}$, response timestamp $T_{\text{resp}}$, HTTP status, and SHA-256 hash of the raw response payload.
- All raw responses are preserved byte-for-byte under `evidence/runs/<RUN_ID>/raw/`.

### Transport Container & Multi-Period Parsing Rules (B-19 & B-21 Resolution)
1. **PKZip Decompression:**
   - Detect PKZip archives via magic bytes `50 4B 03 04` / `b'PK\x03\x04'`.
   - Process member documents in alphabetical filename order (`sorted(zip_ref.namelist())`).
   - Direct XML payloads (`b'<'`) are parsed as single documents.
   - Non-compliant streams trigger `PAYLOAD_FORMAT_UNEXPECTED`.
2. **Multi-Period Iteration within TimeSeries:**
   - Within each `<TimeSeries>`, the parser iterates over **all** `<Period>` elements (`ts.findall('.//ns:Period')`).
   - For each `<Period>`, extract its specific `timeInterval/start` UTC instant ($T_{\text{period\_start}}$).
   - Point timestamp is computed as:
     $$T_{\text{point}} = T_{\text{period\_start}} + 15\text{ min} \times (\text{position} - 1)$$
3. **Price Category Filtering (B-23 Resolution):**
   - Extract points strictly matching `<imbalance_Price.category>A04</imbalance_Price.category>`.
4. **Multi-Document Revision Handling:**
   - Verify `documentType = A85`, `processType = A16`, and `resolution = PT15M`.
   - For repeated `mRID` document revisions across archive members, identify the numerically latest `revisionNumber` as the current-state document while preserving all received revisions in the document inventory.
   - Any remaining collision or conflicting value on the same registered UTC MTU is a duplicate and Target S fails.

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
AND every populated series used by the estimator has the preregistered `PT15M` semantics and passes document identity checks (`documentType == A85` and `processType == A16`).

### S-HALT
Any unexplained deviation from the exact interval population halts scarcity interpretation for the affected zone/window.  
Completeness percentages are not substitutes for this invariant.

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

---

## 8. Scarcity reproduction rule

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
*(Executable environment is strictly pinned in requirements.txt: pandas==2.3.3, numpy==1.26.4, requests==2.34.2).*

Price Category: `<imbalance_Price.category>A04</imbalance_Price.category>` across all six zones.

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

### Primary reproduction comparison
Primary target is classification identity:
$$\text{FR, NL, BE, AT, DK-1} = \text{ELEVATED}$$
$$\text{DK-2} = \text{NOT\_ELEVATED}$$

---

## 10. Decision outcomes & Halt Taxonomy

### S — source-structure outcome
- `STRUCTURE_PASS`
- `STRUCTURE_FAIL`
- `HALT`

### R — published-result reproduction
*(Only evaluated for structurally admissible zones)*
- `REPRODUCED`
- `NOT_REPRODUCED`
- `PARTIALLY_REPRODUCED`
- `NOT_EVALUATED`

### Frozen Halt Taxonomy
1. `HTTP_ERROR`: Non-200 HTTP response code returned by the server (e.g. 400, 401, 403, 429, 500, 503).
2. `REQUEST_CONTRACT_UNSUPPORTED`: API returns an Acknowledgement payload explicitly rejecting the request structure or time window.
3. `API_REPORTS_NO_MATCHING_DATA`: API returns an Acknowledgement payload with Reason 999 ("No matching data found for Data item ... and interval").
4. `API_REASON_OTHER`: API returns an Acknowledgement payload with a reason code other than 999.
5. `PAYLOAD_FORMAT_UNEXPECTED`: Raw payload is not in a supported transport container format (e.g. corrupted PKZip archive, unparseable non-XML stream, decompression failure).
6. `SOURCE_IDENTITY_INVALID`: Returned XML document violates document identity invariants (e.g. `documentType != A85`, `processType != A16`, or unexpected resolution != `PT15M`).
7. `EXECUTION_STATE_INVALID`: Execution environment preconditions violated (e.g. non-clean working tree, git commit mismatch with governing `PREREG_SHA`).

---

## 11. Known prior exposure

Before this preregistration the team has seen:
- published Note #003 results;
- exploratory `run-001` outcomes;
- `run-002` outcomes (PKZip transport format);
- `run-003` outcomes (complete 12/12 HTTP 200 acquisition batch, Multi-Period structure, `A04` vs `A05` price categories).

Therefore:
- this run is not epistemically blind;
- the old result is not treated as unseen confirmatory evidence;
- `run-004` evaluates exact population structure and reproduction under the corrected multi-period parser.

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
- raw responses under `raw/`
- `derived_results.json`
- `expected_grids.json`, `missing_listings.json`, `duplicate_listings.json`, `document_inventory.json`

---

## 13. Freeze and execution order

Required order:
1. Complete L0 source/schema/licence identification, 12-request contract, and executable harness (`runner.py`, `requirements.txt`);
2. Claude pre-execution Gate review of draft specification;
3. Sol addresses any gate findings;
4. Ivan accepts specification;
5. Commit frozen preregistration on `instances/entsoe-scarcity-s2`;
6. Record preregistration SHA (`PREREG_SHA_v4`);
7. No further semantic or code changes;
8. Ananke executes official `run-004-confirmatory` strictly on `PREREG_SHA_v4` (evaluating the preserved `run-003` raw vintage offline or fresh acquisition as specified);
9. Literal evidence packet produced under `evidence/runs/<RUN_ID>/`;
10. Claude final Gate;
11. Ivan ratification.

---

## 14. HALT conditions

HALT when any of the following occurs:
- executed git SHA differs from frozen SHA (`EXECUTION_STATE_INVALID`);
- git working tree is not clean at run initialization (`EXECUTION_STATE_INVALID`);
- exact ENTSO-E source identity is unresolved;
- payload format is corrupted or unexpected (`PAYLOAD_FORMAT_UNEXPECTED`);
- expected A85 document identity cannot be established (`SOURCE_IDENTITY_INVALID`);
- requested period semantics are ambiguous;
- timezone conversion is ambiguous;
- API rejects request duration or structure (`REQUEST_CONTRACT_UNSUPPORTED`);
- API returns missing data acknowledgement (`API_REPORTS_NO_MATCHING_DATA`);
- quantile implementation cannot be executed via pinned `pandas.Series.quantile(0.90, interpolation='linear')`;
- unexpected MTU resolution is present;
- raw artifact is unavailable;
- artifact hash changes inside the same run;
- parser modifies the raw interval population;
- duplicate resolution requires analyst discretion;
- authentication/request failure prevents complete acquisition.

No threshold, selector, or estimator is changed after HALT.

---

## 15. Scope exclusions

This instance does not establish:
- why ENTSO-E may contain a missing interval;
- whether the originating TSO submitted an interval correctly;
- market causality;
- BESS revenue effects;
- independence among the six zones;
- a general European scarcity regime;
- a forecast of future scarcity;
- the Great Britain leg of the earlier regional comparison.

It tests only structural integrity and reproducibility of the stated measurement from the specified public acquisition vintage.
