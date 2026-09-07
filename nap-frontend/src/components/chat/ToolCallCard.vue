<template>
  <div class="h-16 flex items-center gap-2 px-3 py-1.5 rounded-lg border transition-colors" :class="borderClass">
    <t-icon :name="getStatusIconName()" :class="statusIconClass" />
    <span class="text-xs font-medium truncate">{{ toolCall.name }}</span>
    <t-button theme="default" size="extra-small" variant="text" @click="expanded = !expanded">
      <template #icon>
        <t-icon :name="expanded ? 'chevron-up' : 'chevron-down'" />
      </template>
    </t-button>
  </div>

  <transition name="fade">
    <div v-if="expanded" class="mt-2 ml-6 space-y-2 text-xs">
      <div>
        <span class="text-nap-text-secondary">Input:</span>
        <pre class="mt-1 bg-nap-bg rounded p-2 overflow-x-auto text-nap-text">{{ JSON.stringify(toolCall.input, null, 2) }}</pre>
      </div>
      <div>
        <span class="text-nap-text-secondary">Output:</span>
        <pre class="mt-1 bg-nap-bg rounded p-2 overflow-x-auto text-nap-text">{{ JSON.stringify(toolCall.output, null, 2) }}</pre>
      </div>
      <div class="text-nap-text-secondary">Duration: {{ toolCall.duration }}ms</div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ToolCall } from '@/types'

const props = defineProps<{
  toolCall: ToolCall
}>()

const expanded = ref(false)

const borderClass = computed(() => {
  switch (props.toolCall.status) {
    case 'completed': return 'border-nap-success/30 bg-nap-success/5'
    case 'error': return 'border-nap-error/30 bg-nap-error/5'
    case 'running': return 'border-nap-primary/30 bg-nap-primary/5'
    default: return 'border-nap-border bg-nap-surface'
  }
})

const statusIconClass = computed(() => {
  switch (props.toolCall.status) {
    case 'completed': return 'text-nap-success'
    case 'error': return 'text-nap-error'
    case 'running': return 'text-nap-primary animate-spin'
    default: return 'text-nap-text-secondary'
  }
})

function getStatusIconName() {
  switch (props.toolCall.status) {
    case 'completed': return 'check-circle-filled'
    case 'error': return 'close-circle-filled'
    case 'running': return 'loading'
    default: return 'bolt'
  }
}
</script>
