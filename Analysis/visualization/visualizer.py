import mesa_reader as mr
import matplotlib.pyplot as plt
import numpy as np

# Load the data
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = '/Users/pauverdeguer/TFM/MESA/blue_straggler_model_create'
binary_history_path = os.path.join(data_dir, 'binary_history.data')
history_star1_path = os.path.join(data_dir, 'LOGS1', 'history.data')
history_star2_path = os.path.join(data_dir, 'LOGS2', 'history.data')

try:
    bh = mr.MesaData(binary_history_path)
    h1 = mr.MesaData(history_star1_path)
    h2 = mr.MesaData(history_star2_path)
except Exception as e:
    print(f"Error loading data: {e}")
    exit(1)

# Extract summary information
initial_m1 = bh.star_1_mass[0]
initial_m2 = bh.star_2_mass[0]
initial_period = bh.period_days[0]
final_m1 = bh.star_1_mass[-1]
final_m2 = bh.star_2_mass[-1]
final_period = bh.period_days[-1]
max_mdot = 10**np.max(bh.lg_mtransfer_rate)

print("="*60)
print("REPORTE DE SIMULACIÓN BINARIA MESA: FORMACIÓN DE BLUE STRAGGLER")
print("="*60)
print(f"Estado Inicial:")
print(f"  Masa Estrella 1 (Donante): {initial_m1:.3f} Msun")
print(f"  Masa Estrella 2 (Acretora): {initial_m2:.3f} Msun")
print(f"  Período Orbital: {initial_period:.3f} días")
print("-" * 30)
print(f"Estado Final:")
print(f"  Masa Remanente Estrella 1: {final_m1:.3f} Msun")
print(f"  Masa Final Estrella 2 (BSS): {final_m2:.3f} Msun")
print(f"  Período Orbital Final: {final_period:.3f} días")
print("-" * 30)
print(f"Detalles de Simulación:")
print(f"  Tasa Máxima de Transferencia de Masa: {max_mdot:.2e} Msun/año")
print(f"  Duración Total: {bh.age[-1]:.2e} años")
print("="*60)
import matplotlib.ticker as ticker

# Global variables for mass transfer and dynamic formatting
idx_start_bh = np.argmax(bh.lg_mtransfer_rate > -25) if np.any(bh.lg_mtransfer_rate > -25) else 0
age_mt_start = bh.age[idx_start_bh]
t_0_myr_bh = age_mt_start / 1e6

mt_indices = np.where(bh.lg_mtransfer_rate > -60)[0]
age_mt_end = bh.age[mt_indices[-1]] if len(mt_indices) > 0 else bh.age[-1]

idx_mt_start_1 = np.argmin(np.abs(h1.star_age - age_mt_start))
idx_mt_end_1 = np.argmin(np.abs(h1.star_age - age_mt_end))

idx_mt_start_2 = np.argmin(np.abs(h2.star_age - age_mt_start))
idx_mt_end_2 = np.argmin(np.abs(h2.star_age - age_mt_end))

def format_age_bh(value, tick_number):
    idx = np.argmin(np.abs(bh.model_number - value))
    t = bh.age[idx] / 1e6
    if t < 10.0:
        return f"{t:.1f} Myr"
    elif abs(t - t_0_myr_bh) < 2.0:
        delta_kyr = (t - t_0_myr_bh) * 1000
        sign = '+' if delta_kyr >= 0 else ''
        return f"$t_0$ {sign}{delta_kyr:.1f} kyr"
    else:
        return f"{t:.1f} Myr"

t_0_myr_h1 = h1.star_age[idx_mt_start_1] / 1e6
def format_age_rlof1(value, tick_number):
    idx = np.argmin(np.abs(h1.model_number - value))
    t = h1.star_age[idx] / 1e6
    if t < 10.0:
        return f"{t:.1f} Myr"
    elif abs(t - t_0_myr_h1) < 2.0:
        delta_kyr = (t - t_0_myr_h1) * 1000
        sign = '+' if delta_kyr >= 0 else ''
        return f"$t_0$ {sign}{delta_kyr:.1f} kyr"
    else:
        return f"{t:.1f} Myr"

t_0_myr_h2 = h2.star_age[idx_mt_start_2] / 1e6
def format_age_rlof2(value, tick_number):
    idx = np.argmin(np.abs(h2.model_number - value))
    t = h2.star_age[idx] / 1e6
    if t < 10.0:
        return f"{t:.1f} Myr"
    elif abs(t - t_0_myr_h2) < 2.0:
        delta_kyr = (t - t_0_myr_h2) * 1000
        sign = '+' if delta_kyr >= 0 else ''
        return f"$t_0$ {sign}{delta_kyr:.1f} kyr"
    else:
        return f"{t:.1f} Myr"

# Create the visualization
plt.style.use('default') # Base style, can be customized later

donor_color = '#E67E22'  # Orange, slightly desaturated
accretor_color = '#2980B9' # Blue, slightly desaturated
alpha_val = 0.8

# 2. Orbital Evolution (Period and Separation)
fig2, ax2 = plt.subplots(figsize=(7.5, 6.0))

ax2.plot(bh.model_number, bh.period_days, color='#8E44AD', label='Período', linewidth=2.5)
ax2.set_ylabel('Período (días)', color='black', fontsize=14)
ax2.tick_params(axis='y', colors='black')

ax2b = ax2.twinx()
ax2b.plot(bh.model_number, bh.binary_separation, color='#27AE60', label='Separación', linestyle='-', linewidth=2.5)
ax2b.set_ylabel('Separación ($R_\odot$)', color='black', fontsize=14)
ax2b.tick_params(axis='y', colors='black')

# Línea vertical indicando el inicio de la transferencia de masa
ax2.axvline(bh.model_number[idx_start_bh], color='gray', linestyle=':', linewidth=2, alpha=0.8, label='Inicio Transf. Masa')

ax2.xaxis.set_major_formatter(ticker.FuncFormatter(format_age_bh))
ax2.set_xlabel('Edad', fontsize=14)
ax2.set_title('Evolución Orbital', fontsize=14)

# Combinar leyendas de ambos ejes
lines, labels = ax2.get_legend_handles_labels()
lines2, labels2 = ax2b.get_legend_handles_labels()
ax2.legend(lines + lines2, labels + labels2, loc='upper left')

ax2.grid(True, linestyle='--', alpha=0.7)
fig2.savefig(os.path.join(script_dir, 'orbital_evolution.png'), dpi=300, bbox_inches='tight')

# 3. Mass Transfer Rate
fig3, ax3 = plt.subplots(figsize=(7.5, 6.0))
ax3.plot(bh.model_number, bh.lg_mtransfer_rate, color='red', linewidth=1.5)
ax3.axvline(bh.model_number[idx_start_bh], color='gray', linestyle=':', linewidth=2, alpha=0.8, label='Inicio Transf. Masa')
ax3.xaxis.set_major_formatter(ticker.FuncFormatter(format_age_bh))
ax3.set_xlabel('Edad', fontsize=14)
ax3.set_ylabel('$\log \dot{M}$ ($M_\odot$/año)', fontsize=14)
ax3.set_title('Tasa de Transferencia de Masa', fontsize=14)
ax3.set_ylim(-25, 0)
ax3.grid(True, linestyle='--', alpha=0.7)
fig3.savefig(os.path.join(script_dir, 'mass_transfer_rate.png'), dpi=300, bbox_inches='tight')

idx_start_1 = 0
idx_start_2 = 0

# 4. HR Diagram
fig4, ax4 = plt.subplots(figsize=(12.6, 6.5))
# Plot traces
ax4.plot(h1.log_Teff, h1.log_L, color=donor_color, alpha=alpha_val, linewidth=2, label='Donante (Estrella 1)', zorder=1)
ax4.plot(h2.log_Teff, h2.log_L, color=accretor_color, alpha=alpha_val, linewidth=2, label='Acretora (Estrella 2)', zorder=1)

# Plot markers for Donor
ax4.scatter(h1.log_Teff[idx_start_1], h1.log_L[idx_start_1], color=donor_color, alpha=alpha_val, marker='o', s=100, zorder=5, edgecolor='black')
ax4.scatter(h1.log_Teff[idx_mt_start_1], h1.log_L[idx_mt_start_1], color=donor_color, alpha=alpha_val, marker='^', s=100, zorder=5, edgecolor='black')
ax4.scatter(h1.log_Teff[idx_mt_end_1], h1.log_L[idx_mt_end_1], color=donor_color, alpha=alpha_val, marker='s', s=100, zorder=5, edgecolor='black')

# Plot markers for Accretor
ax4.scatter(h2.log_Teff[idx_start_2], h2.log_L[idx_start_2], color=accretor_color, alpha=alpha_val, marker='o', s=100, zorder=5, edgecolor='black')
ax4.scatter(h2.log_Teff[idx_mt_start_2], h2.log_L[idx_mt_start_2], color=accretor_color, alpha=alpha_val, marker='^', s=100, zorder=5, edgecolor='black')
ax4.scatter(h2.log_Teff[idx_mt_end_2], h2.log_L[idx_mt_end_2], color=accretor_color, alpha=alpha_val, marker='s', s=100, zorder=5, edgecolor='black')

ax4.invert_xaxis()
ax4.set_xlabel('$\log T_{eff}$ (K)', fontsize=14)
ax4.set_ylabel('$\log L/L_\odot$', fontsize=14)
ax4.set_title('Diagrama HR', fontsize=14)

from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], color=donor_color, alpha=alpha_val, lw=2, label='Donante (Estrella 1)'),
    Line2D([0], [0], color=accretor_color, alpha=alpha_val, lw=2, label='Acretora (Estrella 2)'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', markersize=10, label='Inicio de la evolución'),
    Line2D([0], [0], marker='^', color='w', markerfacecolor='gray', markersize=10, label='Inicio de transferencia de masa'),
    Line2D([0], [0], marker='s', color='w', markerfacecolor='gray', markersize=10, label='Fin de transferencia de masa')
]
ax4.legend(handles=legend_elements)
ax4.grid(True, linestyle='--', alpha=0.7)
fig4.savefig(os.path.join(script_dir, 'hr_diagram.png'), dpi=300, bbox_inches='tight')

# 5. Center H and He (Both stars)
def format_log_abundance(x, pos):
    return f"{x:g}"
log_formatter = ticker.FuncFormatter(format_log_abundance)

def get_split_x(h, idx_mt_start):
    x_custom = np.zeros_like(h.model_number, dtype=float)
    t_0 = h.star_age[idx_mt_start]
    mn_t0 = h.model_number[idx_mt_start]
    mn_max = h.model_number[-1]
    
    split_point = 0.25
    mask_pre = np.arange(len(h.model_number)) <= idx_mt_start
    x_custom[mask_pre] = split_point * (h.star_age[mask_pre] / t_0)
    
    mask_post = np.arange(len(h.model_number)) > idx_mt_start
    if mn_max > mn_t0:
        x_custom[mask_post] = split_point + (1.0 - split_point) * (h.model_number[mask_post] - mn_t0) / (mn_max - mn_t0)
    else:
        x_custom[mask_post] = split_point
    return x_custom

def get_split_formatter(h, idx_mt_start):
    t_0 = h.star_age[idx_mt_start]
    mn_t0 = h.model_number[idx_mt_start]
    mn_max = h.model_number[-1]
    split_point = 0.25
    
    def formatter(x, pos):
        if x < 0.0 or x > 1.0:
            return ""
        if x <= split_point:
            age = (x / split_point) * t_0
            return f"{age/1e6:.1f} Myr"
        else:
            mn = mn_t0 + ((x - split_point) / (1.0 - split_point)) * (mn_max - mn_t0)
            idx = np.argmin(np.abs(h.model_number - mn))
            age = h.star_age[idx]
            t = age / 1e6
            t_0_myr = t_0 / 1e6
            
            if abs(t - t_0_myr) < 2.0:
                delta_kyr = (t - t_0_myr) * 1000
                if abs(delta_kyr) < 0.1:
                    return f"$t_0$"
                sign = '+' if delta_kyr >= 0 else ''
                return f"$t_0$ {sign}{delta_kyr:.1f} kyr"
            else:
                return f"{t:.1f} Myr"
    return ticker.FuncFormatter(formatter)

x_custom_h1 = get_split_x(h1, idx_mt_start_1)
x_custom_h2 = get_split_x(h2, idx_mt_start_2)
formatter_h1 = get_split_formatter(h1, idx_mt_start_1)

fig5, (ax5a, ax5b) = plt.subplots(2, 1, figsize=(12.6, 7.0), sharex=True)
fig5.suptitle('Abundancias Centrales', fontsize=14, y=0.91)
fig5.subplots_adjust(hspace=0.05)

# Donor
ax5a.plot(x_custom_h1, h1.center_h1, color=donor_color, alpha=alpha_val, label='H1 Central', linewidth=2)
ax5a.plot(x_custom_h1, h1.center_he4, color='grey', alpha=alpha_val, label='He4 Central', linewidth=2, linestyle='--')
ax5a.axvline(0.25, color=donor_color, linestyle=':', linewidth=2, alpha=0.8, label='Inicio Transf. Masa')
ax5a.set_ylabel('Fracción de Masa')
ax5a.yaxis.set_major_formatter(log_formatter)
ax5a.legend()
ax5a.grid(True, linestyle='--', alpha=0.7)

# Accretor
ax5b.plot(x_custom_h2, h2.center_h1, color=accretor_color, alpha=alpha_val, label='H1 Central', linewidth=2)
ax5b.plot(x_custom_h2, h2.center_he4, color='grey', alpha=alpha_val, label='He4 Central', linewidth=2, linestyle='--')
ax5b.axvline(0.25, color=accretor_color, linestyle=':', linewidth=2, alpha=0.8, label='Inicio Transf. Masa')
ax5b.set_ylabel('Fracción de Masa')
ax5b.yaxis.set_major_formatter(log_formatter)
ax5b.legend()
ax5b.grid(True, linestyle='--', alpha=0.7)

ax5b.xaxis.set_major_formatter(formatter_h1)

# Specific ticks requested by user
t_0_h1 = h1.star_age[idx_mt_start_1]
target_ages = [
    t_0_h1 + 580.8 * 1e3,
    t_0_h1 + 590.6 * 1e3,
    t_0_h1 + 808.8 * 1e3,
    1003.8 * 1e6
]

mn_t0_h1 = h1.model_number[idx_mt_start_1]
mn_max_h1 = h1.model_number[-1]

split_point = 0.25
custom_ticks = [0.0, split_point/2] # Ticks for linear pre-MT phase (removed t_0 to avoid overlap)
for t_target in target_ages:
    idx = np.argmin(np.abs(h1.star_age - t_target))
    mn = h1.model_number[idx]
    if mn_max_h1 > mn_t0_h1:
        x_val = split_point + (1.0 - split_point) * (mn - mn_t0_h1) / (mn_max_h1 - mn_t0_h1)
        custom_ticks.append(x_val)

ax5b.set_xticks(custom_ticks)
ax5b.set_xlabel('Edad (Izquierda: Lineal hasta $t_0$, Derecha: Tiempo post-$t_0$)', fontsize=14)
fig5.savefig(os.path.join(script_dir, 'central_abundances.png'), dpi=300, bbox_inches='tight')

# 6 & 7. Kippenhahn Diagrams using mkipp
# Clone mkipp if it's not already installed/cloned
mkipp_path = os.path.join(script_dir, "mkipp")
if not os.path.exists(mkipp_path):
    print("Cloning mkipp repository...")
    import subprocess
    subprocess.run(["git", "clone", "https://github.com/orlox/mkipp.git", mkipp_path], check=True)

import sys
if mkipp_path not in sys.path:
    sys.path.append(mkipp_path)
import mkipp
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches

# Custom extractor for nuclear burning regions
def my_extractor(identifier, log10_on_data, prof, return_data_columns=False):
    if return_data_columns:
        return ["pp", "cno", "tri_alpha"]
    else:
        val = prof.get("pp") + prof.get("cno") + prof.get("tri_alpha")
        if log10_on_data:
            return np.log10(np.maximum(1e-12, np.abs(val)))
        else:
            return val

def plot_mkipp_diagram(ax, logs_dir, title, color_mt, cmap_name="Blues", cores=["He"], show_xlabel=True):
    plt.sca(ax)
    
    args = mkipp.Kipp_Args(
        logs_dirs=[logs_dir],
        xaxis="model_number",
        identifier=r"Quema Nuclear $\log(\epsilon_{nuc})$ [erg g$^{-1}$ s$^{-1}$]",
        extractor=my_extractor,
        contour_colormap=plt.get_cmap(cmap_name),
        core_masses=cores,
        extra_history_cols=['conv_mx1_top', 'conv_mx1_bot', 'conv_mx2_top', 'conv_mx2_bot', 'star_age'],
        save_file=False,
        show_plot=False
    )
    
    plot_result = mkipp.kipp_plot(args, axis=ax)
    
    # Plot additional boundaries and convection zones manually
    for history in plot_result.histories:
        raw_x_vals = history.get('model_number')
        min_x_profile = plot_result.xlims[0]
        mask = raw_x_vals >= min_x_profile
        x_vals = raw_x_vals[mask]
        star_mass = history.get('star_mass')[mask]
        
        # Total Star Mass Boundary
        ax.plot(x_vals, star_mass, color='k', linestyle='-', linewidth=2)
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Convection zones with custom transparent styling
        for i in [1, 2]:
            top_key = f'conv_mx{i}_top'
            bot_key = f'conv_mx{i}_bot'
            if top_key in history.columns and bot_key in history.columns:
                top_vals = history.get(top_key)[mask] * star_mass
                bot_vals = history.get(bot_key)[mask] * star_mass
                top_vals = np.where(top_vals < 0, np.nan, top_vals)
                bot_vals = np.where(bot_vals < 0, np.nan, bot_vals)
                ax.fill_between(x_vals, bot_vals, top_vals, color='lightgray', alpha=0.5, hatch='//', edgecolor='none')
        
        ax.set_xlim(min(x_vals), max(x_vals))
    
    # Add vertical lines for MT using age logic mapped to model_number
    # Access the specific history for this directory to find MT model numbers
    h_local = mr.MesaData(os.path.join(logs_dir, 'history.data'))
    idx_start = np.argmin(np.abs(h_local.star_age - age_mt_start))
    idx_end = np.argmin(np.abs(h_local.star_age - age_mt_end))
    ax.axvline(h_local.model_number[idx_start], color=color_mt, linestyle=':', linewidth=2, alpha=0.8)

    if title:
        ax.set_title(title, fontsize=16, pad=15)
    
    # Custom legend
    legend_elements = [
        Line2D([0], [0], color='k', linestyle='-', label='Masa Total')
    ]
    if "He" in cores:
        legend_elements.append(Line2D([0], [0], color='b', linestyle=':', label='Núcleo de He'))
        
    legend_elements.extend([
        mpatches.Patch(facecolor='lightgray', alpha=0.5, hatch='//', label='Zonas Convectivas'),
        Line2D([0], [0], color=color_mt, linestyle=':', label='Inicio Transf. Masa')
    ])
    ax.legend(handles=legend_elements, loc='upper left', framealpha=0.9)
    
    # Format X-axis to Age dynamically
    import matplotlib.ticker as ticker
    
    t_0_myr = h_local.star_age[idx_start] / 1e6
    
    def format_age(value, tick_number):
        idx = np.argmin(np.abs(h_local.model_number - value))
        t = h_local.star_age[idx] / 1e6
        
        if t < 10.0:
            return f"{t:.1f} Myr"
        elif abs(t - t_0_myr) < 2.0:
            delta_kyr = (t - t_0_myr) * 1000
            sign = '+' if delta_kyr >= 0 else ''
            return f"$t_0$ {sign}{delta_kyr:.1f} kyr"
        else:
            return f"{t:.1f} Myr"
            
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_age))
    if show_xlabel:
        ax.set_xlabel('Edad', fontsize=14)
    else:
        ax.set_xlabel('')
    
    ax.set_ylabel('Masa ($M_\odot$)', fontsize=14)

print("Generando Diagramas de Kippenhahn combinados usando mkipp...")
fig_kipp, (ax_kipp1, ax_kipp2) = plt.subplots(2, 1, figsize=(7.5, 12.5), sharex=True)
fig_kipp.subplots_adjust(hspace=0.08)

plot_mkipp_diagram(
    ax_kipp1,
    os.path.join(script_dir, "../../MESA/blue_straggler_model_create/LOGS1"),
    'Diagramas de Kippenhahn',
    donor_color,
    cmap_name="Oranges",
    show_xlabel=False
)
plot_mkipp_diagram(
    ax_kipp2,
    os.path.join(script_dir, "../../MESA/blue_straggler_model_create/LOGS2"),
    None,
    accretor_color,
    cmap_name="Blues",
    cores=[],
    show_xlabel=True
)

fig_kipp.savefig(os.path.join(script_dir, 'kippenhahn_combined.png'), dpi=300, bbox_inches='tight')

# 8. Evolución del Radio vs Lóbulo de Roche
fig8, (ax8a, ax8b) = plt.subplots(2, 1, figsize=(7.5, 12.5), sharex=True)
fig8.suptitle('Evolución del Radio Estelar\nvs Lóbulo de Roche', fontsize=16, y=0.92)
fig8.subplots_adjust(hspace=0.05)

# Star 1 (Donor)
R1 = 10**h1.log_R
rl_1 = h1.rl_1
ax8a.plot(h1.model_number, R1, color=donor_color, linewidth=2.5, label='Radio Estelar (Donante)')
ax8a.plot(h1.model_number, rl_1, color='gray', linestyle='--', linewidth=2, label='Lóbulo de Roche')
mask_rlof1 = h1.rl_relative_overflow_1 > 0
if np.any(mask_rlof1):
    ax8a.fill_between(h1.model_number, R1, rl_1, where=mask_rlof1, color=donor_color, alpha=0.3, label='Desbordamiento (RLOF)')
ax8a.axvline(h1.model_number[idx_mt_start_1], color=donor_color, linestyle=':', linewidth=2, alpha=0.8, label='Inicio Transf. Masa')

ax8a.set_ylabel('Radio ($R_\odot$)', fontsize=14)
ax8a.grid(True, linestyle='--', alpha=0.7)
ax8a.legend()

ax8a.xaxis.set_major_formatter(ticker.FuncFormatter(format_age_rlof1))
# xlabel omitido para el top subplot al compartir eje X

# Star 2 (Accretor)
R2 = 10**h2.log_R
if 'rl_2' in h2.bulk_names:
    rl_2 = h2.rl_2
    ax8b.plot(h2.model_number, R2, color=accretor_color, linewidth=2.5, label='Radio Estelar (Acretora)')
    ax8b.plot(h2.model_number, rl_2, color='gray', linestyle='--', linewidth=2, label='Lóbulo de Roche')
    if 'rl_relative_overflow_2' in h2.bulk_names:
        mask_rlof2 = h2.rl_relative_overflow_2 > 0
        if np.any(mask_rlof2):
            ax8b.fill_between(h2.model_number, R2, rl_2, where=mask_rlof2, color=accretor_color, alpha=0.3, label='Desbordamiento (RLOF)')
    ax8b.axvline(h2.model_number[idx_mt_start_2], color=accretor_color, linestyle=':', linewidth=2, alpha=0.8, label='Inicio Transf. Masa')

    ax8b.set_ylabel('Radio ($R_\odot$)', fontsize=14)
    ax8b.grid(True, linestyle='--', alpha=0.7)
    ax8b.legend()

    ax8b.xaxis.set_major_formatter(ticker.FuncFormatter(format_age_rlof2))
    ax8b.set_xlabel('Edad', fontsize=14)

# plt.tight_layout() comentado para respetar subplots_adjust
fig8.savefig(os.path.join(script_dir, 'radio_vs_rlof.png'), dpi=300, bbox_inches='tight')

print(f"\nVisualizaciones guardadas en '{script_dir}'")