import os
import mesa_reader as mr
import matplotlib.pyplot as plt

script_dir = '/Users/pauverdeguer/TFM/Analysis/visualization'
data_dir = '/Users/pauverdeguer/TFM/MESA/blue_straggler_model_create/LOGS2'
out_dir = '/Users/pauverdeguer/TFM/TeX/Imagenes'
os.makedirs(out_dir, exist_ok=True)

profile_path = os.path.join(data_dir, 'profile97.data')
p = mr.MesaData(profile_path)

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12.6, 6.5), sharex=True)
fig.subplots_adjust(hspace=0.2, bottom=0.15)

m = p.mass
x_H = p.x_mass_fraction_H
y_He = p.y_mass_fraction_He
z_Z = p.z_mass_fraction_metals

# Colores consistentes
color_H = 'crimson'
color_He = 'indigo'
color_Z = 'forestgreen'

# Plot 1: Hidrógeno
ax1.plot(m, x_H, label='Hidrógeno (X)', color=color_H, linewidth=2.5)
ax1.set_ylabel('X', fontsize=14)
ax1.set_ylim(0.66, 0.70)

# Plot 2: Helio
ax2.plot(m, y_He, label='Helio (Y)', color=color_He, linewidth=2.5)
ax2.set_ylabel('Y', fontsize=14)
ax2.set_ylim(0.28, 0.32)

# Plot 3: Metales
ax3.plot(m, z_Z, label='Metales (Z)', color=color_Z, linewidth=2.5)
ax3.set_ylabel('Z', fontsize=14)
ax3.set_xlabel('Coordenada de Masa ($M_\odot$)', fontsize=14)
ax3.set_ylim(0.02, 0.0206)
ax3.set_xlim(0, max(m))

fig.suptitle('Perfil de Abundancias de la Blue Straggler post-transferencia', fontsize=16, y=0.95)

for ax in (ax1, ax2, ax3):
    ax.tick_params(axis='both', colors='black', labelsize=12)
    for spine in ax.spines.values():
        spine.set_edgecolor('black')
    ax.grid(True, linestyle='--', alpha=0.7)

# Leyenda combinada en la parte inferior
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
lines3, labels3 = ax3.get_legend_handles_labels()

fig.legend(lines1 + lines2 + lines3, labels1 + labels2 + labels3, 
           loc='lower center', ncol=3, bbox_to_anchor=(0.5, -0.05), fontsize=14, frameon=False)

fig.savefig(os.path.join(out_dir, 'bss_radial_profile.png'), dpi=300, bbox_inches='tight')
print(f"Figura guardada en {os.path.join(out_dir, 'bss_radial_profile.png')}")
