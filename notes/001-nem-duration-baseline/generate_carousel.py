import os
import matplotlib.pyplot as plt

# Create output directory
output_dir = './results/carousel'
os.makedirs(output_dir, exist_ok=True)

# Set common style parameters
bg_color = '#121212'
text_color = '#E5E7EB'
emerald_color = '#10B981'
dim_color = '#9CA3AF'
font_family = 'monospace'

def create_slide(slide_num, title, main_val, subtext_lines, list_items=None):
    fig, ax = plt.subplots(figsize=(10, 10), facecolor=bg_color)
    ax.set_facecolor(bg_color)
    
    # Remove all axes
    ax.axis('off')
    
    # Draw VolMax Header
    ax.text(0.08, 0.92, "VOLMAX OPEN MARKET OBSERVATORY", color=emerald_color, fontsize=16, fontweight='bold', fontfamily=font_family, va='center')
    ax.text(0.08, 0.88, "Note #001 // NEM Duration Baseline", color=dim_color, fontsize=13, fontfamily=font_family, va='center')
    
    # Draw Slide Title
    ax.text(0.08, 0.74, title, color=text_color, fontsize=26, fontweight='bold', fontfamily=font_family, va='center')
    
    # Draw Main Metric/Value
    if main_val:
        ax.text(0.08, 0.54, main_val, color=emerald_color, fontsize=52, fontweight='bold', fontfamily=font_family, va='center')
        
    # Draw list items if present
    if list_items:
        y_pos = 0.56
        for item in list_items:
            ax.text(0.08, y_pos, item, color=text_color, fontsize=20, fontfamily=font_family, va='center')
            y_pos -= 0.08
            
    # Draw Subtext
    y_sub = 0.28 if main_val else 0.18
    for line in subtext_lines:
        ax.text(0.08, y_sub, line, color=dim_color, fontsize=16, fontfamily=font_family, va='center')
        y_sub -= 0.05
        
    # Draw Footer
    ax.text(0.08, 0.08, "REPRODUCE: github.com/VolMax-Studio/Open-Market-Notes", color=dim_color, fontsize=11, fontfamily=font_family, va='center')
    ax.text(0.92, 0.08, f"{slide_num}/4", color=emerald_color, fontsize=16, fontweight='bold', fontfamily=font_family, ha='right', va='center')
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/slide_{slide_num}.png", dpi=150, facecolor=bg_color)
    plt.close()

# Slide 1: Scarcity Event Duration
create_slide(
    slide_num=1,
    title="How long do scarcity events last in the NEM?",
    main_val="MEDIAN: 5.0 MINUTES",
    subtext_lines=[
        "Analysis of RRP >= $300/MWh events across 395 days.",
        "NSW1, QLD1, SA1 median is 5 minutes; VIC1 is 10 minutes.",
        "Pricing spikes are highly transient. (Definitions shape the numbers)."
    ]
)

# Slide 2: Charging Window
create_slide(
    slide_num=2,
    title="8-Hour BESS Charging Window Availability",
    main_val="62% VS 28-29% OF DAYS",
    subtext_lines=[
        "SA1 & VIC1 meet requirements on ~62% of days.",
        "NSW1 & QLD1 meet requirements on only ~28-29% of days.",
        "Long-duration storage (LDES) faces steep charging constraints."
    ]
)

# Slide 3: Cycling Decline
create_slide(
    slide_num=3,
    title="Fleet Monthly Average Cycling Trend",
    main_val="-14% YEAR-ON-YEAR",
    subtext_lines=[
        "June 2025 vs June 2026: 1.06 -> 0.91 EFC/day per unit.",
        "Observed alongside fleet capacity growth and weather-driven",
        "spread compression. Seasonality controlled, cause not isolated."
    ]
)

# Slide 4: Verification Method
create_slide(
    slide_num=4,
    title="The VolMax Method",
    main_val=None,
    subtext_lines=[
        "Every number can be reproduced from the linked repository.",
        "A public changelog documents the lifecycle of the Note."
    ],
    list_items=[
        "[x] Frozen Parameters committed before run",
        "[x] Source AEMO SCADA & pricing data hashed",
        "[x] Complete open-source reproduction code",
        "[x] Public dated version changelog"
      ]
)

print("Carousel slides generated successfully.")
