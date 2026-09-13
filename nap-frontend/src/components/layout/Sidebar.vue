<template>
  <t-aside :class="uiStore.collapsed ? 'w-16' : 'w-58' " >
    <t-menu :value="currentPath" :collapsed="uiStore.collapsed" @change="handleMenuChange" class='border-r'>
      <template #logo>
        <AppLogo :show-text="!uiStore.collapsed" />
      </template>

      <t-button block shape="round" @click="handleMenuChange('/playground')" style="margin-bottom: 20px;">
        <template #icon><ChatBubbleIcon /></template>
        <span v-if="!uiStore.collapsed">对话</span>
      </t-button>

      <t-menu-item v-for="item in navItems" :key="item.path" :value="item.path" class="nav-featured">
        <template #icon><t-icon :name="item.icon" /></template>
        {{ item.label }}
      </t-menu-item>
      <template #operations>
        <t-card size="small" v-if="!uiStore.collapsed">
          <h3 class="text-xs font-medium">本月 Token 额度</h3>
          <t-progress :percentage="50" color="var(--accent-100)" />
          <span>已使用: 1.6M / 2.4M</span> 
        </t-card>
      </template>
    </t-menu>
  </t-aside>
</template>

<script setup lang="ts">
import { ChatBubbleIcon } from 'tdesign-icons-vue-next';
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { NavItem } from '@/types'
import { useUIStore } from '@/stores/ui';
import AppLogo from '@/components/common/AppLogo.vue';

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