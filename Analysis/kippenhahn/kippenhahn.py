import os
import sys
import subprocess
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
import matplotlib.ticker as ticker
import mesa_reader as mr

# Determine the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Path where mkipp will be cloned if it doesn't exist
mkipp_path = os.path.join(script_dir, "mkipp")

# Clone mkipp if it's not already installed/cloned
if not os.path.exists(mkipp_path):
    print("Cloning mkipp repository...")
    subprocess.run(["git", "clone", "https://github.com/orlox/mkipp.git", mkipp_path], check=True)

# Add mkipp to the Python path
sys.path.append(mkipp_path)

import mkipp

def my_extractor(identifier, log10_on_data, prof, return_data_columns=False):
    if return_data_columns:
        return ["pp", "cno", "tri_alpha"]
    else:
        # sum the available nuclear burning rates
        val = prof.get("pp") + prof.get("cno") + prof.get("tri_alpha")
        if log10_on_data:
            # avoid log10(0)
            return np.log10(np.maximum(1e-12, np.abs(val)))
        else:
            return val

def plot_mkipp_diagram(ax, logs_dirs_list, title, line_color, cmap_name="Blues", cores=["He"], show_xlabel=True, age_decimals=1, num_ticks=None):
    plt.sca(ax)
    
    args = mkipp.Kipp_Args(
        logs_dirs=logs_dirs_list,
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
    
    all_model_numbers = []
    all_star_ages = []
    
    for d in logs_dirs_list:
        h = mr.MesaData(os.path.join(d, 'history.data'))
        all_model_numbers.append(h.model_number)
        all_star_ages.append(h.star_age)
        
    all_mn = np.concatenate(all_model_numbers)
    all_ages = np.concatenate(all_star_ages)
    
    ax.set_xlim(plot_result.xlims[0], plot_result.xlims[1])
    ax.set_ylim(bottom=0, top=1.9)

    # Plot additional boundaries and convection zones manually
    for history in plot_result.histories:
        raw_x_vals = history.get('model_number')
        min_x_profile = plot_result.xlims[0]
        max_x_profile = plot_result.xlims[1]
        mask = (raw_x_vals >= min_x_profile) & (raw_x_vals <= max_x_profile)
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
                # MESA uses -99 for non-existent zones
                top_vals = np.where(top_vals < 0, np.nan, top_vals)
                bot_vals = np.where(bot_vals < 0, np.nan, bot_vals)
                ax.fill_between(x_vals, bot_vals, top_vals, color='lightgray', alpha=0.5, hatch='//', edgecolor='none')
                
    if title:
        ax.set_title(title, fontsize=16, pad=15)
    
    # Custom legend
    legend_elements = [
        Line2D([0], [0], color='k', linestyle='-', label='Masa Total')
    ]
    if "He" in cores:
        legend_elements.append(Line2D([0], [0], color='b', linestyle=':', label='Núcleo de He'))
        
    legend_elements.extend([
        mpatches.Patch(facecolor='lightgray', alpha=0.5, hatch='//', label='Zonas Convectivas')
    ])
    ax.legend(handles=legend_elements, loc='upper left', framealpha=0.9)
    
    # Format X-axis to Age dynamically
    def format_age(value, tick_number):
        idx = np.argmin(np.abs(all_mn - value))
        t = all_ages[idx] / 1e6
        return f"{t:.{age_decimals}f} Myr"
            
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_age))
    
    if num_ticks is not None:
        ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=num_ticks))

    ax.tick_params(axis='both', labelsize=12)
    
    if show_xlabel:
        ax.set_xlabel('Edad', fontsize=14)
    else:
        ax.set_xlabel('')
    
    ax.set_ylabel(r'Masa ($M_\odot$)', fontsize=14)

def overlay_abundance_shading(ax, logs_dirs_list, identifier, levels, cmap_name):
    """
    Overlays shaded regions (contourf) for a given mass fraction identifier (e.g. 'x_mass_fraction_H').
    """
    import matplotlib.patches as mpatches
    import matplotlib.pyplot as plt
    
    args = mkipp.Kipp_Args(
        logs_dirs=logs_dirs_list,
        xaxis="model_number",
        identifier=identifier,
        extractor=mkipp.default_extractor,
        log10_on_data=False,
        save_file=False,
        show_plot=False
    )
    
    if args.xyz_data.Z.size > 0:
        X = args.xyz_data.X
        Y = args.xyz_data.Y
        Z = args.xyz_data.Z
        
        # Shaded regions with transparency
        CS = ax.contourf(X, Y, Z, levels=levels, cmap=cmap_name, alpha=0.3, zorder=1.5)
            
        # Add this shading to the existing legend
        legend = ax.get_legend()
        if legend is not None:
            handles = list(legend.legend_handles)
            leg_labels = [t.get_text() for t in legend.get_texts()]
        else:
            handles, leg_labels = [], []
            
        elem_name = identifier.split('_')[-1]
        
        # Avoid duplicate legend entries if called multiple times for the same element
        if f'Abundancia >50% ({elem_name})' not in leg_labels:
            cmap = plt.get_cmap(cmap_name)
            new_handle = mpatches.Patch(facecolor=cmap(0.5), alpha=0.4, label=f'Abundancia >50% ({elem_name})')
            handles.append(new_handle)
            ax.legend(handles=handles, loc='upper left', framealpha=0.9)


def main():
    project_root = os.path.dirname(os.path.dirname(script_dir))
    
    # Logs directory for the blue straggler (creation + single star evolution phase)
    logs_dir_bs_creation = os.path.join(project_root, "MESA", "blue_straggler_model_create", "LOGS2")
    logs_dir_bs_evolution = os.path.join(project_root, "MESA", "evolve_created_blue_straggler", "LOGS")
    # Logs directory for the 1.83 Msun star
    logs_dir_183 = os.path.join(project_root, "MESA", "mass_grid", "mass_1.83", "LOGS")
    
    logs_dirs_check = [logs_dir_bs_creation, logs_dir_bs_evolution, logs_dir_183]
    
    # Check if the directories exist
    for d in logs_dirs_check:
        if not os.path.exists(d):
            print(f"Warning: LOGS directory {d} does not exist.")
            
    save_filename = os.path.join(script_dir, "kippenhahn_comparision.png")
    
    # Create an elongated figure with three independent subplots
    fig_kipp, (ax_kipp1, ax_kipp2, ax_kipp3) = plt.subplots(3, 1, figsize=(15, 18), sharex=False)
    fig_kipp.subplots_adjust(hspace=0.25)
    
    # Colors according to visualizer.py style
    bs_color = '#2980B9' # accretor color from visualizer.py
    star_183_color = 'purple'
    
    print("Generating Kippenhahn plot for Blue Straggler Creation (Top Panel)...")
    plot_mkipp_diagram(
        ax_kipp1, 
        [logs_dir_bs_creation], 
        "Formación de la Blue Straggler (Transferencia de Masa)", 
        bs_color, 
        cmap_name="Blues",
        cores=["He"],
        show_xlabel=False,
        age_decimals=2,
        num_ticks=8
    )
    overlay_abundance_shading(ax_kipp1, [logs_dir_bs_creation], 'y_mass_fraction_He', levels=np.linspace(0.5, 1.0, 100), cmap_name='Greens')


    
    print("Generating Kippenhahn plot for Blue Straggler Evolution (Middle Panel)...")
    plot_mkipp_diagram(
        ax_kipp2, 
        [logs_dir_bs_evolution], 
        "Evolución posterior de la Blue Straggler", 
        bs_color, 
        cmap_name="Blues",
        cores=["He"],
        show_xlabel=False,
        num_ticks=8
    )
    overlay_abundance_shading(ax_kipp2, [logs_dir_bs_evolution], 'y_mass_fraction_He', levels=np.linspace(0.5, 1.0, 100), cmap_name='Greens')


    
    print("Generating Kippenhahn plot for 1.83 Msun Star (Bottom Panel)...")
    plot_mkipp_diagram(
        ax_kipp3, 
        [logs_dir_183], 
        r"Evolución de la Estrella de 1.83 $M_\odot$", 
        star_183_color, 
        cmap_name="Purples",
        cores=["He"],
        show_xlabel=True
    )
    overlay_abundance_shading(ax_kipp3, [logs_dir_183], 'y_mass_fraction_He', levels=np.linspace(0.5, 1.0, 100), cmap_name='Greens')


    
    # Save the plot
    #plt.show()
    fig_kipp.savefig(save_filename, dpi=300, bbox_inches='tight')
    
    print(f"Plot successfully saved to: {save_filename}")

if __name__ == "__main__":
    main()
