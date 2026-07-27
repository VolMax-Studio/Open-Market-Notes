import os
import json
import matplotlib.pyplot as plt
import numpy as np

# Set style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig_dir = './figures'
os.makedirs(fig_dir, exist_ok=True)

# Load summary JSON
with open('./data/imbalance_baseline_summary.json', 'r') as f:
    data = json.load(f)

zones = list(data.keys())

# Chart 1: M1 Scarcity Duration Breakdown (Mean, Median, P90, P95, Max)
fig, ax = plt.subplots(figsize=(10, 5), dpi=300)

means = [data[z]['m1_100']['mean_min'] for z in zones]
medians = [data[z]['m1_100']['median_min'] for z in zones]
p90s = [data[z]['m1_100']['p90_min'] for z in zones]
p95s = [data[z]['m1_100']['p95_min'] for z in zones]

x = np.arange(len(zones))
width = 0.2

rects1 = ax.bar(x - 1.5*width, medians, width, label='Median (P50)', color='#2b5c8f')
rects2 = ax.bar(x - 0.5*width, means, width, label='Arithmetic Mean', color='#d95f02')
rects3 = ax.bar(x + 0.5*width, p90s, width, label='P90 Percentile', color='#7570b3')
rects4 = ax.bar(x + 1.5*width, p95s, width, label='P95 Percentile', color='#e7298a')

ax.set_ylabel('Duration (Minutes)', fontsize=12, fontweight='bold')
ax.set_title('M1 System Shortage Scarcity Duration (>= €100/MWh) by Bidding Zone', fontsize=13, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(zones, fontsize=11, fontweight='bold')
ax.legend(frameon=True, facecolor='white', edgecolor='none')
ax.set_ylim(0, max(p95s) * 1.25)

for rect in rects1 + rects2 + rects3 + rects4:
    height = rect.get_height()
    if height > 0:
        ax.annotate(f'{height:.1f}m',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, 'm1_scarcity_duration.png'))
plt.close()

# Chart 2: M2 Grid Surplus Absorption Availability (% of Days)
fig, ax = plt.subplots(figsize=(10, 5), dpi=300)

pct_4h = [data[z]['m2_cheap_25']['pct_4h_bess'] for z in zones]
pct_8h = [data[z]['m2_cheap_25']['pct_8h_bess'] for z in zones]
pct_zero = [data[z]['m2_zero_neg']['pct_4h_bess'] for z in zones]

x = np.arange(len(zones))
width = 0.25

rects1 = ax.bar(x - width, pct_4h, width, label='4h BESS Surplus Window (<= €25/MWh)', color='#1b9e77')
rects2 = ax.bar(x, pct_8h, width, label='8h BESS Surplus Window (<= €25/MWh)', color='#d95f02')
rects3 = ax.bar(x + width, pct_zero, width, label='4h Zero/Negative Days (<= €0/MWh)', color='#7570b3')

ax.set_ylabel('% of Days in 13-Month Period', fontsize=12, fontweight='bold')
ax.set_title('M2 Grid Surplus Absorption Window Availability (% of Days)', fontsize=13, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(zones, fontsize=11, fontweight='bold')
ax.legend(frameon=True, facecolor='white', edgecolor='none')
ax.set_ylim(0, 80)

for rect in rects1 + rects2 + rects3:
    height = rect.get_height()
    if height > 0:
        ax.annotate(f'{height:.1f}%',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, 'm2_surplus_availability.png'))
plt.close()

print("=== GENERATED CHARTS IN ./figures ===")
