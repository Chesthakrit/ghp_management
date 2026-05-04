/**
 * Helper functions for Time and Attendance calculations
 */

export const polarXY = (cx, cy, r, angleDeg) => {
  const rad = (angleDeg * Math.PI) / 180
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) }
}

export const timeToAngleDeg = (timeStr) => {
  if (!timeStr || !timeStr.includes(':')) return null
  const [h, m] = timeStr.split(':').map(Number)
  if (isNaN(h) || isNaN(m)) return null
  return ((h * 60 + m) / 1440) * 360 - 90
}

export const makeArcD = (startDeg, endDeg, cx, cy, r) => {
  let sweep = (endDeg - startDeg + 360) % 360
  if (sweep === 0) return ''
  const largeArc = sweep > 180 ? 1 : 0
  const s = polarXY(cx, cy, r, startDeg)
  const e = polarXY(cx, cy, r, endDeg)
  return `M ${s.x.toFixed(3)} ${s.y.toFixed(3)} A ${r} ${r} 0 ${largeArc} 1 ${e.x.toFixed(3)} ${e.y.toFixed(3)}`
}

export const calcHours = (s, e) => {
  if (!s || !e) return '0.0'
  const toMin = t => {
    const [h, m] = t.split(':').map(Number)
    return h * 60 + m
  }
  let diff = toMin(e) - toMin(s)
  if (diff <= 0) diff += 1440
  return (diff / 60).toFixed(1)
}

/**
 * Validates 24H time string format (HH:mm)
 */
export const isValidTimeFormat = (timeStr) => {
  const regex = /^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/
  return regex.test(timeStr)
}
