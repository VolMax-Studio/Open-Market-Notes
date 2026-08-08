#!/usr/bin/env python3
"""
VolMax Open Market Note #003 Publication Visualizer
Generates Publication-Ready Figures directly from probe_verdict_report.json
"""

import os
import json
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

def generate_probe_figures(report_path='probe_jul2026/probe_verdict_report.json', out_dir='probe_jul2026'):
    if not os.path.exists(report_path):
        raise FileNotFoundError(f"Report not found at {report_path}")

    with open(report_path, 'r') as f:
        report = json.load(f)

    os.makedirs(out_dir, exist_ok=True)

    # Extract metrics dynamically from source report
    gb_metrics = report["benchmark_metrics"]["gb_comparator"]
    eu_metrics = report["benchmark_metrics"]["eu_zones"]

    # Combine markets
    markets = [
        {"name": "FR", "share": eu_metrics["FR"]["jul_2026_share_q90_pct"], "is_gb": False},
        {"name": "GB", "share": gb_metrics["jul_2026_share_q90_pct"], "is_gb": True},
        {"name": "NL", "share": eu_metrics["NL"]["jul_2026_share_q90_pct"], "is_gb": False},
        {"name": "BE", "share": eu_metrics["BE"]["jul_2026_share_q90_pct"], "is_gb": False},
        {"name": "AT", "share": eu_metrics["AT"]["jul_2026_share_q90_pct"], "is_gb": False},
        {"name": "DK_1", "share": eu_metrics["DK_1"]["jul_2026_share_q90_pct"], "is_gb": False},
        {"name": "DK_2", "share": eu_metrics["DK_2"]["jul_2026_share_q90_pct"], "is_gb": False},
    ]

    # Sort descending
    markets = sorted(markets, key=lambda x: x["share"], reverse=True)

    # -------------------------------------------------------------
    # FIGURE 1: Horizontal Bar Chart of 7 Markets vs 15.0% Threshold
    # -------------------------------------------------------------
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6.2), dpi=300)
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#0f172a')

    names = [m["name"] for m in markets]
    shares = [m["share"] for m in markets]
    y_pos = np.arange(len(names))

    # Color palette
    colors = []
    for m in markets:
        if m["is_gb"]:
            colors.append('#f59e0b')  # Warm Amber for GB
        elif m["share"] >= 15.0:
            colors.append('#38bdf8')  # Bright Cyan for Elevated EU
        else:
            colors.append('#64748b')  # Muted Slate for Non-Elevated (DK_2)

    bars = ax.barh(y_pos, shares, align='center', color=colors, height=0.62, edgecolor='none', zorder=3)
    ax.invert_yaxis()  # top-down

    # Add 15% threshold line
    thresh_line = ax.axvline(x=15.0, color='#f43f5e', linestyle='--', linewidth=2.0, zorder=4, label='15.0% Threshold (Frozen 8 Aug 2026, before data)')

    # Add text labels on bars
    for bar, share in zip(bars, shares):
        width = bar.get_width()
        ax.text(width + 0.6, bar.get_y() + bar.get_height()/2.0, f'{share:.1f}%',
                va='center', ha='left', color='#f8fafc', fontsize=11, fontweight='bold')

    # Titles and labels
    ax.set_title('European Imbalance Scarcity Elevation (July 2026 Probe)', fontsize=15, fontweight='bold', pad=22, color='#ffffff', loc='left')
    fig.text(0.125, 0.90, "Share of settlement time above each market's own 11-month Q90 baseline", fontsize=10.5, color='#94a3b8', fontstyle='italic')

    ax.set_xlabel('Time Share Above Baseline Q90 (%)', fontsize=11, fontweight='bold', color='#cbd5e1', labelpad=10)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=12, fontweight='bold', color='#f8fafc')
    ax.set_xlim(0, 37)

    # Gridlines and styling
    ax.grid(True, axis='x', linestyle=':', color='#334155', alpha=0.7, zorder=0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#475569')
    ax.spines['bottom'].set_color('#475569')

    # Legend
    ax.legend(loc='lower right', frameon=True, facecolor='#1e293b', edgecolor='#334155', fontsize=9.5, labelcolor='#f8fafc')

    # Footnote
    fig.text(0.125, 0.02, "Note: European bidding zones are coupled via cross-border interconnectors (C5 spatial non-independence).",
             fontsize=8.5, color='#64748b', fontstyle='italic')

    plt.tight_layout(rect=[0, 0.05, 1, 0.88])
    fig1_path = os.path.join(out_dir, 'figure1_regional_elevation_probe.png')
    plt.savefig(fig1_path, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Saved Figure 1 to {fig1_path}")

    # -------------------------------------------------------------
    # FIGURE 2: GB July 2025 vs July 2026 Comparison
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7, 5.5), dpi=300)
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#0f172a')

    gb_jul25 = gb_metrics["jul_2025_share_q90_pct"]
    gb_jul26 = gb_metrics["jul_2026_share_q90_pct"]
    gb_q90 = gb_metrics["baseline_q90_gbp"]
    yoy_factor = gb_jul26 / gb_jul25 if gb_jul25 > 0 else 0.0

    gb_periods = ['July 2025', 'July 2026']
    gb_shares = [gb_jul25, gb_jul26]
    bar_colors = ['#475569', '#f59e0b']

    bars = ax.bar(gb_periods, gb_shares, color=bar_colors, width=0.45, zorder=3)

    for bar, share in zip(bars, gb_shares):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, height + 0.8, f'{share:.2f}%',
                ha='center', va='bottom', color='#ffffff', fontsize=13, fontweight='bold')

    # Dynamic annotation arrow derived from report source
    annotation_text = f"{yoy_factor:.1f}× Increase"
    ax.annotate(annotation_text, xy=(1, gb_jul26), xytext=(0.45, gb_jul26 * 0.7),
                arrowprops=dict(facecolor='#f43f5e', edgecolor='#f43f5e', shrink=0.08, width=2, headwidth=8),
                fontsize=12, fontweight='bold', color='#f43f5e', bbox=dict(boxstyle="round,pad=0.4", fc="#1e293b", ec="#f43f5e", lw=1.5))

    ax.set_title('Great Britain (GB) July Scarcity Elevation YoY', fontsize=14, fontweight='bold', pad=20, color='#ffffff', loc='left')
    fig.text(0.125, 0.90, f"Share of settlement time above GB Q90 baseline (£{gb_q90:.2f}/MWh)", fontsize=10, color='#94a3b8', fontstyle='italic')

    ax.set_ylabel('Time Share Above Q90 (%)', fontsize=11, fontweight='bold', color='#cbd5e1', labelpad=10)
    ax.set_ylim(0, max(gb_shares) * 1.25)

    ax.grid(True, axis='y', linestyle=':', color='#334155', alpha=0.7, zorder=0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#475569')
    ax.spines['bottom'].set_color('#475569')

    plt.tight_layout(rect=[0, 0.03, 1, 0.88])
    fig2_path = os.path.join(out_dir, 'figure2_gb_july_year_over_year.png')
    plt.savefig(fig2_path, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Saved Figure 2 to {fig2_path}")

if __name__ == '__main__':
    generate_probe_figures()
