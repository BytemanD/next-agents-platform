<template>
  <img :src="imgUrl" alt="NAP" :style="{ height: props.size }">
</template>

<script setup lang="ts">
import { computed } from 'vue'

import { useUIStore } from '@/stores/ui'

const uiStore = useUIStore()

const props = withDefaults(
  defineProps<{
    variant?: "lockup" | "icon" | "icon-circle" | "wordmark" | "mark"
    size?: string
  }>(),
  {
    variant: "lockup",
    size: '50px',
    showText: true,
  },
)

const imgUrl = computed(() => {
  switch (props.variant) {
    case "lockup":
      return uiStore.darkMode ? '/brand/lockup-reversed.svg' : '/brand/lockup.svg';
    case "icon":
      return uiStore.darkMode ? '/brand/icon-midnight.svg' : '/brand/icon.svg';
    case "icon-circle":
      return '/brand/icon-circle.svg';
    case "wordmark":
      return uiStore.darkMode ? '/brand/wordmark-reversed.svg' : '/brand/wordmark.svg';
    case "mark":
      return '/brand/mark-reversed.svg';
    default:
      return '/brand/icon.svg'
  }
});
</script>