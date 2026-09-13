import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUIStore = defineStore('ui', () => {
  const darkMode = ref(false)
  const collapsed = ref(false)

  function toggleThemeMode() {
    darkMode.value = !darkMode.value;
    document.documentElement.setAttribute('theme-mode', darkMode.value ? 'dark' : 'light');

  }
  function toggleCollapsed() {
    collapsed.value = !collapsed.value
  }

  return {
    darkMode,
    collapsed,
    toggleThemeMode,
    toggleCollapsed,
  }
})
