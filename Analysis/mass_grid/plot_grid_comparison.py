import mesa_reader as mr
import matplotlib.pyplot as plt
import numpy as np
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
mesa_dir = os.path.abspath(os.path.join(script_dir, '..', '..', 'MESA'))

bss_dir = os.path.join(mesa_dir, 'evolve_created_blue_straggler')
grid_dir = os.path.join(mesa_dir, 'mass_grid')

# Fracciones de hidrógeno central en las que colocar puntos de hitos
xc_milestones = [0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.005]
# Tamaños de marcador: el más grande para Xc=0.6, el más pequeño para Xc=0.1
xc_marker_sizes = [130, 110, 90, 70, 50, 30, 20]


def plot_xc_dots(hist, color, zorder):
    """Graficar puntos en la trayectoria en los hitos de hidrógeno central."""
    xc = hist.center_h1
    for xc_val, sz in zip(xc_milestones, xc_marker_sizes):
        idx = np.argmin(np.abs(xc - xc_val))
        plt.scatter(hist.log_Teff[idx], hist.log_L[idx],
                    s=sz, color=color, edgecolors='black', linewidths=0.5,
                    zorder=zorder)


print("Cargando el historial de la Rezagada Azul...")
hist_bs = mr.MesaData(f'{bss_dir}/LOGS/history.data')

orig_dir = os.path.join(mesa_dir, 'evolve_1.8_mass_star')
print("Cargando historial Original de 1.82 M_sun...")
hist_orig = mr.MesaData(f'{orig_dir}/LOGS/history.data')

plt.figure(figsize=(8, 8))

# Graficar la Rezagada Azul base de forma prominente
plt.plot(hist_bs.log_Teff, hist_bs.log_L, color='blue', linewidth=4, label='Blue Straggler', zorder=100)
plot_xc_dots(hist_bs, 'blue', zorder=101)

cmap = plt.get_cmap('viridis')
masses = np.round(np.arange(1.75, 1.90, 0.01), 2)

print("Cargando historiales del grid...")
plotted_any = False
for i, m in enumerate(masses):
    m_dir = f'{grid_dir}/mass_{m:.2f}'
    hist_file = f'{m_dir}/LOGS/history.data'
    
    if os.path.exists(hist_file):
        try:
            hist = mr.MesaData(hist_file)
            color = cmap((i) / len(masses))
            plt.plot(hist.log_Teff, hist.log_L, color=color, linewidth=2, alpha=0.8)
            plot_xc_dots(hist, color, zorder=50)
            plotted_any = True
        except Exception as e:
            print(f"Saltando {m_dir} (posiblemente incompleto): {e}")
    else:
        print(f"El archivo de historial aún no se encuentra para {m_dir}...")

if not plotted_any:
    print("Aún no hay datos del grid disponibles para graficar. ¡Espera a que mesa-go termine algunas ejecuciones!")
else:
    # Añadir una entrada de leyenda para los puntos de hitos (un disperso representativo por tamaño)
    for xc_val, sz in zip(xc_milestones, xc_marker_sizes):
        plt.scatter([], [], s=sz, color='grey', edgecolors='black', linewidths=0.5,
                    label = rf'$X_{{Hc}} = {xc_val}$')

    plt.gca().invert_xaxis()
    plt.xlabel(r'$\log T_{\rm eff}$', fontsize=14, fontweight='bold')
    plt.ylabel(r'$\log L/L_\odot$', fontsize=14, fontweight='bold')
    
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=min(masses), vmax=max(masses)))
    cbar = plt.colorbar(sm, ax=plt.gca(), aspect=40, pad=0.02)
    cbar.set_label(r'Masa ($M_\odot$)', fontsize=14)

    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), fontsize=12, ncol=4, frameon=False)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.savefig('mass_grid_comparison.png', dpi=300, bbox_inches='tight')
    print("Gráfico guardado exitosamente en mass_grid_comparison.png")
