<template>
  <router-view v-if="hasRouter" />
  <Home v-else />
</template>

<script setup>
import { computed } from 'vue'
import Home from './views/Home.vue'

const hasRouter = computed(() => false)
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  color: #1f2937;
  background: #f3f4f6;
}
#app {
  height: 100vh;
  width: 100vw;
}
</style>
