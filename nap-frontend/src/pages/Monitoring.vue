<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-nap-text-secondary mt-1">跟踪智能体运行与用量</p>
      </div>
      <t-select v-model="timeRange" :options="timeOptions" size="small" class="w-36" />
    </div>

    <t-row :gutter="[16, 16]">
      <t-col v-for="stat in stats" :key="stat.label" :xs="12" :sm="6" :lg="3">
        <t-card :bordered="true" class="settings-card">
          <p class="text-sm text-nap-text-secondary">{{ stat.label }}</p>
          <p class="text-2xl font-bold mt-1 tabular" style="font-family: var(--font-display)">{{
            stat.value }}</p>
          <p class="text-xs mt-2" :class="stat.changeClass">{{ stat.change }}</p>
        </t-card>
      </t-col>
    </t-row>

    <t-row :gutter="[16, 16]">
      <t-col :xs="24" :lg="6">
        <t-card :bordered="true" class="settings-card" title="Token 使用量" size="small">
          <div class="h-64">
            <v-chart :option="tokenChartOption" autoresize />
          </div>
        </t-card>
      </t-col>
      <t-col :xs="24" :lg="6">
        <t-card :bordered="true" title="延迟分布" size="small">
          <div class="h-64">
            <v-chart :option="latencyChartOption" autoresize />
          </div>
        </t-card>
      </t-col>
    </t-row>

    <t-card :bordered="true" class="settings-card" title="最近追踪" size="small">
      <template #actions>
        <t-input v-model="searchQuery" placeholder="搜索追踪..." size="small" clearable class="w-64" />
      </template>
      <t-table size="small" :data="traces" :columns="traceColumns" row-key="id" :pagination="{ pageSize: 10 }" hover />
    </t-card>
  </div>
</template>

<script setup lang="ts">
import { ref, h } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import StatusBadge from '@/components/common/StatusBadge.vue'

use([CanvasRenderer, LineChart, BarChart, GridComponent, TooltipComponent, LegendComponent])

const searchQuery = ref('')
const timeRange = ref('7d')

const timeOptions = [
  { label: '最近 24 小时', value: '24h' },
  { label: '最近 7 天', value: '7d' },
  { label: '最近 30 天', value: '30d' }
]

const stats = ref([
  { label: '总追踪数', value: '12,847', change: '+15.2% 较上周期', changeClass: 'text-nap-success' },
  { label: '错误率', value: '0.3%', change: '-0.1% 较上周期', changeClass: 'text-nap-success' },
  { label: '平均延迟', value: '1.2s', change: '+0.1s 较上周期', changeClass: 'text-nap-error' },
  { label: '总成本', value: '$24.50', change: '+$3.20 较上周期', changeClass: 'text-nap-error' }
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

const tokenChartOption = ref({
  backgroundColor: 'transparent',
  tooltip: { trigger: 'axis' },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: { type: 'category', data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'], axisLine: { lineStyle: { color: '#e7e9f2' } }, axisLabel: { color: '#5b6478' } },
  yAxis: { type: 'value', axisLine: { lineStyle: { color: '#e7e9f2' } }, splitLine: { lineStyle: { color: '#e7e9f2' } }, axisLabel: { color: '#5b6478' } },
  series: [
    { name: '输入 Token', type: 'bar', stack: 'total', data: [12000, 15000, 13000, 18000, 16000, 8000, 9000], itemStyle: { color: '#4f46e5', borderRadius: [4, 4, 0, 0] } },
    { name: '输出 Token', type: 'bar', stack: 'total', data: [4000, 5000, 4500, 6000, 5500, 2500, 3000], itemStyle: { color: '#c7d2fe' } }
  ]
})

const latencyChartOption = ref({
  backgroundColor: 'transparent',
  tooltip: { trigger: 'axis' },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: { type: 'category', data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'], axisLine: { lineStyle: { color: '#e7e9f2' } }, axisLabel: { color: '#5b6478' } },
  yAxis: { type: 'value', axisLine: { lineStyle: { color: '#e7e9f2' } }, splitLine: { lineStyle: { color: '#e7e9f2' } }, axisLabel: { color: '#5b6478', formatter: '{value}ms' } },
  series: [
    { name: 'P50', type: 'line', data: [800, 850, 780, 900, 820, 750, 800], itemStyle: { color: '#16a34a' }, smooth: true, areaStyle: { color: 'rgba(22, 163, 74, 0.08)' } },
    { name: 'P95', type: 'line', data: [1500, 1600, 1400, 1800, 1550, 1300, 1500], itemStyle: { color: '#d97706' }, smooth: true },
    { name: 'P99', type: 'line', data: [2500, 2800, 2200, 3200, 2600, 2000, 2500], itemStyle: { color: '#dc2626' }, smooth: true }
  ]
})
</script>

<style scoped>
.settings-card {
  background-color: var(--td-bg-color-container);
}
</style>