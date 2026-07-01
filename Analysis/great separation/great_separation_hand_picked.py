import pygyre as pg
import matplotlib.pyplot as plt
import os
import numpy as np
import mesa_reader as mr
import shutil

dir_bs = '/home/pauver/repos/pauverblom/TFM/MESA/evolve_created_blue_straggler'

out_dir = 'great_separations_hand_picked'

if os.path.exists(out_dir):
    shutil.rmtree(out_dir)
os.makedirs(out_dir, exist_ok=True)

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
# Utilizando plasma para mayor contraste
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

    fig, axes = plt.subplots(1, 3, figsize=(12, 3.5))
    
    # Mantener color fijo para BS, usar colormap para la comparación
    color_bs = '#3498db'
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

        dnu_bs = plot_separation(ax, group_bs, color_bs, '^', 'Blue Straggler', '-', 2)
        dnu_comp = plot_separation(ax, group_compare, color_val, 'o', rf'Estrella de {mass_compare:.3f} M$_\odot$', '--', 1.5)
        
        ax.set_xlim(-0.5, 19.5)
        ax.set_xlabel('Índice de gran separación ($k$)', fontsize=10)
        ax.set_xticks(range(0, 20, 2))
        
        all_dnus = dnu_bs + dnu_comp
        if all_dnus:
            min_dnu = min(all_dnus)
            ax.set_ylim(bottom=min_dnu - 0.1)
            
        ax.set_ylabel(r'$\Delta\nu$ (ciclos/día)', fontsize=10)
        
        if l_idx == 0:
            ax.legend(fontsize=9, loc='best', framealpha=0.9)
            
        ax.grid(True, which='both', linestyle=':', color='gray', alpha=0.4)
        ax.tick_params(labelsize=9)
        ax.axvline(0, color='gray', linestyle=':', alpha=0.7, linewidth=1)
        ax.set_title(rf'$l = {l_val}$', fontsize=11, pad=5)
        
    # Bold text at the top left
    fig.text(0.01, 0.95, f"{idx_pair+1} - BSS vs {mass_compare:.3f} " + r"$M_\odot$", fontsize=13, weight='bold', va='top', ha='left')
    
    # Adjust layout to make room for the text at the top
    plt.tight_layout(rect=[0, 0, 1, 0.90])
    
    out_filename = f'{out_dir}/great_separation_mass_{mass_compare}_pcomp_{p_num_compare}_pbs_{p_num_bs}_H_{h_pct}.png'
    plt.savefig(out_filename, dpi=300, bbox_inches='tight')
    plt.close(fig) 
    print(f"Guardado {out_filename}")

# Generar el diagrama HR global
print("Generando diagrama HR global...")
fig_hr, ax_hr = plt.subplots(figsize=(9, 8))

# Color fijo para el BSS
color_bs = '#3498db'

# Trazas base del Blue Straggler
ax_hr.plot(hist_bs.log_Teff, hist_bs.log_L, color=color_bs, alpha=0.7, linewidth=2.5, zorder=1, label='Blue Straggler')

# Trazas de comparación con colores del colormap
masses_labeled = set()
for (idx_pair_1, _, _, _, _, mass), color in zip(global_hr_points, colors):
    hist_comp = hist_compare_cache[mass]
    
    if mass not in masses_labeled:
        ax_hr.plot(hist_comp.log_Teff, hist_comp.log_L, 
                   color=color, alpha=0.6, linewidth=1.5, zorder=1, label=rf'{mass:.3f} $M_\odot$')
        masses_labeled.add(mass)
    else:
        ax_hr.plot(hist_comp.log_Teff, hist_comp.log_L, 
                   color=color, alpha=0.6, linewidth=1.5, zorder=1)

for idx, ((idx_pair, teff_bs, L_bs, teff_compare, L_compare, _), color) in enumerate(zip(global_hr_points, colors)):
    # Marcar los puntos (BS en azul, comparación en color del colormap)
    ax_hr.scatter(teff_bs, L_bs, color=color_bs, s=100, marker='^', zorder=3, edgecolor='black', linewidth=0.5)
    ax_hr.scatter(teff_compare, L_compare, color=color, s=100, marker='o', zorder=3, edgecolor='black', linewidth=0.5)
    
    # Unirlos con una línea
    ax_hr.plot([teff_bs, teff_compare], [L_bs, L_compare], color='black', linestyle=':', linewidth=1.5, alpha=0.7, zorder=2)
    
    # Anotar el número
    mid_teff = (teff_bs + teff_compare) / 2
    mid_L = (L_bs + L_compare) / 2
    ax_hr.annotate(str(idx_pair), (mid_teff, mid_L), textcoords="offset points", xytext=(0,6), ha='center', fontsize=11, fontweight='bold')

ax_hr.invert_xaxis()
ax_hr.set_xlabel(r'$\log T_{\rm eff}$', fontsize=13)
ax_hr.set_ylabel(r'$\log L/L_\odot$', fontsize=13)
ax_hr.tick_params(labelsize=11)
ax_hr.set_title('Diagrama HR Global de Comparaciones', fontsize=15, pad=15)

# La leyenda ahora mostrará el BSS y cada masa (sin anotaciones directas en el gráfico)
# También agregamos una pequeña ayuda visual para los marcadores
from matplotlib.lines import Line2D
handles, labels = ax_hr.get_legend_handles_labels()
handles.extend([
    Line2D([0], [0], marker='^', color='w', markerfacecolor=color_bs, markersize=10, markeredgecolor='black', label='Punto BSS'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', markersize=10, markeredgecolor='black', label='Punto Comparación')
])
ax_hr.legend(handles=handles, fontsize=11, loc='best', framealpha=0.9)

ax_hr.grid(True, linestyle=':', alpha=0.4)

plt.tight_layout()
hr_out = f'{out_dir}/global_hr_diagram.png'
plt.savefig(hr_out, dpi=300, bbox_inches='tight')
plt.close(fig_hr)
print(f"Guardado {hr_out}")

print("¡Todos los gráficos se generaron con éxito!")
