function FitScore({ score, summary }) {
  const color = score >= 70 ? '#0f6e56' : score >= 50 ? '#d97706' : '#dc2626'
  const label = score >= 70 ? 'Strong match' : score >= 50 ? 'Partial match' : 'Weak match'
  const circumference = 2 * Math.PI * 28
  const offset = circumference - (score / 100) * circumference

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5">
      <p className="text-emerald-600 text-xs uppercase tracking-widest font-medium mb-4">
        Fit score
      </p>
      <div className="flex items-center gap-5">
        <div className="relative w-16 h-16 flex-shrink-0">
          <svg width="64" height="64" style={{ transform: 'rotate(-90deg)' }}>
            <circle cx="32" cy="32" r="28" fill="none" stroke="#d1fae5" strokeWidth="5" />
            <circle cx="32" cy="32" r="28" fill="none" stroke={color} strokeWidth="5"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              style={{ transition: 'stroke-dashoffset 0.7s ease' }}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-lg font-medium text-gray-800">{score}</span>
            <span className="text-xs text-gray-400">/100</span>
          </div>
        </div>
        <div>
          <p className="text-sm font-medium mb-1" style={{ color }}>{label}</p>
          <p className="text-gray-500 text-xs leading-relaxed">{summary}</p>
        </div>
      </div>
    </div>
  )
}

export default FitScore