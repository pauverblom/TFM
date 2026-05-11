import { useMemo } from 'react'
import createPlotlyComponent from 'react-plotly.js/factory'
import Plotly from 'plotly.js-dist-min'
import { logTeffToHex } from '../utils/colorUtils.js'

const Plot = createPlotlyComponent(Plotly)

const LAYOUT_BASE = {
  paper_bgcolor: 'transparent',
  plot_bgcolor:  'rgba(8,8,28,0.7)',
  font: { color: '#aabbdd', size: 11, family: 'Inter, system-ui, sans-serif' },
  margin: { l: 46, r: 14, t: 32, b: 38 },
  showlegend: true,
  legend: {
    bgcolor: 'rgba(0,0,0,0)',
    bordercolor: 'rgba(100,120,255,0.2)',
    borderwidth: 1,
    x: 0.02, y: 0.98, xanchor: 'left', yanchor: 'top',
    font: { size: 10 },
  },
  xaxis: {
    gridcolor: 'rgba(255,255,255,0.06)',
    zerolinecolor: 'rgba(255,255,255,0.15)',
  },
  yaxis: {
    gridcolor: 'rgba(255,255,255,0.06)',
    zerolinecolor: 'rgba(255,255,255,0.15)',
  },
}

/**
 * HR Diagram (Hertzsprung-Russell).
 * X-axis: log Teff reversed (hot left), Y-axis: log L.
 * Shows full evolutionary tracks for both stars plus a current-position marker.
 * A fading trail emphasises past evolution.
 */
export default function HRDiagram({ frames, currentIndex }) {
  const { traceS1, traceS2, markerS1, markerS2, isoLines } = useMemo(() => {
    const teff1 = frames.map((f) => f.star1_log_Teff)
    const L1    = frames.map((f) => f.star1_log_L)
    const teff2 = frames.map((f) => f.star2_log_Teff)
    const L2    = frames.map((f) => f.star2_log_L)

    // Full tracks (dim)
    const traceS1 = {
      x: teff1, y: L1,
      mode: 'lines', type: 'scatter',
      name: 'Donor track',
      line: { color: 'rgba(255,120,40,0.30)', width: 1.2 },
      hoverinfo: 'skip',
    }
    const traceS2 = {
      x: teff2, y: L2,
      mode: 'lines', type: 'scatter',
      name: 'Accretor track',
      line: { color: 'rgba(40,180,255,0.30)', width: 1.2 },
      hoverinfo: 'skip',
    }

    // Past trail (brighter)
    const trailLen = Math.min(currentIndex + 1, frames.length)
    const pastS1 = {
      x: teff1.slice(0, trailLen),
      y: L1.slice(0, trailLen),
      mode: 'lines', type: 'scatter',
      name: 'Donor (past)',
      line: { color: 'rgba(255,140,60,0.75)', width: 1.8 },
      showlegend: false,
      hoverinfo: 'skip',
    }
    const pastS2 = {
      x: teff2.slice(0, trailLen),
      y: L2.slice(0, trailLen),
      mode: 'lines', type: 'scatter',
      name: 'Accretor (past)',
      line: { color: 'rgba(60,200,255,0.75)', width: 1.8 },
      showlegend: false,
      hoverinfo: 'skip',
    }

    // Current position markers
    const f = frames[currentIndex]
    const markerS1 = {
      x: [f.star1_log_Teff], y: [f.star1_log_L],
      mode: 'markers', type: 'scatter',
      name: `Donor (${f.star1_mass.toFixed(2)} M☉)`,
      marker: {
        size: 12,
        color: logTeffToHex(f.star1_log_Teff),
        line: { color: '#ff9944', width: 2 },
        symbol: 'circle',
      },
      hovertemplate: 'log Teff=%{x:.3f}<br>log L=%{y:.3f}<extra>Donor</extra>',
    }
    const markerS2 = {
      x: [f.star2_log_Teff], y: [f.star2_log_L],
      mode: 'markers', type: 'scatter',
      name: `Accretor (${f.star2_mass.toFixed(2)} M☉)`,
      marker: {
        size: 12,
        color: logTeffToHex(f.star2_log_Teff),
        line: { color: '#44ddff', width: 2 },
        symbol: 'circle',
      },
      hovertemplate: 'log Teff=%{x:.3f}<br>log L=%{y:.3f}<extra>Accretor</extra>',
    }

    // Approximate ZAMS line (rough reference)
    const zamsTeff = [4.62, 4.48, 4.39, 4.26, 4.10, 3.90, 3.78, 3.74, 3.68]
    const zamsL    = [4.0,  3.5,  3.0,  2.5,  2.0,  1.0,  0.5,  0.1, -0.3]
    const isoLines = {
      x: zamsTeff, y: zamsL,
      mode: 'lines', type: 'scatter',
      name: 'ZAMS (approx)',
      line: { color: 'rgba(200,220,255,0.18)', width: 1, dash: 'dot' },
      hoverinfo: 'skip',
    }

    return { traceS1, traceS2, pastS1, pastS2, markerS1, markerS2, isoLines }
  }, [frames, currentIndex])

  const layout = useMemo(() => ({
    ...LAYOUT_BASE,
    title: { text: 'HR Diagram', font: { color: '#cce0ff', size: 13 }, x: 0.5, y: 0.97 },
    xaxis: {
      ...LAYOUT_BASE.xaxis,
      title: { text: 'log T<sub>eff</sub> (K)', font: { size: 10 } },
      autorange: 'reversed',
      tickformat: '.2f',
    },
    yaxis: {
      ...LAYOUT_BASE.yaxis,
      title: { text: 'log L / L☉', font: { size: 10 } },
    },
  }), [])

  const { pastS1, pastS2 } = useMemo(() => {
    const trailLen = Math.min(currentIndex + 1, frames.length)
    const teff1 = frames.map((f) => f.star1_log_Teff)
    const L1    = frames.map((f) => f.star1_log_L)
    const teff2 = frames.map((f) => f.star2_log_Teff)
    const L2    = frames.map((f) => f.star2_log_L)
    return {
      pastS1: { x: teff1.slice(0, trailLen), y: L1.slice(0, trailLen), mode: 'lines', type: 'scatter', showlegend: false, line: { color: 'rgba(255,140,60,0.70)', width: 1.8 }, hoverinfo: 'skip' },
      pastS2: { x: teff2.slice(0, trailLen), y: L2.slice(0, trailLen), mode: 'lines', type: 'scatter', showlegend: false, line: { color: 'rgba(60,200,255,0.70)', width: 1.8 }, hoverinfo: 'skip' },
    }
  }, [frames, currentIndex])

  return (
    <div className="chart-panel">
      <Plot
        data={[traceS1, traceS2, pastS1, pastS2, markerS1, markerS2, isoLines]}
        layout={layout}
        config={{ displayModeBar: false, responsive: true }}
        style={{ width: '100%', height: '100%' }}
        useResizeHandler
      />
    </div>
  )
}
