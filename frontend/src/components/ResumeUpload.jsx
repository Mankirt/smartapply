import { useState, useRef } from 'react'
import { uploadResume } from '../api'

function ResumeUpload({ onUpload, onError, resume, analyzing }) {
  const [uploading, setUploading] = useState(false)
  const [uploaded, setUploaded] = useState(resume || null)
  const inputRef = useRef(null)

  const handleFile = async (file) => {
    if (!file) return
    if (!file.name.endsWith('.pdf')) { onError('Only PDF files are supported'); return }
    setUploading(true)
    try {
      const result = await uploadResume(file)
      setUploaded(result)
      onUpload(result)
    } catch (err) {
      onError(err.response?.data?.detail || 'Failed to upload resume')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5">
      <p className="text-emerald-600 text-xs uppercase tracking-widest font-medium mb-4">
        Upload resume
      </p>

      {!uploaded ? (
        <div
          onDrop={(e) => { e.preventDefault(); handleFile(e.dataTransfer.files[0]) }}
          onDragOver={(e) => e.preventDefault()}
          onClick={() => inputRef.current.click()}
          className="border-2 border-dashed border-emerald-200 hover:border-emerald-400 hover:bg-emerald-50 rounded-xl p-8 text-center cursor-pointer transition-colors"
        >
          <div className="text-3xl mb-3">📄</div>
          {uploading ? (
            <p className="text-emerald-600 text-sm">Uploading...</p>
          ) : (
            <>
              <p className="text-gray-600 text-sm">Drop your PDF here</p>
              <p className="text-gray-400 text-xs mt-1">or click to browse</p>
            </>
          )}
          <input ref={inputRef} type="file" accept=".pdf" className="hidden" onChange={(e) => handleFile(e.target.files[0])} />
        </div>
      ) : (
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 flex items-center justify-between">
          <div>
            <p className="text-emerald-800 text-sm font-medium">✓ {uploaded.filename}</p>
            <p className="text-emerald-600 text-xs mt-0.5">{uploaded.sections.length} sections parsed</p>
          </div>
          <button
            onClick={() => { setUploaded(null); onUpload(null) }}
            disabled={analyzing}
            className="text-gray-400 hover:text-gray-600 text-xs transition-colors"
          >
            Change
          </button>
        </div>
      )}
    </div>
  )
}

export default ResumeUpload