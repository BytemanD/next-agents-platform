<template>
  <t-tag shape="round" :theme="theme" variant="light">
    {{ status }}
  </t-tag>
</template>

<script setup lang="ts">

defineProps({
  status: String,
  theme: { type: String, default: 'default' }
})

</script>
