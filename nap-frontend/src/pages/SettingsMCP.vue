<template>
    <t-loading :loading="listLoading" size="small">
        <t-row :gutter="12">
            <t-col v-for="server in mcpServers" :key="server.uuid" :xs="24" :sm="12" :md="8" :xl="6">
                <t-card :title="server.name || server.url" size="small" :bordered="true">
                    <t-form :ref="(el: any) => setFormRef(server.uuid, el)" :data="server" :rules="formRules"
                        size="small" :disabled="editingUuid !== server.uuid">
                        <t-form-item label="名称" name="name">
                            <t-input v-model="server.name" placeholder="如：weather" />
                        </t-form-item>
                        <t-form-item label="服务地址" name="url">
                            <t-input v-model="server.url" placeholder="http://localhost:8000/mcp" />
                        </t-form-item>
                        <t-form-item label="协议" name="transport">
                            <t-select v-model="server.transport" :options="transportOptions" />
                        </t-form-item>
                        <t-form-item label="API Key" name="api_key" help="本地 MCP 服务可留空">
                            <t-input v-model="server.api_key" placeholder="认证密钥（可选）" type="password" />
                        </t-form-item>
                    </t-form>
                    <template #actions>
                        <template v-if="editingUuid === server.uuid">
                            <t-button size="small" theme="primary" variant="text" :loading="savingUuid === server.uuid"
                                @click="saveItem(server)"><t-icon name="check"></t-icon></t-button>
                            <t-button size="small" variant="text" @click="cancelEdit"><t-icon
                                    name="close"></t-icon></t-button>
                        </template>
                        <template v-else>
                            <t-button size="small" variant="text" :disabled="!!editingUuid"
                                @click="startEdit(server)"><t-icon name="edit"></t-icon></t-button>
                            <t-popconfirm content="确认删除该 MCP 服务？" @confirm="handleDelete(server)">
                                <t-button theme="danger" size="small" variant="text" :disabled="!!editingUuid"><t-icon
                                        name="delete"></t-icon></t-button>
                            </t-popconfirm>
                        </template>
                    </template>
                </t-card>
            </t-col>

            <t-col v-if="creating" :xs="24" :sm="12" :md="8" :xl="6">
                <t-card title="添加 MCP 服务" size="small" :bordered="true">
                    <t-form :ref="(el: any) => setFormRef(CREATE_KEY, el)" :data="draft" :rules="formRules">
                        <t-form-item label="名称" name="name">
                            <t-input v-model="draft.name" placeholder="如：weather" />
                        </t-form-item>
                        <t-form-item label="服务地址" name="url">
                            <t-input v-model="draft.url" placeholder="http://localhost:8000/mcp" />
                        </t-form-item>
                        <t-form-item label="Transport" name="transport">
                            <t-select v-model="draft.transport" :options="transportOptions" />
                        </t-form-item>
                        <t-form-item label="API Key" name="api_key" help="本地 MCP 服务可留空">
                            <t-input v-model="draft.api_key" placeholder="认证密钥（可选）" type="password" />
                        </t-form-item>
                    </t-form>
                    <template #actions>
                        <t-button size="small" theme="primary" variant="text" :loading="submitting"
                            @click="saveDraft"><t-icon name="check"></t-icon></t-button>
                        <t-button size="small" variant="text" @click="cancelCreate"><t-icon
                                name="close"></t-icon></t-button>
                    </template>
                </t-card>
            </t-col>
        </t-row>
        <t-empty v-if="!listLoading && !mcpServers.length && !creating" title="暂无 MCP 服务" description="点击下方按钮添加">
        </t-empty>
    </t-loading>

    <t-col :xs="24" :sm="12" :md="8" :xl="6" class="mt-4">
        <t-button variant="dashed" :disabled="creating || !!editingUuid" @click="startCreate">
            <template #icon><t-icon name="add" /></template>
            添加MCP服务
        </t-button>
    </t-col>
</template>

<script setup lang="ts">
import { API, type MCPPayload } from '@/api'
import { MessagePlugin } from 'tdesign-vue-next'
import { onMounted, ref } from 'vue'

interface MCPServer extends MCPPayload {
    uuid: string
}

const DEFAULT_TRANSPORT = 'streamable_http'
const CREATE_KEY = '__create__'

const transportOptions = [
    { label: 'Streamable HTTP', value: 'streamable_http' },
    { label: 'SSE', value: 'sse' },
]

const formRules = {
    name: [{ required: true, message: '请填写名称', type: 'error' }],
    url: [{ required: true, message: '请填写服务地址', type: 'error' }],
}

const mcpServers = ref<MCPServer[]>([])
const listLoading = ref(false)

const editingUuid = ref('')
const savingUuid = ref('')
const submitting = ref(false)
const creating = ref(false)

function emptyDraft(): MCPPayload {
    return { name: '', url: '', transport: DEFAULT_TRANSPORT, api_key: '' }
}
const draft = ref<MCPPayload>(emptyDraft())

// 每张卡片一个 form 实例，用 uuid 索引
const formRefs: Record<string, any> = {}
function setFormRef(key: string, el: any) {
    if (el) formRefs[key] = el
    else delete formRefs[key]
}

async function validate(key: string): Promise<boolean> {
    const result = await formRefs[key]?.validate().catch(() => false)
    return result === true
}

async function fetchMCPs() {
    listLoading.value = true
    try {
        const data = await API.fetchMCPs<{ mcps: MCPServer[] }>()
        mcpServers.value = (data.mcps || []).map(m => ({
            ...m,
            transport: m.transport || DEFAULT_TRANSPORT,
            api_key: m.api_key || ''
        }))
    } catch {
        MessagePlugin.error('加载 MCP 服务列表失败')
    } finally {
        listLoading.value = false
    }
}

onMounted(fetchMCPs)

function toPayload(item: MCPPayload): MCPPayload {
    return {
        name: item.name.trim(),
        url: item.url.trim(),
        transport: item.transport,
        api_key: item.api_key?.trim() || null
    }
}

function startEdit(item: MCPServer) {
    editingUuid.value = item.uuid
}

function cancelEdit() {
    editingUuid.value = ''
    // 从服务端重新拉取，丢弃未保存的改动
    fetchMCPs()
}

async function saveItem(item: MCPServer) {
    if (!(await validate(item.uuid))) return

    savingUuid.value = item.uuid
    try {
        await API.updateMCP(item.uuid, toPayload(item))
        MessagePlugin.success('更新成功')
        editingUuid.value = ''
        await fetchMCPs()
    } catch {
        MessagePlugin.error('更新失败')
    } finally {
        savingUuid.value = ''
    }
}

function startCreate() {
    draft.value = emptyDraft()
    creating.value = true
}

function cancelCreate() {
    creating.value = false
}

async function saveDraft() {
    if (!(await validate(CREATE_KEY))) return

    submitting.value = true
    try {
        await API.createMCP(toPayload(draft.value))
        MessagePlugin.success('创建成功')
        creating.value = false
        await fetchMCPs()
    } catch {
        MessagePlugin.error('创建失败')
    } finally {
        submitting.value = false
    }
}

async function handleDelete(item: MCPServer) {
    try {
        await API.deleteMCP(item.uuid)
        MessagePlugin.success('删除成功')
        await fetchMCPs()
    } catch {
        MessagePlugin.error('删除失败')
    }
}
</script>