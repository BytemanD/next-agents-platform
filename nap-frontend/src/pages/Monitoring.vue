<template>
  <t-row class="my-2">
    <t-col :span="6"></t-col>
    <t-col :span="6">
      <t-space class="flex justify-right">
        <t-select v-model="selectedAgentId" :options="agentOptions" clearable class="w-44" placeholder="全部智能体" />
        <t-select v-model="selectedModel" :options="modelOptions" clearable class="w-44" placeholder="全部模型" />
        <t-select v-model="timeRange" :options="timeOptions" class="w-36" />
      </t-space>
    </t-col>
  </t-row>
  <t-row :gutter="[16, 16]">
    <t-col v-for="stat in stats" :key="stat.label" :xs="12" :sm="6" :lg="3">
      <statistic-card :value="stat.value" :title="stat.label" />
    </t-col>
  </t-row>

  <t-row :gutter="[14, 14]" class="my-2">
    <t-col :xs="12" :lg="6">
      <t-card :bordered="true" title="Token 使用量" size="small">
        <div class="h-64">
          <v-chart :option="tokenChartOption" autoresize />
        </div>
      </t-card>
    </t-col>
    <t-col :xs="12" :lg="6">
      <t-card :bordered="true" title="延迟分布" size="small">
        <div class="h-64">
          <v-chart :option="latencyChartOption" autoresize />
        </div>
      </t-card>
    </t-col>
    <t-col :span="12">
      <t-card :bordered="true" class="settings-card" title="最近追踪" size="small">
        <template #actions>
          <t-input v-model="searchQuery" placeholder="搜索追踪..." size="small" clearable class="w-64" />
        </template>
        <t-table size="small" :data="traces" :columns="traceColumns" row-key="id" :pagination="{ pageSize: 10 }"
          hover />
      </t-card>
    </t-col>
  </t-row>

</template>

<script setup lang="ts">
import { ref, h, watch, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import StatusBadge from '@/components/common/StatusBadge.vue'
import { API } from '@/api'
import StatisticCard from '@/components/common/StatisticCard.vue';

use([CanvasRenderer, LineChart, BarChart, GridComponent, TooltipComponent, LegendComponent])

interface TokenUsage {
  days: string[]
  prompt: number[]
  completion: number[]
  total_prompt: number
  total_completion: number
  total_tokens: number
  total_calls: number
}

interface LatencyUsage {
  days: string[]
  p50: number[]
  p95: number[]
  p99: number[]
}

const searchQuery = ref('')
const timeRange = ref('7d')
const selectedAgentId = ref<string | null>(null)
const agentOptions = ref<{ label: string; value: string }[]>([])
const selectedModel = ref<string | null>(null)
const modelOptions = ref<{ label: string; value: string }[]>([])
const tokenUsage = ref<TokenUsage>({
  days: [], prompt: [], completion: [],
  total_prompt: 0, total_completion: 0, total_tokens: 0, total_calls: 0
})
const latencyUsage = ref<LatencyUsage>({ days: [], p50: [], p95: [], p99: [] })

const timeOptions = [
  { label: '最近 24 小时', value: '1d' },
  { label: '最近 7 天', value: '7d' },
  { label: '最近 30 天', value: '30d' }
]

const stats = ref([
  { label: '总调用次数', value: 0 },
  { label: '输入 Token', value: 0 },
  { label: '输出 Token', value: 0 },
  { label: '总 Token', value: 0 }
])

const traces = ref([
  { id: 'tr-001', agent: '研究助理', status: 'success', tokens: 1250, cost: 0.003, duration: 1200, createdAt: '2 分钟前' },
  { id: 'tr-002', agent: '代码评审员', status: 'success', tokens: 890, cost: 0.002, duration: 800, createdAt: '5 分钟前' },
  { id: 'tr-003', agent: '研究助理', status: 'error', tokens: 0, cost: 0, duration: 150, createdAt: '12 分钟前' },
  { id: 'tr-004', agent: '数据分析师', status: 'success', tokens: 2100, cost: 0.005, duration: 2100, createdAt: '1 小时前' }
])

const traceColumns = [
  { colKey: 'id', title: 'ID', width: 100 },
  { colKey: 'agent', title: '智能体' },
  {
    colKey: 'status', title: '状态', width: 100, cell: (_row: any, rowIndex: number) => {
      const trace = traces.value[rowIndex]
      return trace ? h(StatusBadge, { status: trace.status }) : ''
    }
  },
  { colKey: 'tokens', title: 'Token 数', width: 100 },
  {
    colKey: 'cost', title: '成本', width: 100, cell: (_row: any, rowIndex: number) => {
      const trace = traces.value[rowIndex]
      return trace ? `$${trace.cost.toFixed(3)}` : ''
    }
  },
  {
    colKey: 'duration', title: '耗时', width: 100, cell: (_row: any, rowIndex: number) => {
      const trace = traces.value[rowIndex]
      return trace ? `${trace.duration}ms` : ''
    }
  },
  { colKey: 'createdAt', title: '时间', width: 120 }
]

const tokenChartOption = ref<any>({
  backgroundColor: 'transparent',
  tooltip: { trigger: 'axis' },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: { type: 'category', data: [], axisLine: { lineStyle: { color: '#e7e9f2' } }, axisLabel: { color: '#5b6478' } },
  yAxis: { type: 'value', axisLine: { lineStyle: { color: '#e7e9f2' } }, splitLine: { lineStyle: { color: '#e7e9f2' } }, axisLabel: { color: '#5b6478' } },
  series: [
    { name: '输入 Token', type: 'bar', stack: 'total', data: [], itemStyle: { color: '#296266', borderRadius: [0, 0, 0, 0] } },
    { name: '输出 Token', type: 'bar', stack: 'total', data: [], itemStyle: { color: '#a8824a', borderRadius: [8, 8, 0, 0] } }
  ]
})

const loadTokenUsage = async () => {
  const days = timeRange.value === '1d' ? 1 : timeRange.value === '30d' ? 30 : 7
  try {
    const data = await API.fetchTokenUsage<TokenUsage>(days, selectedAgentId.value || undefined, selectedModel.value || undefined)
    tokenUsage.value = data
    tokenChartOption.value.xAxis.data = data.days
    tokenChartOption.value.series[0].data = data.prompt
    tokenChartOption.value.series[1].data = data.completion
    stats.value = [
      { label: '总调用次数', value: data.total_calls },
      { label: '输入 Token', value: data.total_prompt },
      { label: '输出 Token', value: data.total_completion },
      { label: '总 Token', value: data.total_tokens }
    ]
  } catch (e) {
    console.error('load token usage failed', e)
  }
}

const loadMetrics = () => {
  loadTokenUsage()
  loadLatency()
}

watch(timeRange, loadMetrics)
watch(selectedAgentId, loadMetrics)
watch(selectedModel, loadMetrics)
onMounted(loadMetrics)

const loadAgents = async () => {
  try {
    const data = await API.fetchAgents<{ agents: { uuid: string; name: string; status: string }[] }>()
    agentOptions.value = (data.agents || [])
      .filter(a => a.status === 'active')
      .map(a => ({ label: a.name, value: a.uuid }))
  } catch {
    agentOptions.value = []
  }
}
onMounted(loadAgents)

const loadModels = async () => {
  try {
    const data = await API.fetchMonitoringModels<{ models: string[] }>()
    modelOptions.value = (data.models || [])
      .filter(Boolean)
      .map(m => ({ label: m, value: m }))
  } catch {
    modelOptions.value = []
  }
}
onMounted(loadModels)

const loadLatency = async () => {
  const days = timeRange.value === '1d' ? 1 : timeRange.value === '30d' ? 30 : 7
  try {
    const data = await API.fetchLatency<LatencyUsage>(days, selectedAgentId.value || undefined, selectedModel.value || undefined)
    latencyUsage.value = data
    latencyChartOption.value.xAxis.data = data.days
    latencyChartOption.value.series[0].data = data.p50
    latencyChartOption.value.series[1].data = data.p95
    latencyChartOption.value.series[2].data = data.p99
  } catch (e) {
    console.error('load latency failed', e)
  }
}

const latencyChartOption = ref<any>({
  backgroundColor: 'transparent',
  tooltip: { trigger: 'axis' },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: { type: 'category', data: [], axisLine: { lineStyle: { color: '#e7e9f2' } }, axisLabel: { color: '#5b6478' } },
  yAxis: { type: 'value', axisLine: { lineStyle: { color: '#e7e9f2' } }, splitLine: { lineStyle: { color: '#e7e9f2' } }, axisLabel: { color: '#5b6478', formatter: '{value}ms' } },
  series: [
    { name: 'P50', type: 'line', data: [], itemStyle: { color: '#16a34a' }, smooth: true, areaStyle: { color: 'rgba(22, 163, 74, 0.08)' } },
    { name: 'P95', type: 'line', data: [], itemStyle: { color: '#d97706' }, smooth: true },
    { name: 'P99', type: 'line', data: [], itemStyle: { color: '#dc2626' }, smooth: true }
  ]
})
</script>

<style scoped>
.settings-card {
  background-color: var(--td-bg-color-container);
}
</style>