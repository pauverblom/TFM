import pygyre as pg
import matplotlib.pyplot as plt
import os
import numpy as np
import mesa_reader as mr
import matplotlib.cm as cm

def main():
    dir_bs = '/Users/pauverdeguer/TFM/MESA/evolve_created_blue_straggler'
    gyre_dir = f'{dir_bs}/gyre_outputs'
    
    print("Loading HR tracks and profiles index...")
    hist_bs = mr.MesaData(f'{dir_bs}/LOGS/history.data')
    idx_bs = mr.MesaProfileIndex(f'{dir_bs}/LOGS/profiles.index')

    def get_age(hist, idx, p_num):
        model_numbers = idx.model_numbers
        profile_numbers = idx.profile_numbers
        
        if p_num not in profile_numbers:
            return None
            
        m_num = model_numbers[list(profile_numbers).index(p_num)]
        row = np.argmin(np.abs(hist.model_number - m_num))
        return hist.star_age[row]

    print("Extracting frequencies from gyre outputs...")
    # Dictionary to hold data: data[l][n_pg] = {"time": [], "freq": []}
    data = {
        0: {n: {"time": [], "freq": []} for n in range(-10, 11)},
        1: {n: {"time": [], "freq": []} for n in range(-10, 11)},
        2: {n: {"time": [], "freq": []} for n in range(-10, 11)}
    }

    # Extract info from all profiles
    for p_num in sorted(idx_bs.profile_numbers):
        age = get_age(hist_bs, idx_bs, p_num)
        if age is None: 
            continue
            
        file_path = f"{gyre_dir}/profile{p_num}.data/summary.h5"
        if not os.path.exists(file_path):
            continue
            
        try:
            s = pg.read_output(file_path)
            sg = s.group_by('l')
            if not hasattr(sg, 'groups'):
                continue
                
            for g in sg.groups:
                if len(g['l']) == 0: 
                    continue
                l_val = g['l'][0]
                
                if l_val not in [0, 1, 2]: 
                    continue
                
                n_pg = np.array(g['n_pg'])
                freq = np.array(g['freq'].real)
                
                for n, f in zip(n_pg, freq):
                    if -10 <= n <= 10:
                        data[l_val][n]["time"].append(age)
                        data[l_val][n]["freq"].append(f)
                        
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    print("Generating avoided crossing plots...")
    output_dir = '/Users/pauverdeguer/TFM/Analysis/avoided crossing'
    
    # Plotting
    for l_val in [0, 1, 2]:
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Use a colormap to distinguish different n_pg
        cmap = plt.get_cmap('tab20')
        
        for i, n in enumerate(range(-10, 11)):
            times = data[l_val][n]["time"]
            freqs = data[l_val][n]["freq"]
            if len(times) > 0:
                times = np.array(times)
                freqs = np.array(freqs)
                # Sort by time to draw lines properly
                idx = np.argsort(times)
                
                # We use modulo 20 to loop over the tab20 colormap colors
                color_idx = i % 20
                color = cmap.colors[color_idx] if hasattr(cmap, 'colors') else cmap(color_idx / 20.0)
                
                ax.plot(times[idx], freqs[idx], marker='.', markersize=6, linestyle='-', 
                        linewidth=1.5, alpha=0.8, color=color, label=f'$n_{{pg}}={n}$')
                
        ax.set_title(f'Avoided Crossing (l={l_val})', fontsize=15, fontweight='bold', pad=15)
        ax.set_xlabel('Star Age (yr)', fontsize=13)
        ax.set_ylabel('Frequency $\\nu$ (cyc/day)', fontsize=13)
        
        # Grid and aesthetics
        ax.grid(True, which='both', linestyle=':', color='gray', alpha=0.5)
        ax.tick_params(labelsize=11)
        
        # Place legend outside
        ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', ncol=1, fontsize=10, 
                  title='Radial Order ($n_{pg}$)', title_fontsize=11)
        
        plt.tight_layout()
        out_file = os.path.join(output_dir, f'avoided_crossing_l{l_val}.png')
        plt.savefig(out_file, dpi=300)
        plt.close()
        print(f"Saved {out_file}")

    print("All plots generated successfully!")

if __name__ == '__main__':
    main()
