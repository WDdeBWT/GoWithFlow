const API_BASE = import.meta.env.VITE_API_BASE || 'http://47.89.243.26:8088'

export async function recommend(text, lat, lon) {
  const res = await fetch(`${API_BASE}/recommend?lat=${lat}&lon=${lon}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  })
  return res.json()
}

export async function sendFeedback(text, type, lat, lon) {
  const res = await fetch(`${API_BASE}/feedback?feedback_type=${encodeURIComponent(type)}&lat=${lat}&lon=${lon}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  })
  return res.json()
}
