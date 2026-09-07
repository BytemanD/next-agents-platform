<template>
  <t-config-provider :global-config="globalConfig">
    <router-view />
  </t-config-provider>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { GlobalConfigProvider } from 'tdesign-vue-next'

const globalConfig = ref<GlobalConfigProvider>({})
</script>

<style>
:root {
  --td-brand-color: #4f46e5;
  --td-brand-color-hover: #6366f1;
  --td-brand-color-active: #4338ca;
  --td-brand-color-light: rgba(79, 70, 229, 0.08);
  --td-brand-color-light-hover: rgba(79, 70, 229, 0.14);
  --td-brand-color-focus: rgba(79, 70, 229, 0.14);
  --td-brand-color-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);

  --td-bg-color-page: #f6f7fb;
  --td-bg-color-container: #ffffff;
  --td-bg-color-container-hover: #f4f5fa;
  --td-bg-color-container-active: #edf0f7;
  --td-bg-color-anti: #ffffff;
  --td-bg-color-secondarycontainer: #f4f5fa;
  --td-bg-color-secondarycontainer-hover: #edf0f7;

  --td-border-level-1-color: #e7e9f2;
  --td-border-level-2-color: #d9dce8;

  --td-text-color-primary: #1e2431;
  --td-text-color-secondary: #5b6478;
  --td-text-color-placeholder: #9aa3b8;
  --td-text-color-disabled: #c4c9d8;

  --td-error-color: #dc2626;
  --td-warning-color: #d97706;
  --td-success-color: #16a34a;

  --td-shadow-1: 0 1px 2px rgba(23, 27, 45, 0.05);
  --td-shadow-2: 0 6px 24px rgba(23, 27, 45, 0.08);
}
</style>