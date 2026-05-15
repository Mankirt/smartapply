import { useState } from 'react'
import { updateSectionReview } from '../api'

function BulletSuggestion({ suggestion, analysisId, sectionType }) {
  const [status, setStatus] = useState('pending')
  const [editing, setEditing] = useState(false)
  const [editedText, setEditedText] = useState(suggestion.improved)
  const [saving, setSaving] = useState(false)

  const handleAccept = async () => {
    setSaving(true)
    try {
      await updateSectionReview(analysisId, sectionType, 'accepted')
      setStatus('accepted')
    } catch (err) {
      console.error('Failed to save review', err)
    } finally {
      setSaving(false)
    }
  }

  const handleIgnore = async () => {
    setSaving(true)
    try {
      await updateSectionReview(analysisId, sectionType, 'ignored')
      setStatus('ignored')
    } catch (err) {
      console.error('Failed to save review', err)
    } finally {
      setSaving(false)
    }
  }

  const handleSaveEdit = async () => {
    setSaving(true)
    try {
      await updateSectionReview(analysisId, sectionType, 'edited', editedText)
      setStatus('edited')
      setEditing(false)
    } catch (err) {
      console.error('Failed to save review', err)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className={`rounded-lg border p-4 transition-all ${
      status === 'accepted' ? 'border-green-200 bg-green-50' :
      status === 'ignored'  ? 'border-gray-100 bg-gray-50 opacity-50' :
      status === 'edited'   ? 'border-blue-200 bg-blue-50' :
      'border-gray-200 bg-white'
    }`}>

      {/* original bullet */}
      <div className="mb-3">
        <span className="text-xs font-medium text-gray-400 uppercase tracking-wide">
          Original
        </span>
        <p className="text-sm text-gray-600 mt-1 line-through">
          {suggestion.original}
        </p>
      </div>

      {/* improved bullet */}
      <div className="mb-3">
        <span className="text-xs font-medium text-gray-400 uppercase tracking-wide">
          Suggested
        </span>
        {editing ? (
          <textarea
            value={editedText}
            onChange={(e) => setEditedText(e.target.value)}
            className="w-full mt-1 p-2 text-sm border border-blue-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            rows={3}
          />
        ) : (
          <p className="text-sm text-gray-900 mt-1 font-medium">
            {status === 'edited' ? editedText : suggestion.improved}
          </p>
        )}
      </div>

      {/* reason */}
      <p className="text-xs text-gray-400 italic mb-3">
        {suggestion.reason}
      </p>

      {/* action buttons */}
      {status === 'pending' && (
        <div className="flex gap-2">
          <button
            onClick={handleAccept}
            disabled={saving}
            className="px-3 py-1.5 bg-green-600 text-white text-xs font-medium rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
          >
            Accept
          </button>
          <button
            onClick={() => setEditing(!editing)}
            className="px-3 py-1.5 bg-blue-600 text-white text-xs font-medium rounded-lg hover:bg-blue-700 transition-colors"
          >
            Edit
          </button>
          {editing && (
            <button
              onClick={handleSaveEdit}
              disabled={saving}
              className="px-3 py-1.5 bg-blue-800 text-white text-xs font-medium rounded-lg hover:bg-blue-900 disabled:opacity-50 transition-colors"
            >
              Save
            </button>
          )}
          <button
            onClick={handleIgnore}
            disabled={saving}
            className="px-3 py-1.5 bg-gray-100 text-gray-600 text-xs font-medium rounded-lg hover:bg-gray-200 disabled:opacity-50 transition-colors"
          >
            Ignore
          </button>
        </div>
      )}

      {/* status badge */}
      {status !== 'pending' && (
        <div className="flex items-center justify-between">
          <span className={`text-xs font-medium ${
            status === 'accepted' ? 'text-green-600' :
            status === 'edited'   ? 'text-blue-600' :
            'text-gray-400'
          }`}>
            {status === 'accepted' ? '✓ Accepted' :
             status === 'edited'   ? '✎ Edited' :
             '✗ Ignored'}
          </span>
          <button
            onClick={() => setStatus('pending')}
            className="text-xs text-gray-400 hover:text-gray-600"
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

  const similarityPercent = Math.round(section.similarity_score * 100)

  const getSimilarityColor = (score) => {
    if (score >= 60) return 'text-green-600'
    if (score >= 30) return 'text-amber-500'
    return 'text-red-500'
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200">
      {/* section header */}
      <div
        className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50 rounded-xl"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-3">
          <h3 className="font-medium text-gray-900 capitalize">
            {section.section_title}
          </h3>
          <span className={`text-xs font-medium ${getSimilarityColor(similarityPercent)}`}>
            {similarityPercent}% match
          </span>
        </div>
        <div className="flex items-center gap-2">
          {section.suggestions.length > 0 && (
            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">
              {section.suggestions.length} suggestion{section.suggestions.length > 1 ? 's' : ''}
            </span>
          )}
          <span className="text-gray-400 text-sm">
            {expanded ? '▲' : '▼'}
          </span>
        </div>
      </div>

      {/* suggestions list */}
      {expanded && (
        <div className="px-4 pb-4 space-y-3">
          {section.suggestions.length === 0 ? (
            <p className="text-sm text-gray-400 italic">
              No suggestions for this section
            </p>
          ) : (
            section.suggestions.map((suggestion, index) => (
              <BulletSuggestion
                key={index}
                suggestion={suggestion}
                analysisId={analysisId}
                sectionType={section.section_type}
              />
            ))
          )}
        </div>
      )}
    </div>
  )
}

export default SectionCard