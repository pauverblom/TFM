import matplotlib.pyplot as plt
fig = plt.figure(figsize=(18, 12))
gs = fig.add_gridspec(2, 4)
axes_top = [fig.add_subplot(gs[0, i]) for i in range(3)]
axes_bot = [fig.add_subplot(gs[1, i]) for i in range(3)]
ax_hr = fig.add_subplot(gs[:, 3])

for ax in axes_top: ax.plot([1,2],[1,2])
for ax in axes_bot: ax.plot([1,2],[1,2])
ax_hr.plot([1,2],[1,2])
plt.savefig('/Users/pauverdeguer/TFM/Analysis/great separation/test_layout.png')
