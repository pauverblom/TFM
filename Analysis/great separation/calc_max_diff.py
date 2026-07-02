import sys
import os
import numpy as np

# Añadir ruta del módulo
sys.path.append(os.path.abspath('../../Code'))
import pygyre as pg
import mesa_reader as mr

hand_picked_pairs = [
    (1.84, 4, 5, 69.7),
    (1.84, 16, 29, 46.0),
    (1.836, 20, 40, 35.7),
    (1.834, 24, 51, 25.6),
    (1.832, 28, 63, 14.8),
    (1.79, 38, 72, 0.8),
    (1.79, 45, 92, 0.1)
]

dir_bs = '/home/pauver/repos/pauverblom/TFM/MESA/evolve_created_blue_straggler'

def get_dir_compare(mass):
    path_finer = f'/home/pauver/repos/pauverblom/TFM/MESA/finer_mass_grid/mass_{mass}'
    path_coarse = f'/home/pauver/repos/pauverblom/TFM/MESA/mass_grid/mass_{mass}'
    if os.path.exists(path_finer):
        return path_finer
    return path_coarse

def get_center_h1(hist, idx, p_num):
    """Return center_h1 (%) for the model corresponding to profile p_num."""
    profile_numbers = idx.profile_numbers
    model_numbers   = idx.model_numbers
    if p_num not in profile_numbers:
        return None
    m_num = model_numbers[list(profile_numbers).index(p_num)]
    row = np.argmin(np.abs(hist.model_number - m_num))
    return float(hist.center_h1[row]) * 100.0   # mass fraction → percentage

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

# Cache history/index objects to avoid re-reading for same mass
hist_cache = {}
idx_cache  = {}

for idx_pair, (mass_compare, p_num_compare, p_num_bs, h_pct) in enumerate(hand_picked_pairs):
    dir_mass_compare = get_dir_compare(mass_compare)

    # Load comparison star history once per mass
    if mass_compare not in hist_cache:
        hist_cache[mass_compare] = mr.MesaData(f'{dir_mass_compare}/LOGS/history.data')
        idx_cache[mass_compare]  = mr.MesaProfileIndex(f'{dir_mass_compare}/LOGS/profiles.index')

    hist_compare = hist_cache[mass_compare]
    idx_compare  = idx_cache[mass_compare]

    h1_std = get_center_h1(hist_compare, idx_compare, p_num_compare)
    h1_std_str = f"{h1_std:.1f}" if h1_std is not None else "N/A"

    file_bs      = f"{dir_bs}/gyre_outputs/profile{p_num_bs}.data/summary.h5"
    file_compare = f"{dir_mass_compare}/gyre_outputs/profile{p_num_compare}.data/summary.h5"

    if not (os.path.exists(file_bs) and os.path.exists(file_compare)):
        continue

    s_bs      = pg.read_output(file_bs)
    s_compare = pg.read_output(file_compare)

    sg_bs      = s_bs.group_by('l')
    sg_compare = s_compare.group_by('l')

    print(f"Pair {idx_pair+1} (BS p={p_num_bs}, Std p={p_num_compare}, {mass_compare}M, "
          f"H_BSS={h_pct}%, H_std={h1_std_str}%):")

    max_diffs = {}
    for l_val in [0, 1, 2]:
        group_bs   = next((g for g in getattr(sg_bs,      'groups', []) if len(g['l']) > 0 and g['l'][0] == l_val), None)
        group_comp = next((g for g in getattr(sg_compare, 'groups', []) if len(g['l']) > 0 and g['l'][0] == l_val), None)

        dnus_b = get_dnus(group_bs)
        dnus_c = get_dnus(group_comp)

        common_n = set(dnus_b.keys()).intersection(dnus_c.keys())
        if common_n:
            max_diff = max(abs(dnus_b[n] - dnus_c[n]) for n in common_n)
            max_diffs[l_val] = max_diff
            print(f"  l={l_val}: {max_diff:.4f}")
        else:
            print(f"  l={l_val}: no common modes")

    if 0 in max_diffs and max_diffs[0] > 0:
        ratio = max_diffs.get(2, float('nan')) / max_diffs[0]
        print(f"  ratio l=2/l=0: {ratio:.1f}")
    print()
