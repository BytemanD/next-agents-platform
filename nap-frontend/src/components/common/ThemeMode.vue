<template>
    <t-button @click="uiStore.toggleThemeMode" variant="text">
        <MoonIcon v-if="uiStore.darkMode"/>
        <SunnyIcon  v-else/>
    </t-button>
</template>

<script setup lang="ts">
import { SunnyIcon, MoonIcon } from 'tdesign-icons-vue-next';

import { useUIStore } from '@/stores/ui';

const uiStore = useUIStore()


</script>