import mesa_reader as mr
import matplotlib.pyplot as plt
import numpy as np
import os

bss_dir = '/home/pauver/TFM/MESA/evolve_created_blue_straggler'
grid_dir = '/home/pauver/TFM/MESA/evolve_mass_grid'

print("Loading Blue Straggler history...")
hist_bs = mr.MesaData(f'{bss_dir}/LOGS/history.data')

orig_dir = '/home/pauver/TFM/MESA/evolve_1.8_mass_star'
print("Loading Original 1.82 M_sun history...")
hist_orig = mr.MesaData(f'{orig_dir}/LOGS/history.data')

plt.figure(figsize=(12, 8))

# Plot the base Blue Straggler prominently
plt.plot(hist_bs.log_Teff, hist_bs.log_L, color='black', linewidth=4, label='Blue Straggler Target', zorder=100)

# Plot the original 1.82... mass track prominently
plt.plot(hist_orig.log_Teff, hist_orig.log_L, color='red', linewidth=3, linestyle='--', label=r'Original 1.82 M$_\odot$', zorder=90)

masses = np.round(np.arange(1.83, 1.96, 0.01), 2)
cmap = plt.get_cmap('viridis')

print("Loading grid histories...")
plotted_any = False
for i, m in enumerate(masses):
    m_dir = f'{grid_dir}/mass_{m:.2f}'
    hist_file = f'{m_dir}/LOGS/history.data'
    
    if os.path.exists(hist_file):
        try:
            hist = mr.MesaData(hist_file)
            color = cmap(i / len(masses))
            plt.plot(hist.log_Teff, hist.log_L, color=color, linewidth=2, alpha=0.8, label=rf'{m:.2f} M$_\odot$')
            plotted_any = True
        except Exception as e:
            print(f"Skipping {m_dir} (possibly incomplete): {e}")
    else:
        print(f"History file not found yet for {m_dir}...")

if not plotted_any:
    print("No grid data available to plot yet. Wait for mesa-go to finish a few runs!")
else:
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
