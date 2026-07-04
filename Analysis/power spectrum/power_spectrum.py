import pygyre as pg
import matplotlib.pyplot as plt
import os
import numpy as np

# Directory of the Blue Straggler
dir_bs = '/home/pauver/repos/pauverblom/TFM/MESA/evolve_created_blue_straggler'
# We use the first profile (profile1.data)
file_bs = f'{dir_bs}/gyre_outputs/profile1.data/summary.h5'

out_dir = 'plots'
os.makedirs(out_dir, exist_ok=True)
out_dir_tex = '/home/pauver/repos/pauverblom/TFM/TeX/Imagenes/power_spectrum'
os.makedirs(out_dir_tex, exist_ok=True)

try:
    s_bs = pg.read_output(file_bs)
    sg_bs = s_bs.group_by('l')
except Exception as e:
    print(f"Error leyendo el archivo GYRE: {e}")
    exit(1)

# GYRE is a linear adiabatic pulsation code, so it does not compute true amplitudes.
# However, we can use the normalized mode inertia (E_norm) as a proxy.
# Modes with lower inertia are generally easier to excite to higher observable amplitudes.
# We plot 1 / E_norm to simulate a power spectrum.

fig, ax = plt.subplots(figsize=(10, 5))

colors = {0: '#e74c3c', 1: '#3498db', 2: '#2ecc71'}
labels = {0: '$l=0$', 1: '$l=1$', 2: '$l=2$'}
markers = {0: 'o', 1: '^', 2: 's'}

bottom_limit = 0.1

for g in sg_bs.groups:
    if len(g['l']) > 0:
        l_val = g['l'][0]
        if l_val in colors:
            freq = np.array(g['freq'].real)
            e_norm = np.array(g['E_norm'])
            power_proxy = 1.0 / e_norm
            
            # Draw vertical lines down to the bottom limit for the stick plot effect
            ax.vlines(freq, bottom_limit, power_proxy, color=colors[l_val], alpha=0.5, linewidth=2)
            # Add markers at the top of the sticks
            ax.scatter(freq, power_proxy, color=colors[l_val], marker=markers[l_val], s=40, label=labels[l_val], zorder=3)

ax.set_yscale('log')
ax.set_ylim(bottom=bottom_limit)
ax.set_xlabel(r'Frecuencia (ciclos/día)', fontsize=12)
ax.set_ylabel(r'Amplitud proxy ($1/E_{\rm norm}$)', fontsize=12)
ax.set_title('Espectro de Potencia Teórico (Blue Straggler, Perfil 1)', fontsize=14, pad=15)

ax.grid(True, which='major', linestyle='-', color='gray', alpha=0.3)
ax.grid(True, which='minor', linestyle=':', color='gray', alpha=0.2)
ax.legend(fontsize=11)

plt.tight_layout()

out_filename = f'{out_dir}/power_spectrum_profile1.png'
out_filename_tex = f'{out_dir_tex}/power_spectrum_profile1.png'
plt.savefig(out_filename, dpi=300, bbox_inches='tight')
plt.savefig(out_filename_tex, dpi=300, bbox_inches='tight')
print(f"Guardado en {out_filename}")
print(f"Guardado en {out_filename_tex}")
