<template>
  <t-layout class="h-full">
    <Sidebar />
    <t-layout>
      <TopBar />
      <t-content class="px-6 pt-4 overflow-y-auto">
        <router-view />
      </t-content>
    </t-layout>
  </t-layout>
</template>

<script setup lang="ts">
import Sidebar from './Sidebar.vue'
import TopBar from './TopBar.vue'
</script>