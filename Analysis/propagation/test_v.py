import h5py
import glob

files = glob.glob('/Users/pauverdeguer/TFM/MESA/mass_grid/mass_1.83/gyre_temp_out/detail.l1.*.h5')
with h5py.File(files[0], 'r') as f:
    x_bg = f['x'][:]
    if 'V_2' in f.keys():
        V_2 = f['V_2'][:]
        print("V_2:", V_2[10])
    if 'V' in f.keys():
        V = f['V'][:]
        print("V directly available:", V[10])
    print("x:", x_bg[10])

