import { useRef, useMemo } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Stars } from '@react-three/drei'
import { EffectComposer, Bloom } from '@react-three/postprocessing'
import BinarySystem from './BinarySystem.jsx'

export default function Scene3D({ frame, frames, currentIndex }) {
  return (
    <Canvas
      camera={{ position: [0, 35, 65], fov: 42, near: 0.1, far: 2000 }}
      gl={{ antialias: true, alpha: false }}
      style={{ background: '#020210', width: '100%', height: '100%' }}
    >
      {/* ── Lighting ── */}
      <ambientLight intensity={0.08} />

      {/* ── Space background ── */}
      <Stars radius={400} depth={80} count={6000} factor={5} saturation={0.4} fade speed={0.3} />

      {/* ── Binary system (all objects in one component) ── */}
      <BinarySystem frame={frame} />

      {/* ── Camera controls ── */}
      <OrbitControls
        enableDamping
        dampingFactor={0.05}
        minDistance={5}
        maxDistance={300}
        makeDefault
      />

      {/* ── Bloom glow ── */}
      <EffectComposer multisampling={0}>
        <Bloom
          luminanceThreshold={0.15}
          luminanceSmoothing={0.4}
          intensity={1.4}
          mipmapBlur
        />
      </EffectComposer>
    </Canvas>
  )
}
