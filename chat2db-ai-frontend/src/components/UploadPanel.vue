<template>
  <div class="upload-panel">
    <h3>📄 RAG 知识库管理</h3>
    <p class="desc">上传故障分析文档、运维手册、历史案例，自动解析向量化入库</p>

    <el-upload
      drag
      :auto-upload="false"
      :on-change="handleFileChange"
      :file-list="fileList"
      accept=".pdf,.docx,.txt,.md"
      multiple
    >
      <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
      <div class="el-upload__text">
        拖拽文件到此处或 <em>点击上传</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          支持 PDF / Word / TXT / Markdown，单文件不超过 50MB
        </div>
      </template>
    </el-upload>

    <div class="upload-actions">
      <el-select v-model="targetDb" placeholder="选择文档归属数据库" size="small">
        <el-option
          v-for="db in databases"
          :key="db.key"
          :label="db.name"
          :value="db.key"
        />
      </el-select>
      <el-button type="primary" :loading="uploading" @click="submitUpload">
        确认上传
      </el-button>
      <el-button @click="refreshList">刷新列表</el-button>
    </div>

    <el-divider />

    <div class="doc-list">
      <h4>已入库文档 ({{ sources.length }})</h4>
      <el-table :data="sources" size="small" style="width: 100%">
        <el-table-column prop="name" label="文件名" show-overflow-tooltip>
          <template #default="scope">
            <el-icon><Document /></el-icon>
            {{ scope.row }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="scope">
            <el-button link type="danger" size="small" @click="deleteDoc(scope.row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="stats.total_documents" class="stats">
        <el-tag>向量总数: {{ stats.total_documents }}</el-tag>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { UploadFilled, Document } from '@element-plus/icons-vue'
import api from '../api'

const fileList = ref([])
const uploading = ref(false)
const targetDb = ref('general')
const databases = ref([])
const sources = ref([])
const stats = ref({})

onMounted(async () => {
  const dbRes = await api.listDatabases()
  databases.value = dbRes.data || []
  refreshList()
})

function handleFileChange(file, files) {
  fileList.value = files
}

async function submitUpload() {
  if (!fileList.value.length) {
    ElMessage.warning('请先选择文件')
    return
  }
  uploading.value = true
  try {
    if (fileList.value.length === 1) {
      const fd = new FormData()
      fd.append('file', fileList.value[0].raw)
      fd.append('db_type', targetDb.value)
      await api.upload(fd)
      ElMessage.success('上传成功')
    } else {
      const fd = new FormData()
      fileList.value.forEach(f => fd.append('files', f.raw))
      fd.append('db_type', targetDb.value)
      await api.uploadBatch(fd)
      ElMessage.success('批量上传完成')
    }
    fileList.value = []
    await refreshList()
  } catch (err) {
    ElMessage.error(err.message || '上传失败')
  } finally {
    uploading.value = false
  }
}

async function refreshList() {
  const res = await api.listUploads()
  sources.value = res.data?.sources || []
  stats.value = res.data?.stats || {}
}

async function deleteDoc(filename) {
  try {
    await api.deleteUpload(filename)
    ElMessage.success('删除成功')
    await refreshList()
  } catch (err) {
    ElMessage.error(err.message || '删除失败')
  }
}
</script>

<style scoped>
.upload-panel {
  padding: 20px;
}
.desc {
  color: #6b7280;
  font-size: 13px;
  margin-bottom: 16px;
}
.upload-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  align-items: center;
}
.doc-list {
  margin-top: 10px;
}
.doc-list h4 {
  margin-bottom: 10px;
  font-size: 14px;
  color: #374151;
}
.stats {
  margin-top: 12px;
}
</style>
