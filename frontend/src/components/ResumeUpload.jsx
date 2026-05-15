import { useState, useRef } from 'react'
import { uploadResume } from '../api'

function ResumeUpload({ onUpload, onError }) {
  const [uploading, setUploading] = useState(false)
  const [uploaded, setUploaded] = useState(null)
  const inputRef = useRef(null)

  const handleFile = async (file) => {
    if (!file) return
    if (!file.name.endsWith('.pdf')) {
      onError('Only PDF files are supported')
      return
    }

    setUploading(true)
    try {
      const resume = await uploadResume(file)
      setUploaded(resume)
      onUpload(resume)
    } catch (err) {
      onError(err.response?.data?.detail || 'Failed to upload resume')
    } finally {
      setUploading(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    handleFile(file)
  }

  const handleDragOver = (e) => {
    e.preventDefault()
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        Upload Resume
      </h2>

      {!uploaded ? (
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onClick={() => inputRef.current.click()}
          className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-400 hover:bg-blue-50 transition-colors"
        >
          <div className="text-4xl mb-3">📄</div>
          {uploading ? (
            <p className="text-sm text-blue-600 font-medium">Uploading...</p>
          ) : (
            <>
              <p className="text-sm font-medium text-gray-700">
                Drop your PDF here
              </p>
              <p className="text-xs text-gray-400 mt-1">
                or click to browse
              </p>
            </>
          )}
          <input
            ref={inputRef}
            type="file"
            accept=".pdf"
            className="hidden"
            onChange={(e) => handleFile(e.target.files[0])}
          />
        </div>
      ) : (
        <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg border border-green-200">
          <div>
            <p className="text-sm font-medium text-green-800">
              ✓ {uploaded.filename}
            </p>
            <p className="text-xs text-green-600 mt-0.5">
              {uploaded.sections.length} sections parsed
            </p>
          </div>
          <button
            onClick={() => {
              setUploaded(null)
              onUpload(null)
            }}
            className="text-xs text-gray-400 hover:text-gray-600"
          >
            Change
          </button>
        </div>
      )}
    </div>
  )
}

export default ResumeUpload