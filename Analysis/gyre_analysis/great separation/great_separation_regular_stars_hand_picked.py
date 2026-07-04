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

out_dir = f'great_separations_comp_{mass_1}_{mass_2}_hand_picked'
out_dir_tex = f'/home/pauver/repos/pauverblom/TFM/TeX/Imagenes/great_separations_comp_{mass_1}_{mass_2}_hand_picked'

if os.path.exists(out_dir):
    shutil.rmtree(out_dir)
os.makedirs(out_dir, exist_ok=True)

if os.path.exists(out_dir_tex):
    shutil.rmtree(out_dir_tex)
os.makedirs(out_dir_tex, exist_ok=True)

hand_picked_pairs = [
    # (p_num_1, p_num_2, h_pct)
    (9, 9, 64.5),
    (27, 27, 17.9),
    (43, 43, 0.1)
]

print("Generando gráficos comparativos (3 columnas)...")

for idx_pair, (p_num_1, p_num_2, h_pct) in enumerate(hand_picked_pairs):
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
        
    fig, axes = plt.subplots(1, 3, figsize=(9.5, 2.8))
    
    color_1 = '#ab34eb'
    color_val = '#34ebd5'
    
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
        
        expected_modes = {0: 10, 1: 20, 2: 21}[l_val]
        def count_modes(g):
            if g is None: return 0
            n_pg = np.array(g['n_pg'])
            return np.sum((n_pg >= -10) & (n_pg <= 10))
            
        modes_1 = count_modes(group_1)
        modes_2 = count_modes(group_2)
        
        if modes_1 != expected_modes:
            warn_msg = f"AVISO: 1 l={l_val} tiene {modes_1} modos!"
            ax.text(0.5, 0.9, warn_msg, transform=ax.transAxes, color='red', ha='center', fontsize=8, bbox=dict(facecolor='white', alpha=0.8, edgecolor='red'))
            
        if modes_2 != expected_modes:
            warn_msg = f"AVISO: 2 l={l_val} tiene {modes_2} modos!"
            ax.text(0.5, 0.8, warn_msg, transform=ax.transAxes, color='red', ha='center', fontsize=8, bbox=dict(facecolor='white', alpha=0.8, edgecolor='red'))

        def plot_separation(ax, group, color, marker, label, linestyle, linewidth):
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
                ax.plot(n_plot, dnu, color=color, marker=marker, markersize=6, 
                        linestyle=linestyle, linewidth=linewidth, alpha=0.8, label=label)
            return valid_dnu

        dnu_1 = plot_separation(ax, group_1, color_1, '^', rf'Estrella de {mass_1} M$_\odot$', '-', 2)
        dnu_2 = plot_separation(ax, group_2, color_val, 'o', rf'Estrella de {mass_2} M$_\odot$', '--', 1.5)
        
        ax.set_xlim(-0.5, 19.5)
        ax.set_xticks(range(0, 20, 2))
        
        all_dnus = dnu_1 + dnu_2
        if all_dnus:
            min_dnu = min(all_dnus)
            ax.set_ylim(bottom=min_dnu - 0.1)
            
        if l_idx == 0:
            ax.set_ylabel(r'$\Delta\nu$ (ciclos/día)', fontsize=10)
        
        if l_idx == 0:
            ax.legend(fontsize=9, loc='upper left', framealpha=0.9)
            
        ax.grid(True, which='both', linestyle=':', color='gray', alpha=0.4)
        ax.tick_params(labelsize=9)
        ax.axvline(0, color='gray', linestyle=':', alpha=0.7, linewidth=1)
        if idx_pair == 0:
            ax.set_title(rf'$l = {l_val}$', fontsize=11, pad=5)
        else:
            ax.set_title(' ', fontsize=11, pad=5)
        
    # Bold text at the top left
    axes[0].annotate(f"{idx_pair+1}", xy=(-0.22, 0.95), xycoords='axes fraction', fontsize=14, weight='bold', va='bottom', ha='right', 
                     bbox=dict(boxstyle="circle,pad=0.3", fc="white", lw=1, alpha=0.8))
    
    if (idx_pair + 1) in [3]:
        fig.supxlabel('Índice de gran separación ($k$)', fontsize=12, y=0.02)

    # Adjust layout manually to force identical horizontal axes width across all figures
    bottom_margin = 0.22 if (idx_pair + 1) in [3] else 0.08
    plt.subplots_adjust(left=0.09, right=0.98, top=0.85, bottom=bottom_margin, wspace=0.15)
    
    out_filename = f'{out_dir}/great_separation_{mass_1}_vs_{mass_2}_p1_{p_num_1}_p2_{p_num_2}_H_{h_pct}.png'
    out_filename_tex = f'{out_dir_tex}/great_separation_{mass_1}_vs_{mass_2}_p1_{p_num_1}_p2_{p_num_2}_H_{h_pct}.png'
    plt.savefig(out_filename, dpi=300, bbox_inches='tight')
    plt.savefig(out_filename_tex, dpi=300, bbox_inches='tight')
    plt.close(fig) 
    print(f"Guardado {out_filename}")


print("¡Todos los gráficos se generaron con éxito!")
