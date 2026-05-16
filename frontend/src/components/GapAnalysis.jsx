function GapAnalysis({ matchingSkills, missingKeywords }) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5">
      <p className="text-emerald-600 text-xs uppercase tracking-widest font-medium mb-4">
        Gap analysis
      </p>

      <p className="text-gray-400 text-xs mb-2">Matching</p>
      <div className="flex flex-wrap gap-2 mb-4">
        {matchingSkills.map(skill => (
          <span key={skill} className="bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs px-2.5 py-1 rounded-full">
            {skill}
          </span>
        ))}
      </div>

      <p className="text-gray-400 text-xs mb-2">Missing</p>
      <div className="flex flex-wrap gap-2">
        {missingKeywords.map(keyword => (
          <span key={keyword} className="bg-red-50 border border-red-200 text-red-700 text-xs px-2.5 py-1 rounded-full">
            {keyword}
          </span>
        ))}
      </div>
    </div>
  )
}

export default GapAnalysis