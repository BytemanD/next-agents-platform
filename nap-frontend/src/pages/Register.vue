<template>
  <AuthLayout heading="创建账号" hint="注册 NAP，开始编排你的第一个智能体" brand-title="NAP"
    brand-subtitle="Hand it over while you take a nap">
    <t-form :data="form" @submit="handleRegister">
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
      <t-form-item label="邮箱" name="email">
        <t-input v-model="form.email" placeholder="请输入邮箱（可选）">
          <template #prefixIcon><t-icon name="mail" /></template>
        </t-input>
      </t-form-item>
      <t-form-item>
        <t-button theme="primary" type="submit" block size="large" :loading="loading">注册</t-button>
      </t-form-item>
    </t-form>
    <t-divider dashed>已经有账号？</t-divider>
    <router-link to="/login">
      <t-button variant="outline" block size="large">返回登录</t-button>
    </router-link>
  </AuthLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { MessagePlugin } from 'tdesign-vue-next'
import { API } from '@/api'
import AuthLayout from '@/components/auth/AuthLayout.vue'

const router = useRouter()
const loading = ref(false)
const form = ref({ username: '', password: '', email: '' })

async function handleRegister() {
  if (!form.value.username || !form.value.password) {
    MessagePlugin.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    await API.register(form.value.username, form.value.password, form.value.email || undefined)
    MessagePlugin.success('注册成功，请登录')
    router.push('/login')
  } catch {
    MessagePlugin.error('注册失败')
  } finally {
    loading.value = false
  }
}
</script>