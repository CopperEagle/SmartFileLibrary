<script setup lang="ts">
import ResultWindow from '@/components/ResultWindow.vue'
import QueryInput from '../components/QueryInput.vue'

function doNOOP() {}
doNOOP()
</script>

<template>
  <main>
    <QueryInput />
    <ResultWindow />
  </main>
</template>
