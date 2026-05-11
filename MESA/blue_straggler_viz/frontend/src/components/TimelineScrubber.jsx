import { useMemo } from 'react'
import { fmtAge } from '../utils/colorUtils.js'

/**
 * Timeline scrubber with:
 * - Play / Pause button
 * - Slider mapped to model index
 * - RLOF phase highlighted in pink below the slider
 * - Speed selector
 * - Keyboard shortcuts: ← → Space
 */
export default function TimelineScrubber({
  frames, currentIndex, setCurrentIndex,
  isPlaying, setIsPlaying,
  playSpeed, setPlaySpeed,
}) {
  const n = frames.length
  const frame = frames[currentIndex]

  // Find RLOF onset & end for the highlight region
  const { rlofStart, rlofEnd } = useMemo(() => {
    const start = frames.findIndex((f) => f.is_rlof)
    let end = start
    for (let i = frames.length - 1; i >= 0; i--) {
      if (frames[i].is_rlof) { end = i; break }
    }
    return { rlofStart: start, rlofEnd: end }
  }, [frames])

  const pct = ((currentIndex / Math.max(1, n - 1)) * 100).toFixed(2)
  const rlofLeft  = ((rlofStart / (n - 1)) * 100).toFixed(2)
  const rlofWidth = (((rlofEnd - rlofStart) / (n - 1)) * 100).toFixed(2)

  return (
    <div className="timeline-bar">
      <div className="timeline-controls">
        {/* Play / Pause */}
        <button
          className="btn-play"
          onClick={() => setIsPlaying((p) => !p)}
          title="Play / Pause (Space)"
        >
          {isPlaying ? '⏸' : '▶'}
        </button>

        {/* Slider */}
        <div className="slider-wrap">
          {/* Pink RLOF region */}
          {rlofStart >= 0 && (
            <div
              className="rlof-region"
              style={{ left: `${rlofLeft}%`, width: `${rlofWidth}%` }}
            />
          )}
          <input
            type="range"
            className="timeline-slider"
            min={0}
            max={n - 1}
            step={1}
            value={currentIndex}
            style={{ '--pct': `${pct}%` }}
            onChange={(e) => {
              setIsPlaying(false)
              setCurrentIndex(Number(e.target.value))
            }}
          />
        </div>

        {/* Speed */}
        <select
          className="speed-select"
          value={playSpeed}
          onChange={(e) => setPlaySpeed(Number(e.target.value))}
          title="Playback speed"
        >
          <option value={1}>1×</option>
          <option value={3}>3×</option>
          <option value={8}>8×</option>
          <option value={20}>20×</option>
        </select>
      </div>

      <div className="timeline-meta">
        <span>Frame {currentIndex + 1} / {n}</span>
        <span className="timeline-age">{fmtAge(frame.star_age)}</span>
        <span style={{ color: rlofStart >= 0 ? '#ff4488' : 'var(--text-dim)' }}>
          {frame.is_rlof
            ? `⚡ RLOF  Ṁ = 10^${frame.lg_mtransfer_rate.toFixed(1)} M☉/yr`
            : `← ${fmtAge(frames[Math.min(rlofStart > 0 ? rlofStart : n - 1, n - 1)].star_age - frame.star_age)} to RLOF`}
        </span>
      </div>
    </div>
  )
}
