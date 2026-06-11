import mesa_reader as mr
import matplotlib.pyplot as plt
import numpy as np

# Load the data
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = '/home/pauver/TFM/MESA/blue_straggler_model_create'
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
print("MESA BINARY SIMULATION REPORT: BLUE STRAGGLER FORMATION")
print("="*60)
print(f"Initial State:")
print(f"  Star 1 (Donor) Mass: {initial_m1:.3f} Msun")
print(f"  Star 2 (Accretor) Mass: {initial_m2:.3f} Msun")
print(f"  Orbital Period: {initial_period:.3f} days")
print("-" * 30)
print(f"Final State:")
print(f"  Star 1 Remnant Mass: {final_m1:.3f} Msun")
print(f"  Star 2 (BSS) Final Mass: {final_m2:.3f} Msun")
print(f"  Final Orbital Period: {final_period:.3f} days")
print("-" * 30)
print(f"Simulation Details:")
print(f"  Maximum Mass Transfer Rate: {max_mdot:.2e} Msun/yr")
print(f"  Total Duration: {bh.age[-1]:.2e} years")
print("="*60)
mask = bh.lg_mtransfer_rate > -60

# Create the visualization
fig = plt.figure(figsize=(18, 15))
plt.subplots_adjust(hspace=0.4, wspace=0.3)

# 1. Mass Evolution
ax1 = plt.subplot(3, 3, 1)
ax1.plot(bh.age[mask] / 1e9, bh.star_1_mass[mask], label='Donor (Star 1)', color='blue', linewidth=2)
ax1.plot(bh.age[mask] / 1e9, bh.star_2_mass[mask], label='Accretor (Star 2)', color='red', linewidth=2)
ax1.set_xlabel('Age (Gyr)')
ax1.set_ylabel('Mass ($M_\odot$)')
ax1.set_title('Mass Evolution')
ax1.legend()
ax1.grid(True, linestyle='--', alpha=0.7)

# 2. Orbital Evolution (Period and Separation)
ax2 = plt.subplot(3, 3, 2)
ax2.plot(bh.age[mask] / 1e9, bh.period_days[mask], color='purple', label='Period', linewidth=2)
ax2.set_xlabel('Age (Gyr)')
ax2.set_ylabel('Period (days)', color='purple')
ax2.tick_params(axis='y', labelcolor='purple')

ax2b = ax2.twinx()
ax2b.plot(bh.age[mask] / 1e9, bh.binary_separation[mask], color='green', label='Separation', linestyle='--')
ax2b.set_ylabel('Separation ($R_\odot$)', color='green')
ax2b.tick_params(axis='y', labelcolor='green')
ax2.set_title('Orbital Evolution')
ax2.grid(True, linestyle='--', alpha=0.7)

# 3. Mass Transfer Rate
ax3 = plt.subplot(3, 3, 3)
# Masking low mtransfer rates for better visualization
ax3.plot(bh.age[mask] / 1e9, bh.lg_mtransfer_rate[mask], color='black', linewidth=1.5)
ax3.set_xlabel('Age (Gyr)')
ax3.set_ylabel('$\log \dot{M}$ ($M_\odot/yr$)')
ax3.set_title('Mass Transfer Rate')
ax3.grid(True, linestyle='--', alpha=0.7)

# 4. HR Diagram for Star 1
ax4 = plt.subplot(3, 3, 4)
ax4.plot(h1.log_Teff, h1.log_L, color='blue', linewidth=2)
ax4.invert_xaxis()
ax4.set_xlabel('$\log T_{eff}$ (K)')
ax4.set_ylabel('$\log L/L_\odot$')
ax4.set_title('HR Diagram (Donor Star)')
ax4.grid(True, linestyle='--', alpha=0.7)

# 5. Center H and He for Star 1
ax5 = plt.subplot(3, 3, 5)
ax5.plot(h1.star_age / 1e9, h1.center_h1, color='blue', label='Center H1', linewidth=2)
ax5.plot(h1.star_age / 1e9, h1.center_he4, color='orange', label='Center He4', linewidth=2, linestyle='--')
ax5.set_xlabel('Age (Gyr)')
ax5.set_ylabel('Mass Fraction')
ax5.set_title('Central Abundances (Donor Star)')
ax5.legend()
ax5.grid(True, linestyle='--', alpha=0.7)

# 6. HR Diagram for Star 2
ax6 = plt.subplot(3, 3, 7)
ax6.plot(h2.log_Teff, h2.log_L, color='red', linewidth=2)
ax6.invert_xaxis()
ax6.set_xlabel('$\log T_{eff}$ (K)')
ax6.set_ylabel('$\log L/L_\odot$')
ax6.set_title('HR Diagram (Accretor Star)')
ax6.grid(True, linestyle='--', alpha=0.7)

# 7. Center H and He for Star 2
ax7 = plt.subplot(3, 3, 8)
ax7.plot(h2.star_age / 1e9, h2.center_h1, color='blue', label='Center H1', linewidth=2)
ax7.plot(h2.star_age / 1e9, h2.center_he4, color='orange', label='Center He4', linewidth=2, linestyle='--')
ax7.set_xlabel('Age (Gyr)')
ax7.set_ylabel('Mass Fraction')
ax7.set_title('Central Abundances (Accretor Star)')
ax7.legend()
ax7.grid(True, linestyle='--', alpha=0.7)

plt.suptitle('Detailed Binary Evolution Insights', fontsize=18)
plt.savefig(script_dir + '/binary_evolution_visualization.png', dpi=300, bbox_inches='tight')
print(f"\nVisualization saved as '{script_dir}/binary_evolution_visualization.png'")
plt.show()