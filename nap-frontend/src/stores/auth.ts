import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getToken, setToken, clearToken } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(getToken())

  const isAuthenticated = () => !!token.value

  function saveToken(value: string) {
    token.value = value
    setToken(value)
  }

  function logout() {
    token.value = null
    clearToken()
  }

  return {
    token,
    isAuthenticated,
    saveToken,
    logout
  }
})