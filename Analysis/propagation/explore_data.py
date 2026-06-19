#!/usr/bin/env python3
"""Quick exploration of GYRE output files to understand available data."""

import h5py
import numpy as np
import glob
import os

data_dir = '/Users/pauverdeguer/TFM/MESA/evolve_created_blue_straggler/mesa_temp_output'

# 1) Explore summary file
print("=" * 60)
print("SUMMARY FILE")
print("=" * 60)
with h5py.File(os.path.join(data_dir, 'summary.h5'), 'r') as f:
    print("Keys (datasets):", list(f.keys()))
    print("Attrs:", dict(f.attrs))
    for key in f.keys():
        print(f"  {key}: shape={f[key].shape}, dtype={f[key].dtype}")
        if f[key].shape[0] < 200:
            print(f"    values={f[key][:]}")

# 2) Explore one l=1 detail file
print("\n" + "=" * 60)
print("DETAIL FILE: detail.l1.n-1.h5")
print("=" * 60)
with h5py.File(os.path.join(data_dir, 'detail.l1.n-1.h5'), 'r') as f:
    print("Keys (datasets):", list(f.keys()))
    print("Attrs:", dict(f.attrs))
    for key in f.keys():
        print(f"  {key}: shape={f[key].shape}, dtype={f[key].dtype}")

# 3) List all l=1 files
print("\n" + "=" * 60)
print("ALL l=1 FILES")
print("=" * 60)
l1_files = sorted(glob.glob(os.path.join(data_dir, 'detail.l1.*.h5')))
for f in l1_files:
    print(os.path.basename(f))
print(f"\nTotal: {len(l1_files)} files")
