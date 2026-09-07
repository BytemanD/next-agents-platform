<template>
  <t-layout class="h-full w-full">
    <Sidebar />
    <t-layout>
      <TopBar />
      <t-content class="overflow-auto">
        <main class="px-8 py-7 h-full">
          <div class="max-w-[1500px] mx-auto">
            <router-view v-slot="{ Component }">
              <transition name="fade" mode="out-in">
                <component :is="Component" />
              </transition>
            </router-view>
          </div>
        </main>
      </t-content>
    </t-layout>
  </t-layout>
</template>

<script setup lang="ts">
import Sidebar from './Sidebar.vue'
import TopBar from './TopBar.vue'
</script>