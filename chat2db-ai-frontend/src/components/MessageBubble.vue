<template>
  <div :class="['message-bubble', message.role]">
    <div class="avatar">
      <el-avatar v-if="message.role === 'user'" :icon="UserFilled" :size="36" />
      <el-avatar v-else :icon="Cpu" :size="36" type="primary" />
    </div>
    <div class="content-wrapper">
      <div class="meta" v-if="message.role === 'assistant' && message.model_used">
        <span class="model-tag">{{ message.model_used }}</span>
        <span class="time">{{ formatTime(message.timestamp) }}</span>
      </div>
      <div class="content">
        <div v-if="message.structured && message.sections">
          <div v-for="(sec, idx) in message.sections" :key="idx" class="section">
            <h4 v-if="sec.title">{{ sec.title }}</h4>
            <div v-html="renderMarkdown(sec.content)"></div>
          </div>
          <div v-if="message.sources?.length" class="sources">
            <span class="source-label">来源:</span>
            <el-tag v-for="s in message.sources" :key="s" size="small" type="info">{{ s }}</el-tag>
          </div>
          <div v-if="message.suggestion" class="suggestion">
            <el-alert type="info" :closable="false" :title="message.suggestion" />
          </div>
        </div>
        <div v-else v-html="renderMarkdown(message.content)"></div>
      </div>
      <div v-if="message.role === 'assistant' && !message.streaming" class="actions">
        <el-button link size="small" @click="copyContent">
          <el-icon><DocumentCopy /></el-icon> 复制
        </el-button>
        <el-button link size="small" @click="exportMd">
          <el-icon><Download /></el-icon> 导出
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { UserFilled, Cpu, DocumentCopy, Download } from '@element-plus/icons-vue'
import { renderMarkdown, copyToClipboard } from '../utils/format.js'

const props = defineProps({ message: { type: Object, required: true } })

function formatTime(ts) {
  if (!ts) return ''
  return new Date(ts).toLocaleTimeString()
}

function copyContent() {
  const text = props.message.content || props.message.sections?.map(s => s.content).join('\n\n') || ''
  copyToClipboard(text)
  ElMessage.success('已复制到剪贴板')
}

function exportMd() {
  const text = props.message.content || props.message.sections?.map(s => `## ${s.title}\n${s.content}`).join('\n\n') || ''
  const blob = new Blob([text], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `chat2db-answer-${Date.now()}.md`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.message-bubble {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
  padding: 0 16px;
}
.message-bubble.user {
  flex-direction: row-reverse;
}
.message-bubble.user .content-wrapper {
  align-items: flex-end;
  background: #e6f7ff;
  border-radius: 12px 12px 0 12px;
}
.message-bubble.assistant .content-wrapper {
  background: #f6f8fa;
  border-radius: 12px 12px 12px 0;
  border: 1px solid #e5e7eb;
}
.content-wrapper {
  max-width: 80%;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
}
.meta {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 6px;
  font-size: 12px;
  color: #666;
}
.model-tag {
  background: #ecf5ff;
  color: #409eff;
  padding: 2px 6px;
  border-radius: 4px;
}
.content {
  line-height: 1.55;
  color: #1f2937;
  white-space: pre-wrap;
}
.content :deep(pre) {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
}
.content :deep(code) {
  font-family: 'Fira Code', monospace;
  font-size: 13px;
}
.actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  opacity: 0;
  transition: opacity 0.2s;
}
.message-bubble:hover .actions {
  opacity: 1;
}
.section {
  margin-bottom: 8px;
}
.section h4 {
  margin: 0 0 4px 0;
  color: #111827;
  font-size: 15px;
}
.section :deep(p) {
  margin: 4px 0;
}
.section :deep(ul) {
  margin: 4px 0;
  padding-left: 18px;
}
.section :deep(li) {
  margin: 2px 0;
}
.sources {
  margin-top: 6px;
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  align-items: center;
}
.source-label {
  font-size: 12px;
  color: #6b7280;
}
.suggestion {
  margin-top: 6px;
}
.suggestion :deep(.el-alert) {
  padding: 6px 10px;
}
</style>