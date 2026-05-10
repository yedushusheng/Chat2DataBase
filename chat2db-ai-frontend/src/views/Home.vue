<template>
  <div class="home">
    <div class="top-bar">
      <div class="brand">
        <el-icon :size="28" color="#409eff"><DataLine /></el-icon>
        <h1>Chat2DB-AI</h1>
        <el-tag size="small" type="info">Pro</el-tag>
      </div>
      <DatabaseSelector v-model="store.currentDb" @change="onDbChange" />
    </div>

    <div class="main">
      <HistorySidebar />

      <div class="center">
        <ChatWindow />
      </div>

      <div class="right-panel">
        <el-tabs v-model="rightTab" type="border-card">
          <el-tab-pane label="知识库" name="upload">
            <UploadPanel />
          </el-tab-pane>
          <el-tab-pane label="FAQ" name="faq">
            <FAQPanel />
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { DataLine } from '@element-plus/icons-vue'
import { useChatStore } from '../stores/chat.js'
import DatabaseSelector from '../components/DatabaseSelector.vue'
import HistorySidebar from '../components/HistorySidebar.vue'
import ChatWindow from '../components/ChatWindow.vue'
import UploadPanel from '../components/UploadPanel.vue'
import FAQPanel from '../components/FAQPanel.vue'

const store = useChatStore()
const rightTab = ref('upload')

function onDbChange(db) {
  store.setDb(db)
  store.clearMessages()
  ElMessage.success(`已切换至 ${db.toUpperCase()} 模式`)
}
</script>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #ffffff;
}
.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  border-bottom: 1px solid #e5e7eb;
  background: #ffffff;
  z-index: 10;
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
}
.brand h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #111827;
}
.main {
  display: flex;
  flex: 1;
  overflow: hidden;
}
.center {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}
.right-panel {
  width: 380px;
  border-left: 1px solid #e5e7eb;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}
:deep(.right-panel .el-tabs) {
  display: flex;
  flex-direction: column;
  height: 100%;
}
:deep(.right-panel .el-tabs__content) {
  flex: 1;
  overflow-y: auto;
}
</style>
