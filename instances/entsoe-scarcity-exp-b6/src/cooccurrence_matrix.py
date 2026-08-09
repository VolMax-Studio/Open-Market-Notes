#!/usr/bin/env python3
"""
Pairwise elevation co-occurrence over an existing scheduled/exploratory instance.

Reads only runs/<W>/result.json files already produced by run_window.py. It
recomputes nothing: every value here is copied from a measurement that already
exists and is already hashed. If a number here disagrees with a result.json,
the result.json is authoritative and this table is regenerated.

Scope, stated up front because the output invites over-reading:

  - This measures CO-OCCURRENCE, not correlation, not causation, and not
    portfolio return. Two zones "co-occur" in a window when both were
    determinately ELEVATED in that window under the instance's frozen rules.
  - The denominator is EVALUATED windows only. Windows that were
    NOT_EVALUATED contribute to neither numerator nor denominator, and their
    count is reported separately so the reader can see what was excluded.
  - Companion (non-voting) markets are excluded from the pair grid by default.
  - n is small. The output prints n on every line for that reason.

Usage:
  python3 cooccurrence_matrix.py --instance instances/entsoe-scarcity-exp-b6
  python3 cooccurrence_matrix.py --instance <dir> --out results/cooccurrence.json
"""

import os
import json
import argparse
import hashlib
from itertools import combinations


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def load_runs(instance_dir):
    """Read every runs/<W>/result.json. Never recompute; only read."""
    runs_dir = os.path.join(instance_dir, 'runs')
    if not os.path.isdir(runs_dir):
        raise FileNotFoundError(f"runs/ missing at {runs_dir}")

    windows = sorted(
        d for d in os.listdir(runs_dir)
        if os.path.isdir(os.path.join(runs_dir, d)) and len(d) == 7 and d[4] == '-'
    )
    if not windows:
        raise ValueError(f"No run directories found under {runs_dir}")

    runs = []
    for w in windows:
        rp = os.path.join(runs_dir, w, 'result.json')
        if not os.path.exists(rp):
            raise FileNotFoundError(
                f"Window directory {w} exists but result.json is missing. "
                f"A window is never silently skipped — fix or remove the directory."
            )
        with open(rp) as f:
            data = json.load(f)
        runs.append({
            'window': w,
            'result_path': os.path.relpath(rp, instance_dir),
            'result_sha256': sha256_file(rp),
            'data': data,
        })
    return runs


def build(instance_dir):
    params_path = os.path.join(instance_dir, 'PARAMS.md')
    if not os.path.exists(params_path):
        raise FileNotFoundError(f"PARAMS.md missing at {params_path}")
    txt = open(params_path).read()
    params = json.loads(txt[txt.find('{'):txt.rfind('}') + 1])

    comparison_zones = params['comparison_zones']
    companion_zones = params.get('companion_zones', [])

    runs = load_runs(instance_dir)

    evaluated, unevaluated = [], []
    for r in runs:
        if r['data'].get('evaluation_status') == 'EVALUATED':
            evaluated.append(r)
        else:
            unevaluated.append({
                'window': r['window'],
                'evaluation_status': r['data'].get('evaluation_status'),
            })

    n_eval = len(evaluated)
    if n_eval == 0:
        raise ValueError("No EVALUATED windows. Nothing to count.")

    # Per-window elevated set, comparison zones only.
    per_window = []
    for r in evaluated:
        zm = r['data']['zone_metrics']
        elevated = sorted(
            z for z in comparison_zones
            if zm.get(z, {}).get('determinacy') == 'ELEVATED'
        )
        per_window.append({
            'window': r['window'],
            'label': r['data'].get('label'),
            'elevated': elevated,
            'n_elevated': len(elevated),
            'result_sha256': r['result_sha256'],
        })

    # Marginals: how often each zone is elevated on its own.
    marginal = {
        z: sum(1 for w in per_window if z in w['elevated'])
        for z in comparison_zones
    }

    # Pairs.
    pairs = []
    for a, b in combinations(comparison_zones, 2):
        both = [w['window'] for w in per_window if a in w['elevated'] and b in w['elevated']]
        either = sum(1 for w in per_window
                     if a in w['elevated'] or b in w['elevated'])
        # Expected co-occurrence if the two zones were independent, given the
        # observed marginals. Stated as a reference point only: with this n it
        # supports no inference, and no test is performed.
        expected_independent = (marginal[a] / n_eval) * (marginal[b] / n_eval) * n_eval
        pairs.append({
            'zone_a': a,
            'zone_b': b,
            'both_elevated': len(both),
            'either_elevated': either,
            'n_evaluated_windows': n_eval,
            'both_windows': both,
            'marginal_a': marginal[a],
            'marginal_b': marginal[b],
            'expected_if_independent': round(expected_independent, 2),
            'excess_over_independent': round(len(both) - expected_independent, 2),
        })

    pairs.sort(key=lambda p: (-p['both_elevated'], p['zone_a'], p['zone_b']))

    return {
        'instance_id': params.get('instance_id'),
        'instance_dir': instance_dir,
        'selection_mode': params.get('selection_mode'),
        'baseline_months_N': params.get('N'),
        'q_ref': params.get('q_ref'),
        's_thresh_pct': round(params['k_multiplier'] * (1 - params['q_ref']) * 100.0, 4),
        'comparison_zones': comparison_zones,
        'companion_zones_excluded': companion_zones,
        'n_calendar_windows': len(runs),
        'n_evaluated_windows': n_eval,
        'unevaluated_windows': unevaluated,
        'per_window': per_window,
        'marginal_elevation_counts': marginal,
        'pairs': pairs,
        'scope_note': (
            "Co-occurrence of determinate ELEVATED states under this instance's frozen "
            "rules. Not correlation, not causation, not portfolio outcome. Denominator "
            "is EVALUATED windows only; unevaluated windows are listed and excluded. "
            "Labels depend on the baseline length N — a pair count under one N is not "
            "comparable to a count under another. Exploratory: this pairing was not "
            "pre-registered."
        ),
    }


def render(rep):
    n = rep['n_evaluated_windows']
    print("\n" + "=" * 72)
    print("  PAIRWISE ELEVATION CO-OCCURRENCE")
    print("=" * 72)
    print(f"Instance        : {rep['instance_id']}  ({rep['selection_mode']})")
    print(f"Baseline N      : {rep['baseline_months_N']} months   "
          f"q = {rep['q_ref']}   S_thresh = {rep['s_thresh_pct']}%")
    print(f"Windows         : {rep['n_calendar_windows']} calendar, "
          f"{n} evaluated, {len(rep['unevaluated_windows'])} unevaluated")
    if rep['unevaluated_windows']:
        for u in rep['unevaluated_windows']:
            print(f"                  excluded {u['window']}: {u['evaluation_status']}")
    print(f"Companions excl.: {', '.join(rep['companion_zones_excluded']) or 'none'}")

    print("\n--- PER WINDOW ---")
    print(f"{'window':<9} {'label':<10} {'n':<3} elevated")
    for w in rep['per_window']:
        print(f"{w['window']:<9} {str(w['label']):<10} {w['n_elevated']:<3} "
              f"{', '.join(w['elevated']) if w['elevated'] else '—'}")

    print("\n--- MARGINALS (zone elevated on its own) ---")
    for z, c in sorted(rep['marginal_elevation_counts'].items(), key=lambda kv: -kv[1]):
        print(f"{z:<6} {c}/{n}")

    print("\n--- PAIRS (both elevated in the same window) ---")
    print(f"{'pair':<14} {'both':<7} {'of n':<6} {'exp.indep':<11} {'excess':<8} windows")
    for p in rep['pairs']:
        pair = f"{p['zone_a']}–{p['zone_b']}"
        print(f"{pair:<14} {p['both_elevated']:<7} {n:<6} "
              f"{p['expected_if_independent']:<11} {p['excess_over_independent']:<8} "
              f"{', '.join(p['both_windows']) if p['both_windows'] else '—'}")

    print("\n" + rep['scope_note'])
    print("=" * 72 + "\n")


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description="Pairwise elevation co-occurrence")
    ap.add_argument('--instance', required=True, help="Instance directory")
    ap.add_argument('--out', default=None,
                    help="Optional JSON output path (relative to instance dir)")
    args = ap.parse_args()

    report = build(args.instance)
    render(report)

    if args.out:
        out_path = os.path.join(args.instance, args.out)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, 'w') as f:
            json.dump(report, f, indent=2, sort_keys=True)
        print(f"Written: {out_path}")
        print(f"SHA-256: {sha256_file(out_path)}\n")
