function GapAnalysis({ matchingSkills, missingKeywords }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        Gap Analysis
      </h2>

      {/* matching skills */}
      <div className="mb-4">
        <h3 className="text-sm font-medium text-gray-700 mb-2">
          ✓ Matching Skills
        </h3>
        <div className="flex flex-wrap gap-2">
          {matchingSkills.map((skill) => (
            <span
              key={skill}
              className="px-2 py-1 bg-green-50 text-green-700 text-xs rounded-full border border-green-200"
            >
              {skill}
            </span>
          ))}
        </div>
      </div>

      {/* missing keywords */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-2">
          ✗ Missing Keywords
        </h3>
        <div className="flex flex-wrap gap-2">
          {missingKeywords.map((keyword) => (
            <span
              key={keyword}
              className="px-2 py-1 bg-red-50 text-red-700 text-xs rounded-full border border-red-200"
            >
              {keyword}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}

export default GapAnalysis