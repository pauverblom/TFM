import mesa_reader as mr
import matplotlib.pyplot as plt
import numpy as np

# Load the data
binary_history_path = '/Users/pauverdeguer/TFM/MESA/blue_straggler_gyre/binary_history.data'
history_star2_path = '/Users/pauverdeguer/TFM/MESA/blue_straggler_gyre/LOGS2/history.data'

try:
    bh = mr.MesaData(binary_history_path)
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

# Create the visualization
fig = plt.figure(figsize=(15, 12))
plt.subplots_adjust(hspace=0.3, wspace=0.3)

# 1. Mass Evolution
ax1 = plt.subplot(2, 2, 1)
ax1.plot(bh.age / 1e9, bh.star_1_mass, label='Donor (Star 1)', color='blue', linewidth=2)
ax1.plot(bh.age / 1e9, bh.star_2_mass, label='Accretor (Star 2)', color='red', linewidth=2)
ax1.set_xlabel('Age (Gyr)')
ax1.set_ylabel('Mass ($M_\odot$)')
ax1.set_title('Mass Evolution')
ax1.legend()
ax1.grid(True, linestyle='--', alpha=0.7)

# 2. Orbital Evolution (Period and Separation)
ax2 = plt.subplot(2, 2, 2)
ax2.plot(bh.age / 1e9, bh.period_days, color='purple', label='Period', linewidth=2)
ax2.set_xlabel('Age (Gyr)')
ax2.set_ylabel('Period (days)', color='purple')
ax2.tick_params(axis='y', labelcolor='purple')

ax2b = ax2.twinx()
ax2b.plot(bh.age / 1e9, bh.binary_separation, color='green', label='Separation', linestyle='--')
ax2b.set_ylabel('Separation ($R_\odot$)', color='green')
ax2b.tick_params(axis='y', labelcolor='green')
ax2.set_title('Orbital Evolution')
ax2.grid(True, linestyle='--', alpha=0.7)

# 3. HR Diagram for Star 2
ax3 = plt.subplot(2, 2, 3)
ax3.plot(h2.log_Teff, h2.log_L, color='orange', linewidth=2)
ax3.invert_xaxis()
ax3.set_xlabel('$\log T_{eff}$ (K)')
ax3.set_ylabel('$\log L/L_\odot$')
ax3.set_title('HR Diagram (Accretor Star)')
ax3.grid(True, linestyle='--', alpha=0.7)

# 4. Mass Transfer Rate
ax4 = plt.subplot(2, 2, 4)
# Masking low mtransfer rates for better visualization
mask = bh.lg_mtransfer_rate > -12
ax4.plot(bh.age[mask] / 1e9, bh.lg_mtransfer_rate[mask], color='black', linewidth=1.5)
ax4.set_xlabel('Age (Gyr)')
ax4.set_ylabel('$\log \dot{M}$ ($M_\odot/yr$)')
ax4.set_title('Mass Transfer Rate')
ax4.grid(True, linestyle='--', alpha=0.7)

plt.suptitle('Detailed Binary Evolution Insights', fontsize=18)
plt.savefig('binary_evolution_report.png')
print("\nVisualization saved as 'binary_evolution_report.png'")
plt.show()