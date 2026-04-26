const apiBase = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

export function mediaUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `${apiBase}/${path}`
}
