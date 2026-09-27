<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
onMounted(async () => { items.value = (await getJSON('/api/runs')).items })
</script>
<template><div class="page"><h1>记录</h1><ul><li v-for="r in items" :key="r.id">
  #{{ r.id }} {{ r.window_name }}（{{ r.fabric_name }}） 写入时门幅{{ r.result?.fabric_width }}m — {{ r.result?.meters }}m
</li></ul></div></template>
