import pygyre as pg
import matplotlib.pyplot as plt
import numpy as np

s = pg.read_output('MESA/blue_straggler_gyre/gyre/summary.h5')

d = pg.read_output('MESA/blue_straggler_gyre/gyre/detail.l1.n-6.h5')

# Plot the data, grouped by harmonic degree



plt.figure()

sg = s.group_by('l')

plt.plot(sg.groups[0]['n_pg'], sg.groups[0]['freq'].real, label=r'l=0')
plt.plot(sg.groups[1]['n_pg'], sg.groups[1]['freq'].real, label=r'l=1')
plt.plot(sg.groups[2]['n_pg'], sg.groups[2]['freq'].real, label=r'l=2')

plt.xlabel('n_pg')
plt.ylabel('Frequency (cyc/day)')

plt.legend()

plt.show()


plt.figure()

plt.plot(d['x'], d['xi_r'].real, label='xi_r')
plt.plot(d['x'], d['xi_h'].real, label='xi_h')

plt.xlabel('x')

plt.legend()
plt.show()

# Evaluate dimensionless characteristic frequencies

l = d.meta['l']
omega = d.meta['omega']

x = d['x']
V = d['V_2']*d['x']**2
As = d['As']
c_1 = d['c_1']
Gamma_1 = d['Gamma_1']

d['N2'] = d['As']/d['c_1']
d['Sl2'] = l*(l+1)*Gamma_1/(V*c_1)

# Plot the propagation diagram

plt.figure()

plt.plot(d['x'], d['N2'], label='N^2')
plt.plot(d['x'], d['Sl2'], label='S_l^2')

plt.axhline(omega.real**2, dashes=(4,2))

plt.xlabel('x')
plt.ylabel('omega^2')

plt.ylim(5e-2, 5e2)
plt.yscale('log')
plt.legend()

plt.show()