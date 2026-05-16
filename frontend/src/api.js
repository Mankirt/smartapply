import axios from 'axios'

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
})

// ── Resume ──

export const uploadResume = async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/api/resume/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
}

export const getResume = async (resumeId) => {
    const response = await api.get(`/api/resume/${resumeId}`)
    return response.data
}

// ── Analysis ──

export const analyzeResume = async (resumeId, jdText, companyName, role = null) => {
  const response = await api.post('/api/analyze/', {
    resume_id: resumeId,
    jd_text: jdText,
    company_name: companyName,
    role: role,
  })
  return response.data
}

// ── History ──

export const getHistory = async (resumeId = null) => {
    const params = resumeId ? { resume_id: resumeId } : {}
    const response = await api.get('/api/history', { params })
    return response.data
}

export const updateSectionReview = async (analysisId, sectionType, status, editedContent = null) => {
    const response = await api.patch(`/api/history/${analysisId}/review`, {
        section_type: sectionType,
        status,
        edited_content: editedContent,
    })
    return response.data
}

export const deleteAnalysis = async (analysisId) => {
    const response = await api.delete(`/api/history/${analysisId}`)
    return response.data
}

export const getAnalysis = async (analysisId) => {
  const response = await api.get(`/api/history/${analysisId}`)
  return response.data
}