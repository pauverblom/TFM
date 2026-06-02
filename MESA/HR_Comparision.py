import mesa_reader as mr
import matplotlib.pyplot as plt
import numpy as np

# Load the data
blue_straggler_data = '/Users/pauverdeguer/TFM/MESA/blue_straggler_gyre/LOGS2/history.data'
regular_star_mass_data = '/Users/pauverdeguer/TFM/MESA/2.7_mass_evo/LOGS/history.data'

try:
    bh = mr.MesaData(blue_straggler_data)
    h2 = mr.MesaData(regular_star_mass_data)
except Exception as e:
    print(f"Error loading data: {e}")
    exit(1)

plt.figure(figsize=(10, 6))

# 1. HR Diagram Comparison

plt.plot(bh.log_Teff, bh.log_L, label='Blue Straggler', color='blue', linewidth=2)
plt.plot(h2.log_Teff, h2.log_L, label='Regular Star', color='orange', linewidth=2)
plt.xlabel('log(Teff)')
plt.ylabel('log(L)')
plt.gca().invert_xaxis()  # Invert x-axis for HR diagram
plt.title('HR Diagram Comparison')
plt.scatter(4.057, 1.759, color='red', label='Observed Blue Straggler', zorder=5)
plt.scatter(4.055, 1.739, color='green', label='Observed Regular Star', zorder=5)


plt.legend()


plt.show()