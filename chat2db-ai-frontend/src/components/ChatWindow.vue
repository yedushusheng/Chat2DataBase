<template>
  <div class="chat-window">
    <div class="messages" ref="messagesRef">
      <div v-if="!store.messages.length" class="welcome">
        <h2>Chat2DB-AI 智能数据库助手</h2>
        <p>选择数据库类型，输入您的问题，获取专业排查思路和解决方案</p>
        <div class="quick-actions">
          <el-button
            v-for="q in quickQuestions"
            :key="q"
            size="small"
            @click="sendQuick(q)"
          >
            {{ q }}
          </el-button>
        </div>
      </div>
      <MessageBubble
        v-for="(msg, idx) in store.messages"
        :key="idx"
        :message="msg"
      />
      <div v-if="store.isStreaming" class="typing-indicator">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>AI 正在思考...</span>
      </div>
    </div>

    <div class="input-area">
      <el-input
        v-model="inputText"
        type="textarea"
        :rows="2"
        placeholder="输入数据库问题，例如：MySQL连接数打满如何排查？"
        @keydown.enter.prevent="handleEnter"
      />
      <div class="input-actions">
        <el-switch
          v-model="useStream"
          active-text="流式输出"
          inline-prompt
        />
        <el-button
          type="primary"
          :icon="Promotion"
          :loading="store.isStreaming"
          @click="sendMessage"
        >
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'
import { Promotion, Loading } from '@element-plus/icons-vue'
import { useChatStore } from '../stores/chat.js'
import api from '../api'
import MessageBubble from './MessageBubble.vue'

const store = useChatStore()
const inputText = ref('')
const useStream = ref(true)
const messagesRef = ref(null)

const quickQuestions = [
  'MySQL主从延迟怎么排查？',
  'CPU飙高如何定位？',
  '连接数满了怎么办？',
  '慢查询优化技巧',
]

watch(() => store.messages.length, () => {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
})

function handleEnter(e) {
  if (!e.shiftKey) {
    sendMessage()
  }
}

function sendQuick(q) {
  inputText.value = q
  sendMessage()
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || store.isStreaming) return

  store.addMessage('user', text)
  inputText.value = ''
  store.isStreaming = true

  const history = store.messages
    .filter(m => !m.streaming)
    .slice(-6)
    .map(m => ({ role: m.role, content: m.content }))

  if (useStream.value) {
    let fullContent = ''
    await api.chatStream(
      {
        db_type: store.currentDb,
        query: text,
        history,
      },
      (chunk) => {
        fullContent += chunk
        store.appendStreaming(chunk)
      },
      (err) => {
        store.finishStreaming()
        store.isStreaming = false
        ElMessage.error(err.message || '流式响应失败')
      },
      () => {
        store.finishStreaming()
        store.isStreaming = false
      }
    )
  } else {
    try {
      const res = await api.chat({
        db_type: store.currentDb,
        query: text,
        history,
      })
      const data = res.data
      store.addMessage('assistant', '', {
        structured: true,
        sections: data.sections || [],
        sources: data.sources || [],
        suggestion: data.suggestion || '',
        model_used: data.model_used || '',
        type: data.type || 'general',
      })
    } catch (err) {
      ElMessage.error(err.message || '请求失败')
    } finally {
      store.isStreaming = false
    }
  }
}
</script>

<style scoped>
.chat-window {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px 0;
  background: #ffffff;
}
.welcome {
  text-align: center;
  padding: 60px 20px;
  color: #4b5563;
}
.welcome h2 {
  font-size: 24px;
  margin-bottom: 12px;
  color: #111827;
}
.quick-actions {
  margin-top: 24px;
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
}
.input-area {
  padding: 16px 20px;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}
.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 20px;
  color: #6b7280;
  font-size: 13px;
}
</style>