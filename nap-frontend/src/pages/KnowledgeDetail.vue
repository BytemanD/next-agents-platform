<template>
  <div class="space-y-6">
    <div class="flex items-center gap-4">
      <t-button variant="outline" @click="$router.back()">
        <template #icon><t-icon name="arrow-left" /></template>
      </t-button>
      <div>
        <h1 class="text-2xl font-bold text-nap-text">{{ kb?.name || '知识库详情' }}</h1>
        <p class="text-nap-text-secondary mt-1">{{ kb?.description || '暂无描述' }}</p>
      </div>
      <StatusBadge v-if="kb" :status="kb.status" class="ml-2 self-center" />
    </div>

    <t-row :gutter="[16, 16]">
      <t-col :xs="12" :sm="6" :lg="3">
        <t-card :bordered="true" class="settings-card">
          <p class="text-sm text-nap-text-secondary">文档总数</p>
          <p class="text-2xl font-bold text-nap-text mt-1 tabular">{{ docs.length }}</p>
        </t-card>
      </t-col>
      <t-col :xs="12" :sm="6" :lg="3">
        <t-card :bordered="true" class="settings-card">
          <p class="text-sm text-nap-text-secondary">总大小</p>
          <p class="text-2xl font-bold text-nap-text mt-1 tabular">{{ totalSizeText }}</p>
        </t-card>
      </t-col>
      <t-col :xs="12" :sm="6" :lg="3">
        <t-card :bordered="true" class="settings-card">
          <p class="text-sm text-nap-text-secondary">已就绪</p>
          <p class="text-2xl font-bold text-nap-text mt-1 tabular">{{ readyCount }}</p>
        </t-card>
      </t-col>
      <t-col :xs="12" :sm="6" :lg="3">
        <t-card :bordered="true" class="settings-card">
          <p class="text-sm text-nap-text-secondary">待处理</p>
          <p class="text-2xl font-bold text-nap-text mt-1 tabular">{{ pendingCount }}</p>
        </t-card>
      </t-col>
    </t-row>

    <t-card :bordered="true" class="settings-card">
      <template #title><span class="text-nap-text">文档列表</span></template>
      <template #actions>
        <t-space :size="12">
          <t-input v-model="searchQuery" placeholder="搜索文档..." size="small" clearable class="w-64">
            <template #prefixIcon><t-icon name="search" /></template>
          </t-input>
          <t-button size="small" @click="showUpload = true">
            <template #icon><t-icon name="upload" /></template>
            上传文档
          </t-button>
        </t-space>
      </template>
      <t-table :data="filteredDocs" :columns="columns" :pagination="{ pageSize: 10 }" hover />
    </t-card>

    <t-dialog v-model:visible="showUpload" header="上传文档" :footer="null" placement="center" width="600px">
      <t-upload v-model="uploadFiles" theme="file-input" multiple accept=".pdf,.txt,.md,.docx,.csv" :max="10"
        :auto-upload="false">
        <template #default>
          <div class="text-center">
            <t-icon name="upload" size="48" class="text-nap-primary mx-auto mb-4" />
            <p class="text-nap-text">点击或拖拽文件到此处上传</p>
            <p class="text-sm text-nap-text-secondary mt-2">支持 PDF、TXT、Markdown、DOCX、CSV 格式</p>
          </div>
        </template>
      </t-upload>
      <div class="flex justify-end mt-4">
        <t-button @click="handleUpload" :loading="uploading" :disabled="uploadFiles.length === 0">
          上传
        </t-button>
      </div>
    </t-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, h, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { MessagePlugin } from 'tdesign-vue-next'
import StatusBadge from '@/components/common/StatusBadge.vue'
import { useKnowledgeStore } from '@/stores/knowledge'
import type { KnowledgeItem, KnowledgeBase } from '@/types'

const route = useRoute()
const knowledgeStore = useKnowledgeStore()

const baseUuid = computed(() => route.params.id as string)
const kb = computed<KnowledgeBase | undefined>(() =>
  knowledgeStore.knowledgeBases.find(b => b.uuid === baseUuid.value)
)

const searchQuery = ref('')
const showUpload = ref(false)
const uploading = ref(false)
const uploadFiles = ref<any[]>([])

const docs = computed<KnowledgeItem[]>(() => knowledgeStore.itemsByBase(baseUuid.value))

const filteredDocs = computed(() => {
  if (!searchQuery.value) return docs.value
  const q = searchQuery.value.toLowerCase()
  return docs.value.filter(d => d.name.toLowerCase().includes(q))
})

const readyCount = computed(() => docs.value.filter(d => d.status === 'saved' || d.status === 'parsed').length)
const pendingCount = computed(() => docs.value.length - readyCount.value)
const totalSizeText = computed(() => formatSize(docs.value.reduce((sum, d) => sum + d.size, 0)))

function parseType(name: string) {
  const ext = name.split('.').pop()?.toLowerCase() || 'file'
  const map: Record<string, string> = {
    pdf: 'pdf', txt: 'text', md: 'markdown', docx: 'docx', csv: 'csv'
  }
  return map[ext] || 'file'
}

const columns = [
  { colKey: 'name', title: '名称', width: 260 },
  {
    colKey: 'type', title: '类型', width: 110, cell: (row: any) => h('span', parseType(row.name))
  },
  {
    colKey: 'size', title: '大小', width: 120, cell: (row: any) => h('span', formatSize(row.size))
  },
  {
    colKey: 'status', title: '状态', width: 120, cell: (row: any) => h(StatusBadge, { status: row.status })
  },
  {
    colKey: 'created_at', title: '上传时间', width: 180, cell: (row: any) => h('span', new Date(row.created_at).toLocaleString())
  }
]

function handleUpload() {
  if (uploadFiles.value.length === 0) return
  uploading.value = true
  const tasks = uploadFiles.value.map(file =>
    axios.post('/api/v1/docs/upload', buildFormData(file))
  )
  Promise.all(tasks)
    .then(() => {
      MessagePlugin.success('上传成功')
      showUpload.value = false
      uploadFiles.value = []
      return knowledgeStore.fetchKnowledgeItems()
    })
    .catch(() => MessagePlugin.error('上传失败'))
    .finally(() => {
      uploading.value = false
    })
}

function buildFormData(file: any) {
  const form = new FormData()
  const raw = file.raw || file
  form.append('file', raw)
  return form
}

function formatSize(bytes: number) {
  if (bytes >= 1048576) return (bytes / 1048576).toFixed(1) + ' MB'
  if (bytes === 0) return '0 B'
  return (bytes / 1024).toFixed(1) + ' KB'
}

watch(baseUuid, () => knowledgeStore.fetchKnowledgeItems())

onMounted(() => {
  knowledgeStore.fetchKnowledgeItems()
})
</script>
