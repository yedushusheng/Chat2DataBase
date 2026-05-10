<template>
  <div class="faq-panel">
    <h3>🔥 高频问题 (FAQ)</h3>

    <el-input
      v-model="searchText"
      placeholder="搜索问题或关键词..."
      clearable
      @keyup.enter="doSearch"
    >
      <template #append>
        <el-button :icon="Search" @click="doSearch" />
      </template>
    </el-input>

    <el-tabs v-model="activeTab" @tab-change="onTabChange">
      <el-tab-pane label="热门问题" name="hot">
        <el-empty v-if="!hotList.length" description="暂无数据" />
        <div v-else class="faq-list">
          <div
            v-for="item in hotList"
            :key="item.id || item.title"
            class="faq-item"
            @click="selectFaq(item)"
          >
            <div class="faq-title">
              <el-tag size="small" :type="getCategoryType(item.category)">{{ item.category }}</el-tag>
              <span>{{ item.title }}</span>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="搜索结果" name="search">
        <el-empty v-if="!searchResults.length" description="输入关键词搜索" />
        <div v-else class="faq-list">
          <div
            v-for="item in searchResults"
            :key="item.title"
            class="faq-item"
            @click="selectFaq(item)"
          >
            <div class="faq-title">
              <el-tag size="small">{{ item.db_type }}</el-tag>
              <span>{{ item.title }}</span>
            </div>
            <div class="faq-preview">{{ item.content }}</div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { useChatStore } from '../stores/chat.js'
import api from '../api'

const store = useChatStore()
const activeTab = ref('hot')
const searchText = ref('')
const hotList = ref([])
const searchResults = ref([])

onMounted(() => loadHot())

watch(() => store.currentDb, () => {
  if (activeTab.value === 'hot') loadHot()
})

function onTabChange(tab) {
  if (tab === 'hot') loadHot()
}

async function loadHot() {
  const res = await api.hotFaq(store.currentDb, 20)
  hotList.value = res.data || []
}

async function doSearch() {
  if (!searchText.value.trim()) return
  activeTab.value = 'search'
  const res = await api.searchFaq(searchText.value, store.currentDb, 20)
  searchResults.value = res.data || []
}

function selectFaq(item) {
  store.addMessage('user', item.title)
}

function getCategoryType(cat) {
  const map = { troubleshooting: 'danger', tips: 'success', parameters: 'warning', solution: 'primary' }
  return map[cat] || 'info'
}
</script>

<style scoped>
.faq-panel {
  padding: 20px;
}
.faq-list {
  margin-top: 12px;
}
.faq-item {
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  border-bottom: 1px solid #f3f4f6;
}
.faq-item:hover {
  background: #f9fafb;
}
.faq-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #111827;
}
.faq-preview {
  margin-top: 6px;
  font-size: 12px;
  color: #6b7280;
  line-height: 1.5;
}
</style>
