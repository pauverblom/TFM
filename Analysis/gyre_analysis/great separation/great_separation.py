import pygyre as pg
import matplotlib.pyplot as plt
import os
import numpy as np
import mesa_reader as mr
import shutil

mass_compare = 1.838

#dir_bs = '/Users/pauverdeguer/TFM/MESA/evolve_created_blue_straggler'
#dir_mass_compare = f'/Users/pauverdeguer/TFM/MESA/mass_grid/mass_{mass_compare}'

dir_bs = '/home/pauver/repos/pauverblom/TFM/MESA/evolve_created_blue_straggler'
#dir_mass_compare = f'/home/pauver/repos/pauverblom/TFM/MESA/mass_grid/mass_{mass_compare}'
dir_mass_compare = f'/home/pauver/repos/pauverblom/TFM/MESA/finer_mass_grid/mass_{mass_compare}'

out_dir = f'great_separations_comp_mass_{mass_compare}'

if os.path.exists(out_dir):
    shutil.rmtree(out_dir)
os.makedirs(out_dir, exist_ok=True)

print("Cargando trazas HR y el índice de perfiles...")
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

print("Generando gráficos comparativos con diagramas HR insertados...")

# Generate a separate figure for each hydrogen fraction
for p_num_compare, p_num_bs, h_pct in profile_pairs:
    file_bs = f"{dir_bs}/gyre_outputs/profile{p_num_bs}.data/summary.h5"
    file_compare = f"{dir_mass_compare}/gyre_outputs/profile{p_num_compare}.data/summary.h5"
    
    if not (os.path.exists(file_bs) and os.path.exists(file_compare)):
        print(f"Saltando perfiles {mass_compare}M={p_num_compare}, BS={p_num_bs} (H={h_pct}%) ya que faltan los archivos de salida.")
        continue
    
    try:
        s_bs = pg.read_output(file_bs)
        sg_bs = s_bs.group_by('l')
        
        s_compare = pg.read_output(file_compare)
        sg_compare = s_compare.group_by('l')
    except Exception as e:
        print(f"Error leyendo archivos para los perfiles {mass_compare}M={p_num_compare}, BS={p_num_bs}: {e}")
        continue
        
    fig = plt.figure(figsize=(10, 10.5))
    gs = fig.add_gridspec(2, 2)
    
    ax_0 = fig.add_subplot(gs[0, 0])
    ax_1 = fig.add_subplot(gs[0, 1])
    ax_2 = fig.add_subplot(gs[1, 0])
    axes = [ax_0, ax_1, ax_2]
    
    ax_hr = fig.add_subplot(gs[1, 1])
    
    # Distinct styling for the two stars
    color_bs = '#3498db' # Vivid blue
    color_compare = '#e74c3c' # Crimson red
    
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
    
    # ---- Great Separation vs Radial Order (per l) ----
    for l_idx, l_val in enumerate([0, 1, 2]):
        ax = axes[l_idx]
        
        group_bs = groups_bs.get(l_val)
        group_compare = groups_compare.get(l_val)
        
        # Count modes in [-10, 10] for warning (optional but kept for parity)
        expected_modes = {0: 10, 1: 20, 2: 21}[l_val]
        def count_modes(g):
            if g is None: return 0
            n_pg = np.array(g['n_pg'])
            return np.sum((n_pg >= -10) & (n_pg <= 10))
            
        modes_bs = count_modes(group_bs)
        modes_comp = count_modes(group_compare)
        
        if modes_bs != expected_modes:
            warn_msg = f"AVISO: ¡Rezagada Azul (p_num={p_num_bs}) l={l_val} tiene {modes_bs} modos en [-10, 10]!"
            ax.text(0.5, 0.9, warn_msg, transform=ax.transAxes, color='red', ha='center', fontsize=9, bbox=dict(facecolor='white', alpha=0.8, edgecolor='red'))
            
        if modes_comp != expected_modes:
            warn_msg = f"AVISO: ¡{mass_compare}M (p_num={p_num_compare}) l={l_val} tiene {modes_comp} modos en [-10, 10]!"
            ax.text(0.5, 0.8, warn_msg, transform=ax.transAxes, color='red', ha='center', fontsize=9, bbox=dict(facecolor='white', alpha=0.8, edgecolor='red'))

        def plot_separation(ax, group, color, marker, label, linestyle):
            if group is None: return []
            n_pg = np.array(group['n_pg'])
            freq = np.array(group['freq'].real)
            
            sort_idx = np.argsort(n_pg)
            n_pg = n_pg[sort_idx]
            freq = freq[sort_idx]
            
            n_plot = []
            dnu = []
            valid_dnu = []
            for i in range(1, len(n_pg)):
                if n_pg[i] == n_pg[i-1] + 1:
                    n_plot.append(float(n_pg[i] + 9))
                    val = float(freq[i] - freq[i-1])
                    dnu.append(val)
                    valid_dnu.append(val)
                elif len(n_plot) > 0 and not np.isnan(n_plot[-1]):
                    n_plot.append(np.nan)
                    dnu.append(np.nan)
            
            if valid_dnu:
                ax.plot(n_plot, dnu, color=color, marker=marker, markersize=7, 
                        linestyle=linestyle, linewidth=2, alpha=0.6, label=label)
            return valid_dnu

        dnu_bs = plot_separation(ax, group_bs, color_bs, '^', 'Blue  Straggler' if l_idx == 0 else "", '-')
        dnu_comp = plot_separation(ax, group_compare, color_compare, 'o', rf'Estrella de {mass_compare} M$_\odot$' if l_idx == 0 else "", '--')
        
        ax.set_xlim(-0.5, 19.5)
        ax.set_xlabel('Índice de gran separación ($k$)', fontsize=12)
        ax.set_xticks(range(0, 20, 2))
        
        all_dnus = dnu_bs + dnu_comp
        if all_dnus:
            min_dnu = min(all_dnus)
            ax.set_ylim(bottom=min_dnu - 0.1)
            
        ax.set_ylabel(r'Gran separación $\Delta\nu$ (ciclos/día)', fontsize=12)
        
        if l_idx == 0:
            ax.legend(fontsize=11, loc='best', framealpha=0.9)
            
        ax.grid(True, which='both', linestyle=':', color='gray', alpha=0.4)
        ax.tick_params(labelsize=10)
        ax.axvline(0, color='gray', linestyle=':', alpha=0.7, linewidth=1)
        ax.set_title(rf'Gran separación para $l = {l_val}$', fontsize=13, pad=10)
        
    # ---- HR Diagram ----
    ax_hr.plot(hist_bs.log_Teff, hist_bs.log_L, color=color_bs, alpha=0.4, linewidth=1.5, zorder=1,
               label='Blue Straggler')
    ax_hr.plot(hist_compare.log_Teff, hist_compare.log_L, color=color_compare, alpha=0.4, linewidth=1.5, zorder=1,
               label=rf'Estrella de {mass_compare} M$_\odot$')
    
    teff_bs, L_bs = get_hr_point(hist_bs, idx_bs, p_num_bs)
    teff_compare, L_compare = get_hr_point(hist_compare, idx_compare, p_num_compare)
    
    if teff_bs is not None and L_bs is not None:
        ax_hr.scatter([teff_bs], [L_bs], color=color_bs, s=200, marker='*', zorder=3,
                      edgecolor='black', linewidth=0.5)
    if teff_compare is not None and L_compare is not None:
        ax_hr.scatter([teff_compare], [L_compare], color=color_compare, s=200, marker='*', zorder=3,
                      edgecolor='black', linewidth=0.5)
        
    ax_hr.invert_xaxis()
    ax_hr.set_xlabel(r'$\log T_{\rm eff}$', fontsize=12)
    ax_hr.set_ylabel(r'$\log L/L_\odot$', fontsize=12)
    ax_hr.tick_params(labelsize=10)
    ax_hr.set_title('Diagrama HR', fontsize=13, pad=10)
    ax_hr.legend(fontsize=11, loc='best', framealpha=0.9)
    ax_hr.grid(True, linestyle=':', alpha=0.3)
        
    plt.suptitle(rf'Gran separación: Blue Straggler vs Estrella de {mass_compare} M$_\odot$', fontsize=15, y=1.0)
    plt.tight_layout()
    
    out_filename = f'{out_dir}/great_separation_mass_{mass_compare}_pcomp_{p_num_compare}_pbs_{p_num_bs}_H_{h_pct}.png'
    plt.savefig(out_filename, dpi=300, bbox_inches='tight')
    plt.close(fig) 
    print(f"Guardado {out_filename}")

print("¡Todos los gráficos se generaron con éxito!")
