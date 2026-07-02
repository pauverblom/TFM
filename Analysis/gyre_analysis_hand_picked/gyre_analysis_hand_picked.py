import pygyre as pg
import matplotlib.pyplot as plt
import os
import numpy as np
import mesa_reader as mr
import shutil

dir_bs = '/home/pauver/repos/pauverblom/TFM/MESA/evolve_created_blue_straggler'

out_dir = 'gyre_analysis_hand_picked'
out_dir_tex = '/home/pauver/repos/pauverblom/TFM/TeX/Imagenes/gyre_analysis_hand_picked'

if os.path.exists(out_dir):
    shutil.rmtree(out_dir)
os.makedirs(out_dir, exist_ok=True)

if os.path.exists(out_dir_tex):
    shutil.rmtree(out_dir_tex)
os.makedirs(out_dir_tex, exist_ok=True)

hand_picked_pairs = [
    (1.84, 4, 5, 69.7),
    (1.84, 16, 29, 46.0),
    (1.836, 20, 40, 35.7),
    (1.834, 24, 51, 25.6),
    (1.832, 28, 63, 14.8),
    (1.79, 38, 72, 0.8),
    (1.79, 45, 92, 0.1)
]

def get_dir_compare(mass):
    path_finer = f'/home/pauver/repos/pauverblom/TFM/MESA/finer_mass_grid/mass_{mass}'
    path_coarse = f'/home/pauver/repos/pauverblom/TFM/MESA/mass_grid/mass_{mass}'
    if os.path.exists(path_finer):
        return path_finer
    return path_coarse

print("Cargando traza HR y el índice de perfiles de la Blue Straggler...")
hist_bs = mr.MesaData(f'{dir_bs}/LOGS/history.data')
idx_bs = mr.MesaProfileIndex(f'{dir_bs}/LOGS/profiles.index')

def get_hr_point(hist, idx, p_num):
    """Retrieve exactly matched log_Teff and log_L for a given profile number"""
    model_numbers = idx.model_numbers
    profile_numbers = idx.profile_numbers
    
    if p_num not in profile_numbers:
        return None, None
        
    m_num = model_numbers[list(profile_numbers).index(p_num)]
    
    row = np.argmin(np.abs(hist.model_number - m_num))
    return hist.log_Teff[row], hist.log_L[row]

# Cache to avoid reloading the same comparison mass
hist_compare_cache = {}
idx_compare_cache = {}

print("Generando gráficos comparativos (3 columnas)...")

global_hr_points = []

# Generate colormap colors
colors = [plt.cm.gist_heat(0.8 * i / (len(hand_picked_pairs) - 1)) for i in range(len(hand_picked_pairs))]

for idx_pair, (mass_compare, p_num_compare, p_num_bs, h_pct) in enumerate(hand_picked_pairs):
    dir_mass_compare = get_dir_compare(mass_compare)
    
    if mass_compare not in hist_compare_cache:
        hist_compare_cache[mass_compare] = mr.MesaData(f'{dir_mass_compare}/LOGS/history.data')
        idx_compare_cache[mass_compare] = mr.MesaProfileIndex(f'{dir_mass_compare}/LOGS/profiles.index')
        
    hist_compare = hist_compare_cache[mass_compare]
    idx_compare = idx_compare_cache[mass_compare]

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
        
    # Guardamos los puntos para el diagrama HR global
    teff_bs, L_bs = get_hr_point(hist_bs, idx_bs, p_num_bs)
    teff_compare, L_compare = get_hr_point(hist_compare, idx_compare, p_num_compare)
    if teff_bs is not None and teff_compare is not None:
        global_hr_points.append((idx_pair + 1, teff_bs, L_bs, teff_compare, L_compare, mass_compare))

    fig, axes = plt.subplots(1, 3, figsize=(9.5, 2.8))
    
    color_val = colors[idx_pair]
    
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
    
    all_diffs_in_fig = []

    for l_idx, l_val in enumerate([0, 1, 2]):
        ax = axes[l_idx]
        
        group_bs = groups_bs.get(l_val)
        group_compare = groups_compare.get(l_val)
        
        expected_modes = {0: 10, 1: 20, 2: 21}[l_val]
        def count_modes(g):
            if g is None: return 0
            n_pg = np.array(g['n_pg'])
            return np.sum((n_pg >= -10) & (n_pg <= 10))
            
        modes_bs = count_modes(group_bs)
        modes_comp = count_modes(group_compare)
        
        if modes_bs != expected_modes:
            warn_msg = f"AVISO: BS l={l_val} tiene {modes_bs} modos!"
            ax.text(0.5, 0.9, warn_msg, transform=ax.transAxes, color='red', ha='center', fontsize=8, bbox=dict(facecolor='white', alpha=0.8, edgecolor='red'))
            
        if modes_comp != expected_modes:
            warn_msg = f"AVISO: {mass_compare}M l={l_val} tiene {modes_comp} modos!"
            ax.text(0.5, 0.8, warn_msg, transform=ax.transAxes, color='red', ha='center', fontsize=8, bbox=dict(facecolor='white', alpha=0.8, edgecolor='red'))

        def plot_differences(ax, group_bs, group_compare, color, marker, label):
            if group_bs is None or group_compare is None: return []
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
                ax.plot(n_pg_plot, diffs, color=color, marker=marker, markersize=5, 
                        linestyle='None', alpha=0.8, label=label)
            return diffs

        diffs = plot_differences(ax, group_bs, group_compare, color_val, 'o', rf'$\nu_{{{mass_compare} M_\odot}} - \nu_{{\rm BS}}$')
        
        if diffs:
            all_diffs_in_fig.extend(diffs)
            
        ax.set_xlim(-10.5, 10.5)
        ax.set_xticks(range(-10, 11, 4))
        
        if l_idx == 0:
            ax.set_ylabel(r'$\nu_{\rm comp} - \nu_{\rm BS}$ (ciclos/día)', fontsize=10)
        
        if l_idx == 0:
            ax.legend(fontsize=9, loc='upper left', framealpha=0.9)
            
        ax.grid(True, which='both', linestyle=':', color='gray', alpha=0.4)
        ax.tick_params(labelsize=9)
        ax.axvline(0, color='gray', linestyle=':', alpha=0.7, linewidth=1)
        ax.axhline(0, color='black', linestyle='--', alpha=0.5, linewidth=1)
        
        if idx_pair == 0:
            ax.set_title(rf'$l = {l_val}$', fontsize=11, pad=5)
        else:
            ax.set_title(' ', fontsize=11, pad=5)
            
    # Set symmetric y-limits for this row based on all differences
    if all_diffs_in_fig:
        max_abs = max([abs(d) for d in all_diffs_in_fig])
        limit = max_abs * 1.1 + 0.1
        for ax in axes:
            ax.set_ylim(-limit, limit)
        
    # Bold text at the top left
    axes[0].annotate(f"{idx_pair+1}", xy=(-0.22, 0.95), xycoords='axes fraction', fontsize=14, weight='bold', va='bottom', ha='right', 
                     bbox=dict(boxstyle="circle,pad=0.3", fc="white", lw=1, alpha=0.8))
    
    if (idx_pair + 1) in [5, 7]:
        fig.supxlabel('Orden radial ($n_{pg}$)', fontsize=12, y=0.02)

    # Adjust layout manually to force identical horizontal axes width across all figures
    bottom_margin = 0.22 if (idx_pair + 1) in [5, 7] else 0.08
    plt.subplots_adjust(left=0.1, right=0.98, top=0.85, bottom=bottom_margin, wspace=0.15)
    
    out_filename = f'{out_dir}/gyre_analysis_mass_{mass_compare}_pcomp_{p_num_compare}_pbs_{p_num_bs}_H_{h_pct}.png'
    out_filename_tex = f'{out_dir_tex}/gyre_analysis_mass_{mass_compare}_pcomp_{p_num_compare}_pbs_{p_num_bs}_H_{h_pct}.png'
    plt.savefig(out_filename, dpi=300, bbox_inches='tight')
    plt.savefig(out_filename_tex, dpi=300, bbox_inches='tight')
    plt.close(fig) 
    print(f"Guardado {out_filename}")



print("¡Todos los gráficos se generaron con éxito!")