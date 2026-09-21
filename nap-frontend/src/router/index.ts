import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import MainLayout from '@/components/layout/MainLayout.vue'
import { getToken } from '@/api'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/pages/Register.vue'),
    meta: { title: '注册' }
  },
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: "",
        redirect: 'dashboard'
      },
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
        path: 'knowledge/:id',
        name: 'KnowledgeDetail',
        component: () => import('@/pages/KnowledgeDetail.vue'),
        meta: { title: '知识库详情', icon: 'book' }
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
  const token = getToken()
  if (!token && to.name !== 'Login' && to.name !== 'Register') {
    return { name: 'Login' }
  }
  if (token && (to.name === 'Login' || to.name === 'Register')) {
    return { name: 'Dashboard' }
  }
})

export default router
