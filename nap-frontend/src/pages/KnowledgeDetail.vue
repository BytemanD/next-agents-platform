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

  <t-card class="mt-4" size="small" title="文档列表">
    <template #actions>
      <t-space :size="12">
        <t-input v-model="searchQuery" placeholder="搜索文档..." clearable class="w-64">
          <template #prefixIcon><t-icon name="search" /></template>
        </t-input>
        <t-button theme="warning">重置状态</t-button>
        <t-button @click="showUpload = true">
          <template #icon><t-icon name="upload" /></template>
          上传文档
        </t-button>
        <t-button variant="text" @click="handleRefresh">
          <template #icon><t-icon name="refresh" /></template>
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
          <t-button  variant="text" size="small" theme="danger" >删除</t-button>
        </t-popconfirm>
        <t-button variant="text" size="small" theme="primary" @click="handleShowDetail(row)">详情</t-button>
        <t-button v-if="canPreview(row.name)" variant="text" size="small" @click="openPreview(row.uuid)">预览</t-button>
      </template>
    </t-table>
  </t-card>

  <t-dialog v-model:visible="showUpload" header="上传文档" width="700px" :footer="false" @close="resetUpload">
    <t-button variant="outline" @click="() => uploadRef?.triggerUpload()" class="mb-2">
      <template #icon><t-icon name="upload"></t-icon></template>选择文件
    </t-button>
    <t-upload v-model="uploadFiles" ref="uploadRef" multiple :theme="uploadFiles.length == 0 ? 'custom' : 'file-flow'"
      :max="10" :auto-upload="false" draggable :is-batch-upload="false" :request-method="handleUpload"
      :on-success="handleUploadSuccess" :on-fail="handleUploadFail" :abridge-name="ABRIDGE_NAME">
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
import { MessagePlugin } from 'tdesign-vue-next'
import { API } from '@/api'
import { useKnowledgeStore } from '@/stores/knowledge'
import type { KnowledgeItem, KnowledgeBase, KnowledgeDetail, KnowledgeTodo } from '@/types'
import type {
  UploadFile,
  UploadInstanceFunctions,
  UploadProps,
  RequestMethodResponse,
} from 'tdesign-vue-next';
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
const uploadFiles = ref<UploadFile[]>([])
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
    colKey: 'operation', title: '操作', width: 150, fixed: 'right',
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

function openPreview(uuid: string) {
  window.open(`/knowledges/${uuid}`, '_blank')
}

const PREVIEWABLE_EXTS = ['md', 'markdown', 'txt', 'text', 'log', 'html', 'htm']

function canPreview(name: string) {
  const i = (name || '').lastIndexOf('.')
  if (i < 0) return false
  return PREVIEWABLE_EXTS.includes(name.slice(i + 1).toLowerCase())
}

/**
 * t-upload 的 requestMethod 必须返回 RequestMethodResponse 的 Promise，
 * 否则组件内部的 uploading 状态不会被重置，上传按钮会一直显示“上传中”。
 *
 * 同时这里只处理组件传入的文件：is-batch-upload=false 时组件会按文件
 * 逐个调用本方法，若直接遍历 uploadFiles 会把同一批文件重复上传。
 */
async function handleUpload(
  input: UploadFile | UploadFile[]
): Promise<RequestMethodResponse> {
  const files = (Array.isArray(input) ? input : input ? [input] : []).filter(
    (file): file is UploadFile => !!file
  )
  const rawFiles = files
    .map(file => file.raw)
    .filter((file): file is File => !!file)

  if (rawFiles.length === 0) {
    return { status: 'fail', error: '请选择文件', response: {} }
  }

  try {
    await Promise.all(
      rawFiles.map(file => API.uploadKbFile(baseUuid.value, file))
    )
    return { status: 'success', response: { files } }
  } catch (error) {
    const detail = error instanceof Error ? error.message : '上传失败'
    return { status: 'fail', error: detail, response: {} }
  }
}

async function handleUploadSuccess() {
  MessagePlugin.success('上传成功')
  showUpload.value = false
  uploadFiles.value = []
  try {
    await knowledgeStore.fetchKnowledgeItems(baseUuid.value)
  } catch {
    MessagePlugin.error('刷新文档列表失败')
  }
}

function handleUploadFail(context: any) {
  const name = context?.file?.name || '文件'
  const detail =
    context?.file?.response?.error ||
    context?.response?.error ||
    '上传失败'
  MessagePlugin.error(`「${name}」${detail}`)
}

function resetUpload() {
  uploadFiles.value = []
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