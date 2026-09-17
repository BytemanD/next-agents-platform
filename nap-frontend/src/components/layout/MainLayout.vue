<template>
  <t-layout class="h-full">
    <Sidebar />
    <t-layout class="min-h-0 flex flex-col flex-1">
      <TopBar />
      <t-content class="p-2 min-h-0 flex-1 overflow-y-auto">
        <router-view />
      </t-content>
    </t-layout>
  </t-layout>
</template>

<script setup lang="ts">
import Sidebar from './Sidebar.vue'
import TopBar from './TopBar.vue'
</script>