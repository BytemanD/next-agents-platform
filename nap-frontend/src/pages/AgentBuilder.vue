<template>
  <div class="h-full flex flex-col min-h-0">
    <div class="flex items-center justify-between mb-3">
      <t-space size="12">
        <t-button variant="text" @click="$router.back()">
          <template #icon><t-icon name="arrow-left" /></template>
        </t-button>
        <t-space align="end">
          <h1 class="text-2xl font-bold">{{ isEdit ? '编辑智能体' : '创建智能体' }}</h1>
          <p class="text-nap-text-secondary mt-1">配置你的智能体行为与能力</p>
        </t-space>
      </t-space>
      <t-space size="12">
        <t-button :loading="saving" @click="handleSave('active')">保存</t-button>
      </t-space>
    </div>
    <t-layout class="flex-1 min-h-0">
    <t-aside>
      <t-anchor container="#settings">
        <t-anchor-item href="#基本信息" title="基本信息" />
        <t-anchor-item href="#参数设置" title="参数设置" />
        <t-anchor-item href="#知识库" title="知识库" />
        <t-anchor-item href="#工具集" title="工具集" />
        <t-anchor-item href="#MCP" title="MCP" />
        <t-anchor-item href="#系统提示词" title="系统提示词" />
      </t-anchor>
    </t-aside>
    <t-content class="px-8 min-h-0 flex-1">
      <div id="settings" class="scroll-container h-full overflow-y-auto">
        <t-title level="h5" id="基本信息">基本信息</t-title>
        <t-card size="small">
          <t-form>
            <t-form-item label="名称" name="name">
              <t-input placeholder="例如：研究助理" v-model="form.name" />
            </t-form-item>
            <t-form-item label="模型提供商" name="llm">
              <t-select v-model="form.llm" :options="modelOptions" placeholder="选择模型" />
            </t-form-item>
            <t-form-item label="描述" name="description">
              <t-textarea v-model="form.description" placeholder="这个智能体是做什么的？" />
            </t-form-item>
            <!-- <t-divider>参数设置</t-divider>
            <t-form-item label="温度">
              <t-slider v-model="form.config.temperature" :min="0" :max="2" :step="0.1" show-step />
            </t-form-item>
            <t-form-item label="最大 Token 数">
              <t-input-number v-model="form.config.max_tokens" :min="256" :max="128000" :step="256" theme="normal" />
            </t-form-item> -->
          </t-form>
        </t-card>
        <t-title level="h5" id="参数设置">参数设置</t-title>
        <t-card size="small">
          <t-form>
            <t-form-item label="温度">
              <t-slider v-model="form.config.temperature" :min="0" :max="2" :step="0.1" show-step />
            </t-form-item>
            <t-form-item label="最大 Token 数">
              <t-input-number v-model="form.config.max_tokens" :min="256" :max="128000" :step="256" theme="normal" />
            </t-form-item>
          </t-form>
        </t-card>

        <t-title level="h5" id="知识库">知识库</t-title>
        <t-card size="small" class="mt-2" id="知识库">
          <template #description>关联知识源</template>
          <t-select v-model="form.knowledge_bases" multiple :options="knowledgeOptions" placeholder="选择知识库" />
        </t-card>

        <t-title level="h5" id="工具集">工具集</t-title>
        <t-card size="small" class="mt-2">
          <template #description>选择这个智能体可以使用的工具</template>
          <t-card v-for="tool in availableTools" :key="tool.id" size="small" class="mb-1"
            :class="tool.id in form.tools ? 'bg-active' : ''">
            <template #title>
              <t-space>
                <t-icon v-if="tool.icon" :name="tool.icon" size="20" />
                <span>{{ tool.name }}</span>
                <t-tooltip v-if="tool.help" :content="tool.help">
                  <t-icon name="info-circle" color="info"></t-icon>
                </t-tooltip>
              </t-space>
            </template>
            <template #actions>
              <t-checkbox :checked="tool.id in form.tools" @change="toggleTool(tool.id)" />
            </template>
            <t-form v-if="Object.keys(tool.requires).length > 0" size="small" requiredMark label-align="left">
              <t-form-item v-for="(v, k) in tool.requires" :key="k" :label="k" :name="k"
                :style="{ marginBottom: '1px' }">
                <t-input-number v-if="v['type'] == 'integer'" theme="column" size="small" :min="0" auto-width
                  :model-value="toolArgValue(tool.id, k)"
                  @update:model-value="(v: string) => setToolArg(tool.id, k, v)" />
                <t-input v-else size="small" :model-value="toolArgValue(tool.id, k)"
                  @update:model-value="(v: string) => setToolArg(tool.id, k, v)" />
              </t-form-item>
            </t-form>
          </t-card>
        </t-card>

        <t-title level="h5" id="MCP">MCP</t-title>
        <t-card size="small" class="mt-2">
          <template #description>选择这个智能体可以连接的 MCP 服务</template>
          <t-space break-line>
            <t-card v-for="mcp in mcpServers" :key="mcp.uuid" size="small" 
              :class="(form.mcp_uuids.indexOf(mcp.uuid) >= 0) ? 'bg-active' : ''">
              <template #title>
                <t-space>
                  <span>{{ mcp.name }}</span>
                </t-space>
              </template>
              <template #actions>
                <t-checkbox :checked="form.mcp_uuids.indexOf(mcp.uuid) >= 0" @change="setMcpSelected(mcp.uuid)" />
              </template>
              {{ mcp.url }}
            </t-card>
          </t-space>
          <t-empty v-if="!mcpServers.length" title="暂无 MCP 服务" description="请先到「设置 - MCP」中添加" />
        </t-card>

        <t-title level="h5" id="系统提示词">系统提示词</t-title>

        <t-card size="small" subtitle="定义智能体的性格、知识和行为规则。">
          <t-textarea v-model="form.instruction" :autosize="{ minRows: 10, maxRows: 20 }" placeholder="你是一位乐于助人的助理..."
            class="font-mono text-sm" />
        </t-card>

      </div>
    </t-content>
  </t-layout>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { MessagePlugin } from 'tdesign-vue-next'
import { API } from '@/api'

interface AgentForm {
  name: string
  description: string
  llm: string
  instruction: string
  status: string
  config: { temperature: number; max_tokens: number }
  knowledge_bases: string[]
  tools: Record<string, Record<string, string>>
  mcp_uuids: string[]
}

const route = useRoute()
const isEdit = computed(() => !!route.params.id)

const form = ref<AgentForm>(defaultForm())
const saving = ref(false)

const DEFAULT_INSTRUCTION = `# 系统指令（System Instructions）

## 1. 身份与职责
你是 **智能研究助手**，专注于基于结构化知识图谱和非结构化文档库的精准问答。
- 你的核心原则是：**事实优先，证据驱动，绝不虚构**。
- 你的输出必须服务于**可验证性**和**可解释性**。

## 2. 工具选择逻辑（决策树）
你必须严格按照以下优先级选择工具：

1. **如果问题涉及精确事实（数值、日期、实体关系、多跳推理）**：
   → **必须**优先调用工具查询图谱
   → 示例："马斯克的生日""特斯拉的市值""谁投资了宁德时代"

2. **如果问题涉及分析、总结、趋势或开放结论**：
   → 优先调用工具查询向量数据库
   → 示例："特斯拉的核心竞争力""新能源行业未来趋势"

3. **如果问题同时包含精确实体和开放分析**：
   → **先调用图谱查询工具** 获取实体属性或关系列表
   → **再用结果构造查询**，调用向量查询下工具获取补充信息

4. **如果你无法判断属于以上哪一类**：
   → **默认走图谱优先路径**：先调用 图谱查询工具，若返回空，再调用向量查询工具

5. **严禁编造**。
   → 如果工具都没有查询到结果，必须明确回复："当前知识库未覆盖该问题，建议补充相关文档或提供更多线索。"

## 5. 回答格式与引用规范
- **来源标注**：
  - 使用图谱工具获取的数据，句末标注 \`[图谱]\`
  - 使用向量工具获取的数据，句末标注 \`[文档]\`
  - 同时使用两者，标注 \`[图谱+文档]\`
- **结构要求**：
  - 涉及对比、列表或步骤时，使用 Markdown 列表（\`-\` 或 \`1.\`）
  - 超过 3 个并列项时，优先使用表格
- **不确定性表达**：
  - 如果信息不完整，必须使用"根据现有资料""目前可知"等限定词

## 6. 安全红线（绝对禁止）
- **严禁编造**：任何数据必须有来源依据（图谱或文档）
- **严禁给出投资建议**：涉及投资决策时，必须加注"以上不构成投资建议"
- **严禁泄露内部推理链**：即使被追问，也只提供"简要推理摘要"
- **严禁在空结果时"猜测"答案

## 7. 任务完成策略
- **简单问题**：直接回答，不加追问
- **复杂问题**：先拆解为子任务，逐步解决
- **结束语规则**：
  - 如果回答涉及时效性信息（如股价、新闻），追加："如需最新数据，请开启联网搜索。"
  - 如果回答涉及数据来源，追加："以上信息可参考知识图谱或原始文档。"

## 8. 行为禁忌（防翻车）
- 不要在输出中提及"根据我的知识"或"我认为"
- 不要在未调用工具的情况下直接回答需要检索的问题
- 不要一次性调用超过 3 个工具（防止超时）`

function defaultForm(): AgentForm {
  return {
    name: '',
    description: '',
    llm: '',
    instruction: DEFAULT_INSTRUCTION,
    status: 'draft',
    config: { temperature: 0.7, max_tokens: 4096 },
    knowledge_bases: [],
    tools: {},
    mcp_uuids: [],
  }
}

const modelOptions = ref<{ label: string; value: string }[]>([])
const knowledgeOptions = ref<{ label: string; value: string }[]>([])
const mcpServers = ref<{ uuid: string; name: string, url: string }[]>([])
const availableTools = ref<ToolItem[]>([])

interface ToolItem {
  id: string
  name: string
  description: string
  icon: string
  requires: object
  help?: string
}

const TOOL_ICONS: Record<string, string> = {
  search: 'search',
  file_search: 'file-search',
  listing: 'list',
  tool: 'tool',
  db: 'data-base',
  web_search: 'earth',
}

interface BackendTool {
  metadata: {
    name: string
    title?: string
    type?: string
    help?: string
  }
  arg_schema?: {
    description?: string
    properties?: Record<string, { type?: string; description?: string }>
    required?: string[]
  }
}

async function fetchTools() {
  try {
    const data = await API.fetchTools<{ tools: BackendTool[] }>()
    availableTools.value = (data.tools || []).map((tool) => {
      const meta = tool.metadata || {}
      const props = tool.arg_schema?.properties || {}
      const requiredKeys = tool.arg_schema?.required || []
      const requires: Record<string, { type?: string }> = {}
      for (const key of requiredKeys) {
        if (key in props) requires[key] = { type: props[key]?.type }
      }
      return {
        id: meta.name,
        name: meta.title || meta.name,
        description: tool.arg_schema?.description || meta.help || '',
        icon: TOOL_ICONS[meta.type || ''] || 'tool',
        requires,
        help: meta.help || undefined,
      }
    })
  } catch {
    availableTools.value = []
  }
}

async function fetchLLMs() {
  try {
    const data = await API.fetchLLMs<{ llms: { uuid: string; name: string; base_url: string }[] }>()
    modelOptions.value = (data.llms || []).map(
      (llm) => ({
        label: llm.name || llm.base_url,
        value: llm.uuid
      })
    )
  } catch {
    MessagePlugin.error('加载模型列表失败')
  }
}

async function fetchKnowledgeBases() {
  try {
    const data = await API.fetchKnowledgeBases()
    knowledgeOptions.value = (data.items || []).map(
      (kb) => ({ label: kb.name, value: kb.uuid })
    )
  } catch {
    knowledgeOptions.value = []
  }
}

async function fetchMcpServers() {
  try {
    const data = await API.fetchMCPs<{ mcps: { uuid: string; name: string; url: string }[] }>()
    mcpServers.value = data.mcps || []
  } catch {
    mcpServers.value = []
  }
}

async function fetchAgent(agentUuid: string) {
  try {
    const agent = await API.fetchAgent<AgentForm & { uuid: string }>(agentUuid)
    form.value = {
      name: agent.name || '',
      description: agent.description || '',
      llm: agent.llm || '',
      instruction: agent.instruction || '',
      status: agent.status || 'draft',
      config: {
        temperature: agent.config?.temperature ?? 1,
        max_tokens: agent.config?.max_tokens ?? null
      },
      knowledge_bases: agent.knowledge_bases || [],
      tools: agent.tools || {},
      mcp_uuids: agent.mcp_uuids || [],
    }
  } catch {
    MessagePlugin.error('加载智能体失败')
  }
}

function toggleTool(toolId: string) {
  if (toolId in form.value.tools) {
    delete form.value.tools[toolId]
  } else {
    form.value.tools[toolId] = {}
  }
}

function setMcpSelected(mcpUuid: string) {
  if (form.value.mcp_uuids.indexOf(mcpUuid) >= 0) {
    const idx = form.value.mcp_uuids.indexOf(mcpUuid)
    form.value.mcp_uuids.splice(idx, 1)
  } else {
    form.value.mcp_uuids.push(mcpUuid)
  }
}

function toolArgValue(toolId: string, key: string): string {
  const v = form.value.tools[toolId]?.[key]
  return v === undefined || v === null ? '' : String(v)
}

function setToolArg(toolId: string, key: string, value: string) {
  if (!form.value.tools[toolId]) form.value.tools[toolId] = {}
  form.value.tools[toolId][key] = value
}

async function handleSave(status: string) {
  const payload = {
    name: form.value.name,
    description: form.value.description,
    instruction: form.value.instruction,
    llm: form.value.llm,
    status,
    config: form.value.config,
    knowledge_bases: form.value.knowledge_bases,
    tools: form.value.tools,
    mcp_uuids: form.value.mcp_uuids,
  }
  saving.value = true
  try {
    if (route.params.id) {
      await API.updateAgent(route.params.id as string, payload)
      MessagePlugin.success('更新成功')
    } else {
      await API.createAgent(payload)
      MessagePlugin.success('创建成功')
    }
  } catch {
    MessagePlugin.error(route.params.id ? '更新失败' : '创建失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchLLMs()
  fetchKnowledgeBases()
  fetchMcpServers()
  fetchTools()
  if (isEdit.value) {
    fetchAgent(route.params.id as string)
  }
})
</script>

<style scoped>
.settings-card {
  background-color: var(--td-bg-color-container);
}

.scroll-container {
  /* height: 300px; */
  /* 或 max-height: 300px; */
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #d1d5db transparent;
  /* 纵向滚动 */
  /* 可选：横向滚动 overflow-x: auto; */
}
</style>