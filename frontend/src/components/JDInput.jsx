import { useState } from 'react'
import { analyzeResume } from '../api'

function JDInput({ resume, analyzing, onAnalyzing, onComplete, onError }) {
  const [jdText, setJdText] = useState('')

  const handleAnalyze = async () => {
    if (!resume) {
      onError('Please upload a resume first')
      return
    }
    if (jdText.trim().length < 50) {
      onError('Job description is too short — paste the full JD')
      return
    }

    onAnalyzing(true)
    try {
      const result = await analyzeResume(resume.id, jdText)
      onComplete(result)
    } catch (err) {
      onError(err.response?.data?.detail || 'Analysis failed')
    } finally {
      onAnalyzing(false)
    }
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 flex flex-col">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        Job Description
      </h2>

      <textarea
        value={jdText}
        onChange={(e) => setJdText(e.target.value)}
        placeholder="Paste the full job description here..."
        className="flex-1 min-h-48 w-full border border-gray-200 rounded-lg p-3 text-sm text-gray-700 placeholder-gray-400 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
      />

      <div className="mt-4 flex items-center justify-between">
        <span className="text-xs text-gray-400">
          {jdText.length} characters
          {jdText.length < 50 && jdText.length > 0 && (
            <span className="text-red-400 ml-1">(too short)</span>
          )}
        </span>

        <button
          onClick={handleAnalyze}
          disabled={analyzing || !resume || jdText.trim().length < 50}
          className="px-5 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {analyzing ? 'Analyzing...' : 'Analyze Fit'}
        </button>
      </div>

      {!resume && (
        <p className="mt-3 text-xs text-amber-600">
          ⚠ Upload a resume first
        </p>
      )}
    </div>
  )
}

export default JDInput