<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-nap-text">知识库</h1>
        <p class="text-nap-text-secondary mt-1">管理文档与知识源</p>
      </div>
      <t-button theme="primary" @click="showUpload = true">
        <template #icon><t-icon name="upload" /></template>
        上传文档
      </t-button>
    </div>

    <t-row :gutter="[16, 16]">
      <t-col :xs="24" :sm="8">
        <t-card :bordered="true" class="settings-card">
          <t-space :size="12" align="center">
            <t-icon name="file" :size="24" class="text-nap-primary" />
            <div>
              <p class="text-2xl font-bold text-nap-text">{{ documents.length }}</p>
              <p class="text-sm text-nap-text-secondary">文档总数</p>
            </div>
          </t-space>
        </t-card>
      </t-col>
      <t-col :xs="24" :sm="8">
        <t-card :bordered="true" class="settings-card">
          <t-space :size="12" align="center">
            <t-icon name="check-circle-filled" :size="24" class="text-nap-success" />
            <div>
              <p class="text-2xl font-bold text-nap-text">{{ readyCount }}</p>
              <p class="text-sm text-nap-text-secondary">处理完成</p>
            </div>
          </t-space>
        </t-card>
      </t-col>
      <t-col :xs="24" :sm="8">
        <t-card :bordered="true" class="settings-card">
          <t-space :size="12" align="center">
            <t-icon name="database" :size="24" class="text-nap-secondary" />
            <div>
              <p class="text-2xl font-bold text-nap-text">{{ totalChunks }}</p>
              <p class="text-sm text-nap-text-secondary">文档分块数</p>
            </div>
          </t-space>
        </t-card>
      </t-col>
    </t-row>

    <t-card :bordered="true" class="settings-card">
      <template #title><span class="text-nap-text">文档列表</span></template>
      <template #actions>
        <t-input v-model="searchQuery" placeholder="搜索文档..." size="small" clearable class="w-64">
          <template #prefixIcon><t-icon name="search" /></template>
        </t-input>
      </template>
      <t-table
        :data="filteredDocuments"
        :columns="columns"
        :pagination="pagination"
        hover
      />
    </t-card>

    <t-dialog v-model:visible="showUpload" header="上传文档" :footer="null" placement="center" width="600px">
      <t-upload
        action="/api/upload"
        multiple
        :max="10"
        accept=".pdf,.txt,.md,.docx,.csv"
        theme="drag"
      >
        <template #default>
          <div class="text-center">
            <t-icon name="upload" :size="48" class="text-nap-primary mx-auto mb-4" />
            <p class="text-nap-text">点击或拖拽文件到此处上传</p>
            <p class="text-sm text-nap-text-secondary mt-2">支持 PDF、TXT、Markdown、DOCX、CSV 格式</p>
          </div>
        </template>
      </t-upload>
    </t-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, h } from 'vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import type { KnowledgeDocument } from '@/types'

const searchQuery = ref('')
const showUpload = ref(false)

const documents = ref<KnowledgeDocument[]>([
  { id: '1', name: 'research-paper.pdf', type: 'pdf', size: 2048000, status: 'ready', chunks: 156, createdAt: new Date().toISOString() },
  { id: '2', name: 'codebase-docs.md', type: 'markdown', size: 512000, status: 'ready', chunks: 89, createdAt: new Date().toISOString() },
  { id: '3', name: 'data-analysis.csv', type: 'csv', size: 1024000, status: 'processing', chunks: 0, createdAt: new Date().toISOString() },
  { id: '4', name: 'meeting-notes.txt', type: 'text', size: 256000, status: 'ready', chunks: 42, createdAt: new Date().toISOString() }
])

const readyCount = computed(() => documents.value.filter(d => d.status === 'ready').length)
const totalChunks = computed(() => documents.value.reduce((sum, d) => sum + d.chunks, 0))

const filteredDocuments = computed(() => {
  if (!searchQuery.value) return documents.value
  const q = searchQuery.value.toLowerCase()
  return documents.value.filter(d => d.name.toLowerCase().includes(q))
})

const pagination = ref({
  defaultPageSize: 10,
  defaultCurrent: 1
})

const columns = [
  { colKey: 'name', title: '名称', width: 250 },
  { colKey: 'type', title: '类型', width: 100 },
  { colKey: 'size', title: '大小', width: 120, cell: (_row: any, rowIndex: number) => {
    const doc = filteredDocuments.value[rowIndex]
    return doc ? formatSize(doc.size) : ''
  }},
  { colKey: 'chunks', title: '分块数', width: 100 },
  { colKey: 'status', title: '状态', width: 120, cell: (_row: any, rowIndex: number) => {
    const doc = filteredDocuments.value[rowIndex]
    return doc ? h(StatusBadge, { status: doc.status }) : ''
  }}
]

function formatSize(bytes: number) {
  if (bytes >= 1048576) return (bytes / 1048576).toFixed(1) + ' MB'
  return (bytes / 1024).toFixed(1) + ' KB'
}
</script>

<style scoped>
.settings-card {
  background-color: var(--td-bg-color-container);
}
</style>