import { logTeffToHex, fmtAge } from '../utils/colorUtils.js'

export default function InfoPanel({ frame }) {
  const {
    star_age, phase, is_rlof,
    star1_mass, star2_mass,
    star1_log_Teff, star2_log_Teff,
    star1_log_L, star2_log_L,
    star1_log_R, star2_log_R,
    star1_log_g, star2_log_g,
    center_h1_1, center_he4_1,
    center_h1_2, center_he4_2,
    he_core_mass_1, he_core_mass_2,
    lg_mtransfer_rate, binary_separation,
    rl_relative_overflow_1, period_days,
  } = frame

  const teff1 = Math.pow(10, star1_log_Teff).toFixed(0)
  const teff2 = Math.pow(10, star2_log_Teff).toFixed(0)
  const R1    = Math.pow(10, star1_log_R).toFixed(2)
  const R2    = Math.pow(10, star2_log_R).toFixed(2)
  const L1    = Math.pow(10, star1_log_L).toFixed(2)
  const L2    = Math.pow(10, star2_log_L).toFixed(2)

  const color1 = logTeffToHex(star1_log_Teff)
  const color2 = logTeffToHex(star2_log_Teff)

  const h1pct  = (center_h1_1 * 100).toFixed(1)
  const he1pct = (center_he4_1 * 100).toFixed(1)
  const h2pct  = (center_h1_2 * 100).toFixed(1)
  const he2pct = (center_he4_2 * 100).toFixed(1)

  return (
    <div className="info-panel">
      <h3>System State</h3>

      {/* ── Star 1 ── */}
      <div className="star-block">
        <div className="star-label" style={{ color: '#ff9944' }}>
          ★ Donor (Star 1)
        </div>
        <Row label="Mass"   val={`${star1_mass.toFixed(3)} M☉`} />
        <Row label="Radius" val={`${R1} R☉`} />
        <Row label="T_eff"  val={`${teff1} K`} color={color1} />
        <Row label="log L"  val={star1_log_L.toFixed(3)} />
        <Row label="log g"  val={star1_log_g.toFixed(3)} />
        <Row label="He core" val={`${he_core_mass_1.toFixed(3)} M☉`} />
        <div className="composition-bar-wrap">
          <div className="comp-label">
            <span>H {h1pct}%</span>
            <span>He {he1pct}%</span>
          </div>
          <div className="comp-bar">
            <div className="comp-h"  style={{ width: `${center_h1_1 * 100}%` }} />
            <div className="comp-he" style={{ width: `${center_he4_1 * 100}%` }} />
          </div>
        </div>
      </div>

      <div className="divider" />

      {/* ── Star 2 ── */}
      <div className="star-block">
        <div className="star-label" style={{ color: '#44ddff' }}>
          ★ Accretor / BSS (Star 2)
        </div>
        <Row label="Mass"   val={`${star2_mass.toFixed(3)} M☉`} />
        <Row label="Radius" val={`${R2} R☉`} />
        <Row label="T_eff"  val={`${teff2} K`} color={color2} />
        <Row label="log L"  val={star2_log_L.toFixed(3)} />
        <Row label="log g"  val={star2_log_g.toFixed(3)} />
        <Row label="He core" val={`${he_core_mass_2.toFixed(3)} M☉`} />
        <div className="composition-bar-wrap">
          <div className="comp-label">
            <span>H {h2pct}%</span>
            <span>He {he2pct}%</span>
          </div>
          <div className="comp-bar">
            <div className="comp-h"  style={{ width: `${center_h1_2 * 100}%` }} />
            <div className="comp-he" style={{ width: `${center_he4_2 * 100}%` }} />
          </div>
        </div>
      </div>

      <div className="divider" />

      {/* ── Orbital ── */}
      <div className="star-block">
        <div className="star-label" style={{ color: '#aabb88' }}>⊙ Orbit</div>
        <Row label="Separation" val={`${binary_separation.toFixed(2)} R☉`} />
        <Row label="Period"     val={`${period_days.toFixed(4)} d`} />
        <Row label="RL overflow"
             val={rl_relative_overflow_1.toFixed(5)}
             color={is_rlof ? '#ff4488' : undefined} />
        {is_rlof && (
          <Row label="Ṁ transfer"
               val={`10^${lg_mtransfer_rate.toFixed(2)} M☉/yr`}
               color="#ff4488" />
        )}
      </div>

      {is_rlof && (
        <div className="rlof-indicator">⚡ Mass Transfer Active</div>
      )}
    </div>
  )
}

function Row({ label, val, color }) {
  return (
    <div className="star-row">
      <span className="label">{label}</span>
      <span className="val" style={color ? { color } : {}}>{val}</span>
    </div>
  )
}
