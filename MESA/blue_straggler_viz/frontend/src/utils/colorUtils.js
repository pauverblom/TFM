import * as THREE from 'three'

/**
 * Approximates blackbody RGB from an effective temperature in Kelvin.
 * Algorithm by Tanner Helland, adapted for [0,1] range.
 */
export function kelvinToRGB(temp) {
  const t = Math.max(1000, Math.min(40000, temp)) / 100
  let r, g, b

  if (t <= 66) {
    r = 255
    g = Math.max(0, 99.4708025861 * Math.log(t) - 161.1195681661)
    b = t <= 19 ? 0 : Math.max(0, 138.5177312231 * Math.log(t - 10) - 305.0447927307)
  } else {
    r = Math.max(0, 329.698727446 * Math.pow(t - 60, -0.1332047592))
    g = Math.max(0, 288.1221695283 * Math.pow(t - 60, -0.0755148492))
    b = 255
  }

  return {
    r: Math.min(255, r) / 255,
    g: Math.min(255, g) / 255,
    b: Math.min(255, b) / 255,
  }
}

/**
 * Returns a THREE.Color for a given log10(Teff).
 */
export function logTeffToColor(logTeff) {
  const teff = Math.pow(10, logTeff)
  const { r, g, b } = kelvinToRGB(teff)
  return new THREE.Color(r, g, b)
}

/**
 * Returns a CSS hex color string for a given log10(Teff).
 */
export function logTeffToHex(logTeff) {
  const teff = Math.pow(10, logTeff)
  const { r, g, b } = kelvinToRGB(teff)
  const toHex = (v) => Math.round(v * 255).toString(16).padStart(2, '0')
  return `#${toHex(r)}${toHex(g)}${toHex(b)}`
}

/**
 * Maps a mass-transfer rate to a stream opacity/intensity.
 * lg_mtransfer_rate ranges from -99 (none) to ~ -6.5 (peak).
 */
export function mtransferIntensity(lg_mdot) {
  if (lg_mdot < -15) return 0
  return Math.min(1, (lg_mdot + 15) / 8.5)
}

/**
 * Linear interpolation.
 */
export function lerp(a, b, t) {
  return a + (b - a) * t
}

/**
 * Format a number in scientific notation for display.
 */
export function fmtSci(val, decimals = 3) {
  return val.toExponential(decimals)
}

/**
 * Format age in human-readable Gyr/Myr/kyr.
 */
export function fmtAge(yr) {
  if (yr >= 1e9) return `${(yr / 1e9).toFixed(3)} Gyr`
  if (yr >= 1e6) return `${(yr / 1e6).toFixed(2)} Myr`
  return `${(yr / 1e3).toFixed(1)} kyr`
}
