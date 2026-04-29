import api from '../api'

export function mediaUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  const base = api.defaults.baseURL?.replace(/\/$/, '') || 'http://127.0.0.1:8000'
  return `${base}/${path}`
}
