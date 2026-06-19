import numpy as np
import os
import sys

script_dir = "/Users/pauverdeguer/TFM/Analysis/visualization"
import py_mesa_reader as mr

LOGS1 = os.path.join(script_dir, "../../MESA/blue_straggler_model_create/LOGS1")
h1 = mr.MesaData(os.path.join(LOGS1, "history.data"))

# Calculate MT start
rl_relative_overflow_1 = h1.rl_1 # just mock logic, let's use the real logic from visualizer
bh = mr.MesaData(os.path.join(script_dir, "../../MESA/blue_straggler_model_create/binary_history.data"))
idx_start_bh = np.argmax(bh.rl_relative_overflow_1 > 0) if np.any(bh.rl_relative_overflow_1 > 0) else 0
age_mt_start = bh.age[idx_start_bh]

idx_mt_start_1 = np.argmin(np.abs(h1.star_age - age_mt_start))

t_0 = h1.star_age[idx_mt_start_1]
mn_t0 = h1.model_number[idx_mt_start_1]
mn_max = h1.model_number[-1]

print(f"t_0 = {t_0/1e6:.2f} Myr")

target_ages = [
    t_0 + 3.0 * 1e3,
    t_0 + 12.8 * 1e3,
    t_0 + 231.0 * 1e3,
    1003.8 * 1e6
]

custom_ticks = [0.0, 0.25, 0.5]
for t_target in target_ages:
    idx = np.argmin(np.abs(h1.star_age - t_target))
    mn = h1.model_number[idx]
    x_val = 0.5 + 0.5 * (mn - mn_t0) / (mn_max - mn_t0)
    print(f"Target age {t_target} -> idx {idx} -> mn {mn} -> x_val {x_val:.4f}")
    custom_ticks.append(x_val)

print("Ticks:", custom_ticks)

# Simulate formatter
def formatter(x):
    if x <= 0.5:
        age = (x / 0.5) * t_0
        return f"{age/1e6:.1f} Myr"
    else:
        mn = mn_t0 + ((x - 0.5) / 0.5) * (mn_max - mn_t0)
        idx = np.argmin(np.abs(h1.model_number - mn))
        age = h1.star_age[idx]
        t = age / 1e6
        t_0_myr = t_0 / 1e6
        
        if abs(t - t_0_myr) < 2.0:
            delta_kyr = (t - t_0_myr) * 1000
            if abs(delta_kyr) < 0.1:
                return f"$t_0$"
            sign = '+' if delta_kyr >= 0 else ''
            return f"$t_0$ {sign}{delta_kyr:.1f} kyr"
        else:
            return f"{t:.1f} Myr"

print("Formatted:")
for x in custom_ticks:
    print(f"{x:.4f} -> {formatter(x)}")

