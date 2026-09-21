<template>
  <AuthLayout heading="欢迎回来" hint="登录 NAP，继续你的智能体工作流" brand-title="NAP"
    brand-subtitle="Hand it over while you take a nap">
    <t-form :data="form" @submit="handleLogin">
      <t-form-item label="用户名" name="username">
        <t-input v-model="form.username" placeholder="请输入用户名">
          <template #prefixIcon><t-icon name="user" /></template>
        </t-input>
      </t-form-item>
      <t-form-item label="密码" name="password">
        <t-input v-model="form.password" type="password" placeholder="请输入密码">
          <template #prefixIcon><t-icon name="lock-on" /></template>
        </t-input>
      </t-form-item>
      <t-form-item>
        <t-button theme="primary" type="submit" block size="large" :loading="loading" class>登录</t-button>
      </t-form-item>
      <br>
    </t-form>
    <t-divider dashed>还没有账号？</t-divider>
    <router-link to="/register">
      <t-button variant="outline" block size="large">注册新账号</t-button>
    </router-link>
  </AuthLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { MessagePlugin } from 'tdesign-vue-next'
import { API } from '@/api'
import { useAuthStore } from '@/stores/auth'
import AuthLayout from '@/components/auth/AuthLayout.vue'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const form = ref({ username: '', password: '' })

async function handleLogin() {
  if (!form.value.username || !form.value.password) {
    MessagePlugin.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    const data = await API.login<{ token: string }>(form.value.username, form.value.password)
    authStore.saveToken(data.token)
    MessagePlugin.success('登录成功')
    router.push('/dashboard')
  } catch {
    MessagePlugin.error('用户名或密码错误')
  } finally {
    loading.value = false
  }
}
</script>