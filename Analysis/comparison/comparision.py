import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Paths to the profiles
dir1 = "/home/pauver/TFM/MESA/evolve_created_blue_straggler/LOGS"
dir2 = "/home/pauver/TFM/MESA/evolve_1.8_mass_star/LOGS"

out_dir = "/home/pauver/TFM/Analysis/comparison"
os.makedirs(out_dir, exist_ok=True)

def read_mesa_profile(filepath):
    # skip the first 5 rows; the 6th row (index 5) contains the column names
    # sep='\s+' is used to handle variable whitespace separation
    df = pd.read_csv(filepath, sep='\s+', skiprows=5)
    return df

def main():
    try:
        # Load data
        df1 = read_mesa_profile(os.path.join(dir1, "profile1.data"))
        df2 = read_mesa_profile(os.path.join(dir2, "profile1.data"))
        
        # We will create a comprehensive figure with 6 subplots
        fig, axs = plt.subplots(3, 2, figsize=(16, 20))
        fig.suptitle("Internal Structure: Blue Straggler vs Regular 1.8 $M_\odot$ Star\n(First Profile)", fontsize=18)

        # Plot 1: logT vs mass
        axs[0, 0].plot(df1['mass'], df1['logT'], label='Blue Straggler', color='blue', linewidth=2)
        axs[0, 0].plot(df2['mass'], df2['logT'], label='Regular 1.8 $M_\odot$', color='red', linestyle='--', linewidth=2)
        axs[0, 0].set_xlabel('Mass coordinate ($M_\odot$)', fontsize=12)
        axs[0, 0].set_ylabel('$\log_{10}(T)$ [K]', fontsize=12)
        axs[0, 0].set_title('Temperature Profile', fontsize=14)
        axs[0, 0].legend()
        axs[0, 0].grid(True, alpha=0.5)

        # Plot 2: logRho vs mass
        axs[0, 1].plot(df1['mass'], df1['logRho'], label='Blue Straggler', color='blue', linewidth=2)
        axs[0, 1].plot(df2['mass'], df2['logRho'], label='Regular 1.8 $M_\odot$', color='red', linestyle='--', linewidth=2)
        axs[0, 1].set_xlabel('Mass coordinate ($M_\odot$)', fontsize=12)
        axs[0, 1].set_ylabel('$\log_{10}(\\rho)$ [g/cm$^3$]', fontsize=12)
        axs[0, 1].set_title('Density Profile', fontsize=14)
        axs[0, 1].legend()
        axs[0, 1].grid(True, alpha=0.5)

        # Plot 3: logR vs mass
        axs[1, 0].plot(df1['mass'], df1['logR'], label='Blue Straggler', color='blue', linewidth=2)
        axs[1, 0].plot(df2['mass'], df2['logR'], label='Regular 1.8 $M_\odot$', color='red', linestyle='--', linewidth=2)
        axs[1, 0].set_xlabel('Mass coordinate ($M_\odot$)', fontsize=12)
        axs[1, 0].set_ylabel('$\log_{10}(R/R_\odot)$', fontsize=12)
        axs[1, 0].set_title('Radius Profile', fontsize=14)
        axs[1, 0].legend()
        axs[1, 0].grid(True, alpha=0.5)

        # Plot 4: H and He mass fractions vs mass
        axs[1, 1].plot(df1['mass'], df1['x_mass_fraction_H'], label='H (Blue Straggler)', color='blue', linewidth=2)
        axs[1, 1].plot(df2['mass'], df2['x_mass_fraction_H'], label='H (Regular 1.8 $M_\odot$)', color='lightblue', linestyle='--', linewidth=2)
        axs[1, 1].plot(df1['mass'], df1['y_mass_fraction_He'], label='He (Blue Straggler)', color='red', linewidth=2)
        axs[1, 1].plot(df2['mass'], df2['y_mass_fraction_He'], label='He (Regular 1.8 $M_\odot$)', color='lightcoral', linestyle='--', linewidth=2)
        axs[1, 1].set_xlabel('Mass coordinate ($M_\odot$)', fontsize=12)
        axs[1, 1].set_ylabel('Mass Fraction', fontsize=12)
        axs[1, 1].set_title('Chemical Composition (H, He)', fontsize=14)
        axs[1, 1].legend()
        axs[1, 1].grid(True, alpha=0.5)

        # Plot 5: logP vs mass
        axs[2, 0].plot(df1['mass'], df1['logP'], label='Blue Straggler', color='blue', linewidth=2)
        axs[2, 0].plot(df2['mass'], df2['logP'], label='Regular 1.8 $M_\odot$', color='red', linestyle='--', linewidth=2)
        axs[2, 0].set_xlabel('Mass coordinate ($M_\odot$)', fontsize=12)
        axs[2, 0].set_ylabel('$\log_{10}(P)$ [dyn/cm$^2$]', fontsize=12)
        axs[2, 0].set_title('Pressure Profile', fontsize=14)
        axs[2, 0].legend()
        axs[2, 0].grid(True, alpha=0.5)

        # Plot 6: Energy generation (pp and cno) vs mass (log scale)
        def log_safe(val):
            return np.log10(np.maximum(val, 1e-30))
            
        axs[2, 1].plot(df1['mass'], log_safe(df1['pp']), label='pp (Blue Straggler)', color='blue', linewidth=2)
        axs[2, 1].plot(df2['mass'], log_safe(df2['pp']), label='pp (Regular 1.8 $M_\odot$)', color='lightblue', linestyle='--', linewidth=2)
        axs[2, 1].plot(df1['mass'], log_safe(df1['cno']), label='CNO (Blue Straggler)', color='red', linewidth=2)
        axs[2, 1].plot(df2['mass'], log_safe(df2['cno']), label='CNO (Regular 1.8 $M_\odot$)', color='lightcoral', linestyle='--', linewidth=2)
        
        axs[2, 1].set_xlabel('Mass coordinate ($M_\odot$)', fontsize=12)
        axs[2, 1].set_ylabel('$\log_{10}(\epsilon)$ [erg/g/s]', fontsize=12)
        axs[2, 1].set_title('Nuclear Energy Generation Rates', fontsize=14)
        # Limit y-axis to a reasonable range for energy generation
        axs[2, 1].set_ylim([-5, 10]) 
        axs[2, 1].legend()
        axs[2, 1].grid(True, alpha=0.5)

        plt.tight_layout(rect=[0, 0.03, 1, 0.96])
        
        # Save the composite figure
        out_file = os.path.join(out_dir, "comparative_profiles_summary.png")
        plt.savefig(out_file, dpi=300, bbox_inches='tight')
        print(f"Successfully generated summary plot: {out_file}")

        # Also generate separate individual plots for detail
        fig_ind, ax_ind = plt.subplots(figsize=(10, 7))
        cols_to_plot = {
            'logT': ('Temperature ($\log_{10} T$)', '$\log_{10}(T)$ [K]'),
            'logRho': ('Density ($\log_{10} \\rho$)', '$\log_{10}(\\rho)$ [g/cm$^3$]'),
            'logR': ('Radius ($\log_{10} R/R_\odot$)', '$\log_{10}(R/R_\odot)$'),
            'logP': ('Pressure ($\log_{10} P$)', '$\log_{10}(P)$ [dyn/cm$^2$]')
        }

        for col, (title, ylabel) in cols_to_plot.items():
            ax_ind.clear()
            ax_ind.plot(df1['mass'], df1[col], label='Blue Straggler', color='blue', linewidth=2.5)
            ax_ind.plot(df2['mass'], df2[col], label='Regular 1.8 $M_\odot$', color='red', linestyle='--', linewidth=2.5)
            ax_ind.set_xlabel('Mass coordinate ($M_\odot$)', fontsize=14)
            ax_ind.set_ylabel(ylabel, fontsize=14)
            ax_ind.set_title(f'{title} Comparison', fontsize=16)
            ax_ind.legend(fontsize=12)
            ax_ind.grid(True, alpha=0.5)
            
            ind_file = os.path.join(out_dir, f"comparison_{col}.png")
            fig_ind.savefig(ind_file, dpi=300, bbox_inches='tight')
            print(f"Successfully generated individual plot: {ind_file}")
            
    except Exception as e:
        print(f"An error occurred during plotting: {e}")

if __name__ == "__main__":
    main()
