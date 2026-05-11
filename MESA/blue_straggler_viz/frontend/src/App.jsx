import { useRef, useEffect, useState, useCallback } from 'react'
import Scene3D from './components/Scene3D.jsx'
import TimelineScrubber from './components/TimelineScrubber.jsx'
import HRDiagram from './components/HRDiagram.jsx'
import MassPeriodPlot from './components/MassPeriodPlot.jsx'
import InfoPanel from './components/InfoPanel.jsx'
import { logTeffToHex } from './utils/colorUtils.js'

const PHASE_COLORS = {
  'Main Sequence (ZAMS)': '#44ff88',
  'Main Sequence': '#88ffcc',
  'Terminal Age MS': '#ffdd44',
  'Giant Branch': '#ff8844',
  'RLOF Onset': '#ff4488',
  'Active RLOF': '#ff0066',
  'Late RLOF': '#cc0044',
}

export default function App() {
  const [frames, setFrames] = useState([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [playSpeed, setPlaySpeed] = useState(3)   // frames per second
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const playRef = useRef(null)

  useEffect(() => {
    fetch('/api/data')
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json()
      })
      .then((data) => {
        setFrames(data.frames)
        // Start near RLOF onset for an immediate dramatic view
        const rlofIdx = data.frames.findIndex((f) => f.is_rlof)
        setCurrentIndex(rlofIdx > 0 ? Math.max(0, rlofIdx - 5) : 0)
        setLoading(false)
      })
      .catch((e) => {
        setError(e.message)
        setLoading(false)
      })
  }, [])

  // Auto-play
  useEffect(() => {
    if (isPlaying && frames.length > 0) {
      const interval = 1000 / playSpeed
      playRef.current = setInterval(() => {
        setCurrentIndex((i) => {
          if (i >= frames.length - 1) {
            setIsPlaying(false)
            return i
          }
          return i + 1
        })
      }, interval)
    } else {
      clearInterval(playRef.current)
    }
    return () => clearInterval(playRef.current)
  }, [isPlaying, playSpeed, frames.length])

  const handleKeyDown = useCallback(
    (e) => {
      if (e.key === 'ArrowRight') setCurrentIndex((i) => Math.min(i + 1, frames.length - 1))
      if (e.key === 'ArrowLeft') setCurrentIndex((i) => Math.max(i - 1, 0))
      if (e.key === ' ') { e.preventDefault(); setIsPlaying((p) => !p) }
    },
    [frames.length]
  )

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [handleKeyDown])

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner" />
        <p>Parsing MESA binary star data…</p>
        <p className="loading-sub">Computing L1 Lagrange points & aligning timelines</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="loading-screen">
        <p style={{ color: '#ff4444' }}>⚠ Backend error: {error}</p>
        <p className="loading-sub">Make sure the FastAPI server is running on port 8000.</p>
      </div>
    )
  }

  const frame = frames[currentIndex]
  const phaseColor = PHASE_COLORS[frame.phase] ?? '#ffffff'

  return (
    <div className="app">
      {/* ── Header ── */}
      <header className="header">
        <div className="header-left">
          <h1>Blue Straggler Binary Evolution</h1>
          <span className="header-sub">MESA Close Binary Simulation</span>
        </div>
        <div className="header-center">
          <div className="phase-badge" style={{ borderColor: phaseColor, color: phaseColor }}>
            {frame.phase}
          </div>
        </div>
        <div className="header-right">
          <div className="key-values">
            <span>
              <span className="kv-label">Age</span>
              <span className="kv-val">{(frame.star_age_gyr).toFixed(4)} Gyr</span>
            </span>
            <span>
              <span className="kv-label">Period</span>
              <span className="kv-val">{frame.period_days.toFixed(3)} d</span>
            </span>
            <span>
              <span className="kv-label">Separation</span>
              <span className="kv-val">{frame.binary_separation.toFixed(2)} R☉</span>
            </span>
          </div>
        </div>
      </header>

      {/* ── Main 3D + Info panel ── */}
      <div className="scene-container">
        <Scene3D frame={frame} frames={frames} currentIndex={currentIndex} />
        <InfoPanel frame={frame} />
      </div>

      {/* ── Timeline scrubber ── */}
      <TimelineScrubber
        frames={frames}
        currentIndex={currentIndex}
        setCurrentIndex={setCurrentIndex}
        isPlaying={isPlaying}
        setIsPlaying={setIsPlaying}
        playSpeed={playSpeed}
        setPlaySpeed={setPlaySpeed}
      />

      {/* ── 2D Charts ── */}
      <div className="charts-row">
        <HRDiagram frames={frames} currentIndex={currentIndex} />
        <MassPeriodPlot frames={frames} currentIndex={currentIndex} />
      </div>
    </div>
  )
}
