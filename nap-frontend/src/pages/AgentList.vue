<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-sm text-nap-text-secondary mt-1">管理你的 AI 智能体</p>
      </div>
      <t-space :size="12">
        <t-input v-model="searchQuery" placeholder="搜索智能体..." clearable class="w-64">
          <template #prefixIcon><t-icon name="search" /></template>
        </t-input>
        <t-button @click="$router.push('/agents/builder')">
          <template #icon><t-icon name="add" /></template>
          新建智能体
        </t-button>
      </t-space>
    </div>

    <t-radio-group v-model="activeFilter" variant="default-filled">
      <t-radio-button v-for="filter in filters" :key="filter.value" :value="filter.value">
        {{ filter.label }}
      </t-radio-button>
    </t-radio-group>

    <t-row :gutter="[16, 16]">
      <t-col v-for="agent in filteredAgents" :key="agent.id" :xs="12" :sm="12" :md="6">
        <t-card class="card-hover cursor-pointer group" :bordered="true"
          @click="$router.push(`/agents/builder/${agent.id}`)">
          <div class="flex items-start justify-between">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                :class="agent.status === 'active' ? 'bg-emerald-50' : 'bg-amber-50'">
                <t-icon name="robot" size="20"
                  :class="agent.status === 'active' ? 'text-nap-success' : 'text-nap-warning'" />
              </div>
              <div>
                <h3 class="font-semibold text-nap-text group-hover:text-nap-primary transition-colors">{{ agent.name }}
                </h3>
                <p class="text-sm text-nap-text-secondary">{{ agent.model }}</p>
              </div>
            </div>
            <StatusBadge :status="agent.status" />
          </div>

          <p class="text-sm text-nap-text-secondary mt-4 line-clamp-2">{{ agent.description }}</p>

          <t-space :size="8" class="mt-4">
            <t-tag v-for="tool in agent.tools.slice(0, 3)" :key="tool" size="small" variant="light-outline">
              {{ tool }}
            </t-tag>
            <t-tag v-if="agent.tools.length > 3" size="small" variant="light">
              +{{ agent.tools.length - 3 }}
            </t-tag>
          </t-space>

          <div class="flex items-center justify-between mt-4 pt-4 border-t border-nap-border">
            <span class="text-xs text-nap-text-secondary">{{ formatDate(agent.updatedAt) }}</span>
            <t-space :size="4" class="opacity-0 group-hover:opacity-100 transition-opacity">
              <t-button size="small" variant="text" @click.stop="handleChat()">
                <template #icon><t-icon name="chat" /></template>
              </t-button>
              <t-button theme="danger" size="small" variant="text" @click.stop="handleDelete(agent)">
                <template #icon><t-icon name="delete" /></template>
              </t-button>
            </t-space>
          </div>
        </t-card>
      </t-col>
    </t-row>

    <t-empty v-if="filteredAgents.length === 0" class="py-20">
      <template #description>
        <p class="text-nap-text">未找到智能体</p>
        <p class="text-sm text-nap-text-secondary mt-1">创建你的第一个智能体开始使用</p>
        <t-button size="small" class="mt-4" @click="$router.push('/agents/builder')">
          创建智能体
        </t-button>
      </template>
      <template #image>
        <t-icon name="robot" size="48" class="text-nap-text-tertiary" />
      </template>
    </t-empty>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import StatusBadge from '@/components/common/StatusBadge.vue'
import { useAgentStore } from '@/stores/agent'

const router = useRouter()
const agentStore = useAgentStore()
const searchQuery = ref('')
const activeFilter = ref('all')

const filters = computed(() => [
  { label: '全部', value: 'all' },
  { label: '已上线', value: 'active' },
  { label: '草稿', value: 'draft' }
])

const filteredAgents = computed(() => {
  let agents = agentStore.agents
  if (activeFilter.value !== 'all') {
    agents = agents.filter(a => a.status === activeFilter.value)
  }
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    agents = agents.filter(a => a.name.toLowerCase().includes(q) || a.description.toLowerCase().includes(q))
  }
  return agents
})

function formatDate(dateStr: string) {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  if (days === 0) return '今天更新'
  if (days === 1) return '昨天更新'
  return `${days} 天前更新`
}

function handleChat() {
  router.push('/playground')
}

function handleDelete(agent: any) {
  console.log('删除智能体:', agent.id)
}

onMounted(() => {
  agentStore.fetchAgents()
})
</script>