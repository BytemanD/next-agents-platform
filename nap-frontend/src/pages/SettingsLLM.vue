<template>
    <t-loading :loading="listLoading" size="small">
        <t-row :gutter="12">
            <t-col v-for="endpoint in endpoints" :key="endpoint.uuid" :xs="24" :sm="12" :md="8" :xl="6">
                <t-card :title="endpoint.name || endpoint.base_url" size="small" :bordered="true">
                    <t-form :ref="(el: any) => setFormRef(endpoint.uuid, el)" :data="endpoint" :rules="formRules"
                        :disabled="editingUuid !== endpoint.uuid">
                        <t-form-item label="名称" name="name">
                            <t-input v-model="endpoint.name" placeholder="OpenAI" />
                        </t-form-item>
                        <t-form-item label="Base URL" name="base_url">
                            <t-input v-model="endpoint.base_url" placeholder="https://api.openai.com/v1" />
                        </t-form-item>
                        <t-form-item label="API Key" name="api_key">
                            <t-input v-model="endpoint.api_key" placeholder="sk-..." type="password" />
                        </t-form-item>
                        <t-form-item label="模型" name="models" help="输入模型名后回车添加">
                            <t-tag-input v-model="endpoint.models" :disabled="editingUuid !== endpoint.uuid"
                                placeholder="如 gpt-4o" />
                        </t-form-item>
                    </t-form>
                    <template #actions>
                        <template v-if="editingUuid === endpoint.uuid">
                            <t-button size="small" theme="primary" variant="text"
                                :loading="savingUuid === endpoint.uuid" @click="saveItem(endpoint)"><t-icon
                                    name="check"></t-icon></t-button>
                            <t-button size="small" variant="text" @click="cancelEdit"><t-icon
                                    name="close"></t-icon></t-button>
                        </template>
                        <template v-else>
                            <t-button size="small" variant="text" :disabled="!!editingUuid"
                                @click="startEdit(endpoint)"><t-icon name="edit"></t-icon></t-button>
                            <t-popconfirm content="确认删除该模型？" @confirm="handleDelete(endpoint)">
                                <t-button theme="danger" size="small" variant="text" :disabled="!!editingUuid"><t-icon
                                        name="delete"></t-icon></t-button>
                            </t-popconfirm>
                        </template>
                    </template>
                </t-card>
            </t-col>

            <t-col v-if="creating" :xs="24" :sm="12" :md="8" :xl="6">
                <t-card title="添加模型" size="small" :bordered="true">
                    <t-form :ref="(el: any) => setFormRef(CREATE_KEY, el)" :data="draft" :rules="formRules">
                        <t-form-item label="名称" name="name">
                            <t-input v-model="draft.name" placeholder="OpenAI" />
                        </t-form-item>
                        <t-form-item label="Base URL" name="base_url">
                            <t-input v-model="draft.base_url" placeholder="https://api.openai.com/v1" />
                        </t-form-item>
                        <t-form-item label="API Key" name="api_key">
                            <t-input v-model="draft.api_key" placeholder="sk-..." type="password" />
                        </t-form-item>
                        <t-form-item label="模型" name="models" help="输入模型名后回车添加">
                            <t-tag-input v-model="draft.models" placeholder="如 gpt-4o" />
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
        <t-empty v-if="!listLoading && !endpoints.length && !creating" title="暂无模型配置" description="点击下方按钮添加">
        </t-empty>
    </t-loading>

    <t-col :xs="24" :sm="12" :md="8" :xl="6" class="mt-4">
        <t-button variant="dashed" :disabled="creating || !!editingUuid" @click="startCreate">
            <template #icon><t-icon name="add" /></template>
            添加模型
        </t-button>
    </t-col>
</template>

<script setup lang="ts">
import { API, type LLMPayload } from '@/api'
import { MessagePlugin } from 'tdesign-vue-next'
import { onMounted, ref } from 'vue'

interface APIEndpoint extends LLMPayload {
    uuid: string
}

const CREATE_KEY = '__create__'

const formRules = {
    base_url: [{ required: true, message: '请填写 Base URL', type: 'error' }],
    api_key: [{ required: true, message: '请填写 API Key', type: 'error' }],
    models: [{
        validator: (val: unknown) => Array.isArray(val) && val.some(m => m.trim().length > 0),
        message: '请至少添加一个模型',
        type: 'error'
    }]
}

const endpoints = ref<APIEndpoint[]>([])
const listLoading = ref(false)

const editingUuid = ref('')
const savingUuid = ref('')
const submitting = ref(false)
const creating = ref(false)

function emptyDraft(): LLMPayload {
    return { name: '', base_url: '', api_key: '', models: [] }
}
const draft = ref<LLMPayload>(emptyDraft())

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

async function fetchLLMs() {
    listLoading.value = true
    try {
        const data = await API.fetchLLMs<{ llms: APIEndpoint[] }>()
        endpoints.value = (data.llms || []).map(l => ({
            ...l,
            models: l.models || [],
            api_key: l.api_key || ''
        }))
    } catch {
        MessagePlugin.error('加载模型列表失败')
    } finally {
        listLoading.value = false
    }
}

onMounted(fetchLLMs)

function toPayload(item: LLMPayload): LLMPayload {
    return {
        name: item.name.trim(),
        base_url: item.base_url.trim(),
        api_key: item.api_key.trim(),
        // 过滤掉回车产生的空串 / 空白项
        models: item.models.map(m => String(m).trim()).filter(Boolean)
    }
}

function startEdit(item: APIEndpoint) {
    editingUuid.value = item.uuid
}

function cancelEdit() {
    editingUuid.value = ''
    // 从服务端重新拉取，丢弃未保存的改动
    fetchLLMs()
}

async function saveItem(item: APIEndpoint) {
    if (!(await validate(item.uuid))) return

    savingUuid.value = item.uuid
    try {
        await API.updateLLM(item.uuid, toPayload(item))
        MessagePlugin.success('更新成功')
        editingUuid.value = ''
        await fetchLLMs()
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
        await API.createLLM(toPayload(draft.value))
        MessagePlugin.success('创建成功')
        creating.value = false
        await fetchLLMs()
    } catch {
        MessagePlugin.error('创建失败')
    } finally {
        submitting.value = false
    }
}

async function handleDelete(item: APIEndpoint) {
    try {
        await API.deleteLLM(item.uuid)
        MessagePlugin.success('删除成功')
        await fetchLLMs()
    } catch {
        MessagePlugin.error('删除失败')
    }
}
</script>