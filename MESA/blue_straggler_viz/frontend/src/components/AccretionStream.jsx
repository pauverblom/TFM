import { useRef, useMemo, useCallback } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

const N_PARTICLES = 280
const PARTICLE_SPEED = 0.6   // bezier curve units per second

/**
 * Renders the mass-transfer accretion stream from the donor surface, through
 * the L1 Lagrange point, and onto the accretor.
 *
 * Particle positions are animated along a quadratic Bézier curve that curves
 * "downward" (−y) to mimic the Coriolis deflection in the co-rotating frame.
 * The tube mesh provides a static visual channel; points provide flowing motion.
 */
export default function AccretionStream({ x_donor, x_l1, x_accretor, r_accretor, intensity }) {
  const pointsRef = useRef()
  const posArr = useMemo(() => new Float32Array(N_PARTICLES * 3), [])

  // Bézier control points in the co-rotating frame (y=0 plane)
  const [p0, p1, p2] = useMemo(() => {
    const start = new THREE.Vector3(x_l1, 0, 0)
    const end   = new THREE.Vector3(x_accretor, 0, 0)
    const dx    = x_accretor - x_l1
    // Coriolis deflects the stream in the −y direction (prograde orbit)
    const ctrl  = new THREE.Vector3(
      x_l1 + dx * 0.42,
      -Math.abs(dx) * 0.50,
      0
    )
    return [start, ctrl, end]
  }, [x_l1, x_accretor])

  // Tube mesh follows the same Bézier curve
  const tubeCurve = useMemo(() => {
    const pts = []
    for (let i = 0; i <= 40; i++) {
      const t = i / 40
      const u = 1 - t
      pts.push(
        new THREE.Vector3(
          u * u * p0.x + 2 * u * t * p1.x + t * t * p2.x,
          u * u * p0.y + 2 * u * t * p1.y + t * t * p2.y,
          0
        )
      )
    }
    return new THREE.CatmullRomCurve3(pts)
  }, [p0, p1, p2])

  // Animate particles flowing from L1 → accretor
  useFrame(({ clock }) => {
    if (!pointsRef.current) return
    const t = clock.getElapsedTime()
    const attr = pointsRef.current.geometry.attributes.position

    for (let i = 0; i < N_PARTICLES; i++) {
      // Stagger each particle along the curve, all flowing forward
      const u = ((i / N_PARTICLES + t * PARTICLE_SPEED) % 1.0)
      const s = 1 - u
      const x = s * s * p0.x + 2 * s * u * p1.x + u * u * p2.x
      const y = s * s * p0.y + 2 * s * u * p1.y + u * u * p2.y
      attr.setXYZ(i, x, y, (Math.random() - 0.5) * 0.06)
    }
    attr.needsUpdate = true
  })

  const opacity = Math.max(0.2, Math.min(0.9, intensity))

  return (
    <group>
      {/* ── Tube channel ── */}
      <mesh>
        <tubeGeometry args={[tubeCurve, 40, 0.045, 5, false]} />
        <meshBasicMaterial
          color="#00bbff"
          transparent
          opacity={0.18 * opacity}
          depthWrite={false}
        />
      </mesh>

      {/* ── Flowing particles ── */}
      <points ref={pointsRef}>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            array={posArr}
            itemSize={3}
            count={N_PARTICLES}
          />
        </bufferGeometry>
        <pointsMaterial
          size={0.13}
          color="#44ffff"
          transparent
          opacity={0.75 * opacity}
          depthWrite={false}
          sizeAttenuation
        />
      </points>

      {/* ── L1 saddle point marker ── */}
      <mesh position={[x_l1, 0, 0]}>
        <sphereGeometry args={[0.18, 8, 8]} />
        <meshBasicMaterial color="#ff88ff" transparent opacity={0.7} />
      </mesh>
    </group>
  )
}
