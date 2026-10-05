<template>
    <t-button :shape="shape" :theme="selected ? 'primary' : 'default'" @click="toggle">
        <template #icon v-if="icon"> <t-icon name="earth"></t-icon> </template>
        <slot></slot>
    </t-button>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
    icon: { type: String, required: false },
    shape: { type: String, default: 'round' },
})
const emit = defineEmits(['update:modelValue'])

const selected = ref(false)

function toggle() {
    selected.value = !selected.value;
    emit('update:modelValue', selected.value)
}

</script>