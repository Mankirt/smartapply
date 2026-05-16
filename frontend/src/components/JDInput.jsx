import { useState } from 'react'
import { analyzeResume } from '../api'

function Spinner() {
  return (
    <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
  )
}

function JDInput({ resume, analyzing, onAnalyzing, onComplete, onError }) {
  const [jdText, setJdText] = useState('')
  const [companyName, setCompanyName] = useState('')
  const [role, setRole] = useState('')

  const isReady = resume && jdText.trim().length >= 50 && companyName.trim().length > 0

  const handleAnalyze = async () => {
    if (!resume) { onError('Please upload a resume first'); return }
    if (!companyName.trim()) { onError('Please enter a company name'); return }
    if (jdText.trim().length < 50) { onError('Job description is too short'); return }
    onAnalyzing(true)
    try {
      const result = await analyzeResume(resume.id, jdText, companyName.trim(), role.trim() || null)
      onComplete(result)
    } catch (err) {
      onError(err.response?.data?.detail || 'Analysis failed')
    } finally {
      onAnalyzing(false)
    }
  }

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5 flex flex-col gap-3">
      <p className="text-emerald-600 text-xs uppercase tracking-widest font-medium">
        Job description
      </p>

      {/* company name — required */}
      <div>
        <label className="text-gray-500 text-xs mb-1 block">
          Company name <span className="text-red-400">*</span>
        </label>
        <input
          type="text"
          value={companyName}
          onChange={(e) => setCompanyName(e.target.value)}
          placeholder="e.g. Workday, Google, Stripe"
          className="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-700 placeholder-gray-400 focus:outline-none focus:border-emerald-400 transition-colors"
        />
      </div>

      {/* role — optional */}
      <div>
        <label className="text-gray-500 text-xs mb-1 block">
          Role <span className="text-gray-400">(optional)</span>
        </label>
        <input
          type="text"
          value={role}
          onChange={(e) => setRole(e.target.value)}
          placeholder="e.g. Software Engineer II"
          className="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-700 placeholder-gray-400 focus:outline-none focus:border-emerald-400 transition-colors"
        />
      </div>

      {/* JD textarea */}
      <div className="flex flex-col flex-1">
        <label className="text-gray-500 text-xs mb-1 block">
          Job description <span className="text-red-400">*</span>
        </label>
        <textarea
          value={jdText}
          onChange={(e) => setJdText(e.target.value)}
          placeholder="Paste the full job description here..."
          className="flex-1 min-h-32 bg-gray-50 border border-gray-200 rounded-lg p-3 text-sm text-gray-700 placeholder-gray-400 resize-none focus:outline-none focus:border-emerald-400 transition-colors"
        />
      </div>

      <div className="flex items-center justify-between">
        <span className="text-gray-400 text-xs">
          {jdText.length} chars
          {jdText.length < 50 && jdText.length > 0 && (
            <span className="text-red-400 ml-1">(too short)</span>
          )}
        </span>
        <button
          onClick={handleAnalyze}
          disabled={analyzing || !isReady}
          className="bg-emerald-700 hover:bg-emerald-800 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-medium px-5 py-2 rounded-lg transition-colors flex items-center gap-2"
        >
          {analyzing ? (
            <><Spinner /> Analyzing...</>
          ) : (
            'Analyze fit →'
          )}
        </button>
      </div>

      {!resume && (
        <p className="text-amber-500 text-xs">⚠ Upload a resume first</p>
      )}
    </div>
  )
}

export default JDInput