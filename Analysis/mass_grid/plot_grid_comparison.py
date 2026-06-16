import mesa_reader as mr
import matplotlib.pyplot as plt
import numpy as np
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
mesa_dir = os.path.abspath(os.path.join(script_dir, '..', '..', 'MESA'))

bss_dir = os.path.join(mesa_dir, 'evolve_created_blue_straggler')
grid_dir = os.path.join(mesa_dir, 'mass_grid')

# Central hydrogen fractions at which to place milestone dots
xc_milestones = [0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.005]
# Marker sizes: largest for Xc=0.6, smallest for Xc=0.1
xc_marker_sizes = [130, 110, 90, 70, 50, 30, 20]


def plot_xc_dots(hist, color, zorder):
    """Plot dots on the track at the central-hydrogen milestones."""
    xc = hist.center_h1
    for xc_val, sz in zip(xc_milestones, xc_marker_sizes):
        idx = np.argmin(np.abs(xc - xc_val))
        plt.scatter(hist.log_Teff[idx], hist.log_L[idx],
                    s=sz, color=color, edgecolors='black', linewidths=0.5,
                    zorder=zorder)


print("Loading Blue Straggler history...")
hist_bs = mr.MesaData(f'{bss_dir}/LOGS/history.data')

orig_dir = os.path.join(mesa_dir, 'evolve_1.8_mass_star')
print("Loading Original 1.82 M_sun history...")
hist_orig = mr.MesaData(f'{orig_dir}/LOGS/history.data')

plt.figure(figsize=(12, 8))

# Plot the base Blue Straggler prominently
plt.plot(hist_bs.log_Teff, hist_bs.log_L, color='blue', linewidth=4, label='Blue Straggler Target', zorder=100)
plot_xc_dots(hist_bs, 'blue', zorder=101)

cmap = plt.get_cmap('viridis')
masses = np.round(np.arange(1.75, 1.90, 0.01), 2)

print("Loading grid histories...")
plotted_any = False
for i, m in enumerate(masses):
    m_dir = f'{grid_dir}/mass_{m:.2f}'
    hist_file = f'{m_dir}/LOGS/history.data'
    
    if os.path.exists(hist_file):
        try:
            hist = mr.MesaData(hist_file)
            color = cmap((i) / len(masses))
            plt.plot(hist.log_Teff, hist.log_L, color=color, linewidth=2, alpha=0.8, label=rf'{m:.2f} M$_\odot$')
            plot_xc_dots(hist, color, zorder=50)
            plotted_any = True
        except Exception as e:
            print(f"Skipping {m_dir} (possibly incomplete): {e}")
    else:
        print(f"History file not found yet for {m_dir}...")

if not plotted_any:
    print("No grid data available to plot yet. Wait for mesa-go to finish a few runs!")
else:
    # Add a legend entry for the milestone dots (one representative scatter per size)
    for xc_val, sz in zip(xc_milestones, xc_marker_sizes):
        plt.scatter([], [], s=sz, color='grey', edgecolors='black', linewidths=0.5,
                    label=rf'$X_c = {xc_val}$')

    plt.gca().invert_xaxis()
    plt.xlabel(r'$\log T_{\rm eff}$', fontsize=14, fontweight='bold')
    plt.ylabel(r'$\log L/L_\odot$', fontsize=14, fontweight='bold')
    plt.title(r'HR Track Comparison: Blue Straggler vs Standard Stars (1.83 - 1.95 M$_\odot$)', fontsize=16, fontweight='bold')
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=12)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.show()
    #plt.savefig('mass_grid_comparison.png', dpi=300, bbox_inches='tight')
    #print("Plot saved successfully to mass_grid_comparison.png")
