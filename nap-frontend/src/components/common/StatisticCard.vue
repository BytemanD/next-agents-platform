<template>
    <t-card :size="size" :bordered="bordered">
        <t-statistic :title="title" :value="statistic.value" :unit='statistic.unit'
            :animation="{ duration: 1000, valueFrom: 0 }" animation-start />
    </t-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { filesize } from 'filesize'


const props = defineProps({
    title: String,
    value: Number,
    unit: { type: String, default: '' },
    size: { type: String, default: 'small' },
    bordered: { type: Boolean, default: false },
    formatValue: { type: Boolean, default: false },
})

const statistic = computed(() => {
    if (!props.formatValue || !props.value) {
        return { value: props.value, unit: props.unit }
    }
    let v = filesize(props.value).split(' ')
    return { value: Number(v[0]), unit: v[1] || props.unit }
})
</script>