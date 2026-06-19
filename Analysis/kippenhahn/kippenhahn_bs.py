import os
import sys
import subprocess

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

def main():
    # Define LOGS directories for the blue straggler's entire life
    # The project root is two directories up from the script dir (Analysis/kippenhahn -> /Users/pauverdeguer/TFM)
    project_root = os.path.dirname(os.path.dirname(script_dir))
    
    logs_dir_1 = os.path.join(project_root, "MESA", "blue_straggler_model_create", "LOGS2")
    logs_dir_2 = os.path.join(project_root, "MESA", "evolve_created_blue_straggler", "LOGS")
    
    logs_dirs = [logs_dir_1, logs_dir_2]
    
    # Check if the directories exist
    for d in logs_dirs:
        if not os.path.exists(d):
            print(f"Warning: LOGS directory {d} does not exist.")
            
    save_filename = os.path.join(script_dir, "kippenhahn_bs.png")
    
    import numpy as np
    
    # Custom extractor because eps_nuc is missing from these profiles
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

    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    import matplotlib.patches as mpatches
    import numpy as np
    
    # Create an elongated figure with two independent subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 12))
    
    def plot_kipp_on_axis(logs_dir, axis, title):
        # Set the current axis so plt.colorbar() in mkipp works correctly on this specific axis
        plt.sca(axis)
        
        # Configure Kippenhahn plot arguments
        args = mkipp.Kipp_Args(
            logs_dirs=[logs_dir],
            xaxis="model_number",
            identifier="eps_nuc",
            extractor=my_extractor,
            core_masses=["He"],
            extra_history_cols=['conv_mx1_top', 'conv_mx1_bot', 'conv_mx2_top', 'conv_mx2_bot', 'co_core_mass', 'rl_relative_overflow_1'],
            save_file=False, # We will save manually
            show_plot=False
        )
        
        # Generate the plot
        plot_result = mkipp.kipp_plot(args, axis=axis)
        
        # Plot additional data manually from the histories
        mass_transfer_marked = False
        
        for history in plot_result.histories:
            raw_x_vals = history.get('model_number')
            # Discard history data before the first profile so lines align with contours perfectly
            min_x_profile = plot_result.xlims[0]
            mask = raw_x_vals >= min_x_profile
            
            x_vals = raw_x_vals[mask]
            star_mass = history.get('star_mass')[mask]
            
            # 1. Total Star Mass Boundary
            axis.plot(x_vals, star_mass, color='k', linestyle='-', linewidth=2)
            
            # 2. C/O Core Mass Boundary
            if 'co_core_mass' in history.columns:
                co_core = history.get('co_core_mass')[mask]
                axis.plot(x_vals, co_core, color='r', linestyle=':', linewidth=2)
                
            # 3. Convection zones
            for i in [1, 2]:
                top_key = f'conv_mx{i}_top'
                bot_key = f'conv_mx{i}_bot'
                if top_key in history.columns and bot_key in history.columns:
                    top_vals = history.get(top_key)[mask] * star_mass
                    bot_vals = history.get(bot_key)[mask] * star_mass
                    # MESA uses -99 for non-existent zones
                    top_vals = np.where(top_vals < 0, np.nan, top_vals)
                    bot_vals = np.where(bot_vals < 0, np.nan, bot_vals)
                    axis.fill_between(x_vals, bot_vals, top_vals, color='Chartreuse', alpha=0.5, hatch='//', edgecolor='none')
                    
            # 4. Mass Transfer Onset
            if 'rl_relative_overflow_1' in history.columns and not mass_transfer_marked:
                rl_ov = history.get('rl_relative_overflow_1')[mask]
                mt_indices = rl_ov > 0
                if np.any(mt_indices):
                    first_mt_x = x_vals[np.argmax(mt_indices)]
                    axis.axvline(x=first_mt_x, color='purple', linestyle='--', linewidth=2, alpha=0.8)
                    mass_transfer_marked = True # Only mark once
            
            # Enforce tight x-axis limits based on the trimmed data
            axis.set_xlim(min(x_vals), max(x_vals))
        
        axis.set_title(title, fontsize=16, fontweight='bold')
    
    print(f"Generating Kippenhahn plot for BS Creation (Top Panel)...")
    plot_kipp_on_axis(logs_dir_1, ax1, "Creation of the Blue Straggler (Mass Transfer Phase)")
    
    print(f"Generating Kippenhahn plot for BS Evolution (Bottom Panel)...")
    plot_kipp_on_axis(logs_dir_2, ax2, "Subsequent Evolution of the Blue Straggler")

    # Update the legend for the first plot
    legend_elements = [
        Line2D([0], [0], color='k', linestyle='-', label='Star Mass (Surface)'),
        Line2D([0], [0], color='b', linestyle=':', label='He core mass boundary'),
        Line2D([0], [0], color='r', linestyle=':', label='C/O core mass boundary'),
        mpatches.Patch(facecolor='Chartreuse', alpha=0.5, hatch='//', label='Convection Zones'),
        Line2D([0], [0], color='purple', linestyle='--', label='Onset of Mass Transfer')
    ]
    ax1.legend(handles=legend_elements, loc='upper left', framealpha=0.9)
    
    # Save the plot
    plt.tight_layout()
    plt.savefig(save_filename, dpi=300)
    
    print(f"Plot successfully saved to: {save_filename}")

if __name__ == "__main__":
    main()
