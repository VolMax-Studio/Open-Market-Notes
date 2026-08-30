"""
make_figure.py — generates figure from coupling_lookups.csv ONLY.
No literal price values. Fails loudly if row count != 32.
"""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(BASE_DIR, "data", "coupling_lookups.csv")
FIG_DIR = os.path.join(BASE_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)
OUT = os.path.join(FIG_DIR, "coupling_evening.png")

df = pd.read_csv(CSV)
assert len(df) == 32, f"expected 32 lookups, got {len(df)}"

# CSV columns
COL_TS, COL_DATE = "time_cest", "date"
ZONE_COLS = {
    "FR": "price_FR",
    "BE": "price_BE",
    "DE_LU": "price_DE_LU"
}

fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), sharey=True)

for ax, (d, g) in zip(axes, df.groupby(COL_DATE, sort=True)):
    g = g.sort_values(COL_TS)
    x = range(len(g))
    for z_label, z_col in ZONE_COLS.items():
        ax.plot(x, g[z_col], marker="o", ms=4, lw=1.6, label=z_label)
    div = g[g["verdict"] == "DIVERGED"]
    for i, _ in zip([list(g[COL_TS]).index(t) for t in div[COL_TS]], div.index):
        ax.axvspan(i - 0.4, i + 0.4, color="0.85", zorder=0)
    ax.set_xticks(list(x))
    # format time label as HH:MM
    ax.set_xticklabels([str(t)[11:16] for t in g[COL_TS]], rotation=90, fontsize=8)
    date_display = "2026-08-12" if "2026-08-12" in d else "2026-08-13"
    ax.set_title(f"{date_display}   COUPLED_EXACT {int((g.verdict=='COUPLED_EXACT').sum())}/16", fontsize=10)
    ax.grid(alpha=0.25)

axes[0].set_ylabel("Day-ahead price, EUR/MWh (15-min MTU)")
axes[0].legend(frameon=False)
fig.suptitle("FR / BE / DE_LU day-ahead prices, evening window 18:00–22:00 CEST\n"
             "Shaded = max pairwise difference > 0.01 EUR/MWh", fontsize=11)
fig.text(0.01, 0.01,
         "Source: ENTSO-E Transparency Platform (transparency.entsoe.eu), under CC BY 4.0 license | "
         "instance fr-be-de-eclipse-coupling-probe, pre-registration e8d267c",
         fontsize=7)
fig.tight_layout(rect=[0, 0.04, 1, 0.93])
fig.savefig(OUT, dpi=200)
print(f"wrote {OUT}")
