<template>
    <t-card :size="size" :bordered="bordered">
        <t-statistic :title="title" :value="value" :unit='unit' />
    </t-card>
</template>

<script setup lang="ts">
defineProps({
    title: String,
    value: [String, Number],
    unit: { type: String, default: '' },
    size: { type: String, default: 'small' },
    bordered: { type: Boolean, default: false },
})

</script>