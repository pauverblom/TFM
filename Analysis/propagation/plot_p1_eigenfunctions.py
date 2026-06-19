#!/usr/bin/env python3
import h5py
import matplotlib.pyplot as plt
import numpy as np
import os

data_dir = '/Users/pauverdeguer/TFM/MESA/evolve_created_blue_straggler/mesa_temp_output'
output_dir = '/Users/pauverdeguer/TFM/Analysis/propagation'

# Path to the p1 mode file
file_path = os.path.join(data_dir, 'detail.l1.n+5.h5')

if not os.path.exists(file_path):
    print(f"File {file_path} not found.")
    exit(1)

with h5py.File(file_path, 'r') as f:
    x = f['x'][:]
    xi_r = f['xi_r']['re'][:]
    xi_h = f['xi_h']['re'][:]
    n_pg = f.attrs['n_pg']
    l = f.attrs['l']

fig, ax = plt.subplots(figsize=(12, 6))

ax.plot(x, xi_r, label=r'$\xi_r$ (Desplazamiento Radial)', color='blue', linewidth=2)
ax.plot(x, xi_h, label=r'$\xi_h$ (Desplazamiento Horizontal)', color='red', linewidth=2)

# Find and plot the nodes for xi_r
crossings = np.where(np.diff(np.signbit(xi_r)))[0]
for i in crossings:
    x0, x1 = x[i], x[i+1]
    y0, y1 = xi_r[i], xi_r[i+1]
    if y1 - y0 != 0:
        x_node = x0 - y0 * (x1 - x0) / (y1 - y0)
        ax.plot(x_node, 0, 'ko', markersize=6, zorder=3)

# Add a label for the nodes in the legend
ax.plot([], [], 'ko', label=r'Nodos de $\xi_r$')

ax.axhline(0, color='gray', linestyle='--', alpha=0.5)

ax.set_xlabel('Radio Fraccional ($x$)', fontsize=14)
ax.set_ylabel('Amplitud de las Autofunciones', fontsize=14)
ax.set_title(f'Autofunciones para el Modo p1 ($l={l}, n_{{pg}}={n_pg}$)', fontsize=16)
ax.set_ylim(-1,1)
ax.legend(fontsize=12)
ax.grid(True, which="both", ls="--", alpha=0.3)

plt.tight_layout()
out_file = os.path.join(output_dir, 'p1_eigenfunctions.png')
plt.savefig(out_file, dpi=300, bbox_inches='tight')
print(f"Diagram saved to {out_file}")
