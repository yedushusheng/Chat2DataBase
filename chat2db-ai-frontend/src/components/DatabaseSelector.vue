<template>
  <div class="db-selector">
    <el-select
      v-model="selected"
      placeholder="选择数据库类型"
      size="large"
      style="width: 220px"
      @change="onChange"
    >
      <template #prefix>
        <el-icon><DataLine /></el-icon>
      </template>
      <el-option
        v-for="db in databases"
        :key="db.key"
        :label="db.name"
        :value="db.key"
      >
        <span style="display:flex; align-items:center; gap:8px">
          <span class="db-dot" :style="{ background: db.color }"></span>
          <span>{{ db.name }}</span>
          <el-tag v-if="db.is_self" type="warning" size="small">内部</el-tag>
        </span>
      </el-option>
    </el-select>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const emit = defineEmits(['change'])
const props = defineProps({ modelValue: { type: String, default: 'mysql' } })

const selected = ref(props.modelValue)
const databases = ref([])

onMounted(async () => {
  const res = await api.listDatabases()
  databases.value = res.data || []
})

function onChange(val) {
  emit('update:modelValue', val)
  emit('change', val)
}
</script>

<style scoped>
.db-selector {
  display: flex;
  align-items: center;
}
.db-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}
</style>