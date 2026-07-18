import { useState, useEffect } from 'react'
import { recommend, sendFeedback } from './api'

const EXAMPLES = [
  '开车去山里，凉快，喝咖啡写代码，顺便爬两步山',
  '想找个安静的地方看书，最好有电源，车程别超过1小时',
  '带狗去户外，有水有树荫，不要太远',
]

const DEFAULT_CENTER = { lat: 39.9042, lon: 116.4074 }

function App() {
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [location, setLocation] = useState(DEFAULT_CENTER)

  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => setLocation({ lat: pos.coords.latitude, lon: pos.coords.longitude }),
        () => {}
      )
    }
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!text.trim()) return
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const data = await recommend(text, location.lat, location.lon)
      setResult(data)
    } catch (err) {
      setError('请求失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  const handleFeedback = async (type) => {
    if (!result) return
    setLoading(true)
    try {
      const data = await sendFeedback(text, type, location.lat, location.lon)
      setResult(data)
    } catch (err) {
      setError('反馈替换失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 text-gray-800">
      <div className="max-w-2xl mx-auto px-4 py-12">
        <h1 className="text-3xl font-bold mb-2">GoWithFlow</h1>
        <p className="text-gray-500 mb-8">描述你想去的周末氛围，我们推荐 3 个地方。</p>

        <form onSubmit={handleSubmit} className="bg-white p-6 rounded-xl shadow-sm mb-8">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="比如：开车去山里，凉快，喝咖啡写代码，顺便爬两步山"
            className="w-full h-24 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          />
          <div className="flex gap-2 mt-4 flex-wrap">
            {EXAMPLES.map((ex) => (
              <button
                key={ex}
                type="button"
                onClick={() => setText(ex)}
                className="text-sm px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-600"
              >
                {ex}
              </button>
            ))}
          </div>
          <button
            type="submit"
            disabled={loading}
            className="mt-4 w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? '推荐中...' : '开始推荐'}
          </button>
        </form>

        {error && <p className="text-red-500 mb-4">{error}</p>}

        {result?.follow_up && (
          <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg mb-6">
            <p className="font-medium text-yellow-800">{result.follow_up}</p>
          </div>
        )}

        {result?.recommendations?.length > 0 && (
          <div className="space-y-6">
            {result.recommendations.map((r) => (
              <div key={r.id} className="bg-white p-6 rounded-xl shadow-sm">
                <div className="flex justify-between items-start">
                  <div>
                    <h2 className="text-xl font-semibold">{r.name}</h2>
                    <p className="text-sm text-gray-500">{r.type} · {r.district} · 预计车程 {r.drive_time}</p>
                  </div>
                  <span className="text-sm bg-blue-50 text-blue-700 px-2 py-1 rounded">
                    {r.lat.toFixed(4)}, {r.lon.toFixed(4)}
                  </span>
                </div>
                <div className="flex gap-2 flex-wrap mt-3">
                  {r.tags.map((tag) => (
                    <span key={tag} className="text-xs px-2 py-1 bg-gray-100 rounded text-gray-600">{tag}</span>
                  ))}
                </div>
                <ul className="mt-4 space-y-2">
                  {r.reasons.map((reason, i) => (
                    <li key={i} className="text-sm text-gray-700">• {reason}</li>
                  ))}
                </ul>
              </div>
            ))}

            <div className="bg-white p-4 rounded-xl shadow-sm">
              <p className="text-sm text-gray-600 mb-3">哪里不对？</p>
              <div className="flex gap-2 flex-wrap">
                {['太远了', '太热了', '太吵了', '太网红'].map((type) => (
                  <button
                    key={type}
                    onClick={() => handleFeedback(type)}
                    disabled={loading}
                    className="text-sm px-3 py-1 border rounded-full hover:bg-gray-50 disabled:opacity-50"
                  >
                    {type}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
