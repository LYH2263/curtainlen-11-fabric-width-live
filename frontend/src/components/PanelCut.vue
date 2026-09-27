<script setup>
import { computed } from 'vue'
const props = defineProps({ panels: Number, cutHeight: Number, meters: Number, fabricWidth: Number })
// 每幅按门幅等比缩放，门幅越大条幅越宽，直观反映门幅改动
const panelStyle = (n) => ({
  height: `${(props.cutHeight || 1) * 40}px`,
  width: `${Math.max(12, (Number(props.fabricWidth) || 1) * 24)}px`,
})
const shown = computed(() => Math.min(props.panels || 0, 12))
</script>
<template>
  <div class="panel-cut">
    <div v-for="n in shown" :key="n" class="panel" :style="panelStyle(n)"></div>
    <p>{{ panels }} 幅 × {{ cutHeight }} m（门幅 {{ fabricWidth }}m）= {{ meters }} m</p>
  </div>
</template>
