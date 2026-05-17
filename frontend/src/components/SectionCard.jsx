import { useState } from 'react'
import { updateSectionReview } from '../api'

function BulletSuggestion({ suggestion, analysisId }) {
  const [status, setStatus] = useState(suggestion.status || 'pending')
  const [editing, setEditing] = useState(false)
  const [editedText, setEditedText] = useState(suggestion.edited_content || suggestion.improved)
  const [saving, setSaving] = useState(false)

  const save = async (s, content = null) => {
    setSaving(true)
    try {
      await updateSectionReview(analysisId, suggestion.id, s, content)
      setStatus(s)
      if (s === 'edited') setEditing(false)
    } catch (err) {
      console.error(err)
    } finally {
      setSaving(false)
    }
  }

  const cardClass = status === 'accepted'
    ? 'border-emerald-200 bg-emerald-50'
    : status === 'ignored'
    ? 'border-gray-100 bg-gray-50 opacity-50'
    : status === 'edited'
    ? 'border-blue-200 bg-blue-50'
    : 'border-gray-200 bg-gray-50'

  return (
    <div className={`border rounded-xl p-4 transition-all ${cardClass}`}>
      <p className="text-gray-400 text-xs uppercase tracking-widest mb-1">Original</p>
      <p className="text-gray-400 text-sm line-through mb-3">{suggestion.original}</p>

      <p className="text-gray-400 text-xs uppercase tracking-widest mb-1">Suggested</p>
      {editing ? (
        <textarea
          value={editedText}
          onChange={(e) => setEditedText(e.target.value)}
          className="w-full bg-white border border-blue-300 rounded-lg p-2 text-sm text-gray-700 resize-none focus:outline-none focus:border-blue-400 mb-3"
          rows={3}
        />
      ) : (
        <p className="text-gray-800 text-sm leading-relaxed mb-2">
          {status === 'edited' ? editedText : suggestion.improved}
        </p>
      )}

      <p className="text-gray-400 text-xs italic mb-4">{suggestion.reason}</p>

      {status === 'pending' && (
        <div className="flex gap-2">
          <button
            onClick={() => save('accepted')}
            disabled={saving}
            className="bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-medium px-3 py-1.5 rounded-lg transition-colors"
          >
            Accept
          </button>
          <button
            onClick={() => editing ? save('edited', editedText) : setEditing(true)}
            className="bg-white hover:bg-blue-50 border border-blue-200 text-blue-600 text-xs px-3 py-1.5 rounded-lg transition-colors"
          >
            {editing ? 'Save' : 'Edit'}
          </button>
          <button
            onClick={() => save('ignored')}
            disabled={saving}
            className="bg-white hover:bg-gray-100 border border-gray-200 text-gray-400 text-xs px-3 py-1.5 rounded-lg transition-colors"
          >
            Ignore
          </button>
        </div>
      )}

      {status !== 'pending' && (
        <div className="flex items-center justify-between">
          <span className={`text-xs font-medium ${
            status === 'accepted' ? 'text-emerald-600' :
            status === 'edited' ? 'text-blue-500' :
            'text-gray-400'
          }`}>
            {status === 'accepted' ? '✓ Accepted' :
             status === 'edited' ? '✎ Edited' : '✗ Ignored'}
          </span>
          <button
            onClick={() => setStatus('pending')}
            className="text-gray-400 hover:text-gray-600 text-xs transition-colors"
          >
            Undo
          </button>
        </div>
      )}
    </div>
  )
}

function SectionCard({ section, analysisId }) {
  const [expanded, setExpanded] = useState(true)
  const pct = Math.round(section.similarity_score * 100)
  const matchColor = pct >= 60 ? 'text-emerald-600' : pct >= 30 ? 'text-amber-500' : 'text-red-500'

  return (
    <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
      <div
        onClick={() => setExpanded(!expanded)}
        className="flex items-center justify-between px-5 py-4 cursor-pointer hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className="text-gray-800 font-medium text-sm">{section.section_title}</span>
          {section.suggestions.length > 0 && (
            <span className="bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs px-2 py-0.5 rounded-full">
              {section.suggestions.length} suggestion{section.suggestions.length > 1 ? 's' : ''}
            </span>
          )}
          <span className={`text-xs ${matchColor}`}>{pct}% match</span>
        </div>
        <span className="text-gray-400 text-xs">{expanded ? '▲' : '▼'}</span>
      </div>

      {expanded && (
        <div className="px-5 pb-5 border-t border-gray-100">
          <div className="mt-3 flex flex-col gap-3">
            {section.suggestions.length === 0 ? (
              <p className="text-gray-400 text-sm italic">No suggestions for this section</p>
            ) : (
              section.suggestions.map((s, i) => (
                <BulletSuggestion
                  key={s.id || i}
                  suggestion={s}
                  analysisId={analysisId}
                />
              ))
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default SectionCard