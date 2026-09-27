<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
import PanelCut from '../components/PanelCut.vue'
const windows = ref([]); const fabrics = ref([]); const wid = ref(null); const fid = ref(null)
const out = ref(null); const err = ref('')

async function loadFabrics() {
  const list = (await getJSON('/api/fabrics')).items.filter(x => x.data_quality === 'clean')
  fabrics.value = list
  if (!list.some(x => x.id === fid.value)) fid.value = list[0]?.id ?? null
}
onMounted(async () => {
  windows.value = (await getJSON('/api/windows')).items.filter(x => x.data_quality === 'clean')
  await loadFabrics()
  if (windows.value.length) wid.value = windows.value[0].id
})
async function go(save) {
  err.value = ''
  out.value = null
  try {
    // 门幅以布料页最新保存值为准：试算前重新拉取布料
    await loadFabrics()
    out.value = save
      ? await postJSON('/api/estimate', { window_id: wid.value, fabric_id: fid.value, save: true })
      : await getJSON(`/api/estimate?window_id=${wid.value}&fabric_id=${fid.value}`)
  } catch (e) {
    err.value = e.message
  }
}
</script>
<template><div class="page"><h1>算料</h1>
<select v-model.number="wid"><option v-for="x in windows" :key="x.id" :value="x.id">{{ x.name }}</option></select>
<select v-model.number="fid"><option v-for="x in fabrics" :key="x.id" :value="x.id">{{ x.name }}（门幅 {{ x.fabric_width }}m）</option></select>
<button @click="go(false)">试算</button><button @click="go(true)">保存</button>
<p v-if="err" style="color:#c0392b">{{ err }}</p>
<PanelCut v-if="out" :panels="out.panels" :cut-height="out.cut_height" :meters="out.meters" :fabric-width="out.fabric_width" />
</div></template>
