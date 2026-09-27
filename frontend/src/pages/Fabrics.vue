<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'
const items = ref([])
const drafts = ref({})
const errors = ref({})
onMounted(load)
async function load() {
  items.value = (await getJSON('/api/fabrics')).items
  drafts.value = {}
  errors.value = {}
  for (const f of items.value) drafts.value[f.id] = String(f.fabric_width)
}
async function save(f) {
  const v = Number(drafts.value[f.id])
  if (!Number.isFinite(v) || v <= 0) {
    errors.value[f.id] = '门幅须为正数'
    drafts.value[f.id] = String(f.fabric_width)
    return
  }
  try {
    const updated = await putJSON(`/api/fabrics/${f.id}`, { fabric_width: v })
    Object.assign(f, updated)
    drafts.value[f.id] = String(updated.fabric_width)
    errors.value[f.id] = ''
  } catch (e) {
    // 保存失败：库内旧值保留，输入回滚为库值
    errors.value[f.id] = '保存失败：门幅须为正数'
    drafts.value[f.id] = String(f.fabric_width)
  }
}
</script>
<template><div class="page"><h1>面料</h1>
<div v-for="f in items" :key="f.id" class="fab">
  <span>{{ f.name }}</span>
  门幅 <input v-model="drafts[f.id]" type="number" step="0.01" min="0" style="width:5rem" /> m
  <button @click="save(f)">保存</button>
  <span v-if="errors[f.id]" class="bad">{{ errors[f.id] }}</span>
</div>
</div></template>
