import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000,
  headers: { 'Content-Type': 'application/json' }
})

api.interceptors.response.use(
  (res) => {
    if (res.data && res.data.code !== 0) {
      return Promise.reject(new Error(res.data.message || '请求失败'))
    }
    return res.data
  },
  (err) => Promise.reject(err)
)

export default {
  chat(data) {
    return api.post('/chat', data)
  },

  chatStream(data, onMessage, onError, onDone) {
    const payload = JSON.stringify(data)
    return fetch('/api/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: payload
    }).then(async (response) => {
      if (!response.ok) {
        const text = await response.text().catch(() => '请求失败')
        throw new Error(text)
      }
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) {
          onDone && onDone()
          break
        }
        buffer += decoder.decode(value, { stream: true })
        const events = buffer.split('\n\n')
        buffer = events.pop() || ''

        for (const event of events) {
          const dataLines = event.split('\n').filter(l => l.startsWith('data: '))
          const chunk = dataLines.map(l => l.slice(6)).join('\n')
          if (chunk === '[DONE]') {
            onDone && onDone()
            return
          }
          if (chunk.startsWith('[ERROR]')) {
            onError && onError(new Error(chunk))
            return
          }
          onMessage && onMessage(chunk)
        }
      }
    }).catch((err) => onError && onError(err))
  },

  upload(formData) {
    return api.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  uploadBatch(formData) {
    return api.post('/upload/batch', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  listUploads() {
    return api.get('/upload/list')
  },

  deleteUpload(filename) {
    return api.delete(`/upload/${encodeURIComponent(filename)}`)
  },

  hotFaq(dbType, limit = 10) {
    return api.get('/faq/hot', { params: { db_type: dbType, limit } })
  },

  searchFaq(q, dbType, limit = 10) {
    return api.get('/faq/search', { params: { q, db_type: dbType, limit } })
  },

  listDatabases() {
    return api.get('/databases')
  },

  systemStats() {
    return api.get('/health/stats')
  }
}