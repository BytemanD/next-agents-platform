<template>
  <t-row>
    <t-col :span="6">
      <p class="text-sm text-nap-text-secondary mt-1">管理知识库与知识来源</p>
    </t-col>
    <t-col :span="6">
      <t-space class="flex justify-end">
        <statistic-card title="知识库总数" :value="knowledgeStore.knowledgeBases.length" unit="个" />
        <statistic-card title="文档总数" :value="knowledgeStore.totalDocs" unit="个" />
      </t-space>
    </t-col>
  </t-row>
  <t-space></t-space>
  <t-row>
    <t-col :span="12">
      <tools>
        <t-input v-model="searchQuery" placeholder="搜索知识库..." clearable class="w-64">
          <template #prefixIcon><t-icon name="search" /></template>
        </t-input>
        <t-radio-group v-model="filterByStatus" variant="default-filled">
          <t-radio-button v-for="filter in statusOptions" :key="filter.value" :value="filter.value">
            {{ filter.label }}
          </t-radio-button>
        </t-radio-group>
        <t-button @click="showCreate = true">
          <template #icon><t-icon name="add" /></template>
          新建知识库
        </t-button>
      </tools>
    </t-col>
  </t-row>
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
    <t-col v-for="kb in filteredBases" :key="kb.uuid" :xs="12" :sm="12" :md="8" :lg="4">
      <nap-card :title="kb.name" :subtitle="kb.uuid" >
        <template #actions>
          <t-space align="center">
            <t-tag shape="round" theme="success" variant="light" v-if="kb.active">启用</t-tag>
            <t-tag shape="round" theme="warning" variant="light" v-else>禁用</t-tag>
            <t-button variant="text" shape="circle" @click="$router.push(`/knowledge/${kb.uuid}`)">
              <t-icon name="link" ></t-icon>
            </t-button>
          </t-space>
        </template>
        <template #footer-left>
          <span>{{ docCount(kb.uuid) }} 个文档</span>
        </template>
        <template #footer-right>
          <t-popconfirm :content="`确定删除知识库「${kb.name}」吗？`" theme="danger" @confirm="handleDelete(kb)">
            <t-button theme="danger" variant="text"><t-icon name="delete" /></t-button>
          </t-popconfirm>
        </template>
        <p>{{ kb.description || '暂无描述' }}</p>
      </nap-card>
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
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { MessagePlugin } from 'tdesign-vue-next'
import { API } from '@/api'
import { useKnowledgeStore } from '@/stores/knowledge'

import StatisticCard from '@/components/common/StatisticCard.vue'
import Tools from '@/components/common/Tools.vue'
import NapCard from '@/components/common/NapCard.vue'

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

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    bases = bases.filter(kb => kb.name.toLowerCase().includes(q) || (kb.description || '').toLowerCase().includes(q))
  }
  return bases
})

function docCount(baseUuid: string) {
  return knowledgeStore.docCounts[baseUuid] ?? 0
}

function handleCreate() {
  if (!createForm.value.name.trim()) {
    MessagePlugin.warning('请输入知识库名称')
    return
  }
  creating.value = true
  API.createKnowledgeBase({
    name: createForm.value.name,
    description: createForm.value.description,
    active: true
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

async function handleDelete(kb: { uuid: string; name: string }) {
  try {
    await API.deleteKnowledgeBase(kb.uuid)
    MessagePlugin.success('删除成功')
    knowledgeStore.fetchKnowledgeBases()
  } catch {
    MessagePlugin.error('删除失败')
  }
}

onMounted(() => {
  knowledgeStore.fetchKnowledgeBases().then(() => knowledgeStore.fetchDocCounts())
})
</script>
