import { useState } from 'react'
import ResumeUpload from './components/ResumeUpload'
import JDInput from './components/JDInput'
import FitScore from './components/FitScore'
import GapAnalysis from './components/GapAnalysis'
import SectionCard from './components/SectionCard'
import HistoryPanel from './components/HistoryPanel'

function App() {
  // step 1 — resume uploaded
  const [resume, setResume] = useState(null)

  // step 2 — analysis complete
  const [analysis, setAnalysis] = useState(null)

  // loading and error states
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState(null)

  const handleAnalysisComplete = (result) => {
    setAnalysis(result)
    setError(null)
  }

  const handleError = (message) => {
    setError(message)
    setAnalyzing(false)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">SmartApply</h1>
            <p className="text-sm text-gray-500">AI-powered resume fit analyzer</p>
          </div>
          {resume && (
            <span className="text-sm text-green-600 font-medium">
              ✓ {resume.filename}
            </span>
          )}
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Step 1 + 2 — Upload and Analyze */}
        {!analysis && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <ResumeUpload
              onUpload={setResume}
              onError={handleError}
            />
            <JDInput
              resume={resume}
              onAnalyzing={setAnalyzing}
              onComplete={handleAnalysisComplete}
              onError={handleError}
              analyzing={analyzing}
            />
          </div>
        )}

        {/* Step 3 — Results */}
        {analysis && (
          <div className="space-y-6">
            {/* back button */}
            <button
              onClick={() => setAnalysis(null)}
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              ← New analysis
            </button>

            {/* fit score + gap analysis side by side */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <FitScore score={analysis.fit_score} summary={analysis.summary} />
              <GapAnalysis
                matchingSkills={analysis.matching_skills}
                missingKeywords={analysis.missing_keywords}
              />
            </div>

            {/* section cards */}
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-gray-900">
                Section Suggestions
              </h2>
              {analysis.sections.map((section) => (
                <SectionCard
                  key={section.section_type}
                  section={section}
                  analysisId={analysis.id}
                />
              ))}
            </div>

            {/* history panel */}
            <HistoryPanel resumeId={analysis.resume_id} />
          </div>
        )}
      </main>
    </div>
  )
}

export default App