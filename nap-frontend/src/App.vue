<template>
  <t-config-provider :global-config="globalConfig">
    <router-view />
  </t-config-provider>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { GlobalConfigProvider } from 'tdesign-vue-next'

document.documentElement.setAttribute('theme-mode', 'light');


const globalConfig = ref<GlobalConfigProvider>({})
</script>

<style>

html,
body,
#app {
    height: 100%;
    width: 100%;
    overflow: hidden;
}


:root {
  --primary-100:#296266;
  --primary-200:#589094;
  --primary-300:#b9f3f7;
  --accent-100:#a8824a;
  --accent-200:#482d00;
  --text-100:#4b4a47;
  --text-200:#777672;
  --bg-100:#fffbf2;
  --bg-200:#f5f1e8;
  --bg-300:#ccc8bf;

  --font-body: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
  --font-display: 'Space Grotesk Variable', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  --nap-page: #f6f7fb;
  --nap-surface: #ffffff;
  --nap-surface-hover: #f4f5fa;
  --nap-border: #e7e9f2;
  --nap-border-strong: #d9dce8;
  --nap-ink: #1e2431;
  --nap-muted: #5b6478;
  --nap-faint: #9aa3b8;
  --nap-accent: #4f46e5;
  --nap-accent-hover: #6366f1;
  --nap-accent-soft: #eef0ff;
  --nap-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  --nap-success: #16a34a;
  --nap-warning: #d97706;
  --nap-error: #dc2626;

  --nap-shadow-sm: 0 1px 2px rgba(23, 27, 45, 0.05);
  --nap-shadow-md: 0 6px 24px rgba(23, 27, 45, 0.08);
  --nap-shadow-lg: 0 16px 40px rgba(23, 27, 45, 0.12);

  --nap-radius-sm: 6px;
  --nap-radius-md: 10px;
  --nap-radius-lg: 14px;
  --nap-radius-xl: 18px;
}

.text-accent-100 {
  color: var(--accent-100);
}
</style>