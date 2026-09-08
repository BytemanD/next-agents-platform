<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-sm text-nap-text-secondary mt-1">管理知识库与知识来源</p>
      </div>
      <div class="flex items-center gap-3">
        <t-input v-model="searchQuery" placeholder="搜索知识库..." clearable class="w-64">
          <template #prefixIcon><t-icon name="search" /></template>
        </t-input>
        <t-select :disabled="knowledgeStore.loading" class="w-36" size="small" v-model="filterByStatus"
          :options="statusOptions" />
        <t-button @click="showCreate = true">
          <template #icon><t-icon name="add" /></template>
          新建知识库
        </t-button>
      </div>
    </div>

    <div class="flex items-center gap-6">
      <t-statistic title="知识库总数" :value="knowledgeStore.knowledgeBases.length" unit="个" />
      <t-statistic title="文档总数" :value="knowledgeStore.items.length" unit="个" />
      <t-statistic title="占用空间" :value="totalSizeText" unit="" />
    </div>

    <t-empty v-if="filteredBases.length === 0 && !knowledgeStore.loading" class="py-20">
      <template #description>
        <p class="text-nap-text">未找到知识库</p>
        <p class="text-sm text-nap-text-secondary mt-1">创建你的第一个知识库开始使用</p>
        <t-button size="small" class="mt-4" @click="showCreate = true">
          新建知识库
        </t-button>
      </template>
      <template #image>
        <t-icon name="book" size="48" class="text-nap-text-tertiary" />
      </template>
    </t-empty>

    <t-row v-else :gutter="[16, 16]">
      <t-col v-for="kb in filteredBases" :key="kb.uuid" :xs="12" :sm="12" :md="8" :lg="6">
        <t-card class="card-hover cursor-pointer group h-full" :bordered="true"
          @click="$router.push(`/knowledge/${kb.uuid}`)">
          <div class="flex flex-col h-full">
            <div class="flex items-start justify-between">
              <div class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 bg-nap-primary/10 text-nap-primary">
                <t-icon name="book" size="20" />
              </div>
              <t-tag shape="round" theme="success" v-if="kb.active">启用</t-tag>
              <t-tag shape="round" theme="danger" v-else >禁用</t-tag>
            </div>

            <h3 class="font-semibold text-nap-text mt-3 group-hover:text-nap-primary transition-colors">{{ kb.name }}</h3>
            <p class="text-sm text-nap-text-secondary mt-1 line-clamp-2 flex-1">{{ kb.description || '暂无描述' }}</p>

            <div class="flex items-center justify-between mt-4 pt-4 border-t border-nap-border">
              <span class="text-xs text-nap-text-secondary">{{ formatSize(kb.file_size) }}</span>
              <t-space :size="6" class="items-center">
                <span class="text-xs text-nap-text-secondary">{{ docCount(kb.uuid) }} 个文档</span>
                <t-icon name="chevron-right" size="14" class="text-nap-text-tertiary opacity-0 group-hover:opacity-100 transition-opacity" />
              </t-space>
            </div>
          </div>
        </t-card>
      </t-col>
    </t-row>

    <t-dialog v-model:visible="showCreate" header="新建知识库" placement="center" width="520px"
      :confirm-btn="{ content: '创建', loading: creating }" :cancel-btn="{}" @confirm="handleCreate">
      <t-form label-align="top">
        <t-form-item label="名称">
          <t-input v-model="createForm.name" placeholder="例如：产品文档库" />
        </t-form-item>
        <t-form-item label="描述">
          <t-textarea v-model="createForm.description" :autosize="{ minRows: 2, maxRows: 4 }" placeholder="这个知识库是做什么的？" />
        </t-form-item>
      </t-form>
    </t-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { MessagePlugin } from 'tdesign-vue-next'
import axios from 'axios'
import StatusBadge from '@/components/common/StatusBadge.vue'
import { useKnowledgeStore } from '@/stores/knowledge'

const knowledgeStore = useKnowledgeStore()

const searchQuery = ref('')
const filterByStatus = ref('all')
const showCreate = ref(false)
const creating = ref(false)
const createForm = ref({ name: '', description: '' })

const statusOptions = [
  { label: '全部状态', value: 'all' },
  { label: '启用', value: 'true' },
  { label: '禁用', value: 'false' },
]

const filteredBases = computed(() => {
  let bases = knowledgeStore.knowledgeBases
  if (filterByStatus.value !== 'all') {
    bases = bases.filter(kb => String(kb.active) == filterByStatus.value)
  }
    console.log('xxxxxxxxx', bases)

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    bases = bases.filter(kb => kb.name.toLowerCase().includes(q) || (kb.description || '').toLowerCase().includes(q))
  }
  return bases
})

const totalSizeText = computed(() => formatSize(knowledgeStore.totalSize))

function docCount(baseUuid: string) {
  return knowledgeStore.itemsByBase(baseUuid).length
}

function handleCreate() {
  if (!createForm.value.name.trim()) {
    MessagePlugin.warning('请输入知识库名称')
    return
  }
  creating.value = true
  axios
    .post('/api/v1/knowledge-bases', {
      name: createForm.value.name,
      description: createForm.value.description,
      file_size: 0,
      file_path: null,
      status: 'pending'
    })
    .then(() => {
      MessagePlugin.success('知识库创建成功')
      showCreate.value = false
      createForm.value = { name: '', description: '' }
      return knowledgeStore.fetchKnowledgeBases()
    })
    .catch(() => MessagePlugin.error('创建失败'))
    .finally(() => {
      creating.value = false
    })
}

function formatSize(bytes: number) {
  if (bytes >= 1048576) return (bytes / 1048576).toFixed(1) + ' MB'
  if (bytes === 0) return '0 B'
  return (bytes / 1024).toFixed(1) + ' KB'
}

onMounted(() => {
  knowledgeStore.fetchKnowledgeBases()
  knowledgeStore.fetchKnowledgeItems()
})
</script>
