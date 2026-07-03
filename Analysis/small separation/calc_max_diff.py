"""
calc_max_diff.py  –  small separation
Computes the maximum absolute difference in the small separation
    δν_02(n) = ν(n, l=0) − ν(n−1, l=2)
between the Blue Straggler and each comparison star, restricted to
n_pg ∈ [-10, 10] for l=0 and n_pg ∈ [-11, 9] for l=2 (i.e. the
matching partner n-1 lives in [-11, 9]).

Usage:  run from this directory with the TFM .venv active.
"""

import sys
import os
import numpy as np

sys.path.append(os.path.abspath('../../Code'))
import pygyre as pg
import mesa_reader as mr

hand_picked_pairs = [
    (1.84,  4,   5,  69.7),
    (1.84,  16,  29, 46.0),
    (1.836, 20,  40, 35.7),
    (1.834, 24,  51, 25.6),
    (1.832, 28,  63, 14.8),
    (1.79,  38,  72,  0.8),
    (1.79,  45,  92,  0.1),
]

dir_bs = '/home/pauver/repos/pauverblom/TFM/MESA/evolve_created_blue_straggler'

def get_dir_compare(mass):
    path_finer  = f'/home/pauver/repos/pauverblom/TFM/MESA/finer_mass_grid/mass_{mass}'
    path_coarse = f'/home/pauver/repos/pauverblom/TFM/MESA/mass_grid/mass_{mass}'
    return path_finer if os.path.exists(path_finer) else path_coarse

def get_center_h1(hist, idx, p_num):
    """Return center_h1 (%) for the model corresponding to profile p_num."""
    profile_numbers = idx.profile_numbers
    model_numbers   = idx.model_numbers
    if p_num not in profile_numbers:
        return None
    m_num = model_numbers[list(profile_numbers).index(p_num)]
    row   = np.argmin(np.abs(hist.model_number - m_num))
    return float(hist.center_h1[row]) * 100.0

def get_small_sep(group_l0, group_l2):
    """
    Compute δν_02(n) = ν(n, l=0) − ν(n−1, l=2) for all n where both
    ν(n, l=0) and ν(n−1, l=2) exist.
    Returns dict  n → δν_02(n).
    """
    if group_l0 is None or group_l2 is None:
        return {}

    n_l0  = np.array(group_l0['n_pg'])
    f_l0  = np.array(group_l0['freq'].real)
    n_l2  = np.array(group_l2['n_pg'])
    f_l2  = np.array(group_l2['freq'].real)

    freq_l2 = {int(n): float(f) for n, f in zip(n_l2, f_l2)}

    result = {}
    for n, f0 in zip(n_l0, f_l0):
        n = int(n)
        if -10 <= n <= 10 and (n - 1) in freq_l2:
            result[n] = float(f0) - freq_l2[n - 1]
    return result

# Cache MESA objects
hist_cache = {}
idx_cache  = {}

print(f"{'Pair':<45} {'H_c (%)':>7}  {'|Δ(δν_02)|_max':>15}")
print("-" * 75)

for idx_pair, (mass_compare, p_num_compare, p_num_bs, h_pct) in enumerate(hand_picked_pairs):
    dir_mass_compare = get_dir_compare(mass_compare)

    if mass_compare not in hist_cache:
        hist_cache[mass_compare] = mr.MesaData(f'{dir_mass_compare}/LOGS/history.data')
        idx_cache[mass_compare]  = mr.MesaProfileIndex(f'{dir_mass_compare}/LOGS/profiles.index')

    hist_compare = hist_cache[mass_compare]
    idx_compare  = idx_cache[mass_compare]

    h1_std     = get_center_h1(hist_compare, idx_compare, p_num_compare)
    h1_std_str = f"{h1_std:.1f}" if h1_std is not None else "N/A"

    file_bs      = f"{dir_bs}/gyre_outputs/profile{p_num_bs}.data/summary.h5"
    file_compare = f"{dir_mass_compare}/gyre_outputs/profile{p_num_compare}.data/summary.h5"

    if not (os.path.exists(file_bs) and os.path.exists(file_compare)):
        print(f"  [skipping pair {idx_pair+1}: files not found]")
        continue

    s_bs      = pg.read_output(file_bs)
    s_compare = pg.read_output(file_compare)

    sg_bs      = s_bs.group_by('l')
    sg_compare = s_compare.group_by('l')

    def get_group(sg, l_val):
        return next((g for g in getattr(sg, 'groups', [])
                     if len(g['l']) > 0 and g['l'][0] == l_val), None)

    ss_bs   = get_small_sep(get_group(sg_bs,      0), get_group(sg_bs,      2))
    ss_comp = get_small_sep(get_group(sg_compare, 0), get_group(sg_compare, 2))

    common_n = set(ss_bs.keys()).intersection(ss_comp.keys())
    if common_n:
        max_diff = max(abs(ss_bs[n] - ss_comp[n]) for n in common_n)
        result_str = f"{max_diff:.4f}"
    else:
        result_str = "N/A"

    label = f"Par {idx_pair+1} ({mass_compare} M_sun, H_BSS={h_pct}%, H_std={h1_std_str}%)"
    print(f"{label:<45} {h_pct:>7.1f}  {result_str:>15}")

print()
print("Done.")
