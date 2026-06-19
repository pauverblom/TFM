import mesa_reader as mr
import matplotlib.pyplot as plt
import numpy as np

h2 = mr.MesaData('/Users/pauverdeguer/TFM/MESA/blue_straggler_model_create/LOGS2/history.data')
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(h2.model_number, h2.star_mass, color='black')

for i in range(1, 10):
    top_col = f'conv_mx{i}_top'
    bot_col = f'conv_mx{i}_bot'
    if top_col in h2.bulk_names and bot_col in h2.bulk_names:
        top_mass = h2.data(top_col) * h2.star_mass
        bot_mass = h2.data(bot_col) * h2.star_mass
        mask = (top_mass > bot_mass) & (top_mass > 0)
        ax.vlines(h2.model_number[mask], bot_mass[mask], top_mass[mask], color='lightgray')

fig.savefig('test_vlines.png')
