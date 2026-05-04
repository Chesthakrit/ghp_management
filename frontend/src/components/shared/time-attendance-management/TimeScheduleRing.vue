<template>
  <div class="card ring-overview-card">
    <div class="card-header">
      <h3><i class="fas fa-dot-circle"></i> 24-Hour Schedule Overview</h3>
      <span class="status-badge live-badge">
        <i class="fas fa-circle" style="font-size:0.45rem;color:#22c55e;"></i> Live Preview
      </span>
    </div>
    <div class="ring-overview-body">
      <div class="ring-wrap">
        <svg viewBox="0 0 300 300" class="ring-svg" xmlns="http://www.w3.org/2000/svg">
          <circle cx="150" cy="150" r="100" fill="none" stroke="#f1f5f9" stroke-width="26"/>
          <path v-for="arc in ringArcs" :key="arc.id"
            :d="arc.d" fill="none" :stroke="arc.color" stroke-width="26" stroke-linecap="butt"/>
          <line v-for="(tick, i) in ringHourTicks" :key="'tick'+i"
            :x1="tick.x1.toFixed(2)" :y1="tick.y1.toFixed(2)"
            :x2="tick.x2.toFixed(2)" :y2="tick.y2.toFixed(2)"
            :stroke="tick.isMajor ? '#94a3b8' : '#cbd5e1'"
            :stroke-width="tick.isMajor ? 2 : 1"/>
          <text v-for="(lbl, i) in ringHourLabels" :key="'lbl'+i"
            :x="lbl.x.toFixed(2)" :y="lbl.y.toFixed(2)"
            :text-anchor="lbl.anchor"
            dominant-baseline="middle"
            class="ring-hour-label">{{ lbl.text }}</text>
          <text x="150" y="138" text-anchor="middle" dominant-baseline="middle" class="ring-center-title">TIMELINE</text>
          <text x="150" y="158" text-anchor="middle" dominant-baseline="middle" class="ring-center-hours">24H</text>
          <text x="150" y="176" text-anchor="middle" dominant-baseline="middle" class="ring-center-sub">OVERVIEW</text>
        </svg>
      </div>
      <div class="ring-legend-panel">
        <div class="legend-title">Time Block Summary</div>
        <div v-for="arc in ringArcs" :key="'leg-'+arc.id" class="legend-row">
          <div class="legend-dot" :style="{ background: arc.color }"></div>
          <div class="legend-info">
            <span class="legend-label">{{ arc.label }}</span>
            <span class="legend-time">{{ arc.start }} – {{ arc.end }}</span>
          </div>
          <span class="legend-hrs">{{ arc.hours }}h</span>
        </div>
        <div v-if="ringArcs.length === 0" class="legend-empty">
          <i class="fas fa-info-circle"></i> Configure times to preview schedule
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { polarXY, timeToAngleDeg, makeArcD, calcHours } from './attendance_helpers'

const props = defineProps({
  config: Object
})



const ringArcs = computed(() => {
  const cx = 150, cy = 150, r = 100
  const arcs = []
  const s = props.config.check_in_time, e = props.config.check_out_time
  const sa = timeToAngleDeg(s), ea = timeToAngleDeg(e)
  if (sa !== null && ea !== null && sa !== ea) {
    const d = makeArcD(sa, ea, cx, cy, r)
    if (d) arcs.push({ id: 'work', d, color: '#3b82f6', label: 'Work Hours', start: s, end: e, hours: calcHours(s, e) })
  }
  return arcs
})

const ringHourTicks = computed(() => {
  const cx = 150, cy = 150, r = 100, sw = 26
  const ticks = []
  for (let h = 0; h < 24; h++) {
    const deg = (h / 24) * 360 - 90
    const isMajor = h % 6 === 0
    const innerR = r + sw / 2 + 2
    const outerR = r + sw / 2 + (isMajor ? 10 : 5)
    const p1 = polarXY(cx, cy, innerR, deg)
    const p2 = polarXY(cx, cy, outerR, deg)
    ticks.push({ x1: p1.x, y1: p1.y, x2: p2.x, y2: p2.y, isMajor })
  }
  return ticks
})

const ringHourLabels = computed(() => {
  const cx = 150, cy = 150, r = 100, sw = 26
  const labelR = r + sw / 2 + 18
  return Array.from({ length: 24 }, (_, i) => i).map(h => {
    const deg = (h / 24) * 360 - 90
    const p = polarXY(cx, cy, labelR, deg)
    let anchor = 'middle'
    if (h > 0 && h < 12) anchor = 'start'
    else if (h > 12 && h < 24) anchor = 'end'
    return { x: p.x, y: p.y, text: h.toString().padStart(2, '0'), anchor }
  })
})
</script>

<style scoped>
.card { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; }
.card-header { padding: 16px 20px; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; background: #fafafa; }
.card-header h3 { margin: 0; font-size: 0.95rem; font-weight: 700; color: #1a2a3a; display: flex; align-items: center; gap: 8px; }
.status-badge { background: #f1f5f9; padding: 4px 10px; border-radius: 100px; font-size: 0.7rem; font-weight: 700; color: #1a2a3a; }
.live-badge { border: 1px solid #e2e8f0; }

.ring-overview-body { display: flex; align-items: center; justify-content: center; padding: 30px; gap: 40px; flex-wrap: wrap; }
.ring-wrap { position: relative; width: 260px; height: 260px; }
.ring-svg { width: 100%; height: 100%; transform: rotate(-0.01deg); }
.ring-hour-label { font-size: 8px; font-weight: 700; fill: #94a3b8; }
.ring-center-title { font-size: 8px; font-weight: 800; fill: #94a3b8; letter-spacing: 0.1em; }
.ring-center-hours { font-size: 24px; font-weight: 900; fill: #1a2a3a; }
.ring-center-sub { font-size: 8px; font-weight: 800; fill: #94a3b8; letter-spacing: 0.1em; }

.ring-legend-panel { flex: 1; min-width: 200px; max-width: 350px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; }
.legend-title { font-size: 0.75rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; margin-bottom: 16px; letter-spacing: 0.05em; }
.legend-row { display: flex; align-items: center; gap: 12px; padding: 12px; background: #fff; border-radius: 10px; border: 1px solid #f1f5f9; margin-bottom: 8px; }
.legend-dot { width: 10px; height: 10px; border-radius: 3px; flex-shrink: 0; }
.legend-info { flex: 1; display: flex; flex-direction: column; }
.legend-label { font-size: 0.8rem; font-weight: 700; color: #1a2a3a; }
.legend-time { font-size: 0.7rem; font-weight: 600; color: #64748b; }
.legend-hrs { font-size: 0.85rem; font-weight: 800; color: #1a2a3a; background: #f1f5f9; padding: 4px 8px; border-radius: 6px; }
.legend-empty { padding: 20px; text-align: center; color: #94a3b8; font-size: 0.75rem; font-style: italic; }
</style>
