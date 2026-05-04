<template>
  <div class="card">
    <div class="card-header">
      <h3><i class="fas fa-calendar-day"></i> Work Days</h3>
      <button class="btn-primary-sm" @click="save">Save</button>
    </div>
    <div class="card-body">
      <div class="work-days-compact-grid">
        <div v-for="(day, idx) in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']" :key="idx" class="work-day-mini-item">
          <span class="day-abbr">{{ day }}</span>
          <select v-model="localConfig['work_day_' + idx]" class="work-day-mini-select" :class="localConfig['work_day_' + idx]">
            <option value="work">Work</option>
            <option value="off">Off</option>
          </select>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import api from '../../../api'
import Swal from 'sweetalert2'

const props = defineProps({ modelValue: Object })
const emit = defineEmits(['update:modelValue', 'saved'])

const localConfig = ref({ ...props.modelValue })
watch(() => props.modelValue, (newVal) => { localConfig.value = { ...newVal } }, { deep: true })

const save = async () => {
  try {
    const keys = [0,1,2,3,4,5,6].map(idx => 'work_day_' + idx)
    const payload = keys.map(k => ({ key: k, value: String(localConfig.value[k] || 'work') }))
    await api.put('/attendance/settings', payload)
    Swal.fire({ icon: 'success', title: 'Updated', toast: true, position: 'top-end', showConfirmButton: false, timer: 2000 })
    emit('saved')
  } catch (err) { console.error(err) }
}
</script>

<style scoped>
.card { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; }
.card-header { padding: 16px 20px; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; background: #fafafa; }
.card-header h3 { margin: 0; font-size: 0.95rem; font-weight: 700; color: #1a2a3a; display: flex; align-items: center; gap: 8px; }
.card-body { padding: 20px; }
.btn-primary-sm { background: #1a2a3a; color: #fff; border: none; padding: 6px 14px; border-radius: 6px; font-size: 0.8rem; font-weight: 700; cursor: pointer; }

.work-days-compact-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(80px, 1fr)); gap: 10px; }
.work-day-mini-item { display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 10px 5px; background: #f8fafc; border-radius: 10px; border: 1px solid #e2e8f0; }
.day-abbr { font-size: 0.7rem; font-weight: 800; color: #64748b; text-transform: uppercase; }
.work-day-mini-select { padding: 4px 6px; border-radius: 6px; border: 1.5px solid #cbd5e1; font-size: 0.75rem; font-weight: 800; width: 65px; text-align: center; }
.work-day-mini-select.work { color: #10b981; background: #ecfdf5; border-color: #10b981; }
.work-day-mini-select.off { color: #ef4444; background: #fef2f2; border-color: #ef4444; }
</style>
