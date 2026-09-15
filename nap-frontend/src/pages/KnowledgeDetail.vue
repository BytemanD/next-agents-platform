<template>
  <t-space align="center">
    <t-button variant="outline" @click="$router.back()">
      <template #icon><t-icon name="arrow-left" /></template>
    </t-button>

    <t-space direction="vertical" :size="1">
      <h4 class="text-2xl font-bold text-nap-text">{{ kb?.name || '知识库详情' }}</h4>
      <p class="text-nap-text-secondary mt-1">{{ kb?.description || '暂无描述' }}</p>
    </t-space>
    <t-tag v-if="kb" shape="round" class="self-center ml-12" :theme="kb.active ? 'success' : 'danger'">
      {{ kb.active ? '启用' : '禁用' }}
    </t-tag>
  </t-space>

  <t-row :gutter="[16, 16]" class="mt-4">
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

  <t-card class="mt-4">
    <template #title><span class="text-nap-text">文档列表</span></template>
    <template #actions>
      <t-space :size="12">
        <t-button variant="outline" shape="square" @click="handleRefresh">
          <template #icon><t-icon name="refresh" /></template>
        </t-button>
        <t-input v-model="searchQuery" placeholder="搜索文档..." clearable class="w-64">
          <template #prefixIcon><t-icon name="search" /></template>
        </t-input>
        <t-button theme="warning">重置状态</t-button>
        <t-button @click="showUpload = true">
          <template #icon><t-icon name="upload" /></template>
          上传文档
        </t-button>
      </t-space>
    </template>
    <t-table size="small" :data="filteredDocs" :columns="columns" :pagination="{ pageSize: 10 }" hover>
      <template #status="{ row }">
        <t-tag shape="round" v-if="row.status == 'save_waiting'" variant="light-outline">等待保存</t-tag>
        <t-tag shape="round" v-else-if="row.status == 'save_running'" variant="light-outline">保存中</t-tag>
        <t-tag shape="round" v-else-if="row.status == 'save_completed'" variant="light-outline"
          theme="success">保存完成</t-tag>
        <t-tag shape="round" v-else-if="row.status == 'save_failed'" variant="light-outline" theme="danger">保存失败</t-tag>

        <t-tag shape="round" v-else-if="row.status == 'parse_pending'" variant="light-outline">等待解析</t-tag>
        <t-tag shape="round" v-else-if="row.status == 'parse_running'" variant="light-outline">解析中</t-tag>
        <t-tag shape="round" v-else-if="row.status == 'parse_completed'" variant="light-outline"
          theme="success">解析完成</t-tag>
        <t-tag shape="round" v-else-if="row.status == 'parse_failed'" variant="light-outline" theme="danger">解释</t-tag>

        <t-tag shape="round" v-else-if="row.status == 'vector_pending'" variant="light-outline">等待向量化</t-tag>
        <t-tag shape="round" v-else-if="row.status == 'vector_running'" variant="light-outline">向量化中</t-tag>
        <t-tag shape="round" v-else-if="row.status == 'vector_completed'" variant="light-outline"
          theme="success">向量化完成</t-tag>
        <t-tag shape="round" v-else-if="row.status == 'vector_failed'" variant="light-outline"
          theme="danger">向量化失败</t-tag>

        <t-tag shape="round" v-else-if="row.status == 'enrich_pending'" variant="light-outline">等待抽取</t-tag>
        <t-tag shape="round" v-else-if="row.status == 'enrich_running'" variant="light-outline">抽取中</t-tag>
        <t-tag shape="round" v-else-if="row.status == 'enrich_completed'" variant="light-outline"
          theme="success">抽取完成</t-tag>
        <t-tag shape="round" v-else-if="row.status == 'enrich_failed'" variant="light-outline"
          theme="danger">抽取失败</t-tag>

        <t-tag shape="round" v-else-if="row.status == 'delete'" variant="light-outline">等待删除</t-tag>
        <t-tag shape="round" v-else-if="row.status == 'delete_pending'" variant="light-outline">等待删除</t-tag>
        <t-tag shape="round" v-else-if="row.status == 'delete_running'" variant="light-outline">删除中</t-tag>
        <t-tag shape="round" v-else-if="row.status == 'delete_completed'" variant="light-outline"
          theme="success">删除完成</t-tag>
        <t-tag shape="round" v-else-if="row.status == 'delete_failed'" variant="light-outline"
          theme="danger">删除完成</t-tag>

        <t-tag shape="round" v-else variant="light-outline">{{ row.status }}</t-tag>
      </template>
      <template #operation="{ row }">
        <t-popconfirm :content="`确定删除文档「${row.name}」吗？`" theme="danger" @confirm="handleDelete(row)">
          <t-button variant="text" theme="danger">删除</t-button>
        </t-popconfirm>
        <t-button variant="text" theme="primary" @click="handleShowDetail(row)">详情</t-button>
      </template>
    </t-table>
  </t-card>

  <t-dialog v-model:visible="showUpload" footer header="上传文档" placement="center" width="600px"
    :on-confirm="handleUpload" :confirm-on-enter="false" :confirm-btn="uploadFiles.length == 0 ? null : '上传'">
    <t-upload v-model="uploadFiles" multiple accept=".pdf,.txt,.md,.docx,.csv" :max="10" :auto-upload="false">
      <template #default>
        <t-space direction="vertical" align="center" class="pa-4" style="border: 3px dashed #dcdcdc;">
          <t-icon name="upload" size="48" class="text-nap-primary mx-auto mb-4" />
          <p class="text-nap-text">点击或拖拽文件到此处上传</p>
          <p class="text-sm text-nap-text-secondary mt-2">支持 PDF、TXT、Markdown、DOCX、CSV 格式</p>
        </t-space>
      </template>
    </t-upload>
  </t-dialog>

  <t-drawer v-model:visible="showDetail" :header="detail?.name || '文档详情'" size="560px" :footer="false">
    <div v-if="loadingDetail">
      <t-loading size="large" text="加载中..." />
    </div>
    <template v-else-if="detail">
      <t-descriptions :column="1" size="small" bordered table-layout="auto">
        <t-descriptions-item label="UUID">{{ detail.uuid }}</t-descriptions-item>
        <t-descriptions-item label="状态">{{ statusText(detail.status) }}</t-descriptions-item>
        <t-descriptions-item label="上传者">{{ detail.creator || '-' }}</t-descriptions-item>
        <t-descriptions-item label="大小">{{ formatSize(detail.size) }}</t-descriptions-item>
        <t-descriptions-item label="上传时间">{{ new Date(detail.created_at).toLocaleString() }}</t-descriptions-item>
        <t-descriptions-item label="更新时间">{{ new Date(detail.updated_at).toLocaleString() }}</t-descriptions-item>
      </t-descriptions>
      <t-divider>内容抽取摘要</t-divider>
      <template v-if="detail.enrichment">
        <h2 class="my-2"><b>关键词</b></h2>
        <t-space size="small" breakLine>
          <span v-if="!detail.enrichment.keywords || detail.enrichment.keywords.length === 0">暂无关键词</span>
          <t-tag v-for="kw in detail.enrichment.keywords || []" :key="kw" theme="warning" variant="light"
            shape="round">{{ kw }}
          </t-tag>
        </t-space>
        <h2 class="my-2"><b>摘要</b></h2>
        <p style="white-space: pre-wrap">{{ detail.enrichment.summary || '暂无摘要' }}</p>
      </template>
      <div v-else>
        该文档尚未完成内容抽取，暂无摘要与关键词。
      </div>
    </template>
  </t-drawer>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { MessagePlugin, Button as TButton } from 'tdesign-vue-next'
import { API } from '@/api'
import { useKnowledgeStore } from '@/stores/knowledge'
import type { KnowledgeItem, KnowledgeBase, KnowledgeDetail } from '@/types'

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
const showDetail = ref(false)
const loadingDetail = ref(false)
const detail = ref<KnowledgeDetail | null>(null)

async function handleShowDetail(row: any) {
  showDetail.value = true
  loadingDetail.value = true
  detail.value = null
  try {
    detail.value = await API.fetchKnowledgeDetail(row.uuid)
  } catch {
    MessagePlugin.error('加载文档详情失败')
  } finally {
    loadingDetail.value = false
  }
}

async function handleRefresh() {
  try {
    await Promise.all([
      knowledgeStore.fetchKnowledgeBases(),
      knowledgeStore.fetchKnowledgeItems(baseUuid.value)
    ])
    MessagePlugin.success('已刷新')
  } catch {
    MessagePlugin.error('刷新失败')
  }
}

const docs = computed<KnowledgeItem[]>(() => knowledgeStore.items)

const filteredDocs = computed(() => {
  if (!searchQuery.value) return docs.value
  const q = searchQuery.value.toLowerCase()
  return docs.value.filter(d => d.name.toLowerCase().includes(q))
})

const readyCount = computed(() => docs.value.filter(d => d.status === 2 || d.status === 4).length)
const pendingCount = computed(() => docs.value.length - readyCount.value)
const totalSizeText = computed(() => formatSize(docs.value.reduce((sum, d) => sum + d.size, 0)))

function parseType(name: string) {
  const ext = name.split('.').pop()?.toLowerCase() || 'file'
  // const map: Record<string, string> = {
  //   pdf: 'pdf', txt: 'text', md: 'md', docx: 'docx', csv: 'csv'
  // }
  return ext || 'file'
}

const columns = [
  { colKey: 'name', title: '名称', width: 260 },
  {
    colKey: 'type', title: '类型', width: 50, cell: (h: any, { row }: any) => h('span', parseType(row.name))
  },
  {
    colKey: 'size', title: '大小', width: 80, cell: (h: any, { row }: any) => h('span', formatSize(row.size))
  },
  {
    colKey: 'creator', title: '上传者', width: 120, cell: (h: any, { row }: any) => h('span', row.creator || '-')
  },
  {
    colKey: 'status', title: '状态', width: 60,
  },
  {
    colKey: 'created_at', title: '上传时间', width: 100, cell: (h: any, { row }: any) => h('span', new Date(row.created_at).toLocaleString())
  },
  {
    colKey: 'operation', title: '操作', width: 80, fixed: 'right',
    // cell: (h: any, { row }: any) => h('div', { class: 'flex justify-center' }, [
    //   h(Popconfirm,
    //     {
    //       content: `确定删除文档「${row.name}」吗？`,
    //       onConfirm: () => handleDelete(row)
    //     },
    //     {
    //       default: () => h(TButton, {
    //         variant: 'text',
    //         theme: 'danger'
    //       }, { default: () => '删除' })
    //     })
    // ])
  }
]

async function handleDelete(row: any) {
  try {
    await API.deleteKnowledge(row.uuid)
    MessagePlugin.success('删除成功')
    await knowledgeStore.fetchKnowledgeItems(baseUuid.value)
  } catch {
    MessagePlugin.error('删除失败')
  }
}

function handleUpload() {
  if (uploadFiles.value.length === 0) {
    MessagePlugin.error('请选择文件')
    return
  }
  uploading.value = true
  const tasks = uploadFiles.value.map(file =>
    API.uploadKbFile(baseUuid.value, file.raw || file)
  )
  Promise.all(tasks)
    .then(() => {
      MessagePlugin.success('上传成功')
      showUpload.value = false
      uploadFiles.value = []
      return knowledgeStore.fetchKnowledgeItems(baseUuid.value)
    })
    .catch(() => MessagePlugin.error('上传失败'))
    .finally(() => {
      uploading.value = false
    })
}

function formatSize(bytes: number) {
  if (!bytes) return '0 B'
  if (bytes === 0) return '0 B'
  if (bytes >= 1048576) return (bytes / 1048576).toFixed(1) + ' MB'
  return (bytes / 1024).toFixed(1) + ' KB'
}

const STATUS_TEXT: Record<string, string> = {
  save_waiting: '等待保存', save_running: '保存中', save_completed: '保存完成', save_failed: '保存失败',
  parse_pending: '等待解析', parse_running: '解析中', parse_completed: '解析完成', parse_failed: '解析失败',
  vector_pending: '等待向量化', vector_running: '向量化中', vector_completed: '向量化完成', vector_failed: '向量化失败',
  enrich_pending: '等待抽取', enrich_running: '抽取中', enrich_completed: '抽取完成', enrich_failed: '抽取失败',
  delete: '等待删除', delete_pending: '等待删除', delete_running: '删除中', delete_completed: '删除完成', delete_failed: '删除失败'
}

function statusText(status: string | number): string {
  return STATUS_TEXT[String(status)] || String(status)
}

watch(baseUuid, () => knowledgeStore.fetchKnowledgeItems(baseUuid.value))

onMounted(() => {
  knowledgeStore.fetchKnowledgeItems(baseUuid.value)
})
</script>
