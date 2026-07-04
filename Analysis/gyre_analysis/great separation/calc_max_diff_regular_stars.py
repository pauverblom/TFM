import sys
import os
import numpy as np

# Añadir ruta del módulo
sys.path.append(os.path.abspath('../../Code'))
import pygyre as pg
import mesa_reader as mr

mass_1 = 1.832
mass_2 = 1.834

dir_1 = f'/home/pauver/repos/pauverblom/TFM/MESA/finer_mass_grid/mass_{mass_1}'
dir_2 = f'/home/pauver/repos/pauverblom/TFM/MESA/finer_mass_grid/mass_{mass_2}'

hand_picked_pairs = [
    # (p_num_1, p_num_2, h_pct)
    (9, 9, 64.5),
    (27, 27, 17.9),
    (43, 43, 0.1)
]

def get_dnus(group):
    if group is None:
        return {}
    n_pg = np.array(group['n_pg'])
    freq = np.array(group['freq'].real)
    sort_idx = np.argsort(n_pg)
    n_pg = n_pg[sort_idx]
    freq = freq[sort_idx]
    dnus = {}
    for i in range(1, len(n_pg)):
        if n_pg[i] == n_pg[i-1] + 1:
            if -10 <= n_pg[i] <= 10 and -10 <= n_pg[i-1] <= 10:
                dnus[n_pg[i]] = freq[i] - freq[i-1]
    return dnus

print("Calculando diferencias máximas...")

for idx_pair, (p_num_1, p_num_2, h_pct) in enumerate(hand_picked_pairs):
    file_1 = f"{dir_1}/gyre_outputs/profile{p_num_1}.data/summary.h5"
    file_2 = f"{dir_2}/gyre_outputs/profile{p_num_2}.data/summary.h5"

    if not (os.path.exists(file_1) and os.path.exists(file_2)):
        print(f"Archivos faltantes para el par {idx_pair + 1}")
        continue

    s_1 = pg.read_output(file_1)
    s_2 = pg.read_output(file_2)

    sg_1 = s_1.group_by('l')
    sg_2 = s_2.group_by('l')

    print(f"Par {idx_pair+1} ({mass_1}M p={p_num_1} vs {mass_2}M p={p_num_2}, H_c ~ {h_pct}%):")

    max_diffs = {}
    for l_val in [0, 1, 2]:
        group_1 = next((g for g in getattr(sg_1, 'groups', []) if len(g['l']) > 0 and g['l'][0] == l_val), None)
        group_2 = next((g for g in getattr(sg_2, 'groups', []) if len(g['l']) > 0 and g['l'][0] == l_val), None)

        dnus_1 = get_dnus(group_1)
        dnus_2 = get_dnus(group_2)

        common_n = set(dnus_1.keys()).intersection(dnus_2.keys())
        if common_n:
            max_diff = max(abs(dnus_1[n] - dnus_2[n]) for n in common_n)
            max_diffs[l_val] = max_diff
            print(f"  l={l_val}: {max_diff:.4f}")
        else:
            print(f"  l={l_val}: no common modes")

    if 0 in max_diffs and max_diffs[0] > 0:
        ratio = max_diffs.get(2, float('nan')) / max_diffs[0]
        print(f"  ratio l=2/l=0: {ratio:.1f}")
    print()
