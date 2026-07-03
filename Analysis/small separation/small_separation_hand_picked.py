import pygyre as pg
import matplotlib.pyplot as plt
import os
import numpy as np
import mesa_reader as mr
import shutil

dir_bs = '/home/pauver/repos/pauverblom/TFM/MESA/evolve_created_blue_straggler'

out_dir = 'small_separations_hand_picked'
out_dir_tex = '/home/pauver/repos/pauverblom/TFM/TeX/Imagenes/small_separations_hand_picked'

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

print("Generando gráficos comparativos agrupados en 2x1...")

global_hr_points = []

# Generate colormap colors
colors = [plt.cm.gist_heat(0.8 * i / (len(hand_picked_pairs) - 1)) for i in range(len(hand_picked_pairs))]

all_data = []

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
        
    teff_bs, L_bs = get_hr_point(hist_bs, idx_bs, p_num_bs)
    teff_compare, L_compare = get_hr_point(hist_compare, idx_compare, p_num_compare)
    if teff_bs is not None and teff_compare is not None:
        global_hr_points.append((idx_pair + 1, teff_bs, L_bs, teff_compare, L_compare, mass_compare))

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
                
    if 0 in groups_bs and 2 in groups_bs and 0 in groups_compare and 2 in groups_compare:
        all_data.append({
            'idx_pair': idx_pair,
            'mass_compare': mass_compare,
            'p_num_compare': p_num_compare,
            'p_num_bs': p_num_bs,
            'h_pct': h_pct,
            'group_bs_l1': groups_bs[0],
            'group_bs_l2': groups_bs[2],
            'group_comp_l1': groups_compare[0],
            'group_comp_l2': groups_compare[2],
            'color': colors[idx_pair]
        })

# Chunk data into pairs (2 comparisons per figure)
chunk_size = 2
chunks = [all_data[i:i + chunk_size] for i in range(0, len(all_data), chunk_size)]

for chunk_idx, chunk in enumerate(chunks):
    n_plots = len(chunk)
    
    # We want 2x1 to be around 9.5 width and 2.8 height, similar to great separation
    # If 1 plot, half the width to preserve aspect ratio (4.75 width)
    fig_width = 9.5 if n_plots == 2 else 4.75
    fig, axes = plt.subplots(1, n_plots, figsize=(fig_width, 2.8), squeeze=False)
    axes = axes[0] # Make 1D array
    
    for i, data in enumerate(chunk):
        ax = axes[i]
        idx_pair = data['idx_pair']
        color_val = data['color']
        mass_compare = data['mass_compare']
        
        group_bs_l1 = data['group_bs_l1']
        group_bs_l2 = data['group_bs_l2']
        group_comp_l1 = data['group_comp_l1']
        group_comp_l2 = data['group_comp_l2']

        def plot_small_separation(ax, group1, group2, color, marker, label, linestyle, linewidth):
            if group1 is None or group2 is None: return []
            n_pg_1 = np.array(group1['n_pg'])
            freq_1 = np.array(group1['freq'].real)
            
            n_pg_2 = np.array(group2['n_pg'])
            freq_2 = np.array(group2['freq'].real)
            
            # Sort by n_pg
            sort_idx_1 = np.argsort(n_pg_1)
            n_pg_1 = n_pg_1[sort_idx_1]
            freq_1 = freq_1[sort_idx_1]
            
            sort_idx_2 = np.argsort(n_pg_2)
            n_pg_2 = n_pg_2[sort_idx_2]
            freq_2 = freq_2[sort_idx_2]
            
            n_plot = []
            dnu = []
            valid_dnu = []
            
            # Compare radial order n for l=0 with n-1 for l=2
            for j in range(len(n_pg_1)):
                n = n_pg_1[j]
                idx2 = np.where(n_pg_2 == n - 1)[0]
                if len(idx2) > 0:
                    n_plot.append(float(n + 9)) # Using same +9 offset as original script
                    val = float(freq_1[j] - freq_2[idx2[0]])
                    
                    dnu.append(val)
                    valid_dnu.append(val)
            
            if valid_dnu:
                ax.plot(n_plot, dnu, color=color, marker=marker, markersize=6, 
                        linestyle=linestyle, linewidth=linewidth, alpha=0.8, label=label)
            return valid_dnu

        dnu_bs = plot_small_separation(ax, group_bs_l1, group_bs_l2, '#3498db', '^', 'Blue Straggler', '-', 2)
        dnu_comp = plot_small_separation(ax, group_comp_l1, group_comp_l2, color_val, 'o', rf'Estrella de {mass_compare:.3f} M$_\odot$', '--', 1.5)
        
        ax.set_xlim(9.5, 19.5)
        ax.set_xticks(range(10, 20, 2))
        
        all_dnus = dnu_bs + dnu_comp
        if all_dnus:
            min_dnu = min(all_dnus)
            max_dnu = max(all_dnus)
            ax.set_ylim(bottom=min_dnu - 0.1, top=max_dnu + 0.1)
            
        if i == 0:
            ax.set_ylabel(r'$\delta\nu_{02}$ (ciclos/día)', fontsize=10)
        else:
            ax.set_ylabel(r'$\delta\nu_{02}$', fontsize=10)
        
        ax.legend(fontsize=9, loc='best', framealpha=0.9)
            
        ax.grid(True, which='both', linestyle=':', color='gray', alpha=0.4)
        ax.tick_params(labelsize=9)
        ax.axvline(0, color='gray', linestyle=':', alpha=0.7, linewidth=1)
        ax.set_title(rf'$l = 0$ vs $l = 2$', fontsize=11, pad=5)
        
        # Bold text indicator for which comparison this is
        ax.annotate(f"{idx_pair+1}", xy=(-0.22, 0.95), xycoords='axes fraction', fontsize=14, weight='bold', va='bottom', ha='right', 
                     bbox=dict(boxstyle="circle,pad=0.3", fc="white", lw=1, alpha=0.8))
    
    if chunk_idx == len(chunks) - 1:
        fig.supxlabel('Índice de pequeña separación ($k$)', fontsize=12, y=0.02)
    # To maintain the exact subplot aspect ratio while increasing wspace,
    # we would normally adjust figsize, but here we just increase wspace 
    # to fit the -0.22 annotation on the second subplot.
    plt.subplots_adjust(left=0.09, right=0.98, top=0.85, bottom=0.22, wspace=0.35)
    
    pair_indices = "_".join([str(d['idx_pair'] + 1) for d in chunk])
    out_filename = f'{out_dir}/small_separation_group_{pair_indices}.png'
    out_filename_tex = f'{out_dir_tex}/small_separation_group_{pair_indices}.png'
    plt.savefig(out_filename, dpi=300, bbox_inches='tight')
    plt.savefig(out_filename_tex, dpi=300, bbox_inches='tight')
    plt.close(fig) 
    print(f"Guardado {out_filename}")


print("¡Todos los gráficos se generaron con éxito!")
