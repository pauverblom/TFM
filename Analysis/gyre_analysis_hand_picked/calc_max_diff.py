"""
calc_max_diff.py  –  gyre_analysis_hand_picked
Computes the maximum absolute difference in individual mode frequencies
    |ν_comp(n,l) − ν_BS(n,l)|
for each hand-picked (pair, l) combination, restricted to n_pg ∈ [-10, 10].

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
    return float(hist.center_h1[row]) * 100.0   # mass fraction → %

def get_freqs(group):
    """Return dict  n_pg → frequency (c/d)  for n_pg ∈ [-10, 10]."""
    if group is None:
        return {}
    n_pg = np.array(group['n_pg'])
    freq = np.array(group['freq'].real)
    mask = (n_pg >= -10) & (n_pg <= 10)
    return {int(n): float(f) for n, f in zip(n_pg[mask], freq[mask])}

# Cache MESA history/index objects
hist_cache = {}
idx_cache  = {}

print(f"{'Pair':<45} {'H_c (%)':>7}  "
      f"{'|Δν|_max l=0':>12}  {'|Δν|_max l=1':>12}  {'|Δν|_max l=2':>12}  "
      f"{'r=l2/l0':>8}")
print("-" * 110)

for idx_pair, (mass_compare, p_num_compare, p_num_bs, h_pct) in enumerate(hand_picked_pairs):
    dir_mass_compare = get_dir_compare(mass_compare)

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
        print(f"  [skipping pair {idx_pair+1}: files not found]")
        continue

    s_bs      = pg.read_output(file_bs)
    s_compare = pg.read_output(file_compare)

    sg_bs      = s_bs.group_by('l')
    sg_compare = s_compare.group_by('l')

    max_diffs = {}
    for l_val in [0, 1, 2]:
        group_bs   = next((g for g in getattr(sg_bs,      'groups', [])
                           if len(g['l']) > 0 and g['l'][0] == l_val), None)
        group_comp = next((g for g in getattr(sg_compare, 'groups', [])
                           if len(g['l']) > 0 and g['l'][0] == l_val), None)

        freqs_bs   = get_freqs(group_bs)
        freqs_comp = get_freqs(group_comp)

        common_n = set(freqs_bs.keys()).intersection(freqs_comp.keys())
        if common_n:
            max_diff = max(abs(freqs_bs[n] - freqs_comp[n]) for n in common_n)
            max_diffs[l_val] = max_diff
        else:
            max_diffs[l_val] = float('nan')

    ratio = (max_diffs.get(2, float('nan')) / max_diffs.get(0, float('nan')))

    label = f"Par {idx_pair+1} ({mass_compare} M_sun, H_BSS={h_pct}%, H_std={h1_std_str}%)"
    print(f"{label:<45} {h_pct:>7.1f}  "
          f"{max_diffs.get(0, float('nan')):>12.4f}  "
          f"{max_diffs.get(1, float('nan')):>12.4f}  "
          f"{max_diffs.get(2, float('nan')):>12.4f}  "
          f"{ratio:>8.1f}")

print()
print("Done.")
