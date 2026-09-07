import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import MainLayout from '@/components/layout/MainLayout.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/pages/Dashboard.vue'),
        meta: { title: '仪表盘', icon: 'home' }
      },
      {
        path: 'agents',
        name: 'Agents',
        component: () => import('@/pages/AgentList.vue'),
        meta: { title: '智能体', icon: 'robot' }
      },
      {
        path: 'agents/builder',
        name: 'AgentBuilder',
        component: () => import('@/pages/AgentBuilder.vue'),
        meta: { title: '智能体构建', icon: 'edit' }
      },
      {
        path: 'agents/builder/:id',
        name: 'AgentEdit',
        component: () => import('@/pages/AgentBuilder.vue'),
        meta: { title: '编辑智能体', icon: 'edit' }
      },
      {
        path: 'playground',
        name: 'Playground',
        component: () => import('@/pages/Playground.vue'),
        meta: { title: '对话工作台', icon: 'chat' }
      },
      {
        path: 'knowledge',
        name: 'Knowledge',
        component: () => import('@/pages/KnowledgeBase.vue'),
        meta: { title: '知识库', icon: 'book' }
      },
      {
        path: 'monitoring',
        name: 'Monitoring',
        component: () => import('@/pages/Monitoring.vue'),
        meta: { title: '监控中心', icon: 'chart-bar' }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/pages/Settings.vue'),
        meta: { title: '设置', icon: 'setting' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  document.title = `${to.meta.title || '打包'} - NAP 下一代智能体平台`
})

export default router
