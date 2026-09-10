<template>
  <t-aside :width="uiStore.collapsed ? '64px' : '232px'" style="height: 100vh;">
    <t-menu :collapsed="uiStore.collapsed" @change="handleMenuChange" class='border-r' v-model:value="currentPath">
      <template #logo>
        <div
          class="w-8 h-8 rounded-[10px] bg-nap-gradient flex items-center justify-center text-white font-bold text-sm flex-shrink-0 shadow-[0_4px_12px_rgba(79,70,229,0.35)]">
          N
        </div>
        <t-space direction="vertical" size="" v-if="!uiStore.collapsed">
          <div class="text-sm font-semibold text-nap-text leading-none" style="font-family: var(--font-display)">
            NAP
          </div>
          <div class="text-xs text-nap-text-secondary mt-1">Take a NAP</div>
        </t-space>
      </template>

      <t-button block shape="round" @click="handleMenuChange('/playground')" style="margin-bottom: 20px;">
        <template #icon><chat-icon /></template>
        <span v-if="!uiStore.collapsed">对话</span>
      </t-button>

      <t-menu-item v-for="item in navItems" :key="item.path" :value="item.path" class="nav-featured">
        <template #icon><t-icon :name="item.icon" /></template>
        {{ item.label }}
      </t-menu-item>
      <template #operations>
        <t-card size="small" v-if="!uiStore.collapsed">
          <div class="flex items-center justify-between">
            <span class="text-xs font-medium text-nap-text">本月 Token 额度</span>
            <span class="text-xs text-nap-text-secondary tabular">68%</span>
          </div>
          <div class="mt-2.5 h-1.5 rounded-full bg-nap-border/70 overflow-hidden">
            <div class="h-full rounded-full bg-nap-gradient" style="width: 68%" />
          </div>
          <p class="mt-2 text-xs text-nap-text-secondary">
            已使用 <span class="tabular text-nap-text">1.6M</span> / 2.4M
          </p>
        </t-card>
      </template>
    </t-menu>
  </t-aside>
</template>

<script setup lang="ts">
import { ChatIcon } from 'tdesign-icons-vue-next';
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { NavItem } from '@/types'
import { useUIStore } from '@/stores/ui';

const route = useRoute()
const router = useRouter()

const uiStore = useUIStore()

const navItems: NavItem[] = [
  { label: '知识库', path: '/knowledge', icon: 'book' },
  { label: '仪表盘', path: '/dashboard', icon: 'dashboard' },
  { label: '智能体', path: '/agents', icon: 'robot' },
  { label: '监控中心', path: '/monitoring', icon: 'chart-bar' },
  { label: '设置', path: '/settings', icon: 'setting' }
]

const currentPath = computed(() =>{
  return route.path;
})

function handleMenuChange(value: any) {
  router.push(value);
}
</script>

<style scoped>
.sidebar-aside {
  position: relative;
  background: var(--td-bg-color-container);
  border-right: 1px solid var(--td-border-level-1-color);
  display: flex;
  flex-direction: column;
}

.custom-menu {
  flex: 1;
  min-height: 0;
}

.custom-menu :deep(.t-menu) {
  padding: 0 8px;
}

.custom-menu :deep(.t-menu__item) {
  height: 38px;
  margin-bottom: 1px;
  border-radius: 10px;
  color: var(--nap-muted);
}

.custom-menu :deep(.t-menu__item .t-menu__item-link) {
  border-radius: 10px;
}

.custom-menu :deep(.t-menu__item:hover) {
  color: var(--nap-ink);
  background: var(--td-bg-color-container-hover);
}

.custom-menu :deep(.t-menu__item.t-is-active) {
  color: var(--td-brand-color);
  background: var(--td-brand-color-light);
  font-weight: 600;
}

.custom-menu :deep(.t-menu__item::after) {
  display: none;
}

.custom-menu :deep(.nav-featured) {
  position: relative;
  margin-top: 4px;
  margin-bottom: 18px;
}

.custom-menu :deep(.nav-featured:not(.t-is-active)::after) {
  content: '';
  position: absolute;
  left: 8px;
  right: 8px;
  bottom: -9px;
  height: 1px;
  background: var(--nap-border);
}

.custom-menu :deep(.nav-featured:not(.t-is-active)) {
  background: linear-gradient(90deg, rgba(79, 70, 229, 0.1), rgba(139, 92, 246, 0.05)) !important;
  color: var(--td-brand-color) !important;
}

.custom-menu :deep(.nav-featured:not(.t-is-active) .t-icon) {
  color: var(--td-brand-color);
}

.custom-menu :deep(.nav-featured:not(.t-is-active)::before) {
  content: '';
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 6px;
  height: 6px;
  border-radius: 9999px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
}

.custom-menu :deep(.nav-featured.t-is-active) {
  background: var(--td-brand-color) !important;
  color: #fff !important;
}

.custom-menu :deep(.nav-featured.t-is-active .t-icon) {
  color: #fff;
}

.sidebar-collapsed .custom-menu :deep(.nav-featured) {
  margin-top: 2px;
  margin-bottom: 14px;
}

.sidebar-collapsed .custom-menu :deep(.nav-featured:not(.t-is-active)::after) {
  display: none;
}
</style>