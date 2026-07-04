import pygyre as pg
import matplotlib.pyplot as plt
import os
import numpy as np
import mesa_reader as mr
import shutil

mass_1 = 1.832
mass_2 = 1.834

dir_1 = f'/home/pauver/repos/pauverblom/TFM/MESA/finer_mass_grid/mass_{mass_1}'
dir_2 = f'/home/pauver/repos/pauverblom/TFM/MESA/finer_mass_grid/mass_{mass_2}'

out_dir = f'great_separations_comp_{mass_1}_{mass_2}'

if os.path.exists(out_dir):
    shutil.rmtree(out_dir)
os.makedirs(out_dir, exist_ok=True)

print("Cargando trazas HR y el índice de perfiles...")
hist_1 = mr.MesaData(f'{dir_1}/LOGS/history.data')
idx_1 = mr.MesaProfileIndex(f'{dir_1}/LOGS/profiles.index')

hist_2 = mr.MesaData(f'{dir_2}/LOGS/history.data')
idx_2 = mr.MesaProfileIndex(f'{dir_2}/LOGS/profiles.index')

def get_hr_point(hist, idx, p_num):
    """Retrieve exactly matched log_Teff and log_L for a given profile number"""
    model_numbers = idx.model_numbers
    profile_numbers = idx.profile_numbers
    
    if p_num not in profile_numbers:
        return None, None
        
    m_num = model_numbers[list(profile_numbers).index(p_num)]
    
    row = np.argmin(np.abs(hist.model_number - m_num))
    return hist.log_Teff[row], hist.log_L[row]

# Pre-calculate all HR points for star 1 profiles
hr_points_1 = {}
for p_num in idx_1.profile_numbers:
    teff, L = get_hr_point(hist_1, idx_1, p_num)
    if teff is not None and L is not None:
        hr_points_1[p_num] = (teff, L)

# Dynamically map compare star 2 profile index to the closest star 1 profile in HR diagram
profile_pairs = []
for p_num_2, m_num_2 in zip(idx_2.profile_numbers, idx_2.model_numbers):
    teff_2, L_2 = get_hr_point(hist_2, idx_2, p_num_2)
    if teff_2 is None or L_2 is None:
        continue
        
    row_2 = np.argmin(np.abs(hist_2.model_number - m_num_2))
    h_pct = round(hist_2.center_h1[row_2] * 100.0, 1)
    
    closest_p_1 = None
    min_dist = float('inf')
    for p_1, (teff_1, L_1) in hr_points_1.items():
        dist = np.sqrt((teff_2 - teff_1)**2 + (L_2 - L_1)**2)
        if dist < min_dist:
            min_dist = dist
            closest_p_1 = p_1
            
    if closest_p_1 is not None:
        profile_pairs.append((closest_p_1, p_num_2, h_pct))

print("Generando gráficos comparativos con diagramas HR insertados...")

for p_num_1, p_num_2, h_pct in profile_pairs:
    file_1 = f"{dir_1}/gyre_outputs/profile{p_num_1}.data/summary.h5"
    file_2 = f"{dir_2}/gyre_outputs/profile{p_num_2}.data/summary.h5"
    
    if not (os.path.exists(file_1) and os.path.exists(file_2)):
        print(f"Saltando perfiles 1={p_num_1}, 2={p_num_2} (H={h_pct}%) ya que faltan los archivos de salida.")
        continue
    
    try:
        s_1 = pg.read_output(file_1)
        sg_1 = s_1.group_by('l')
        
        s_2 = pg.read_output(file_2)
        sg_2 = s_2.group_by('l')
    except Exception as e:
        print(f"Error leyendo archivos para los perfiles 1={p_num_1}, 2={p_num_2}: {e}")
        continue
        
    fig = plt.figure(figsize=(10, 10.5))
    gs = fig.add_gridspec(2, 2)
    
    ax_0 = fig.add_subplot(gs[0, 0])
    ax_1 = fig.add_subplot(gs[0, 1])
    ax_2 = fig.add_subplot(gs[1, 0])
    axes = [ax_0, ax_1, ax_2]
    
    ax_hr = fig.add_subplot(gs[1, 1])
    
    color_1 = '#ab34eb' 
    color_2 = '#34ebd5'
    
    groups_1 = {}
    groups_2 = {}
    if hasattr(sg_1, 'groups'):
        for g in sg_1.groups:
            if len(g['l']) > 0:
                groups_1[g['l'][0]] = g
    if hasattr(sg_2, 'groups'):
        for g in sg_2.groups:
            if len(g['l']) > 0:
                groups_2[g['l'][0]] = g
    
    for l_idx, l_val in enumerate([0, 1, 2]):
        ax = axes[l_idx]
        
        group_1 = groups_1.get(l_val)
        group_2 = groups_2.get(l_val)
        
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

        dnu_1 = plot_separation(ax, group_1, color_1, '^', rf'Estrella de {mass_1} M$_\odot$' if l_idx == 0 else "", '-')
        dnu_2 = plot_separation(ax, group_2, color_2, 'o', rf'Estrella de {mass_2} M$_\odot$' if l_idx == 0 else "", '--')
        
        ax.set_xlim(-0.5, 19.5)
        ax.set_xlabel('Índice de gran separación ($k$)', fontsize=12)
        ax.set_xticks(range(0, 20, 2))
        
        all_dnus = dnu_1 + dnu_2
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
    ax_hr.plot(hist_1.log_Teff, hist_1.log_L, color=color_1, alpha=0.4, linewidth=1.5, zorder=1,
               label=rf'Estrella de {mass_1} M$_\odot$')
    ax_hr.plot(hist_2.log_Teff, hist_2.log_L, color=color_2, alpha=0.4, linewidth=1.5, zorder=1,
               label=rf'Estrella de {mass_2} M$_\odot$')
    
    teff_1, L_1 = get_hr_point(hist_1, idx_1, p_num_1)
    teff_2, L_2 = get_hr_point(hist_2, idx_2, p_num_2)
    
    if teff_1 is not None and L_1 is not None:
        ax_hr.scatter([teff_1], [L_1], color=color_1, s=200, marker='*', zorder=3,
                      edgecolor='black', linewidth=0.5)
    if teff_2 is not None and L_2 is not None:
        ax_hr.scatter([teff_2], [L_2], color=color_2, s=200, marker='*', zorder=3,
                      edgecolor='black', linewidth=0.5)
        
    ax_hr.invert_xaxis()
    ax_hr.set_xlabel(r'$\log T_{\rm eff}$', fontsize=12)
    ax_hr.set_ylabel(r'$\log L/L_\odot$', fontsize=12)
    ax_hr.tick_params(labelsize=10)
    ax_hr.set_title('Diagrama HR', fontsize=13, pad=10)
    ax_hr.legend(fontsize=11, loc='best', framealpha=0.9)
    ax_hr.grid(True, linestyle=':', alpha=0.3)
        
    plt.suptitle(rf'Gran separación: {mass_1} M$_\odot$ vs {mass_2} M$_\odot$', fontsize=15, y=1.0)
    plt.tight_layout()
    
    out_filename = f'{out_dir}/great_separation_{mass_1}_vs_{mass_2}_p1_{p_num_1}_p2_{p_num_2}_H_{h_pct}.png'
    plt.savefig(out_filename, dpi=300, bbox_inches='tight')
    plt.close(fig) 
    print(f"Guardado {out_filename}")

print("¡Todos los gráficos se generaron con éxito!")
