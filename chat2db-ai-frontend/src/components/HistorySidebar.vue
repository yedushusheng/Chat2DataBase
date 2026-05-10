<template>
  <div class="history-sidebar">
    <div class="header">
      <h4>💬 历史会话</h4>
      <el-button link :icon="Plus" @click="newChat">新建</el-button>
    </div>
    <div class="session-list">
      <div
        v-for="session in sessions"
        :key="session.id"
        :class="['session-item', { active: currentId === session.id }]"
        @click="switchSession(session.id)"
      >
        <el-icon><ChatDotRound /></el-icon>
        <span class="title">{{ session.title }}</span>
        <span class="time">{{ formatDate(session.time) }}</span>
      </div>
      <el-empty v-if="!sessions.length" description="暂无历史会话" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Plus, ChatDotRound } from '@element-plus/icons-vue'
import { useChatStore } from '../stores/chat.js'

const store = useChatStore()
const currentId = ref(null)
const sessions = ref([])

function newChat() {
  store.clearMessages()
  currentId.value = null
}

function switchSession(id) {
  currentId.value = id
}

function formatDate(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  return `${d.getMonth() + 1}/${d.getDate()}`
}
</script>

<style scoped>
.history-sidebar {
  width: 260px;
  border-right: 1px solid #e5e7eb;
  background: #f9fafb;
  display: flex;
  flex-direction: column;
  height: 100%;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
}
.header h4 {
  margin: 0;
  font-size: 14px;
  color: #374151;
}
.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}
.session-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 4px;
  font-size: 13px;
  color: #4b5563;
}
.session-item:hover, .session-item.active {
  background: #e5e7eb;
  color: #111827;
}
.session-item .title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.session-item .time {
  font-size: 11px;
  color: #9ca3af;
}
</style>
