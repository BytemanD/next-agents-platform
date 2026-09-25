<template>
  <t-header>
    <t-head-menu>
      <template #logo>
        <t-button variant="text" shape="square" :title="uiStore.collapsed ? '展开导航' : '收起导航'"
          @click="uiStore.toggleCollapsed()">
          <t-icon :name="uiStore.collapsed ? 'chevron-right' : 'chevron-left'" size="18" />
        </t-button>
        <t-divider layout="vertical"></t-divider>
        <h1 class="w-30">{{ currentTitle }}</h1>
      </template>

      <template #operations>
        <t-space align="center">
          <t-input v-model="searchQuery" placeholder="搜索智能体、会话、文档..." clearable class="w-72" @focus="showSearch = true">
            <template #prefixIcon>
              <t-icon name="search" />
            </template>
            <template #suffixIcon>
              <kbd
                class="text-[11px] leading-none bg-nap-surface-hover border border-nap-border rounded px-1.5 py-0.5 text-nap-text-secondary select-none">
                ⌘K
              </kbd>
            </template>
          </t-input>
          <t-badge :count="3" size="small" :offset="[0, 2]">
            <t-button variant="text" shape="square">
              <template #icon><t-icon name="notification" size="20" /></template>
            </t-button>
          </t-badge>
          <theme-mode></theme-mode>
        </t-space>
        <t-divider layout="vertical"></t-divider>

        <t-dropdown :options="userMenuOptions" @click="userMenuHandler">
          <t-button variant="text">
            <template #icon>
              <t-avatar size="small">
                <user-1-icon></user-1-icon>
              </t-avatar>
            </template>
            <span class="ml-1">{{ userName || '用户' }}</span>
          </t-button>
        </t-dropdown>
      </template>
    </t-head-menu>
  </t-header>

  <t-dialog v-model:visible="showSearch" header="搜索" :footer="null" placement="top">
    <t-input v-model="searchQuery" placeholder="搜索智能体、会话、文档..." clearable>
      <template #prefixIcon><t-icon name="search" /></template>
    </t-input>
    <p class="mt-4 text-sm text-nap-text-secondary">
      输入关键字搜索整个工作区...
    </p>
  </t-dialog>
</template>

<script setup lang="ts">
import { useUIStore } from '@/stores/ui'
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { MessagePlugin } from 'tdesign-vue-next';
import ThemeMode from '../common/ThemeMode.vue';
import { useAuthStore } from '@/stores/auth';
import { API } from '@/api';

const route = useRoute()
const router = useRouter()
const showSearch = ref(false)
const searchQuery = ref('')
const uiStore = useUIStore()

const currentTitle = computed(() => route.meta.title as string || '仪表盘')

const authStore = useAuthStore()
const userName = ref('')

function redirectToLogin() {
  authStore.logout()
  router.replace('/login')
}

onMounted(async () => {
  if (!authStore.token) {
    redirectToLogin()
    return
  }
  try {
    const data = await API.fetchUserMe<{ username: string; email?: string }>()
    userName.value = data.username || ''
  } catch {
    redirectToLogin()
  }
})

const userMenuOptions = [
  { content: '个人信息', value: 'profile' },
  { content: '设置', value: 'settings' },
  { divider: true, content: '', value: 'd1' },
  { content: '退出登录', value: 'signout', theme: 'error', }
]

const userMenuHandler = (data: any) => {
  if (data.value == 'settings') {
    router.push('settings')
    return
  }
  if (data.value == 'signout') {
    authStore.logout()
    router.push('/login')
    return
  }
  MessagePlugin.success(`选中【${data.content}】`);
};

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