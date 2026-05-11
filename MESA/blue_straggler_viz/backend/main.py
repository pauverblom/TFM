"""
Blue Straggler Binary Evolution - FastAPI Backend
Parses MESA binary star simulation output and serves unified timeline data.
"""

from pathlib import Path
import numpy as np
from scipy.optimize import brentq
import mesa_reader as mr
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Blue Straggler MESA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# MESA data lives one level above the backend/
DATA_DIR = Path(__file__).parent.parent


def compute_l1(M1: float, M2: float, a: float) -> float:
    """
    Compute L1 Lagrange point position from the center of mass.

    Uses the restricted three-body potential in the co-rotating frame.
    In normalized units (a=1, Mtot=1) with CoM at origin:
        Star 1 at x = -mu2   (donor, heavier initially)
        Star 2 at x = +mu1   (accretor)
    The L1 condition (dΦ_eff/dx = 0) between the stars:
        mu1/(x+mu2)^2  -  mu2/(mu1-x)^2  -  x  = 0

    Returns the L1 x-coordinate in Rsun, measured from CoM.
    """
    mu1 = M1 / (M1 + M2)
    mu2 = M2 / (M1 + M2)

    def dphi(x):
        return mu1 / (x + mu2) ** 2 - mu2 / (mu1 - x) ** 2 - x

    try:
        x_l1 = brentq(dphi, -mu2 + 1e-7, mu1 - 1e-7)
        return float(x_l1 * a)
    except Exception:
        # Eggleton (1983) Roche lobe radius as fallback approximation
        q = M1 / M2
        rl1_a = 0.49 * q ** (2 / 3) / (0.6 * q ** (2 / 3) + np.log(1 + q ** (1 / 3)))
        return float((-mu2 + rl1_a * 1.05) * a)


def classify_phase(h1_center: float, is_rlof: bool, m1: float, m1_init: float) -> str:
    if is_rlof:
        fraction_lost = (m1_init - m1) / m1_init
        if fraction_lost < 0.05:
            return "RLOF Onset"
        elif fraction_lost < 0.5:
            return "Active RLOF"
        else:
            return "Late RLOF"
    elif h1_center > 0.50:
        return "Main Sequence (ZAMS)"
    elif h1_center > 0.05:
        return "Main Sequence"
    else:
        return "Giant Branch"


def load_data() -> list[dict]:
    logger.info("Loading MESA history files via mesa_reader…")
    l1 = mr.MesaData(str(DATA_DIR / "LOGS1" / "history.data"))
    l2 = mr.MesaData(str(DATA_DIR / "LOGS2" / "history.data"))

    ages = l1.data("star_age")
    n = len(ages)
    logger.info(f"  {n} timesteps  |  age: {ages[0]:.3e} → {ages[-1]:.3e} yr")

    m1_arr = l1.data("star_1_mass")
    m2_arr = l1.data("star_2_mass")
    sep_arr = l1.data("binary_separation")
    rlof_arr = l1.data("rl_relative_overflow_1")
    mdot_arr = l1.data("lg_mtransfer_rate")

    m1_init = float(m1_arr[0])

    frames = []
    for i in range(n):
        M1 = float(m1_arr[i])
        M2 = float(m2_arr[i])
        a = float(sep_arr[i])
        rl_ov = float(rlof_arr[i])
        lg_mdot = float(mdot_arr[i])
        is_rlof = bool(rl_ov > -0.05 and lg_mdot > -15.0)
        h1_1 = float(l1.data("center_h1")[i])

        # Orbital radii from CoM (Rsun)
        r1_orb = a * M2 / (M1 + M2)
        r2_orb = a * M1 / (M1 + M2)

        frames.append({
            "index": i,
            "star_age": float(ages[i]),
            "star_age_gyr": float(ages[i]) / 1e9,
            "model_number": int(l1.data("model_number")[i]),
            "period_days": float(l1.data("period_days")[i]),
            "binary_separation": a,
            "r1_orb": r1_orb,
            "r2_orb": r2_orb,
            # Star masses
            "star1_mass": M1,
            "star2_mass": M2,
            # Star 1 (donor)
            "star1_log_Teff": float(l1.data("log_Teff")[i]),
            "star1_log_L": float(l1.data("log_L")[i]),
            "star1_log_R": float(l1.data("log_R")[i]),
            "star1_log_g": float(l1.data("log_g")[i]),
            # Star 2 (accretor → Blue Straggler)
            "star2_log_Teff": float(l2.data("log_Teff")[i]),
            "star2_log_L": float(l2.data("log_L")[i]),
            "star2_log_R": float(l2.data("log_R")[i]),
            "star2_log_g": float(l2.data("log_g")[i]),
            # Binary/orbital
            "rl_relative_overflow_1": rl_ov,
            "lg_mtransfer_rate": lg_mdot,
            "lg_mstar_dot_1": float(l1.data("lg_mstar_dot_1")[i]),
            "rl_1": float(l1.data("rl_1")[i]),
            "rl_2": float(l1.data("rl_2")[i]),
            # Composition
            "center_h1_1": h1_1,
            "center_he4_1": float(l1.data("center_he4")[i]),
            "center_h1_2": float(l2.data("center_h1")[i]),
            "center_he4_2": float(l2.data("center_he4")[i]),
            # Core masses
            "he_core_mass_1": float(l1.data("he_core_mass")[i]),
            "he_core_mass_2": float(l2.data("he_core_mass")[i]),
            # L1 point position from CoM (Rsun, positive toward Star 2)
            "l1_position": compute_l1(M1, M2, a),
            # Flags
            "is_rlof": is_rlof,
            "phase": classify_phase(h1_1, is_rlof, M1, m1_init),
        })

    logger.info("Data loading complete.")
    return frames


_frames: list[dict] = []


@app.on_event("startup")
async def startup_event():
    global _frames
    _frames = load_data()


@app.get("/api/data")
async def get_all_data():
    return {"frames": _frames, "count": len(_frames)}


@app.get("/api/frame/{index}")
async def get_frame(index: int):
    if 0 <= index < len(_frames):
        return _frames[index]
    return {"error": "index out of range", "max": len(_frames) - 1}


@app.get("/api/health")
async def health():
    return {"status": "ok", "frames_loaded": len(_frames)}
