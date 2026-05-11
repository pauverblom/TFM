import { useMemo } from 'react'
import createPlotlyComponent from 'react-plotly.js/factory'
import Plotly from 'plotly.js-dist-min'

const Plot = createPlotlyComponent(Plotly)

/**
 * Dual-y-axis plot of:
 *   Left  – Star 1 mass (orange), Star 2 mass (cyan)
 *   Right – Orbital period (green)
 * A vertical red line follows the current scrubber position.
 * Annotates key evolutionary events.
 */
export default function MassPeriodPlot({ frames, currentIndex }) {
  const ages   = useMemo(() => frames.map((f) => f.star_age_gyr), [frames])
  const m1     = useMemo(() => frames.map((f) => f.star1_mass), [frames])
  const m2     = useMemo(() => frames.map((f) => f.star2_mass), [frames])
  const period = useMemo(() => frames.map((f) => f.period_days), [frames])

  const currentAge = frames[currentIndex].star_age_gyr

  const BASE = {
    paper_bgcolor: 'transparent',
    plot_bgcolor:  'rgba(8,8,28,0.7)',
    font: { color: '#aabbdd', size: 11, family: 'Inter, system-ui, sans-serif' },
    margin: { l: 46, r: 46, t: 32, b: 38 },
    showlegend: true,
    legend: {
      bgcolor: 'rgba(0,0,0,0)',
      bordercolor: 'rgba(100,120,255,0.2)',
      borderwidth: 1,
      x: 0.02, y: 0.98, xanchor: 'left', yanchor: 'top',
      font: { size: 10 },
    },
  }

  const layout = useMemo(() => {
    const rlofOnset  = frames.find((f) => f.is_rlof)?.star_age_gyr ?? null
    const massReversal = (() => {
      for (let i = 1; i < frames.length; i++) {
        if (frames[i].star1_mass < frames[i].star2_mass &&
            frames[i-1].star1_mass >= frames[i-1].star2_mass) {
          return frames[i].star_age_gyr
        }
      }
      return null
    })()

    const shapes = [
      // Current time vertical line
      {
        type: 'line',
        x0: currentAge, x1: currentAge,
        y0: 0, y1: 1, yref: 'paper',
        line: { color: 'rgba(255,80,80,0.8)', width: 1.5, dash: 'solid' },
      },
    ]

    const annotations = []
    if (rlofOnset) {
      shapes.push({
        type: 'rect',
        x0: rlofOnset, x1: ages[ages.length - 1],
        y0: 0, y1: 1, yref: 'paper',
        fillcolor: 'rgba(255,20,80,0.06)',
        line: { width: 0 },
        layer: 'below',
      })
      annotations.push({
        x: rlofOnset, y: 0.92, yref: 'paper',
        text: 'RLOF', showarrow: false,
        font: { color: '#ff4488', size: 9 },
        xanchor: 'left',
      })
    }
    if (massReversal) {
      annotations.push({
        x: massReversal, y: 0.76, yref: 'paper',
        text: 'M₁=M₂', showarrow: false,
        font: { color: '#aaffcc', size: 9 },
        xanchor: 'center',
      })
    }

    return {
      ...BASE,
      title: { text: 'Mass & Orbital Period Evolution', font: { color: '#cce0ff', size: 13 }, x: 0.5, y: 0.97 },
      xaxis: {
        title: { text: 'Age (Gyr)', font: { size: 10 } },
        gridcolor: 'rgba(255,255,255,0.06)',
        zerolinecolor: 'rgba(255,255,255,0.15)',
      },
      yaxis: {
        title: { text: 'Mass (M☉)', font: { size: 10 } },
        gridcolor: 'rgba(255,255,255,0.06)',
        zerolinecolor: 'rgba(255,255,255,0.15)',
        rangemode: 'tozero',
      },
      yaxis2: {
        title: { text: 'Period (days)', font: { size: 10 }, standoff: 4 },
        overlaying: 'y',
        side: 'right',
        gridcolor: 'transparent',
        showgrid: false,
        rangemode: 'tozero',
      },
      shapes,
      annotations,
    }
  }, [frames, currentAge, ages])

  const traces = useMemo(() => [
    {
      x: ages, y: m1,
      mode: 'lines', type: 'scatter',
      name: 'M₁ Donor',
      line: { color: '#ff8833', width: 2 },
      yaxis: 'y',
      hovertemplate: 'Age=%{x:.4f} Gyr<br>M₁=%{y:.4f} M☉<extra></extra>',
    },
    {
      x: ages, y: m2,
      mode: 'lines', type: 'scatter',
      name: 'M₂ Accretor',
      line: { color: '#44ccff', width: 2 },
      yaxis: 'y',
      hovertemplate: 'Age=%{x:.4f} Gyr<br>M₂=%{y:.4f} M☉<extra></extra>',
    },
    {
      x: ages, y: period,
      mode: 'lines', type: 'scatter',
      name: 'Period',
      line: { color: '#88ff88', width: 1.5, dash: 'dot' },
      yaxis: 'y2',
      hovertemplate: 'Age=%{x:.4f} Gyr<br>P=%{y:.3f} d<extra></extra>',
    },
  ], [ages, m1, m2, period])

  return (
    <div className="chart-panel">
      <Plot
        data={traces}
        layout={layout}
        config={{ displayModeBar: false, responsive: true }}
        style={{ width: '100%', height: '100%' }}
        useResizeHandler
      />
    </div>
  )
}
