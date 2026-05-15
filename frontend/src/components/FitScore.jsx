function FitScore({ score, summary }) {
  const getScoreColor = (score) => {
    if (score >= 70) return 'text-green-600'
    if (score >= 50) return 'text-amber-500'
    return 'text-red-500'
  }

  const getScoreLabel = (score) => {
    if (score >= 70) return 'Strong Match'
    if (score >= 50) return 'Partial Match'
    return 'Weak Match'
  }

  const getRingColor = (score) => {
    if (score >= 70) return 'stroke-green-500'
    if (score >= 50) return 'stroke-amber-500'
    return 'stroke-red-500'
  }

  // SVG circle progress math
  const radius = 54
  const circumference = 2 * Math.PI * radius
  const progress = circumference - (score / 100) * circumference

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        Fit Score
      </h2>

      <div className="flex items-center gap-6">
        {/* circular progress ring */}
        <div className="relative flex-shrink-0">
          <svg width="120" height="120" className="-rotate-90">
            {/* background ring */}
            <circle
              cx="60" cy="60" r={radius}
              fill="none"
              stroke="#e5e7eb"
              strokeWidth="8"
            />
            {/* progress ring */}
            <circle
              cx="60" cy="60" r={radius}
              fill="none"
              strokeWidth="8"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={progress}
              className={`transition-all duration-700 ${getRingColor(score)}`}
            />
          </svg>
          {/* score number in center */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={`text-3xl font-bold ${getScoreColor(score)}`}>
              {score}
            </span>
            <span className="text-xs text-gray-400">/ 100</span>
          </div>
        </div>

        {/* label + summary */}
        <div className="flex-1">
          <span className={`text-sm font-semibold ${getScoreColor(score)}`}>
            {getScoreLabel(score)}
          </span>
          <p className="text-sm text-gray-600 mt-2 leading-relaxed">
            {summary}
          </p>
        </div>
      </div>
    </div>
  )
}

export default FitScore