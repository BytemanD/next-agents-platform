<template>
  <t-aside
    :width="collapsed ? '76px' : '256px'"
    :class="collapsed ? 'sidebar-collapsed' : ''"
    class="h-full transition-all duration-300 sidebar-aside"
  >
    <div class="h-16 flex items-center px-4 border-b border-nap-border overflow-hidden">
      <div
        class="w-8 h-8 rounded-[10px] bg-nap-gradient flex items-center justify-center text-white font-bold text-sm flex-shrink-0 shadow-[0_4px_12px_rgba(79,70,229,0.35)]"
        style="font-family: var(--font-display)"
      >
        N
      </div>
      <transition name="fade">
        <div v-if="!collapsed" class="ml-3 overflow-hidden whitespace-nowrap">
          <div class="text-sm font-semibold text-nap-text leading-none" style="font-family: var(--font-display)">
            NAP
          </div>
          <div class="text-xs text-nap-text-secondary mt-1">Next Agents Platform</div>
        </div>
      </transition>
    </div>

    <div class="flex-1 min-h-0 overflow-y-auto overflow-x-hidden py-1 custom-menu">
      <t-menu
        :collapsed="collapsed"
        :value="activeMenu"
        :collapsed-width="76"
        :width="256"
        theme="light"
        class="border-0"
        @change="handleMenuChange"
      >
        <t-menu-item
          v-for="item in navItems"
          :key="item.path"
          :value="item.path"
          :class="item.featured ? 'nav-featured' : ''"
        >
          <template #icon><t-icon :name="item.icon" /></template>
          {{ item.label }}
        </t-menu-item>
      </t-menu>
    </div>

    <div class="p-3 border-t border-nap-border sidebar-footer">
      <transition name="fade">
        <div v-if="!collapsed" class="rounded-xl border border-nap-border bg-nap-surface-hover p-3 mb-2">
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
        </div>
      </transition>
      <t-button theme="default" variant="text" block @click="collapsed = !collapsed">
        <template #icon>
          <t-icon :name="collapsed ? 'chevron-right' : 'chevron-left'" :size="20" />
        </template>
        <span v-if="!collapsed" class="text-sm">收起导航</span>
      </t-button>
    </div>
  </t-aside>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { NavItem } from '@/types'

const route = useRoute()
const router = useRouter()
const collapsed = ref(false)

const navItems: NavItem[] = [
  { label: '对话工作台', path: '/playground', icon: 'chat', featured: true },
  { label: '仪表盘', path: '/', icon: 'home' },
  { label: '智能体', path: '/agents', icon: 'robot' },
  { label: '知识库', path: '/knowledge', icon: 'book' },
  { label: '监控中心', path: '/monitoring', icon: 'chart-bar' },
  { label: '设置', path: '/settings', icon: 'setting' }
]

const activeMenu = computed(() => {
  if (route.path === '/') return '/'
  return navItems.find(item => item.path !== '/' && route.path.startsWith(item.path))?.path || '/'
})

function handleMenuChange(value: any) {
  router.push(value)
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