import pygyre as pg
import matplotlib.pyplot as plt
import os
import numpy as np
import mesa_reader as mr

dir_bs = '/home/pauver/TFM/MESA/evolve_created_blue_straggler_only_MS'
dir_18 = '/home/pauver/TFM/MESA/evolve_1.8_mass_star_only_MS'

print("Loading HR tracks and profiles index...")
# Load MESA history and profiles to dynamically access exact HR track data points
hist_bs = mr.MesaData(f'{dir_bs}/LOGS/history.data')
idx_bs = mr.MesaProfileIndex(f'{dir_bs}/LOGS/profiles.index')

hist_18 = mr.MesaData(f'{dir_18}/LOGS/history.data')
idx_18 = mr.MesaProfileIndex(f'{dir_18}/LOGS/profiles.index')

# Dynamically map profile index to hydrogen mass fraction using profiles.index
profile_mapping = {}
for p_num, m_num in zip(idx_bs.profile_numbers, idx_bs.model_numbers):
    # Find the closest matching model in history (in case of slight logging misalignments)
    row = np.argmin(np.abs(hist_bs.model_number - m_num))
    h_pct = hist_bs.center_h1[row] * 100.0
    profile_mapping[p_num] = round(h_pct, 1)

def get_hr_point(hist, idx, p_num):
    """Retrieve exactly matched log_Teff and log_L for a given profile number"""
    model_numbers = idx.model_numbers
    profile_numbers = idx.profile_numbers
    
    if p_num not in profile_numbers:
        return None, None
        
    m_num = model_numbers[list(profile_numbers).index(p_num)]
    
    # Safely find the closest row in history 
    row = np.argmin(np.abs(hist.model_number - m_num))
    return hist.log_Teff[row], hist.log_L[row]

print("Generating comparison plots with HR diagram insets...")

# Generate a separate figure for each hydrogen fraction
for p_num, h_pct in profile_mapping.items():
    file_bs = f"{dir_bs}/gyre_outputs/profile{p_num}.data/summary.h5"
    file_18 = f"{dir_18}/gyre_outputs/profile{p_num}.data/summary.h5"
    
    if not (os.path.exists(file_bs) and os.path.exists(file_18)):
        print(f"Skipping profile {p_num} (H={h_pct}%) as outputs are missing.")
        continue
    
    try:
        s_bs = pg.read_output(file_bs)
        sg_bs = s_bs.group_by('l')
        
        s_18 = pg.read_output(file_18)
        sg_18 = s_18.group_by('l')
    except Exception as e:
        print(f"Error reading files for profile {p_num}: {e}")
        continue
        
    fig, axes = plt.subplots(1, 2, figsize=(12, 6), sharey=True)
    
    # Distinct styling for the two stars
    color_bs = '#3498db' # Vivid blue
    color_18 = '#e74c3c' # Crimson red
    
    for l_idx, l_val in enumerate([1, 2]):
        ax = axes[l_idx]
        
        # Plot Blue Straggler
        group_bs = None
        if hasattr(sg_bs, 'groups'):
            for g in sg_bs.groups:
                if len(g['l']) > 0 and g['l'][0] == l_val:
                    group_bs = g
                    break
        if group_bs is not None:
            ax.plot(group_bs['n_pg'], group_bs['freq'].real, 
                    color=color_bs, marker='^', markersize=7, linestyle='-', linewidth=2, alpha=0.9,
                    label='Blue Straggler' if l_idx == 0 else "")
                    
        # Plot 1.8 Mass Star
        group_18 = None
        if hasattr(sg_18, 'groups'):
            for g in sg_18.groups:
                if len(g['l']) > 0 and g['l'][0] == l_val:
                    group_18 = g
                    break
        if group_18 is not None:
            ax.plot(group_18['n_pg'], group_18['freq'].real, 
                    color=color_18, marker='o', markersize=6, linestyle='--', linewidth=2, alpha=0.8,
                    label='1.8 M$_\odot$ Star' if l_idx == 0 else "")
        
        ax.set_title(f'Harmonic Degree $l = {l_val}$', fontsize=14, fontweight='bold', pad=12)
        ax.set_xlabel('Radial Order ($n_{pg}$)', fontsize=12)
        if l_idx == 0:
            ax.set_ylabel('Frequency $\\nu$ (cyc/day)', fontsize=12)
            ax.legend(fontsize=11, loc='best', framealpha=0.9)
            
        # Subtle aesthetic grid
        ax.grid(True, which='both', linestyle=':', color='gray', alpha=0.4)
        ax.tick_params(labelsize=10)
        ax.axvline(0, color='gray', linestyle=':', alpha=0.7, linewidth=1)
        
        # Add HR Diagram Inset on the second subplot (l=2)
        if l_val == 2:
            # Position the inset in the top left corner of the l=2 plot
            axins = ax.inset_axes([0.1, 0.55, 0.35, 0.4])
            
            # Plot the full background HR tracks for both stars
            axins.plot(hist_bs.log_Teff, hist_bs.log_L, color=color_bs, alpha=0.4, linewidth=1.5, zorder=1)
            axins.plot(hist_18.log_Teff, hist_18.log_L, color=color_18, alpha=0.4, linewidth=1.5, zorder=1)
            
            # Retrieve the exact HR points using profiles.index -> model_number -> history.data
            teff_bs, L_bs = get_hr_point(hist_bs, idx_bs, p_num)
            teff_18, L_18 = get_hr_point(hist_18, idx_18, p_num)
            
            # Scatter plot the exact points being compared with a prominent star marker
            if teff_bs is not None and L_bs is not None:
                axins.scatter([teff_bs], [L_bs], color=color_bs, s=120, marker='*', zorder=3, edgecolor='black', linewidth=0.5)
            if teff_18 is not None and L_18 is not None:
                axins.scatter([teff_18], [L_18], color=color_18, s=120, marker='*', zorder=3, edgecolor='black', linewidth=0.5)
                
            # HR diagrams are always plotted with Temperature reversed!
            axins.invert_xaxis()
            
            # Format the inset
            axins.set_xlabel(r'$\log T_{\rm eff}$', fontsize=8, labelpad=2)
            axins.set_ylabel(r'$\log L/L_\odot$', fontsize=8, labelpad=2)
            axins.tick_params(labelsize=7)
            axins.set_title('HR Track', fontsize=10, pad=4, fontweight='bold')
            axins.grid(True, linestyle=':', alpha=0.3)
            
    plt.suptitle(f'Frequency Comparison: Blue Straggler vs 1.8 M$_\odot$ Star\nCentral Hydrogen: ~{h_pct}%', 
                 fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    # Save the figure as a separate PNG
    out_filename = f'gyre_comparison_H_{h_pct}.png'
    plt.savefig(out_filename, dpi=300, bbox_inches='tight')
    plt.close() 
    print(f"Saved {out_filename}")

print("All plots generated successfully!")