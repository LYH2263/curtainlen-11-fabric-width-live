<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, patchJSON } from '../api'
const items = ref([])
const drafts = ref({})
const errors = ref({})
const saved = ref({})

onMounted(load)
async function load() {
  items.value = (await getJSON('/api/fabrics')).items
  drafts.value = Object.fromEntries(items.value.map(f => [f.id, f.fabric_width]))
  errors.value = {}
  saved.value = {}
}
async function save(f) {
  const v = Number(drafts.value[f.id])
  errors.value[f.id] = ''
  if (!Number.isFinite(v) || v <= 0) {
    errors.value[f.id] = '门幅必须为正数，旧值已保留'
    drafts.value[f.id] = f.fabric_width
    return
  }
  try {
    const updated = await patchJSON(`/api/fabrics/${f.id}`, { fabric_width: v })
    const i = items.value.findIndex(x => x.id === f.id)
    if (i >= 0) items.value[i] = { ...items.value[i], ...updated }
    drafts.value[f.id] = updated.fabric_width
    saved.value[f.id] = '已保存'
    setTimeout(() => { saved.value[f.id] = '' }, 2000)
  } catch (e) {
    errors.value[f.id] = e.message || '保存失败，旧值已保留'
    drafts.value[f.id] = f.fabric_width
  }
}
</script>
<template><div class="page"><h1>面料</h1>
<div v-for="f in items" :key="f.id" class="fab">
  <span>{{ f.name }}</span>
  门幅
  <input v-model.number="drafts[f.id]" type="number" step="0.01" min="0" style="width:6em">
  m
  <button @click="save(f)">保存门幅</button>
  <em v-if="errors[f.id]" style="color:#c0392b">{{ errors[f.id] }}</em>
  <em v-if="saved[f.id]" style="color:#27ae60">{{ saved[f.id] }}</em>
</div></div></template>
