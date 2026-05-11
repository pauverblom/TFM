import { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import { Html } from '@react-three/drei'
import * as THREE from 'three'
import StarMesh from './StarMesh.jsx'
import AccretionStream from './AccretionStream.jsx'
import { logTeffToColor } from '../utils/colorUtils.js'

// One full animated orbit = this many seconds
const ANIM_PERIOD_S = 6.0

export default function BinarySystem({ frame }) {
  const orbitGroupRef = useRef()

  const {
    binary_separation: a,
    r1_orb, r2_orb,
    star1_log_R, star2_log_R,
    star1_log_Teff, star2_log_Teff,
    star1_log_L, star2_log_L,
    star1_mass, star2_mass,
    he_core_mass_1, he_core_mass_2,
    l1_position,
    is_rlof, lg_mtransfer_rate,
    rl_1, rl_2,
  } = frame

  const R1 = Math.pow(10, star1_log_R)   // Rsun
  const R2 = Math.pow(10, star2_log_R)   // Rsun
  const L1 = Math.pow(10, star1_log_L)   // Lsun
  const L2 = Math.pow(10, star2_log_L)   // Lsun

  const color1 = useMemo(() => logTeffToColor(star1_log_Teff), [star1_log_Teff])
  const color2 = useMemo(() => logTeffToColor(star2_log_Teff), [star2_log_Teff])

  // Animate the orbit group rotation
  useFrame(({ clock }) => {
    if (!orbitGroupRef.current) return
    orbitGroupRef.current.rotation.z = (clock.getElapsedTime() / ANIM_PERIOD_S) * Math.PI * 2
  })

  // Orbital ring geometry (lazy – recreated on separation change)
  const ring1Curve = useMemo(() => buildRingPoints(r1_orb), [r1_orb])
  const ring2Curve = useMemo(() => buildRingPoints(r2_orb), [r2_orb])
  const gridPoints = useMemo(() => buildEquatorialGrid(a * 1.6), [a])

  // Point-light intensities from luminosities (log scale, cap for sanity)
  const lightInt1 = Math.min(12, Math.pow(10, (star1_log_L - 1)))
  const lightInt2 = Math.min(12, Math.pow(10, (star2_log_L - 1)))

  return (
    <group>
      {/* ── Faint equatorial reference grid ── */}
      <lineSegments>
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" array={gridPoints} itemSize={3} count={gridPoints.length / 3} />
        </bufferGeometry>
        <lineBasicMaterial color="#1a1a44" transparent opacity={0.5} />
      </lineSegments>

      {/* ── Orbital rings (static in lab frame) ── */}
      <OrbitalRing points={ring1Curve} color="#ff7722" />
      <OrbitalRing points={ring2Curve} color="#22bbff" />

      {/* ── Center of mass dot ── */}
      <mesh>
        <sphereGeometry args={[0.12, 8, 8]} />
        <meshBasicMaterial color="#ffffff" />
      </mesh>

      {/* ── Co-rotating group: stars + stream ── */}
      <group ref={orbitGroupRef}>
        {/* Star 1 – Donor */}
        <group position={[-r1_orb, 0, 0]}>
          <StarMesh
            radius={R1}
            color={color1}
            luminosity={L1}
            mass={star1_mass}
            heCoreRadius={R1 * (he_core_mass_1 / star1_mass) ** (1 / 3)}
            isRlof={is_rlof}
          />
          <pointLight color={color1} intensity={lightInt1} distance={a * 6} decay={2} />
          <Html center distanceFactor={22} zIndexRange={[0, 10]}>
            <span style={{ color: '#ffaa55', fontSize: 11, fontWeight: 700, letterSpacing: '0.05em',
                           textShadow: '0 0 6px #ff7700', whiteSpace: 'nowrap', userSelect: 'none' }}>
              Donor {(star1_mass).toFixed(2)} M☉
            </span>
          </Html>
        </group>

        {/* Star 2 – Accretor / Blue Straggler */}
        <group position={[r2_orb, 0, 0]}>
          <StarMesh
            radius={R2}
            color={color2}
            luminosity={L2}
            mass={star2_mass}
            heCoreRadius={R2 * (he_core_mass_2 / star2_mass) ** (1 / 3)}
            isAccretor={is_rlof}
          />
          <pointLight color={color2} intensity={lightInt2} distance={a * 6} decay={2} />
          <Html center distanceFactor={22} zIndexRange={[0, 10]}>
            <span style={{ color: '#44ddff', fontSize: 11, fontWeight: 700, letterSpacing: '0.05em',
                           textShadow: '0 0 6px #00bbff', whiteSpace: 'nowrap', userSelect: 'none' }}>
              {is_rlof ? 'Blue Straggler ★' : 'Accretor'} {(star2_mass).toFixed(2)} M☉
            </span>
          </Html>

          {/* Accretion disk – torus around Star 2 during RLOF */}
          {is_rlof && (
            <AccretionDisk
              innerRadius={R2 * 1.1}
              outerRadius={Math.min(rl_2 * 0.55, R2 * 3.5)}
              intensity={Math.min(1, (lg_mtransfer_rate + 15) / 9)}
            />
          )}
        </group>

        {/* ── Accretion stream through L1 ── */}
        {is_rlof && (
          <AccretionStream
            x_donor={-r1_orb}
            x_l1={l1_position}
            x_accretor={r2_orb}
            r_accretor={R2}
            intensity={Math.min(1, (lg_mtransfer_rate + 15) / 9)}
          />
        )}

        {/* ── Roche lobe wireframes ── */}
        <RocheLobe center={-r1_orb} radius={rl_1} isOverflowing={is_rlof} colorStr="#ff8844" />
        <RocheLobe center={r2_orb}  radius={rl_2} isOverflowing={false}   colorStr="#44bbff" />
      </group>
    </group>
  )
}

/* ────────────────────────────────── helpers ── */

function OrbitalRing({ points, color }) {
  const geo = useMemo(() => {
    const g = new THREE.BufferGeometry()
    g.setAttribute('position', new THREE.BufferAttribute(points, 3))
    return g
  }, [points])

  return (
    <lineLoop geometry={geo}>
      <lineBasicMaterial color={color} transparent opacity={0.20} />
    </lineLoop>
  )
}

function RocheLobe({ center, radius, isOverflowing, colorStr }) {
  return (
    <mesh position={[center, 0, 0]}>
      <sphereGeometry args={[radius, 20, 14]} />
      <meshBasicMaterial
        color={colorStr}
        wireframe
        transparent
        opacity={isOverflowing ? 0.30 : 0.10}
      />
    </mesh>
  )
}

function AccretionDisk({ innerRadius, outerRadius, intensity }) {
  const tubeRadius = (outerRadius - innerRadius) * 0.48
  const midRadius = innerRadius + tubeRadius
  return (
    <mesh rotation={[Math.PI / 2, 0, 0]}>
      <torusGeometry args={[midRadius, tubeRadius, 8, 60]} />
      <meshStandardMaterial
        color="#0066cc"
        emissive="#003399"
        emissiveIntensity={0.8 * intensity}
        transparent
        opacity={0.35 * intensity}
      />
    </mesh>
  )
}

function buildRingPoints(radius) {
  const N = 128
  const arr = new Float32Array(N * 3)
  for (let i = 0; i < N; i++) {
    const theta = (i / N) * Math.PI * 2
    arr[i * 3]     = Math.cos(theta) * radius
    arr[i * 3 + 1] = Math.sin(theta) * radius
    arr[i * 3 + 2] = 0
  }
  return arr
}

function buildEquatorialGrid(extent) {
  const lines = []
  const step = Math.ceil(extent / 5)
  for (let x = -Math.ceil(extent); x <= Math.ceil(extent); x += step) {
    lines.push(x, 0, -extent, x, 0, extent)
  }
  for (let z = -Math.ceil(extent); z <= Math.ceil(extent); z += step) {
    lines.push(-extent, 0, z, extent, 0, z)
  }
  return new Float32Array(lines)
}
