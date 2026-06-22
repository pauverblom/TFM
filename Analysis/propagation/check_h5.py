import h5py
import glob

files = glob.glob('/Users/pauverdeguer/TFM/MESA/mass_grid/mass_1.83/gyre_temp_out/detail.l1.*.h5')
if files:
    with h5py.File(files[0], 'r') as f:
        xi_r = f['xi_r']['re'][:]
        x = f['x'][:]
        print("x limits:", x[0], x[-1])
        print("xi_r[0]:", xi_r[0], "xi_r[-1]:", xi_r[-1])
        print("omega attrs:", f.attrs['omega'])
        print("n_pg:", f.attrs['n_pg'])
