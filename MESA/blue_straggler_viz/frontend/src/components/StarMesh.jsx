import { useRef, useMemo } from 'react'
import * as THREE from 'three'

/**
 * A single star rendered as a glowing sphere.
 * Uses emissive material so it lights itself + blooms in post-processing.
 * An optional inner sphere shows the helium core growth.
 */
export default function StarMesh({ radius, color, luminosity, mass, heCoreRadius, isRlof, isAccretor }) {
  const clampedRadius = Math.max(0.08, radius)
  const segments = radius > 4 ? 40 : 28

  // Emissive intensity scales with luminosity (log scale, 1 Lsun = 0.6)
  const emissiveInt = Math.min(3.5, 0.4 + Math.log10(Math.max(1, luminosity)) * 0.55)

  return (
    <group>
      {/* ── Main stellar body ── */}
      <mesh>
        <sphereGeometry args={[clampedRadius, segments, segments]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={emissiveInt}
          roughness={0.7}
          metalness={0}
        />
      </mesh>

      {/* ── Outer corona glow (visible back-face) ── */}
      <mesh>
        <sphereGeometry args={[clampedRadius * 1.25, 16, 12]} />
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.06}
          side={THREE.BackSide}
          depthWrite={false}
        />
      </mesh>

      {/* ── Second corona layer ── */}
      <mesh>
        <sphereGeometry args={[clampedRadius * 1.65, 12, 10]} />
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.025}
          side={THREE.BackSide}
          depthWrite={false}
        />
      </mesh>

      {/* ── Helium core indicator (golden inner sphere) ── */}
      {heCoreRadius > 0.05 && heCoreRadius < clampedRadius * 0.98 && (
        <mesh>
          <sphereGeometry args={[heCoreRadius, 18, 14]} />
          <meshStandardMaterial
            color="#ffcc55"
            emissive="#ffaa00"
            emissiveIntensity={0.8}
            transparent
            opacity={0.55}
          />
        </mesh>
      )}

      {/* ── RLOF distortion ring (shows mass loss side) ── */}
      {isRlof && (
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[clampedRadius * 0.85, clampedRadius * 0.08, 6, 32]} />
          <meshBasicMaterial color="#ff4488" transparent opacity={0.4} />
        </mesh>
      )}
    </group>
  )
}
