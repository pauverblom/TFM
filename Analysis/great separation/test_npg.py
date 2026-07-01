import pygyre as pg
import numpy as np

file_bs = '/Users/pauverdeguer/TFM/MESA/evolve_created_blue_straggler/gyre_outputs/profile21.data/summary.h5'
s_bs = pg.read_output(file_bs)
sg_bs = s_bs.group_by('l')
for g in sg_bs.groups:
    if len(g['l']) > 0:
        l = g['l'][0]
        n_pg = np.sort(g['n_pg'])
        print(f"l={l}, n_pg={n_pg}")
