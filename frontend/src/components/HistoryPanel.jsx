import { useState, useEffect } from 'react'
import { getHistory } from '../api'

function HistoryPanel({ resumeId }) {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const data = await getHistory(resumeId)
        setHistory(data)
      } catch (err) {
        console.error('Failed to fetch history', err)
      } finally {
        setLoading(false)
      }
    }
    fetchHistory()
  }, [resumeId])

  const getScoreColor = (score) => {
    if (score >= 70) return 'text-green-600'
    if (score >= 50) return 'text-amber-500'
    return 'text-red-500'
  }

  if (loading) return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <p className="text-sm text-gray-400">Loading history...</p>
    </div>
  )

  if (history.length === 0) return null

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        Past Analyses
      </h2>

      <div className="space-y-3">
        {history.map((item) => (
          <div
            key={item.id}
            className="flex items-start justify-between p-3 rounded-lg border border-gray-100 hover:bg-gray-50 transition-colors"
          >
            <div className="flex-1 mr-4">
              <p className="text-sm text-gray-600 line-clamp-2">
                {item.summary}
              </p>
              <p className="text-xs text-gray-400 mt-1">
                {new Date(item.created_at).toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </p>
            </div>
            <span className={`text-2xl font-bold flex-shrink-0 ${getScoreColor(item.fit_score)}`}>
              {item.fit_score}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default HistoryPanel