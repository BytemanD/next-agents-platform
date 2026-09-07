<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between nap-rise">
      <div>
        <p class="text-sm text-nap-text-secondary mt-1.5">把所有重复劳动交给智能体，你只负责决策</p>
      </div>
    </div>

    <t-row :gutter="[16, 16]">
      <t-col :xs="24" :sm="12" :xl="4">
        <t-card class="hero-stat nap-rise" size="small" :style="{ animationDelay: '0ms' }">
          <div class="flex items-start justify-between relative z-10">
            <div>
              <p class="text-sm text-white/75">{{ stats[0].label }}</p>
              <p class="text-4xl font-bold text-white mt-2 tabular" style="font-family: var(--font-display)">
                {{ stats[0].value }}
              </p>
            </div>
            <span class="inline-flex items-center gap-1 text-xs text-white rounded-full bg-white/15 px-2 py-1">
              <t-icon :name="stats[0].change >= 0 ? 'trend-up' : 'trend-down'" :size="12" />
              <span class="tabular">{{ stats[0].change >= 0 ? '+' : '' }}{{ stats[0].change }}%</span>
            </span>
          </div>
          <div class="relative z-10 mt-4">
            <svg width="100%" height="48" viewBox="0 0 260 48" fill="none" preserveAspectRatio="none" class="block">
              <defs>
                <linearGradient id="heroSpark" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="white" stop-opacity="0.28" />
                  <stop offset="100%" stop-color="white" stop-opacity="0" />
                </linearGradient>
              </defs>
              <path d="M0 38 C24 34, 40 40, 62 34 S104 22, 128 26 S176 12, 198 16 S244 8, 260 4 V48 H0 Z"
                fill="url(#heroSpark)" />
              <path d="M0 38 C24 34, 40 40, 62 34 S104 22, 128 26 S176 12, 198 16 S244 8, 260 4" stroke="white"
                stroke-width="1.6" stroke-linecap="round" />
            </svg>
          </div>
        </t-card>
      </t-col>

      <t-col v-for="(stat, i) in stats.slice(1)" :key="stat.label" :xs="12" :sm="6" :xl="2">
        <t-card :bordered="false" class="metric-card nap-rise" size="large"
          :style="{ animationDelay: `${(i + 1) * 60}ms` }"
          style="min-height: 150px; border-radius: var(--nap-radius-lg)">
          <t-statistic :title="stat.label" :value="stat.value" />
          <div class="mt-3 flex items-center gap-1 text-xs" :class="stat.changeClass">
            <t-icon :name="stat.change >= 0 ? 'trend-up' : 'trend-down'" size="14" />
            <span class="tabular">较上周 {{ stat.change >= 0 ? '+' : '' }}{{ stat.change }}%</span>
          </div>
        </t-card>
      </t-col>
    </t-row>

    <t-row :gutter="[16, 16]">
      <t-col :xs="24" :xl="16">
        <t-card :bordered="true" class="canvas-card" :class="{ 'nap-rise': true }" :style="{ animationDelay: '220ms' }">
          <div class="flex items-center justify-between mb-4">
            <div>
              <h2 class="text-base font-semibold text-nap-text leading-none">最近智能体</h2>
              <p class="text-xs text-nap-text-secondary mt-1.5">团队的智能体运行状态</p>
            </div>
            <t-button variant="text" size="small" @click="$router.push('/agents')">
              查看全部
              <t-icon name="arrow-right" size="14" class="ml-1" />
            </t-button>
          </div>

          <div class="divide-y divide-nap-border">
            <div v-for="agent in recentAgents" :key="agent.id"
              class="agent-row flex items-center gap-4 py-3.5 -mx-3 px-3 rounded-xl cursor-pointer"
              @click="$router.push(`/agents/builder/${agent.id}`)">
              <div class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0" :class="agent.avatarClass">
                <t-icon name="robot" size="18" :class="agent.avatarColor" />
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2">
                  <h3 class="font-medium text-nap-text truncate text-sm">{{ agent.name }}</h3>
                  <StatusBadge :status="agent.status" />
                </div>
                <p class="text-xs text-nap-text-secondary mt-0.5 truncate">{{ agent.description }}</p>
              </div>
              <div class="hidden md:flex items-center gap-2 flex-shrink-0">
                <span
                  class="inline-flex items-center gap-1 text-xs text-nap-text-secondary rounded-full bg-nap-surface-hover border border-nap-border px-2.5 py-1">
                  <t-icon name="cpu" :size="12" />
                  {{ agent.model }}
                </span>
                <span
                  class="inline-flex items-center gap-1 text-xs text-nap-text-secondary rounded-full bg-nap-surface-hover border border-nap-border px-2.5 py-1">
                  <t-icon name="tools" :size="12" />
                  {{ agent.tools.length }} 个工具
                </span>
              </div>
              <t-icon name="chevron-right" size="16"
                class="text-nap-text-tertiary flex-shrink-0 transition-transform group-hover:translate-x-1" />
            </div>
          </div>
        </t-card>
      </t-col>

      <t-col :xs="24" :xl="4">
        <div class="space-y-4">
          <t-card :bordered="true" class="nap-rise" :style="{ animationDelay: '300ms' }">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-base font-semibold text-nap-text leading-none">快速开始</h2>
            </div>
            <t-row :gutter="[12, 12]">
              <t-col v-for="template in templates" :key="template.name" :xs="12">
                <div
                  class="template-tile flex items-center gap-3 rounded-xl border border-nap-border p-3 cursor-pointer"
                  @click="createFromTemplate(template)">
                  <div class="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" :class="template.tint">
                    <t-icon :name="template.icon" size="16" :class="template.iconClass" />
                  </div>
                  <div class="min-w-0">
                    <h3 class="font-medium text-nap-text text-[13px] leading-none">{{ template.name }}</h3>
                    <p class="text-xs text-nap-text-secondary mt-1 truncate">{{ template.description }}</p>
                  </div>
                </div>
              </t-col>
            </t-row>
          </t-card>

        </div>
      </t-col>
      <t-col :xs="24" :xl="4">
        <t-card :bordered="true" class="nap-rise" :style="{ animationDelay: '360ms' }">
          <h2 class="text-base font-semibold text-nap-text leading-none mb-4">动态</h2>
          <div class="activity-list">
            <div v-for="(activity, i) in activities" :key="i" class="relative flex gap-3 activity-item">
              <div v-if="i < activities.length - 1" class="absolute left-[3px] top-3 bottom-0 w-px bg-nap-border" />
              <div class="w-[7px] h-[7px] rounded-full mt-1.5 flex-shrink-0 relative z-10" :class="activity.dotClass" />
              <div class="pb-4">
                <p class="text-sm text-nap-text">{{ activity.text }}</p>
                <p class="text-xs text-nap-text-secondary mt-0.5">{{ activity.time }}</p>
              </div>
            </div>
          </div>
        </t-card>
      </t-col>
    </t-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import StatusBadge from '@/components/common/StatusBadge.vue'

const router = useRouter()

const stats = ref([
  { label: '知识文档', value: '48', change: 8, icon: 'book', tint: 'bg-emerald-50', iconClass: 'text-nap-success', changeClass: 'text-nap-success' },
  { label: '会话数', value: '1,284', change: 15, icon: 'chat', tint: 'bg-nap-accent-soft', iconClass: 'text-nap-primary', changeClass: 'text-nap-success' },
  { label: '智能体总数', value: '12', change: 20 },
  { label: '总 Token 数', value: '2.4M', change: -5, icon: 'bolt', tint: 'bg-amber-50', iconClass: 'text-nap-warning', changeClass: 'text-nap-error' }
])

const recentAgents = ref([
  { id: '1', name: '研究助理', description: '协助进行研究和文献综述', model: 'gpt-4o', status: 'active', tools: ['web_search', 'file_read'], avatarClass: 'bg-nap-accent-soft', avatarColor: 'text-nap-primary' },
  { id: '2', name: '代码评审员', description: '审查代码并提供改进建议', model: 'claude-3.5', status: 'active', tools: ['code_review', 'file_read'], avatarClass: 'bg-emerald-50', avatarColor: 'text-nap-success' },
  { id: '3', name: '数据分析师', description: '分析数据并生成报告', model: 'gpt-4o', status: 'draft', tools: ['code_exec'], avatarClass: 'bg-violet-50', avatarColor: 'text-nap-secondary' },
  { id: '4', name: '内容创作者', description: '创作优质的博客和文案内容', model: 'claude-3.5', status: 'active', tools: ['web_search'], avatarClass: 'bg-amber-50', avatarColor: 'text-nap-warning' }
])

const templates = ref([
  { name: '研究专家', description: '联网深度研究', icon: 'book', tint: 'bg-nap-accent-soft', iconClass: 'text-nap-primary' },
  { name: '代码助手', description: '代码审查与生成', icon: 'code', tint: 'bg-emerald-50', iconClass: 'text-nap-success' },
  { name: '对话助手', description: '通用智能对话', icon: 'chat', tint: 'bg-violet-50', iconClass: 'text-nap-secondary' },
  { name: '任务自动化', description: '自动化重复任务', icon: 'bolt', tint: 'bg-amber-50', iconClass: 'text-nap-warning' }
])

const activities = ref([
  { text: '研究助理完成了一项任务', time: '2 分钟前', dotClass: 'bg-nap-success' },
  { text: '知识库新增了一篇文档', time: '15 分钟前', dotClass: 'bg-nap-primary' },
  { text: '代码评审员提示了一个问题', time: '1 小时前', dotClass: 'bg-nap-warning' },
  { text: '数据分析师生成了一份报告', time: '3 小时前', dotClass: 'bg-nap-secondary' }
])

function createFromTemplate(_template: any) {
  router.push('/agents/builder')
}
</script>

<style scoped>
.hero-stat {
  position: relative;
  border-radius: var(--nap-radius-lg);
  overflow: hidden;
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  box-shadow: 0 12px 32px rgba(79, 70, 229, 0.28);
}

.hero-stat::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: radial-gradient(rgba(255, 255, 255, 0.22) 1px, transparent 1px);
  background-size: 16px 16px;
  opacity: 0.45;
}

.hero-stat::after {
  content: '';
  position: absolute;
  right: -40px;
  top: -40px;
  width: 160px;
  height: 160px;
  border-radius: 9999px;
  background: rgba(255, 255, 255, 0.08);
}

.metric-card {
  background-color: var(--td-bg-color-container);
}

.canvas-card {
  background-color: var(--td-bg-color-container);
  position: relative;
}

.canvas-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: radial-gradient(#e7e9f2 1px, transparent 1px);
  background-size: 20px 20px;
  pointer-events: none;
}

.canvas-card :deep(.t-card__body) {
  position: relative;
}

.agent-row {
  transition: background-color 0.18s ease;
}

.agent-row:hover {
  background-color: var(--td-bg-color-container-hover);
}

.agent-row:hover :deep(.t-icon) {
  transform: translateX(2px);
}

.template-tile {
  background-color: var(--td-bg-color-container);
  transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s ease, border-color 0.2s ease;
}

.template-tile:hover {
  transform: translateY(-2px);
  box-shadow: var(--nap-shadow-md);
  border-color: var(--nap-border-strong);
}

.template-tile:active {
  transform: translateY(-1px) scale(0.99);
}

.activity-list :deep(.t-icon) {
  transition: transform 0.2s ease;
}
</style>