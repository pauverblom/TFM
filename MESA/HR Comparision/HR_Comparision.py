import mesa_reader as mr
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

def fetch_cluster_gaia(cluster_name, cache_path):
    if os.path.exists(cache_path) and os.path.getsize(cache_path) > 0:
        print(f"Loading {cluster_name} Gaia data from cache...")
        data = np.genfromtxt(cache_path, delimiter=",", skip_header=1,
                             names=["log_teff", "log_lum"])
        return data["log_teff"], data["log_lum"]

    print(f"Querying Simbad for {cluster_name} properties...")
    from astroquery.simbad import Simbad
    Simbad.add_votable_fields('pmra', 'pmdec', 'plx_value', 'dimensions')
    simbad_result = Simbad.query_object(cluster_name)
    if simbad_result is None:
        raise ValueError(f"Cluster {cluster_name} not found in Simbad.")
    
    ra = float(simbad_result['ra'][0])
    dec = float(simbad_result['dec'][0])
    
    if np.ma.is_masked(simbad_result['pmra'][0]) or np.ma.is_masked(simbad_result['pmdec'][0]) or np.ma.is_masked(simbad_result['plx_value'][0]):
        print(f"Warning: Missing proper motion or parallax data for {cluster_name} in Simbad.")
        pmra_min, pmra_max = -100.0, 100.0
        pmdec_min, pmdec_max = -100.0, 100.0
        plx_min, plx_max = 0.0, 20.0
    else:
        pmra = float(simbad_result['pmra'][0])
        pmdec = float(simbad_result['pmdec'][0])
        plx = float(simbad_result['plx_value'][0])
        
        pm_margin = 5.0
        plx_margin = max(0.5, plx * 0.3)
        
        pmra_min, pmra_max = pmra - pm_margin, pmra + pm_margin
        pmdec_min, pmdec_max = pmdec - pm_margin, pmdec + pm_margin
        plx_min, plx_max = max(0, plx - plx_margin), plx + plx_margin

    if 'galdim_majaxis' in simbad_result.columns and not np.ma.is_masked(simbad_result['galdim_majaxis'][0]):
        radius_deg = float(simbad_result['galdim_majaxis'][0]) / 60.0
        if radius_deg < 0.1: radius_deg = 1.5
    else:
        radius_deg = 1.5

    print(f"Querying Gaia DR3 for {cluster_name} members (this may take ~30 s)...")
    from astroquery.gaia import Gaia

    query = f"""
        SELECT gs.source_id,
               ap.teff_gspphot,
               ap.lum_flame
        FROM gaiadr3.gaia_source AS gs
        JOIN gaiadr3.astrophysical_parameters AS ap
          ON gs.source_id = ap.source_id
        WHERE CONTAINS(
            POINT('ICRS', gs.ra, gs.dec),
            CIRCLE('ICRS', {ra}, {dec}, {radius_deg})
        ) = 1
          AND gs.pmra  BETWEEN {pmra_min} AND {pmra_max}
          AND gs.pmdec BETWEEN {pmdec_min} AND {pmdec_max}
          AND gs.parallax BETWEEN {plx_min} AND {plx_max}
          AND ap.teff_gspphot IS NOT NULL
          AND ap.lum_flame    IS NOT NULL
    """
    job = Gaia.launch_job(query)
    table = job.get_results()
    
    if len(table) == 0:
        raise ValueError(f"No stars found for {cluster_name} in Gaia DR3 with given parameters.")
        
    log_teff = np.log10(np.array(table["teff_gspphot"], dtype=float))
    log_lum  = np.log10(np.array(table["lum_flame"],    dtype=float))
    with open(cache_path, "w") as f:
        f.write("log_teff,log_lum\n")
        for lt, ll in zip(log_teff, log_lum):
            f.write(f"{lt},{ll}\n")
    print(f"Cached {len(log_teff)} {cluster_name} member stars to {cache_path}")
    return log_teff, log_lum

script_dir = os.path.dirname(os.path.abspath(__file__))
current_dir = script_dir
workspace_root = None
for _ in range(4):
    if os.path.exists(os.path.join(current_dir, "MESA")):
        workspace_root = current_dir
        break
    current_dir = os.path.dirname(current_dir)
if workspace_root is None:
    workspace_root = script_dir

blue_straggler_data    = os.path.join(workspace_root, "MESA", "blue_straggler_gyre", "LOGS2", "history.data")
regular_star_mass_data = os.path.join(workspace_root, "MESA", "2.7_mass_evo", "LOGS", "history.data")

try:
    bh = mr.MesaData(blue_straggler_data)
    h2 = mr.MesaData(regular_star_mass_data)
except Exception as e:
    print(f"Error loading data: {e}")
    exit(1)

cluster_name = sys.argv[1] if len(sys.argv) > 1 else "Pleiades"
cluster_cache = os.path.join(workspace_root, f"{cluster_name.lower().replace(' ', '_')}_gaia.csv")
cluster_log_teff, cluster_log_lum = fetch_cluster_gaia(cluster_name, cluster_cache)

plt.figure(figsize=(10, 6))
plt.scatter(cluster_log_teff, cluster_log_lum, s=10, color="gray", alpha=0.5,
            label=f"{cluster_name} cluster (Gaia DR3, N={len(cluster_log_teff)})", zorder=1)
plt.plot(bh.log_Teff, bh.log_L, label="Blue Straggler (MESA)", color="blue",   linewidth=2, zorder=3)
plt.plot(h2.log_Teff, h2.log_L, label="Regular Star (MESA)",   color="orange",  linewidth=2, zorder=3)
plt.scatter(4.057, 1.759, color="red",   label="Observed Blue Straggler", zorder=5)
plt.scatter(4.055, 1.739, color="green", label="Observed Regular Star",   zorder=5)
plt.xlabel("log(Teff)")
plt.ylabel("log(L/L☉)")
plt.gca().invert_xaxis()
plt.title(f"HR Diagram — MESA tracks vs {cluster_name} (Gaia DR3)")
plt.legend()
plt.tight_layout()
plt.show()

