import wsssss
import numpy as np
import os
from wsssss.inlists.create_grid import MesaGrid

base_dir = '/home/pauver/TFM/MESA/evolve_1.8_mass_star'
grid_dir = '/home/pauver/TFM/MESA/mass_grid'

# Create grid generator
grid = MesaGrid(
    mesa_dir='/home/pauver/mesa/mesa-26.04.1',
    inlist_filename='inlist',
    starjob_filename='inlist_project',
    controls_filename='inlist_project',
    eos_filename='inlist_project',
    kap_filename='inlist_project',
    pgstar_filename='inlist_pgstar'
)

# Add MESA execution files explicitly so they are copied into each grid subfolder
for f in ['clean', 'mk', 'rn', 're', 'gyre.in', 'run_gyre_all.sh']:
    grid.add_file(os.path.join(base_dir, f))
for d in ['src', 'make']:
    grid.add_dir(os.path.join(base_dir, d))

# Override with an array of initial masses
masses = np.round(np.arange(1.75, 1.90, 0.01), 2)
grid.controls['initial_mass'] = masses.tolist()

# Baseline simple star parameters
grid.kap['use_Type2_opacities'] = True
grid.kap['Zbase'] = 0.02
grid.controls['initial_z'] = 0.02
grid.controls['xa_central_lower_limit_species(1)'] = "h1"
grid.controls['xa_central_lower_limit(1)'] = 1e-3
grid.controls['energy_eqn_option'] = "dedt"
grid.controls['use_gold_tolerances'] = True
grid.controls['profile_interval'] = 5
grid.controls['pulse_data_format'] = 'GYRE'
grid.controls['write_pulse_data_with_profile'] = True
# Speed up timesteps
grid.controls['time_delta_coeff'] = 0.5 
grid.controls['delta_HR_limit'] = 0.1   

# Turn off pgstar
grid.star_job['pgstar_flag'] = False

def name_function(unpacked_inlist):
    m = unpacked_inlist['controls']['initial_mass']
    return f"mass_{float(m):.2f}"

grid.set_name_function(name_function)

print("Creating grid...")
grid.create_grid(grid_dir)
print("Grid created successfully in:", grid_dir)
