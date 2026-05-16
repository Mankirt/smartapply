import { useState, useEffect } from 'react'
import { getHistory, getAnalysis } from '../api'

function HistoryPanel({ resumeId, resumeFilename, onSelect }) {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [loadingId, setLoadingId] = useState(null)

  useEffect(() => {
    const fetch = async () => {
      try {
        const data = await getHistory(resumeId)
        setHistory(data)
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    fetch()
  }, [resumeId])

  const handleSelect = async (item) => {
    setLoadingId(item.id)
    try {
      const full = await getAnalysis(item.id)
      onSelect(full)
    } catch (err) {
      console.error(err)
    } finally {
      setLoadingId(null)
    }
  }

  if (loading || history.length < 2) return null

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5">
      <p className="text-emerald-600 text-xs uppercase tracking-widest font-medium mb-4">
        Past analyses
      </p>
      <div className="flex flex-col gap-2">
        {history.map(item => (
          <div
            key={item.id}
            onClick={() => handleSelect(item)}
            className="flex items-center justify-between bg-gray-50 hover:bg-emerald-50 border border-gray-200 hover:border-emerald-200 rounded-lg px-4 py-3 cursor-pointer transition-colors"
          >
            <div className="flex-1 mr-4">
              {/* company + role */}
              <p className="text-gray-800 text-sm font-medium">
                {item.company_name || 'Unknown company'}
                {item.role && (
                  <span className="text-gray-500 font-normal"> · {item.role}</span>
                )}
              </p>
              {/* filename + date */}
              <p className="text-gray-400 text-xs mt-0.5">
                {resumeFilename} · {new Date(item.created_at).toLocaleDateString('en-US', {
                  month: 'short', day: 'numeric',
                  hour: '2-digit', minute: '2-digit'
                })}
              </p>
            </div>
            <div className="flex items-center gap-2">
              {loadingId === item.id && (
                <svg className="animate-spin h-3 w-3 text-emerald-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
              )}
              <span className={`text-xl font-medium ${
                item.fit_score >= 70 ? 'text-emerald-600' :
                item.fit_score >= 50 ? 'text-amber-500' : 'text-red-500'
              }`}>
                {item.fit_score}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default HistoryPanel