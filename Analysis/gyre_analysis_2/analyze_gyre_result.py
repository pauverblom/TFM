import pygyre as pg
import matplotlib.pyplot as plt
import os
import numpy as np
import mesa_reader as mr
import shutil

mass_compare = 1.84

dir_bs = '/home/pauver/repos/pauverblom/TFM/MESA/evolve_created_blue_straggler'
dir_mass_compare = f'/home/pauver/repos/pauverblom/TFM/MESA/mass_grid/mass_{mass_compare}'

out_dir = f'comp_mass_{mass_compare}'

if os.path.exists(out_dir):
    shutil.rmtree(out_dir)
os.makedirs(out_dir, exist_ok=True)

print("Loading HR tracks and profiles index...")
# Load MESA history and profiles to dynamically access exact HR track data points
hist_bs = mr.MesaData(f'{dir_bs}/LOGS/history.data')
idx_bs = mr.MesaProfileIndex(f'{dir_bs}/LOGS/profiles.index')

hist_compare = mr.MesaData(f'{dir_mass_compare}/LOGS/history.data')
idx_compare = mr.MesaProfileIndex(f'{dir_mass_compare}/LOGS/profiles.index')

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

# Pre-calculate all HR points for blue straggler profiles
bs_hr_points = {}
for p_num in idx_bs.profile_numbers:
    teff, L = get_hr_point(hist_bs, idx_bs, p_num)
    if teff is not None and L is not None:
        bs_hr_points[p_num] = (teff, L)

# Dynamically map compare Msun profile index to the closest blue straggler profile in HR diagram
profile_pairs = []
for p_num_compare, m_num_compare in zip(idx_compare.profile_numbers, idx_compare.model_numbers):
    teff_compare, L_compare = get_hr_point(hist_compare, idx_compare, p_num_compare)
    if teff_compare is None or L_compare is None:
        continue
        
    row_compare = np.argmin(np.abs(hist_compare.model_number - m_num_compare))
    h_pct = round(hist_compare.center_h1[row_compare] * 100.0, 1)
    
    closest_p_bs = None
    min_dist = float('inf')
    for p_bs, (teff_bs, L_bs) in bs_hr_points.items():
        dist = np.sqrt((teff_compare - teff_bs)**2 + (L_compare - L_bs)**2)
        if dist < min_dist:
            min_dist = dist
            closest_p_bs = p_bs
            
    if closest_p_bs is not None:
        profile_pairs.append((p_num_compare, closest_p_bs, h_pct))

print("Generating comparison plots with HR diagram insets...")

# Generate a separate figure for each hydrogen fraction
for p_num_compare, p_num_bs, h_pct in profile_pairs:
    file_bs = f"{dir_bs}/gyre_outputs/profile{p_num_bs}.data/summary.h5"
    file_compare = f"{dir_mass_compare}/gyre_outputs/profile{p_num_compare}.data/summary.h5"
    
    if not (os.path.exists(file_bs) and os.path.exists(file_compare)):
        print(f"Skipping profiles {mass_compare}M={p_num_compare}, BS={p_num_bs} (H={h_pct}%) as outputs are missing.")
        continue
    
    try:
        s_bs = pg.read_output(file_bs)
        sg_bs = s_bs.group_by('l')
        
        s_compare = pg.read_output(file_compare)
        sg_compare = s_compare.group_by('l')
    except Exception as e:
        print(f"Error reading files for profiles {mass_compare}M={p_num_compare}, BS={p_num_bs}: {e}")
        continue
        
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    # Share y-axis for top row only (frequency vs n_pg plots)
    for ax in axes[0, 1:]:
        ax.sharey(axes[0, 0])
    
    # Distinct styling for the two stars
    color_bs = '#3498db' # Vivid blue
    color_compare = '#e74c3c' # Crimson red
    
    # Colors and markers per harmonic degree for échelle diagrams
    l_colors = {0: '#1abc9c', 1: '#e74c3c', 2: '#9b59b6'}
    l_markers = {0: 'o', 1: 's', 2: '^'}
    l_labels = {0: '$l=0$', 1: '$l=1$', 2: '$l=2$'}
    
    # Calculate large separation (dnu) from l=0 p-modes
    def get_dnu(sg):
        if not hasattr(sg, 'groups'): return None
        for g in sg.groups:
            if len(g['l']) > 0 and g['l'][0] == 0:
                p_modes = [f.real for n, f in zip(g['n_pg'], g['freq']) if n > 0]
                if len(p_modes) > 1:
                    return float(np.median(np.diff(np.sort(p_modes))))
        return None

    dnu_bs = get_dnu(sg_bs)
    dnu_compare = get_dnu(sg_compare)
    print(f"Calculated large separations: BS = {dnu_bs if dnu_bs is None else round(dnu_bs, 3)}, Compare = {dnu_compare if dnu_compare is None else round(dnu_compare, 3)}")
    
    # Collect groups by l value for each star
    groups_bs = {}
    groups_compare = {}
    if hasattr(sg_bs, 'groups'):
        for g in sg_bs.groups:
            if len(g['l']) > 0:
                groups_bs[g['l'][0]] = g
    if hasattr(sg_compare, 'groups'):
        for g in sg_compare.groups:
            if len(g['l']) > 0:
                groups_compare[g['l'][0]] = g
    
    # ---- Top Row: Frequency vs Radial Order (per l) ----
    for l_idx, l_val in enumerate([0, 1, 2]):
        ax = axes[0, l_idx]
        
        group_bs = groups_bs.get(l_val)
        group_compare = groups_compare.get(l_val)
        
        # Plot Blue Straggler
        if group_bs is not None:
            ax.plot(group_bs['n_pg'], group_bs['freq'].real, 
                    color=color_bs, marker='^', markersize=7, linestyle='-', linewidth=2, alpha=0.9,
                    label='Blue Straggler' if l_idx == 0 else "")
                    
        # Plot Compare Star
        if group_compare is not None:
            ax.plot(group_compare['n_pg'], group_compare['freq'].real, 
                    color=color_compare, marker='o', markersize=6, linestyle='--', linewidth=2, alpha=0.8,
                    label=rf'{mass_compare} M$_\odot$ Star' if l_idx == 0 else "")
                    
        # Count modes in [-10, 10]
        expected_modes = {0: 10, 1: 20, 2: 21}[l_val]
        
        def count_modes(g):
            if g is None: return 0
            n_pg = np.array(g['n_pg'])
            return np.sum((n_pg >= -10) & (n_pg <= 10))
            
        modes_bs = count_modes(group_bs)
        modes_comp = count_modes(group_compare)
        
        if modes_bs != expected_modes:
            warn_msg = f"WARNING: BS (p_num={p_num_bs}) l={l_val} has {modes_bs} modes in [-10, 10] (expected {expected_modes})!"
            print(f"\033[91m{warn_msg}\033[0m")
            ax.text(0.5, 0.9, warn_msg, transform=ax.transAxes, color='red', weight='bold', ha='center', fontsize=10, bbox=dict(facecolor='white', alpha=0.8, edgecolor='red'))
            
        if modes_comp != expected_modes:
            warn_msg = f"WARNING: {mass_compare}M (p_num={p_num_compare}) l={l_val} has {modes_comp} modes in [-10, 10] (expected {expected_modes})!"
            print(f"\033[91m{warn_msg}\033[0m")
            ax.text(0.5, 0.8, warn_msg, transform=ax.transAxes, color='red', weight='bold', ha='center', fontsize=10, bbox=dict(facecolor='white', alpha=0.8, edgecolor='red'))

        ax.set_xlim(-10.5, 10.5)
        
        ax.set_title(f'Harmonic Degree $l = {l_val}$', fontsize=14, fontweight='bold', pad=12)
        ax.set_xlabel('Radial Order ($n_{pg}$)', fontsize=12)
        if l_idx == 0:
            ax.set_ylabel('Frequency $\\nu$ (cyc/day)', fontsize=12)
            ax.legend(fontsize=11, loc='best', framealpha=0.9)
            
        # Subtle aesthetic grid
        ax.grid(True, which='both', linestyle=':', color='gray', alpha=0.4)
        ax.tick_params(labelsize=10)
        ax.axvline(0, color='gray', linestyle=':', alpha=0.7, linewidth=1)
    
    # ---- Bottom Row: Frequency Differences + HR Diagram ----
    
    gs = axes[1, 0].get_gridspec()
    for ax in axes[1, :]:
        ax.remove()
        
    ax_diff = fig.add_subplot(gs[1, 0:2])
    ax_hr = fig.add_subplot(gs[1, 2])
    
    for l_val in [0, 1, 2]:
        group_bs = groups_bs.get(l_val)
        group_compare = groups_compare.get(l_val)
        
        if group_bs is not None and group_compare is not None:
            n_pg_bs = np.array(group_bs['n_pg'])
            freq_bs = np.array(group_bs['freq'].real)
            
            n_pg_comp = np.array(group_compare['n_pg'])
            freq_comp = np.array(group_compare['freq'].real)
            
            diffs = []
            n_pg_plot = []
            
            for i, n in enumerate(n_pg_comp):
                idx_match_bs = np.where(n_pg_bs == n)[0]
                if len(idx_match_bs) > 0:
                    f_comp = freq_comp[i]
                    f_bs = freq_bs[idx_match_bs[0]]
                    diffs.append(f_comp - f_bs)
                    n_pg_plot.append(n)
            
            if n_pg_plot:
                ax_diff.plot(n_pg_plot, diffs, color=l_colors[l_val], marker=l_markers[l_val],
                             markersize=7, linestyle='None', alpha=0.9,
                             label=l_labels[l_val])
                             
    ax_diff.set_title(rf'Frequency Differences ($\nu_{{{mass_compare} M_\odot}} - \nu_{{\rm BS}}$)', fontsize=13, fontweight='bold', pad=10)
    ax_diff.set_xlabel('Radial Order ($n_{pg}$)', fontsize=12)
    ax_diff.set_ylabel(r'$\Delta\nu$ (cyc/day)', fontsize=12)
    ax_diff.legend(fontsize=11, loc='best', framealpha=0.9)
    ax_diff.grid(True, which='both', linestyle=':', color='gray', alpha=0.4)
    ax_diff.tick_params(labelsize=10)
    ax_diff.axhline(0, color='black', linestyle='--', alpha=0.5, linewidth=1)
    ax_diff.set_xlim(-10.5, 10.5)
    
    # Bottom right: HR Diagram (full subplot)
    
    # Plot the full background HR tracks for both stars
    ax_hr.plot(hist_bs.log_Teff, hist_bs.log_L, color=color_bs, alpha=0.4, linewidth=1.5, zorder=1,
               label='Blue Straggler')
    ax_hr.plot(hist_compare.log_Teff, hist_compare.log_L, color=color_compare, alpha=0.4, linewidth=1.5, zorder=1,
               label=rf'{mass_compare} M$_\odot$ Star')
    
    # Retrieve the exact HR points using profiles.index -> model_number -> history.data
    teff_bs, L_bs = get_hr_point(hist_bs, idx_bs, p_num_bs)
    teff_compare, L_compare = get_hr_point(hist_compare, idx_compare, p_num_compare)
    
    # Scatter plot the exact points being compared with a prominent star marker
    if teff_bs is not None and L_bs is not None:
        ax_hr.scatter([teff_bs], [L_bs], color=color_bs, s=200, marker='*', zorder=3,
                      edgecolor='black', linewidth=0.5)
    if teff_compare is not None and L_compare is not None:
        ax_hr.scatter([teff_compare], [L_compare], color=color_compare, s=200, marker='*', zorder=3,
                      edgecolor='black', linewidth=0.5)
        
    # HR diagrams are always plotted with Temperature reversed!
    ax_hr.invert_xaxis()
    ax_hr.set_xlabel(r'$\log T_{\rm eff}$', fontsize=12)
    ax_hr.set_ylabel(r'$\log L/L_\odot$', fontsize=12)
    ax_hr.tick_params(labelsize=10)
    ax_hr.set_title('HR Diagram', fontsize=13, fontweight='bold', pad=10)
    ax_hr.legend(fontsize=10, loc='best', framealpha=0.9)
    ax_hr.grid(True, linestyle=':', alpha=0.3)
        
    plt.suptitle(rf'Frequency Comparison: Blue Straggler vs {mass_compare} M$_\odot$ Star' + '\n' + f'Central Hydrogen: ~{h_pct}%', 
                 fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    # Save the figure as a separate PNG
   
    out_filename = f'{out_dir}/gyre_comparison_comp_mass_{mass_compare}_pcomp_{p_num_compare}_pbs_{p_num_bs}_H_{h_pct}.png'
    plt.savefig(out_filename, dpi=300, bbox_inches='tight')
    plt.close() 
    print(f"Saved {out_filename}")

print("All plots generated successfully!")