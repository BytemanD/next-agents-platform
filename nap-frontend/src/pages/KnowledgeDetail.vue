<template>
  <t-row :gutter="[16, 16]">
    <t-col :span="4">
      <t-space align="center">
        <t-button variant="text" @click="$router.back()">
          <template #icon><t-icon name="arrow-left" /></template>
        </t-button>
        <t-space direction="vertical" :size="2">
          <t-title level="h5">{{ kb?.name || '知识库详情' }}</t-title>
          <t-text theme="secondary">{{ kb?.description || '暂无描述' }}</t-text>
        </t-space>
      </t-space>
    </t-col>
    <t-col :span="8">
      <t-row :gutter="[16, 16]">
        <t-col :xs="12" :sm="6" :lg="3">
          <statistic-card title="文档总数" :value="docs.length" />
        </t-col>
        <t-col :xs="12" :sm="6" :lg="3">
          <statistic-card title="总大小" :value="totalSizeText" format-value />
        </t-col>
        <t-col :xs="12" :sm="6" :lg="3">
          <statistic-card title="已就绪" :value="readyCount" />
        </t-col>
        <t-col :xs="12" :sm="6" :lg="3">
          <statistic-card title="待处理" :value="pendingCount" />
        </t-col>
      </t-row>
    </t-col>
  </t-row>

  <t-card class="mt-4" size="small">
    <template #title><span class="text-nap-text">文档列表</span></template>
    <template #actions>
      <t-space :size="12">
        <t-button variant="outline" shape="circle" @click="handleRefresh">
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
    <t-table size="small" :data="filteredDocs" :columns="columns" :pagination="pagination" rowKey="uuid" hover>
      <template #status="{ row }">
        <t-tag shape="round" v-if="row.status == 'pending_process'" variant="light-outline">等待处理</t-tag>
        <t-tag shape="round" v-else-if="row.status == 'processing'" theme="warning" variant="light-outline">处理中</t-tag>
        <t-tag shape="round" v-else-if="row.status == 'process_failed'" theme="danger"
          variant="light-outline">处理失败</t-tag>

        <t-tag shape="round" v-else-if="row.status == 'pending_delete'" variant="light-outline"
          theme="danger">等待删除</t-tag>
        <t-tag shape="round" v-else-if="row.status == 'deleting'" variant="light-outline">删除中</t-tag>
        <t-tag shape="round" v-else-if="row.status == 'deleted'" variant="light-outline">已删除</t-tag>

        <t-tag shape="round" v-else-if="row.status == 'active'" variant="light-outline" theme="success">完成</t-tag>
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

  <t-dialog v-model:visible="showUpload" header="上传文档" width="700px" :on-confirm="handleUpload"
    :confirm-on-enter="false" :footer="false">
    <t-button variant="outline" @click="() => uploadRef?.triggerUpload()" class="mb-2">
      <template #icon><t-icon name="upload"></t-icon></template>选择文件
    </t-button>
    <t-upload v-model="uploadFiles" ref="uploadRef" multiple :theme="uploadFiles.length == 0 ? 'custom' : 'file-flow'"
      :max="10" :auto-upload="false" draggable :is-batch-upload="false" :request-method="handleUpload"
      :abridge-name="ABRIDGE_NAME">
      <template #dragContent>
        <t-space class="flex justify-between" align="center" direction="vertical" :size="2">
          <t-icon name="upload" size="48" class="text-nap-primay" />
          <span class="w-auto">点击或拖拽文件到此处上传</span>
          <span class="text-nap-accent" style="font-size: x-small;">支持格式: PDF、TXT、Markdown、DOCX、CSV </span>
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
        <t-descriptions-item label="大小">{{ filesize(detail.size) }}</t-descriptions-item>
        <t-descriptions-item label="上传时间">{{ new Date(detail.created_at).toLocaleString() }}</t-descriptions-item>
        <t-descriptions-item label="更新时间">{{ new Date(detail.updated_at).toLocaleString() }}</t-descriptions-item>
      </t-descriptions>

      <t-collapse v-model="todosCollapse" class="my-3">
        <t-collapse-panel value="todos" header="处理进度">
          <t-steps layout="vertical" :current="currentTodo" theme="dot" readonly>
            <t-step-item v-for="todo in todos" :key="todo.id" :title="todoName(todo.name)"
              :status="todoStatus(todo.status)" :content="todo.detail" />
          </t-steps>
        </t-collapse-panel>
      </t-collapse>

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
import type { KnowledgeItem, KnowledgeBase, KnowledgeDetail, KnowledgeTodo } from '@/types'
import type { UploadInstanceFunctions, UploadProps } from 'tdesign-vue-next';
import StatisticCard from '@/components/common/StatisticCard.vue';
import { filesize } from 'filesize'

const uploadRef = ref<UploadInstanceFunctions>();


const ABRIDGE_NAME: UploadProps['abridgeName'] = [10, 7];

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
const todos = ref<KnowledgeTodo[]>([])
const todosCollapse = ref([])

async function handleShowDetail(row: any) {
  showDetail.value = true
  loadingDetail.value = true
  detail.value = null
  todos.value = []
  try {
    const [d, t] = await Promise.all([
      API.fetchKnowledgeDetail(row.uuid),
      API.fetchKnowledgeTodos(row.uuid)
    ])
    detail.value = d
    todos.value = t.items
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

const pagination = computed(() => ({ pageSize: 10, total: filteredDocs.value.length }))

const isDone = (s: any) => {
  const v = String(s || '')
  return v === 'active' || v === '6'
}
const readyCount = computed(() => docs.value.filter(d => isDone(d.status)).length)
const pendingCount = computed(() => docs.value.length - readyCount.value)
const totalSizeText = computed(() => docs.value.reduce((sum, d) => sum + d.size, 0))

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
    colKey: 'size', title: '大小', width: 80, align: 'right', cell: (h: any, { row }: any) => h('span', filesize(row.size))
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

const STATUS_TEXT: Record<string, string> = {
  pending_process: '待处理', processing: '处理中', process_failed: '处理失败',
  pending_delete: '待删除', deleting: '删除中', deleted: '已删除',
  active: '已就绪'
}

function statusText(status: string | number): string {
  return STATUS_TEXT[String(status)] || String(status)
}

const TODO_NAME_TEXT: Record<string, string> = {
  convert: '内容转换', vector: '向量化', enrich: '内容抽取'
}

function todoName(name: string): string {
  return TODO_NAME_TEXT[name] || name
}

function todoStatus(status: string): 'default' | 'process' | 'finish' | 'error' {
  if (status === 'running') return 'process'
  if (status === 'completed') return 'finish'
  if (status === 'failed') return 'error'
  return 'default'
}

const currentTodo = computed(() => {
  const idx = todos.value.findIndex(t => t.status !== 'completed')
  return idx === -1 ? todos.value.length - 1 : idx
})

watch(baseUuid, () => knowledgeStore.fetchKnowledgeItems(baseUuid.value))

onMounted(() => {
  knowledgeStore.fetchKnowledgeItems(baseUuid.value)
})
</script>