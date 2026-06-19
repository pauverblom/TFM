import os
from PIL import Image

script_dir = '/Users/pauverdeguer/TFM/Analysis/visualization'

# Open images
orbit = Image.open(os.path.join(script_dir, 'orbital_evolution.png'))
mdot = Image.open(os.path.join(script_dir, 'mass_transfer_rate.png'))
hr = Image.open(os.path.join(script_dir, 'hr_diagram.png'))
rad = Image.open(os.path.join(script_dir, 'radio_vs_rlof.png'))
abund = Image.open(os.path.join(script_dir, 'central_abundances.png'))
kipp = Image.open(os.path.join(script_dir, 'kippenhahn_combined.png'))

# Convert all to RGB
for name in ['orbit', 'mdot', 'hr', 'rad', 'abund', 'kipp']:
    img = locals()[name]
    if img.mode != 'RGB':
        locals()[name] = img.convert('RGB')

GAP = 30  # pixels gap between plots

# ============================================================
# MACROFIGURE 1: "Evolución del sistema"
# Layout:
#   Row 1: orbital_evolution | mass_transfer_rate  (side by side)
#   Row 2: hr_diagram (full width, centered)
# ============================================================

# Scale top row plots to same height
top_h1 = max(orbit.height, mdot.height)
orbit_scaled = orbit.resize((int(orbit.width * top_h1 / orbit.height), top_h1), Image.LANCZOS)
mdot_scaled = mdot.resize((int(mdot.width * top_h1 / mdot.height), top_h1), Image.LANCZOS)

row1_w = orbit_scaled.width + GAP + mdot_scaled.width
row1_h = top_h1

# Scale HR to match row1 width
hr_scale = row1_w / hr.width
hr_scaled = hr.resize((row1_w, int(hr.height * hr_scale)), Image.LANCZOS)

total_w1 = row1_w
total_h1 = row1_h + GAP + hr_scaled.height

canvas1 = Image.new('RGB', (total_w1, total_h1), 'white')
canvas1.paste(orbit_scaled, (0, 0))
canvas1.paste(mdot_scaled, (orbit_scaled.width + GAP, 0))
canvas1.paste(hr_scaled, (0, row1_h + GAP))

out_dir = '/Users/pauverdeguer/TFM/TeX/Imagenes'
os.makedirs(out_dir, exist_ok=True)

canvas1.save(os.path.join(out_dir, 'macrofigure_1.png'), dpi=(300, 300))
print(f"Macrofigure 1 saved at {out_dir}")

# ============================================================
# MACROFIGURE 2: "Estructura estelar"
# Layout:
#   Row 1: radio_vs_rlof | kippenhahn_combined  (side by side)
#   Row 2: central_abundances (full width, centered)
# ============================================================

# Scale top row to same height
top_h2 = max(rad.height, kipp.height)
rad_scaled = rad.resize((int(rad.width * top_h2 / rad.height), top_h2), Image.LANCZOS)
kipp_scaled = kipp.resize((int(kipp.width * top_h2 / kipp.height), top_h2), Image.LANCZOS)

row1_w2 = rad_scaled.width + GAP + kipp_scaled.width
row1_h2 = top_h2

# Scale abundances to match row1 width
abund_scale = row1_w2 / abund.width
abund_scaled = abund.resize((row1_w2, int(abund.height * abund_scale)), Image.LANCZOS)

total_w2 = row1_w2
total_h2 = row1_h2 + GAP + abund_scaled.height

canvas2 = Image.new('RGB', (total_w2, total_h2), 'white')
canvas2.paste(rad_scaled, (0, 0))
canvas2.paste(kipp_scaled, (rad_scaled.width + GAP, 0))
canvas2.paste(abund_scaled, (0, row1_h2 + GAP))

canvas2.save(os.path.join(out_dir, 'macrofigure_2.png'), dpi=(300, 300))
print(f"Macrofigure 2 saved at {out_dir}")

# Report aspect ratios
print(f"\nMacrofigure 1 aspect ratio: {total_w1/total_h1:.2f} (target ~0.70 for portrait A4)")
print(f"Macrofigure 2 aspect ratio: {total_w2/total_h2:.2f} (target ~0.70 for portrait A4)")
