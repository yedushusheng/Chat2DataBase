import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useChatStore = defineStore('chat', () => {
  const currentDb = ref('mysql')
  const messages = ref([])
  const historySessions = ref([])
  const isStreaming = ref(false)

  function setDb(db) {
    currentDb.value = db
  }

  function addMessage(role, content, extra = {}) {
    messages.value.push({ role, content, ...extra, timestamp: Date.now() })
  }

  function clearMessages() {
    messages.value = []
  }

  function appendStreaming(content) {
    const last = messages.value[messages.value.length - 1]
    if (last && last.role === 'assistant' && last.streaming) {
      last.content += content
    } else {
      addMessage('assistant', content, { streaming: true })
    }
  }

  function finishStreaming() {
    const last = messages.value[messages.value.length - 1]
    if (last && last.streaming) {
      last.streaming = false
    }
  }

  return {
    currentDb,
    messages,
    historySessions,
    isStreaming,
    setDb,
    addMessage,
    clearMessages,
    appendStreaming,
    finishStreaming,
  }
})