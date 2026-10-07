<template>
  <t-card class="mt-4" title="附件列表">
    <template #actions>
      <t-space :size="12">
        <t-input v-model="searchQuery" placeholder="搜索附件..." clearable class="w-64">
          <template #prefixIcon><t-icon name="search" /></template>
        </t-input>
        <t-button :disabled="selectedUuids.length === 0" @click="openSaveDialog">
          <template #icon><t-icon name="save" /></template>
          保存到知识库
        </t-button>
        <t-button variant="text" @click="fetchAttachments">
          <template #icon><t-icon name="refresh" /></template>
        </t-button>
      </t-space>
    </template>
    <t-empty v-if="filteredAttachments.length === 0 && !loading" class="py-10">
      <template #description>
        <t-text theme="secondary">在对话中上传的附件会显示在这里</t-text>
      </template>
      <template #image>
        <t-icon name="file" size="40" class="text-nap-text-tertiary" />
      </template>
    </t-empty>
    <t-table v-else size="small" :data="filteredAttachments" :columns="columns" :pagination="pagination" rowKey="uuid" hover
      :selected-row-keys="selectedUuids" select-on-row-click @select-change="handleSelectChange">
      <template #size="{ row }">
        {{ filesize(row.size) }}
      </template>
      <template #created_at="{ row }">
        {{ formatTime(row.created_at) }}
      </template>
      <template #operation="{ row }">
        <t-popconfirm :content="`确定删除附件「${row.name}」吗？`" theme="danger" @confirm="handleDelete(row)">
          <t-button variant="text" theme="danger">删除</t-button>
        </t-popconfirm>
      </template>
    </t-table>
  </t-card>

  <t-dialog v-model:visible="showKbDialog" header="选择知识库" placement="center"
    :confirm-btn="{ content: '确认保存', loading: savingToKb }" :cancel-btn="{}" @confirm="handleSaveToKb"
    :confirm-on-enter="false">
    <p v-if="selectedUuids.length > 0" class="text-sm text-nap-text-secondary">
      将 {{ selectedUuids.length }} 个附件添加到所选知识库
    </p>
    <br>
    <t-form label-align="top">
      <t-form-item label="目标知识库">
        <t-select v-model="selectedKbUuid" :options="kbOptions" :disabled="savingToKb" placeholder="请选择知识库" />
      </t-form-item>
    </t-form>
  </t-dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { MessagePlugin } from 'tdesign-vue-next'
import type { PrimaryTableCol } from 'tdesign-vue-next'
import { API } from '@/api'
import type { Attachment, KnowledgeBase } from '@/types'
import { filesize } from 'filesize'

const searchQuery = ref('')
const loading = ref(false)
const attachments = ref<Attachment[]>([])

const selectedUuids = ref<string[]>([])
const showKbDialog = ref(false)
const savingToKb = ref(false)
const selectedKbUuid = ref('')
const knowledgeBases = ref<KnowledgeBase[]>([])

const kbOptions = computed(() =>
  knowledgeBases.value.map(kb => ({ label: kb.name, value: kb.uuid }))
)

const columns: PrimaryTableCol[] = [
  { colKey: 'row-select', type: 'multiple', width: 48 },
  { colKey: 'name', title: '文件名', ellipsis: true },
  { colKey: 'size', title: '大小', align: 'right' },
  { colKey: 'created_at', title: '上传时间' },
  { colKey: 'operation', title: '操作', width: 100 },
]

const filteredAttachments = computed(() => {
  if (!searchQuery.value) return attachments.value
  const q = searchQuery.value.toLowerCase()
  return attachments.value.filter(att => att.name.toLowerCase().includes(q))
})

const pagination = computed(() => ({
  pageSize: 10,
  size: 'small' as const,
  total: filteredAttachments.value.length,
}))

function handleSelectChange(keys: Array<string | number>) {
  selectedUuids.value = keys.map(String)
}


function formatTime(iso: string) {
  if (!iso) return ''
  return new Date(iso).toLocaleString()
}

async function fetchAttachments() {
  loading.value = true
  try {
    const data = await API.fetchAttachments<{ attachments: Attachment[] }>()
    attachments.value = data.attachments || []
  } catch {
    attachments.value = []
  } finally {
    loading.value = false
  }
}

async function openSaveDialog() {
  if (selectedUuids.value.length === 0) {
    MessagePlugin.warning('请先选择附件')
    return
  }
  try {
    const data = await API.fetchKnowledgeBases()
    knowledgeBases.value = data.items || []
  } catch {
    knowledgeBases.value = []
  }
  selectedKbUuid.value = ''
  showKbDialog.value = true
}

async function handleSaveToKb() {
  if (!selectedKbUuid.value) {
    MessagePlugin.warning('请选择知识库')
    return
  }
  savingToKb.value = true
  try {
    await API.addAttachmentsToKnowledgeBase(selectedKbUuid.value, selectedUuids.value)
    MessagePlugin.success('已添加到知识库')
    showKbDialog.value = false
    selectedUuids.value = []
  } catch {
    MessagePlugin.error('保存失败')
  } finally {
    savingToKb.value = false
  }
}

async function handleDelete(att: Attachment) {
  try {
    await API.deleteAttachment(att.uuid)
    MessagePlugin.success('删除成功')
    selectedUuids.value = selectedUuids.value.filter(u => u !== att.uuid)
    fetchAttachments()
  } catch {
    MessagePlugin.error('删除失败')
  }
}

onMounted(fetchAttachments)
</script>