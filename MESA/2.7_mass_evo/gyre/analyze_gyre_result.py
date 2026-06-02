import pygyre as pg
import matplotlib.pyplot as plt
import numpy as np

# Read the outputs for both stars
s_regular_star = pg.read_output('/Users/pauverdeguer/TFM/MESA/2.7_mass_evo/gyre/summary.h5')
s_blue_straggler = pg.read_output('/Users/pauverdeguer/TFM/MESA/blue_straggler_gyre/gyre/summary.h5')

# Group data by harmonic degree (l)
sg_regular_star = s_regular_star.group_by('l')
sg_blue_straggler = s_blue_straggler.group_by('l')

# Create a figure with three subplots comparing each harmonic degree side by side
fig, axes = plt.subplots(1, 3, figsize=(15, 6), sharey=True)

# Curated high-contrast aesthetic colors
color_regular = '#E05D5D'          # Deep slate blue
color_blue_straggler = "#7AABFF"   # Soft sunset coral

# Iterate over each harmonic degree group (l = 0, 1, 2)
for i, l_val in enumerate([0, 1, 2]):
    ax = axes[i]
    
    # Regular Star data
    reg_group = sg_regular_star.groups[i]
    reg_n = reg_group['n_pg']
    reg_freq = reg_group['freq'].real
    
    # Blue Straggler data
    bs_group = sg_blue_straggler.groups[i]
    bs_n = bs_group['n_pg']
    bs_freq = bs_group['freq'].real
    
    # Plot Regular Star
    ax.plot(reg_n, reg_freq, 
            label='Regular Star', 
            color=color_regular, 
            marker='o', 
            markersize=6, 
            linestyle='-', 
            linewidth=1.8, 
            alpha=0.9)
    
    # Plot Blue Straggler
    ax.plot(bs_n, bs_freq, 
            label='Blue Straggler', 
            color=color_blue_straggler, 
            marker='^', 
            markersize=7, 
            linestyle='--', 
            linewidth=1.8, 
            alpha=0.9)
    
    # Customize subplot presentation
    ax.set_title(f'Harmonic Degree $l = {l_val}$', fontsize=14, fontweight='bold', pad=12)
    ax.set_xlabel('Radial Order ($n_{pg}$)', fontsize=12)
    if i == 0:
        ax.set_ylabel('Frequency $\\nu$ (cyc/day)', fontsize=12)
    
    # Subtle grid styling
    ax.grid(True, which='both', linestyle=':', color='gray', alpha=0.5)
    ax.tick_params(labelsize=10)
    
    # Draw vertical reference line at radial order 0 for gravity vs pressure modes
    if l_val > 0:
        ax.axvline(0, color='gray', linestyle=':', alpha=0.7, linewidth=1)
        
    ax.legend(fontsize=10, loc='best')

# Figure-level titles and layout adjustments
plt.suptitle('GYRE Frequency Spectrum Comparison: Regular Star vs. Blue Straggler', fontsize=16, fontweight='bold', y=0.98)
plt.tight_layout()

# Save the figure and display it
plt.savefig('gyre_comparison.png', dpi=300)
plt.show()
