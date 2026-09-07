<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <t-space :size="12">
        <t-button variant="outline" @click="$router.back()">
          <template #icon><t-icon name="arrow-left" /></template>
        </t-button>
        <div>
          <h1 class="text-2xl font-bold text-nap-text">{{ isEdit ? '编辑智能体' : '创建智能体' }}</h1>
          <p class="text-nap-text-secondary mt-1">配置你的智能体行为与能力</p>
        </div>
      </t-space>
      <t-space :size="12">
        <t-button @click="handleSave('draft')">保存草稿</t-button>
        <t-button @click="handleSave('active')">发布</t-button>
      </t-space>
    </div>

    <t-row :gutter="[24, 24]">
      <t-col :xs="24" :lg="16">
        <t-space direction="vertical" size="24" style="width: 100%">
          <t-card :bordered="true" class="settings-card">
            <template #title><span class="text-nap-text">基本信息</span></template>
            <t-row :gutter="16">
              <t-col :xs="24" :sm="12">
                <t-form-item label="智能体名称">
                  <t-input v-model="form.name" placeholder="例如：研究助理" />
                </t-form-item>
              </t-col>
              <t-col :xs="24" :sm="12">
                <t-form-item label="模型">
                  <t-select v-model="form.model" :options="modelOptions" placeholder="选择模型" />
                </t-form-item>
              </t-col>
            </t-row>
            <t-form-item label="描述">
              <t-textarea v-model="form.description" :autosize="{ minRows: 2, maxRows: 4 }" placeholder="这个智能体是做什么的？" />
            </t-form-item>
          </t-card>

          <t-card :bordered="true" class="settings-card">
            <template #title><span class="text-nap-text">系统提示词</span></template>
            <t-textarea v-model="form.systemPrompt" :autosize="{ minRows: 10, maxRows: 20 }"
              placeholder="你是一位乐于助人的助理..." class="font-mono text-sm" />
            <p class="text-xs text-nap-text-secondary mt-2">定义智能体的性格、知识和行为规则。</p>
          </t-card>

          <t-card :bordered="true" class="settings-card">
            <template #title><span class="text-nap-text">参数设置</span></template>
            <t-row :gutter="16">
              <t-col :xs="24" :sm="12">
                <t-form-item label="温度">
                  <t-slider v-model="form.temperature" :min="0" :max="2" :step="0.1" show-step />
                </t-form-item>
              </t-col>
              <t-col :xs="24" :sm="12">
                <t-form-item label="最大 Token 数">
                  <t-input-number v-model="form.maxTokens" :min="256" :max="128000" :step="256" theme="normal" />
                </t-form-item>
              </t-col>
            </t-row>
          </t-card>
        </t-space>
      </t-col>

      <t-col :xs="24" :lg="8">
        <t-space direction="vertical" size="24" style="width: 100%">
          <t-card :bordered="true" class="settings-card">
            <template #title><span class="text-nap-text">工具</span></template>
            <template #description><span class="text-nap-text-secondary">选择这个智能体可以使用的工具</span></template>
            <t-space direction="vertical" :size="8" style="width: 100%">
              <div v-for="tool in availableTools" :key="tool.id"
                class="flex items-center justify-between p-3 rounded-lg border border-nap-border hover:border-nap-primary/30 transition-colors cursor-pointer"
                :class="form.tools.includes(tool.id) ? 'border-nap-primary/50 bg-nap-primary/5' : ''"
                @click="toggleTool(tool.id)">
                <div class="flex items-center gap-3">
                  <t-icon :name="tool.icon" class="text-nap-text-secondary" />
                  <div>
                    <p class="text-sm font-medium text-nap-text">{{ tool.name }}</p>
                    <p class="text-xs text-nap-text-secondary">{{ tool.description }}</p>
                  </div>
                </div>
                <t-checkbox :checked="form.tools.includes(tool.id)" />
              </div>
            </t-space>
          </t-card>

          <t-card :bordered="true" class="settings-card">
            <template #title><span class="text-nap-text">知识库</span></template>
            <template #description><span class="text-nap-text-secondary">关联知识源</span></template>
            <t-select v-model="form.knowledgeBaseIds" multiple :options="knowledgeOptions" placeholder="选择知识库" />
          </t-card>
        </t-space>
      </t-col>
    </t-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)

const form = ref({
  name: '',
  description: '',
  model: null as string | null,
  systemPrompt: '',
  temperature: 0.7,
  maxTokens: 4096,
  tools: [] as string[],
  knowledgeBaseIds: [] as string[]
})

const modelOptions = [
  { label: 'GPT-4o', value: 'gpt-4o' },
  { label: 'GPT-4o Mini', value: 'gpt-4o-mini' },
  { label: 'Claude 3.5 Sonnet', value: 'claude-3.5-sonnet' },
  { label: 'Claude 3 Opus', value: 'claude-3-opus' },
  { label: 'Llama 3.1 70B', value: 'llama-3.1-70b' },
  { label: 'DeepSeek V3', value: 'deepseek-v3' }
]

const availableTools = [
  { id: 'web_search', name: '联网搜索', description: '搜索互联网', icon: 'search' },
  { id: 'code_exec', name: '代码执行', description: '运行 Python 代码', icon: 'code' },
  { id: 'file_read', name: '文件读取', description: '读取文件与文档', icon: 'file' },
  { id: 'file_write', name: '文件写入', description: '创建和编辑文件', icon: 'edit' },
  { id: 'database', name: '数据库查询', description: '查询数据库', icon: 'database' },
  { id: 'api_call', name: 'API 调用', description: '发起 HTTP 请求', icon: 'link' }
]

const knowledgeOptions = [
  { label: '我的文档', value: 'kb-1' },
  { label: '代码库', value: 'kb-2' },
  { label: '研究论文', value: 'kb-3' }
]

function toggleTool(toolId: string) {
  const idx = form.value.tools.indexOf(toolId)
  if (idx >= 0) {
    form.value.tools.splice(idx, 1)
  } else {
    form.value.tools.push(toolId)
  }
}

function handleSave(status: string) {
  console.log('保存智能体:', { ...form.value, status })
  router.push('/agents')
}

onMounted(() => {
  if (isEdit.value) {
    form.value = {
      name: '研究助理',
      description: '协助进行研究和文献综述',
      model: 'gpt-4o',
      systemPrompt: '你是一位乐于助人的研究助理...',
      temperature: 0.7,
      maxTokens: 4096,
      tools: ['web_search', 'file_read'],
      knowledgeBaseIds: ['kb-1']
    }
  }
})
</script>

<style scoped>
.settings-card {
  background-color: var(--td-bg-color-container);
}
</style>