<template>
  <div class="h-screen overflow-y-auto">
    <t-loading :loading="loading" size="large" class="block w-full h-full">
      <t-empty v-if="!loading && error" type="fail" class="py-16">
        <template #description>
          <t-text theme="danger">{{ error }}</t-text>
        </template>
      </t-empty>

      <div v-else-if="!loading" class="preview-body">
        <div v-if="kind === 'markdown'" class="md-body" v-html="renderedHtml"></div>
        <div v-else-if="kind === 'html'" class="md-body" v-html="content"></div>
        <pre v-else-if="kind === 'text'" class="txt-body">{{ content }}</pre>
        <t-empty v-else class="py-16">
          <template #description>
            <t-text theme="secondary">仅支持预览 md、txt、html 文件</t-text>
          </template>
          <template #image>
            <t-icon name="file-unknown" size="40" class="text-nap-text-tertiary" />
          </template>
        </t-empty>
      </div>
    </t-loading>

  </div>
  <t-button v-if="!loading && name && source === 'attachment'" class="fixed bottom-6 right-6" shape="circle" size="large" @click="handleDownload">
    <template #icon><t-icon name="download" /></template>
  </t-button>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import { MessagePlugin } from 'tdesign-vue-next'
import { API } from '@/api'
import type { Attachment, KnowledgeDetail } from '@/types'

const route = useRoute()
const uuid = computed(() => String(route.params.id || ''))
const source = computed(() => String(route.meta.source || 'attachment'))

const name = ref('')
const content = ref('')
const loading = ref(true)
const error = ref('')

const md = new MarkdownIt({
  html: true,
  linkify: true,
  breaks: true,
  highlight(str: string, lang: string) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, { language: lang }).value
      } catch {
        // ignore
      }
    }
    return ''
  },
})

const ext = computed(() => {
  const i = name.value.lastIndexOf('.')
  return i >= 0 ? name.value.slice(i + 1).toLowerCase() : ''
})

type Kind = 'markdown' | 'html' | 'text' | 'unsupported'
const kind = computed<Kind>(() => {
  switch (ext.value) {
    case 'md':
    case 'markdown':
      return 'markdown'
    case 'html':
    case 'htm':
      return 'html'
    case 'txt':
    case 'text':
    case 'log':
      return 'text'
    default:
      return 'unsupported'
  }
})

const renderedHtml = computed(() => md.render(content.value))

async function load() {
  loading.value = true
  error.value = ''
  try {
    if (source.value === 'knowledge') {
      const detail = await API.fetchKnowledgeDetail<KnowledgeDetail>(uuid.value)
      name.value = detail.name || ''
      if (kind.value === 'unsupported') return
      content.value = await API.fetchKnowledgeContent(uuid.value)
    } else {
      const meta = await API.fetchAttachment<Attachment>(uuid.value)
      name.value = meta.name || ''
      if (kind.value === 'unsupported') return
      content.value = await API.fetchAttachmentContent(uuid.value)
    }
  } catch (e: unknown) {
    const err = e as { response?: { status?: number }; message?: string }
    const status = err?.response?.status
    if (status === 404) error.value = source.value === 'knowledge' ? '文档不存在' : '附件不存在'
    else if (status === 403) error.value = '无权限'
    else error.value = err?.message || '加载失败'
  } finally {
    loading.value = false
  }
}

async function handleDownload() {
  try {
    const raw = await API.fetchAttachmentContent(uuid.value)
    const blob = new Blob([raw], { type: 'application/octet-stream' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = name.value || 'download'
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    MessagePlugin.error('下载失败')
  }
}

onMounted(load)
</script>

<style scoped>
.preview-body {
  max-width: 900px;
  margin: 0 auto;
}

.md-body {
  font-size: 14px;
  line-height: 1.75;
  color: var(--td-text-color-primary);
  word-break: break-word;
}

.md-body :deep(h1),
.md-body :deep(h2),
.md-body :deep(h3),
.md-body :deep(h4) {
  margin: 1.2em 0 0.6em;
  font-weight: 600;
  line-height: 1.3;
}

.md-body :deep(h1) {
  font-size: 1.6em;
}

.md-body :deep(h2) {
  font-size: 1.4em;
}

.md-body :deep(h3) {
  font-size: 1.2em;
}

.md-body :deep(p) {
  margin: 0.6em 0;
}

.md-body :deep(a) {
  color: var(--td-brand-color);
  text-decoration: none;
}

.md-body :deep(a:hover) {
  text-decoration: underline;
}

.md-body :deep(ul),
.md-body :deep(ol) {
  margin: 0.6em 0;
  padding-left: 1.6em;
}

.md-body :deep(li) {
  margin: 0.2em 0;
}

.md-body :deep(blockquote) {
  margin: 0.8em 0;
  padding: 0.4em 1em;
  border-left: 3px solid var(--td-brand-color);
  background: var(--td-bg-color-container-hover);
  color: var(--td-text-color-secondary);
}

.md-body :deep(code) {
  padding: 0.15em 0.4em;
  border-radius: 4px;
  background: var(--td-bg-color-container-hover);
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.9em;
}

.md-body :deep(pre) {
  margin: 0.8em 0;
  padding: 12px 16px;
  border-radius: 8px;
  background: #282c34;
  color: #abb2bf;
  overflow-x: auto;
}

.md-body :deep(pre code) {
  padding: 0;
  background: transparent;
  color: inherit;
}



.md-body :deep(th),
.md-body :deep(td) {
  padding: 6px 12px;
  border: 1px solid var(--td-component-border);
  text-align: left;
}

.md-body :deep(th) {
  background: var(--td-bg-color-container-hover);
  font-weight: 600;
}

.md-body :deep(img) {
  max-width: 100%;
}

.md-body :deep(hr) {
  margin: 1.2em 0;
  border: none;
  border-top: 1px solid var(--td-component-border);
}

.txt-body {
  margin: 0;
  padding: 4px 0;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 13px;
  line-height: 1.7;
  color: var(--td-text-color-primary);
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
