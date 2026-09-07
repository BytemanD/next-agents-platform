<template>
  <t-header class="h-16 border-b border-nap-border flex items-center justify-between px-6 bg-nap-surface/80 backdrop-blur-[6px]">
    <div class="flex items-center gap-4 min-w-0">
      <div class="flex items-center gap-2 text-sm whitespace-nowrap">
        <span class="text-nap-text-tertiary">工作空间</span>
        <t-icon name="chevron-right" :size="14" class="text-nap-text-tertiary" />
        <span class="text-nap-text font-medium">{{ currentTitle }}</span>
      </div>
      <div class="hidden xl:flex items-center gap-1.5 rounded-full bg-nap-success/10 text-nap-success px-2.5 py-1 text-xs">
        <span class="w-1.5 h-1.5 rounded-full bg-nap-success nap-pulse" />
        运行正常
      </div>
    </div>

    <div class="flex items-center gap-3">
      <t-input
        v-model="searchQuery"
        placeholder="搜索智能体、会话、文档..."
        clearable
        class="w-72"
        @focus="showSearch = true"
      >
        <template #prefixIcon>
          <t-icon name="search" />
        </template>
        <template #suffixIcon>
          <kbd class="text-[11px] leading-none bg-nap-surface-hover border border-nap-border rounded px-1.5 py-0.5 text-nap-text-secondary select-none">
            ⌘K
          </kbd>
        </template>
      </t-input>

      <t-badge :count="3" size="small" :offset="[0, 2]">
        <t-button theme="default" variant="text" shape="square">
          <template #icon><t-icon name="notification" :size="20" /></template>
        </t-button>
      </t-badge>

      <div class="w-px h-6 bg-nap-border mx-1" />

      <t-dropdown :options="userMenuOptions" @click="handleMenuClick">
        <div class="flex items-center gap-2.5 cursor-pointer hover:opacity-85 transition-opacity select-none">
          <div class="w-8 h-8 rounded-full bg-nap-gradient flex items-center justify-center text-white text-xs font-medium flex-shrink-0">
            用
          </div>
          <span class="hidden md:block text-sm text-nap-text">管理员</span>
          <t-icon name="chevron-down" :size="14" class="text-nap-text-tertiary" />
        </div>
      </t-dropdown>
    </div>
  </t-header>

  <t-dialog v-model:visible="showSearch" header="搜索" :footer="null" placement="top">
    <t-input
      v-model="searchQuery"
      placeholder="搜索智能体、会话、文档..."
      clearable
    >
      <template #prefixIcon><t-icon name="search" /></template>
    </t-input>
    <p class="mt-4 text-sm text-nap-text-secondary">
      输入关键字搜索整个工作区...
    </p>
  </t-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const showSearch = ref(false)
const searchQuery = ref('')

const currentTitle = computed(() => route.meta.title as string || '仪表盘')

const userMenuOptions = [
  { content: '个人信息', value: 'profile' },
  { content: '工作区设置', value: 'workspace' },
  { divider: true, content: '', value: 'd1' },
  { content: '退出登录', value: 'signout' }
]

function handleMenuClick(data: any) {
  console.log('菜单点击:', data.value)
}

function handleKeydown(e: KeyboardEvent) {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    showSearch.value = true
  }
}

if (typeof window !== 'undefined') {
  window.addEventListener('keydown', handleKeydown)
}
</script>