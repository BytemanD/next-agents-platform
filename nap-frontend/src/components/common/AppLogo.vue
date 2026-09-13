<template>
  <div class="inline-flex items-center gap-2.5 select-none">
    <div
      class="flex items-center justify-center text-white shadow-[0_4px_12px_rgba(79,70,229,0.35)]"
      :class="[sizeClass, roundedClass, 'bg-nap-gradient']"
      style="font-family: var(--font-display)"
    >
      N
    </div>
    <template v-if="showText">
      <div class="flex flex-col leading-none" :class="textSizeClass">
        <span style="font-family: var(--font-display)">NAP</span>
        <span class="text-nap-text-secondary mt-1.5" :class="subtitleSizeClass">Take a NAP</span>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    size?: 'small' | 'medium' | 'large'
    showText?: boolean
  }>(),
  {
    size: 'medium',
    showText: true,
  },
)

const sizeClass = computed(() => {
  const map = { small: 'w-8 h-8 text-[13px]', medium: 'w-10 h-10 text-sm', large: 'w-16 h-16 text-2xl' }
  return map[props.size]
})

const roundedClass = computed(() => (props.size === 'large' ? 'rounded-2xl' : 'rounded-[10px]'))

const textSizeClass = computed(() => (props.size === 'large' ? 'text-2xl' : 'text-sm'))

const subtitleSizeClass = computed(() => (props.size === 'large' ? 'text-base' : 'text-xs'))
</script>