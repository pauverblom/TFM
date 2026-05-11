import mesa_reader as mr
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os
import numpy as np
import subprocess

# --- Configuration ---
LOGS_DIR = 'MESA/blue_straggler_gyre/LOGS2'
OUTPUT_DIR = 'profile_2d_frames'
MOVIE_FILENAME = 'stellar_2d_evolution.mp4'

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# --- Pre-computation: Global Limits from History ---
print("Loading history.data to find global limits...")
try:
    h = mr.MesaData(f"{LOGS_DIR}/history.data")
    
    # Global extremes
    MAX_AGE = np.max(h.star_age)
    MAX_RADIUS = 10**np.max(h.log_R)  # Assuming log_R is in solar radii
    
    # We will still use global limits for Temperature color consistency
    MAX_LOGT = np.max(h.log_cntr_T)
    MIN_LOGT = np.min(h.log_Teff)
    
    print(f"  Max Age: {MAX_AGE:.2e} yr")
    print(f"  Max Radius: {MAX_RADIUS:.2f} Rsun")
    print(f"  Temp Range (logT): {MIN_LOGT:.2f} to {MAX_LOGT:.2f}")
except Exception as e:
    print(f"Error reading history.data: {e}")
    exit(1)

# --- Load Profiles Index ---
try:
    index = mr.MesaProfileIndex(f"{LOGS_DIR}/profiles.index")
    profile_numbers = index.profile_numbers
    model_numbers = index.model_numbers
except Exception as e:
    print(f"Error reading profiles index: {e}")
    exit(1)

print(f"Found {len(profile_numbers)} profiles.")

def get_burning_data(eps_array):
    """Safely converts energy generation rates to a log scale, filtering out zero/negative values."""
    # Clip at 1e-10 to avoid log(0) and highlight only significant burning
    log_eps = np.log10(np.clip(eps_array, 1e-10, None))
    max_val = np.max(log_eps)
    
    # If there's no burning happening, return a flat dark array
    if max_val <= -9.0:
        return log_eps, -10, -9
    
    # Scale dynamically to show the top 10 orders of magnitude of burning in this frame
    vmin = max_val - 10
    vmax = max_val
    return log_eps, vmin, vmax

# --- Plotting Function ---
def plot_profile_2d(profile_number, model_number, total_profiles):
    try:
        p = mr.MesaData(f"{LOGS_DIR}/profile{profile_number}.data")
        
        # Prepare 1D to 2D polar mapping
        r = 10**p.logR
        current_R = np.max(r)
        theta = np.linspace(0, 2*np.pi, 100)
        R_mesh, Theta_mesh = np.meshgrid(r, theta)
        
        # --- Figure Layout ---
        fig = plt.figure(figsize=(24, 13))
        gs = GridSpec(3, 4, height_ratios=[1, 1, 0.15], hspace=0.35, wspace=0.3)
        
        # Define Axes
        ax_size = fig.add_subplot(gs[0, 0], projection='polar')
        ax_temp = fig.add_subplot(gs[0, 1], projection='polar')
        ax_h = fig.add_subplot(gs[0, 2], projection='polar')
        ax_he = fig.add_subplot(gs[0, 3], projection='polar')
        
        ax_pp = fig.add_subplot(gs[1, 0], projection='polar')
        ax_cno = fig.add_subplot(gs[1, 1], projection='polar')
        ax_tri = fig.add_subplot(gs[1, 2], projection='polar')
        
        ax_info = fig.add_subplot(gs[1, 3]) # Text panel
        timeline_ax = fig.add_subplot(gs[2, :]) # Timeline at bottom
        
        polar_axes = [ax_size, ax_temp, ax_h, ax_he, ax_pp, ax_cno, ax_tri]
        
        # --- 1. Global Size Evolution (Fixed Axis Limits) ---
        T_2d = np.tile(p.logT, (len(theta), 1))
        im_size = ax_size.pcolormesh(Theta_mesh, R_mesh, T_2d, cmap='magma', vmin=MIN_LOGT, vmax=MAX_LOGT, shading='auto')
        ax_size.set_title('Global Size Evolution\n(Fixed Scale)', pad=15, fontsize=14)
        ax_size.set_ylim(0, MAX_RADIUS) # THIS IS THE ONLY ONE WITH FIXED YLIM
        
        # Draw a white outline for the star surface
        ax_size.plot(theta, np.full_like(theta, current_R), color='white', linewidth=1.5, alpha=0.8)

        # --- 2. Temperature (Auto-scaling Radius) ---
        im_temp = ax_temp.pcolormesh(Theta_mesh, R_mesh, T_2d, cmap='magma', vmin=MIN_LOGT, vmax=MAX_LOGT, shading='auto')
        ax_temp.set_title('Log Temperature (K)', pad=15, fontsize=14)
        fig.colorbar(im_temp, ax=ax_temp, fraction=0.046, pad=0.1)

        # --- 3. Hydrogen Fraction ---
        H_2d = np.tile(p.x_mass_fraction_H, (len(theta), 1))
        im_h = ax_h.pcolormesh(Theta_mesh, R_mesh, H_2d, cmap='Blues_r', vmin=0, vmax=0.75, shading='auto')
        ax_h.set_title('Hydrogen Fraction', pad=15, fontsize=14)
        fig.colorbar(im_h, ax=ax_h, fraction=0.046, pad=0.1)

        # --- 4. Helium Fraction ---
        He_2d = np.tile(p.y_mass_fraction_He, (len(theta), 1))
        im_he = ax_he.pcolormesh(Theta_mesh, R_mesh, He_2d, cmap='Oranges', vmin=0, vmax=1.0, shading='auto')
        ax_he.set_title('Helium Fraction', pad=15, fontsize=14)
        fig.colorbar(im_he, ax=ax_he, fraction=0.046, pad=0.1)

        # --- Nuclear Burning Processes ---
        # 5. PP Chain
        pp_log, vmin_pp, vmax_pp = get_burning_data(p.pp)
        pp_2d = np.tile(pp_log, (len(theta), 1))
        im_pp = ax_pp.pcolormesh(Theta_mesh, R_mesh, pp_2d, cmap='inferno', vmin=vmin_pp, vmax=vmax_pp, shading='auto')
        ax_pp.set_title('PP Chain (Log ε)', pad=15, fontsize=14)
        fig.colorbar(im_pp, ax=ax_pp, fraction=0.046, pad=0.1)

        # 6. CNO Cycle
        cno_log, vmin_cno, vmax_cno = get_burning_data(p.cno)
        cno_2d = np.tile(cno_log, (len(theta), 1))
        im_cno = ax_cno.pcolormesh(Theta_mesh, R_mesh, cno_2d, cmap='inferno', vmin=vmin_cno, vmax=vmax_cno, shading='auto')
        ax_cno.set_title('CNO Cycle (Log ε)', pad=15, fontsize=14)
        fig.colorbar(im_cno, ax=ax_cno, fraction=0.046, pad=0.1)

        # 7. Triple Alpha
        tri_log, vmin_tri, vmax_tri = get_burning_data(p.tri_alpha)
        tri_2d = np.tile(tri_log, (len(theta), 1))
        im_tri = ax_tri.pcolormesh(Theta_mesh, R_mesh, tri_2d, cmap='inferno', vmin=vmin_tri, vmax=vmax_tri, shading='auto')
        ax_tri.set_title('Triple-Alpha (Log ε)', pad=15, fontsize=14)
        fig.colorbar(im_tri, ax=ax_tri, fraction=0.046, pad=0.1)

        # Common settings for auto-scaling polar plots (Axes 1 through 6)
        for ax in polar_axes[1:]:
            ax.set_ylim(0, current_R)
        
        # Clean up grid and ticks for ALL polar axes
        for ax in polar_axes:
            ax.set_yticklabels([])
            ax.set_xticklabels([])
            ax.grid(False)

        # --- 8. Text Information Panel ---
        ax_info.axis('off')
        
        # Extract metadata safely from header
        star_age = p.header_data.get('star_age', 0)
        star_mass = p.header_data.get('star_mass', 0)
        
        info_text = (
            f"Model Number: {model_number}\n\n"
            f"Current Age: {star_age:.3e} yr\n\n"
            f"Current Mass: {star_mass:.3f} M$_\odot$\n\n"
            f"Current Radius: {current_R:.3f} R$_\odot$\n\n"
            f"Central LogT: {np.max(p.logT):.2f}"
        )
        ax_info.text(0.1, 0.5, info_text, fontsize=16, va='center', ha='left',
                     bbox=dict(facecolor='white', alpha=0.8, edgecolor='lightgray', boxstyle='round,pad=1'))

        # --- 9. Timeline ---
        timeline_ax.plot([0, MAX_AGE], [0, 0], color='lightgray', lw=6, zorder=1) # Background track
        timeline_ax.plot(star_age, 0, marker='o', color='red', markersize=16, zorder=2) # Playhead
        timeline_ax.fill_between([0, star_age], -0.1, 0.1, color='red', alpha=0.3, zorder=1) # Progress fill
        
        timeline_ax.set_xlim(0, MAX_AGE)
        timeline_ax.set_ylim(-1, 1)
        timeline_ax.set_yticks([])
        timeline_ax.set_xlabel('Star Age (years)', fontsize=14, fontweight='bold')
        for spine in ['top', 'right', 'left', 'bottom']:
            timeline_ax.spines[spine].set_visible(False)

        # Master Title
        plt.suptitle(f'Internal Stellar Evolution Structure', fontsize=22, fontweight='bold', y=0.95)
        
        # Save frame
        order = np.where(profile_numbers == profile_number)[0][0] + 1
        frame_path = f"{OUTPUT_DIR}/frame_{order:03d}.png"
        plt.savefig(frame_path, bbox_inches='tight', facecolor='white', dpi=100)
        plt.close(fig)
        
        return frame_path
        
    except Exception as e:
        print(f"Error plotting profile {profile_number}: {e}")
        import traceback
        traceback.print_exc()
        return None

# --- Generate Frames and Movie ---
print("Generating 2D frames...")
for i, (p_num, m_num) in enumerate(zip(profile_numbers, model_numbers)):
    plot_profile_2d(p_num, m_num, len(profile_numbers))
    if (i+1) % 10 == 0:
        print(f"  Processed {i+1}/{len(profile_numbers)} profiles...")

print(f"Successfully generated frames in {OUTPUT_DIR}/")

print("Combining frames into movie using ffmpeg...")
cmd = [
    'ffmpeg', '-y', '-r', '10', 
    '-i', f'{OUTPUT_DIR}/frame_%03d.png', '-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2', 
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', 
    MOVIE_FILENAME
]

try:
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"Movie successfully saved as {MOVIE_FILENAME}")
except FileNotFoundError:
    print("ffmpeg not found. Please install ffmpeg to generate the mp4.")
except subprocess.CalledProcessError as e:
    print(f"Error running ffmpeg: {e.stderr.decode()}")