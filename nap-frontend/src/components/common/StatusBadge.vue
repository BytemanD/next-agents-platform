<template>
  <span
    class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
    :class="badgeClass"
  >
    {{ status }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  status: string
}>()

const badgeClass = computed(() => {
  switch (props.status) {
    case 'active':
      return 'bg-nap-success/15 text-nap-success'
    case 'draft':
      return 'bg-nap-warning/15 text-nap-warning'
    case 'error':
      return 'bg-nap-error/15 text-nap-error'
    case 'processing':
      return 'bg-nap-secondary/15 text-nap-secondary'
    case 'ready':
      return 'bg-nap-success/15 text-nap-success'
    default:
      return 'bg-nap-border/50 text-nap-text-secondary'
  }
})
</script>
