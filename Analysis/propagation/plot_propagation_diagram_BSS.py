#!/usr/bin/env python3
import h5py
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
from matplotlib.lines import Line2D

data_dir = '/Users/pauverdeguer/TFM/MESA/evolve_created_blue_straggler/gyre_temp_output'
output_dir = '/Users/pauverdeguer/TFM/Analysis/propagation'

l1_files = sorted(glob.glob(os.path.join(data_dir, 'detail.l1.*.h5')))

if not l1_files:
    print("No detail files found for l=1.")
    exit(1)

# Read background from the first file
with h5py.File(l1_files[0], 'r') as f:
    x_bg = f['x'][:]
    V_2 = f['V_2'][:]
    V = V_2 * x_bg**2
    As = f['As'][:]
    c_1 = f['c_1'][:]
    Gamma_1 = f['Gamma_1'][:]

l = 1
# Handle division by zero or invalid values
with np.errstate(divide='ignore', invalid='ignore'):
    N2 = As / c_1
    Sl2 = l * (l + 1) * Gamma_1 / (V * c_1)

# Plotting
fig, ax = plt.subplots(figsize=(10, 12))

# Plot N2 and Sl2 curves (x on X-axis, N2/Sl2 on Y-axis)
ax.plot(x_bg, N2, label=r'$N^2$', color='black', linestyle='-', linewidth=2)
ax.plot(x_bg, Sl2, label=r'$S_1^2$', color='black', linestyle='-.', linewidth=2)

ax.set_yscale('log')
ax.set_xlim(0, 1)

all_omega2 = []

for file_path in l1_files:
    try:
        with h5py.File(file_path, 'r') as f:
            n_pg = f.attrs['n_pg']
            omega = f.attrs['omega']['re']
            omega2 = omega**2
            all_omega2.append(omega2)
            
            xi_r = f['xi_r']['re'][:]
            x_val = f['x'][:]
            
            # Find nodes where xi_r crosses 0
            crossings = np.where(np.diff(np.signbit(xi_r)))[0]
            
            nodes_x = []
            for i in crossings:
                x0, x1 = x_val[i], x_val[i+1]
                y0, y1 = xi_r[i], xi_r[i+1]
                if y1 - y0 != 0:
                    x_node = x0 - y0 * (x1 - x0) / (y1 - y0)
                    nodes_x.append(x_node)
                    
            # Determine label and color based on mode type
            show_label = True
            if n_pg > 0:
                lbl = f"p{n_pg}"
                mode_color = 'blue'
            elif n_pg < 0:
                g_num = -n_pg
                lbl = f"g{g_num}"
                mode_color = 'red'
                # Only show label for g-modes up to 10, or every 10 modes after that
                if g_num > 10 and g_num % 10 != 0:
                    show_label = False
            else:
                lbl = "f"
                mode_color = 'purple'
                
            # Plot horizontal line for the mode
            ax.axhline(omega2, color=mode_color, linestyle=':', alpha=0.5, linewidth=1.5,)
            
            # Plot nodes on the horizontal line
            if nodes_x:
                ax.scatter(nodes_x, [omega2]*len(nodes_x), color=mode_color, s=15, zorder=3)
                
            # Add label to the right side of the plot if applicable
            if show_label:
                ax.text(1.01, omega2, lbl, va='center', ha='left', fontsize=8, color=mode_color, clip_on=False)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

# Include max(N2) when determining y-limits
if all_omega2:
    min_w2 = max(min(all_omega2) * 0.8, 1e-6)
    max_w2 = 2e3
    #ax.set_ylim(min_w2, max_w2)

ax.set_xlabel('Radio Fraccional ($x$)', fontsize=14)
ax.set_ylabel(r'Frecuencia adimensional al Cuadrado ($\omega^2$)', fontsize=14)
ax.set_title('Diagrama de Propagación con nodos ($l=1$)', fontsize=16)

# Create custom legend entries
custom_lines = [
    Line2D([0], [0], color='black', lw=2, linestyle='-'),
    Line2D([0], [0], color='black', lw=2, linestyle='-.'),
    Line2D([0], [0], color='blue', alpha=0.5, lw=1.5),
    Line2D([0], [0], color='red', alpha=0.5, lw=1.5),
]
ax.legend(custom_lines, [r'$N^2$', r'$S_1^2$', 'p-modes', 'g-modes'], loc='lower right', fontsize=12)

ax.grid(True, which="both", ls="--", alpha=0.2)

plt.tight_layout()
# Adjust margins so the text outside the axes fits nicely
fig.subplots_adjust(right=0.92)

out_file = os.path.join(output_dir, 'propagation_diagram.png')
plt.savefig(out_file, dpi=300, bbox_inches='tight')
print(f"Diagram saved to {out_file}")
