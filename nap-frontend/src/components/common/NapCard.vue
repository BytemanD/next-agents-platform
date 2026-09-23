<template>
    <t-card class="h-full card-hover" :bordered="true" :title="title" :subtitle="subtitle" size="small">
        <template #actions>
            <t-space>
                <slot name="actions"></slot>
            </t-space>
        </template>
        <template #footer>
            <t-space align="center" class="flex justify-between" size="large">
                <t-space @click.stop>
                    <slot name="footer-left"></slot>
                </t-space>
                <t-space @click.stop>
                    <slot name="footer-right"></slot>
                </t-space>
            </t-space>
        </template>
        <slot></slot>
    </t-card>
</template>

<script setup lang="ts">

defineProps({
    title: { type: String, default: '' },
    subtitle: { type: String, default: '' },
})
defineSlots<{
    default?: () => any
    actions?: () => any
    'footer-left'?: () => any
    'footer-right'?: () => any
}>()
</script>