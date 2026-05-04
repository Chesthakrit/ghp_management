<template>
  <div class="card">
    <div class="card-header">
      <h3><i class="fas fa-calendar-alt"></i> Annual Leave Quotas</h3>
      <button class="btn-primary-sm" @click="save">Save Quotas</button>
    </div>
    <div class="card-body quota-body">
      <div class="quota-item">
        <div class="q-icon"><i class="fas fa-briefcase-medical"></i></div>
        <div class="q-data">
          <label>Sick Leave</label>
          <div class="q-val-wrap">
             <input type="number" v-model="localConfig.quota_sick_leave" />
             <span>days</span>
          </div>
        </div>
      </div>
      <div class="quota-item">
        <div class="q-icon"><i class="fas fa-umbrella-beach"></i></div>
        <div class="q-data">
          <label>Annual Leave</label>
          <div class="q-val-wrap">
             <input type="number" v-model="localConfig.quota_annual_leave" />
             <span>days</span>
          </div>
        </div>
      </div>
      <div class="quota-item">
        <div class="q-icon"><i class="fas fa-user-clock"></i></div>
        <div class="q-data">
          <label>Personal Leave</label>
          <div class="q-val-wrap">
             <input type="number" v-model="localConfig.quota_personal_leave" />
             <span>days</span>
          </div>
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
    const keys = ['quota_sick_leave', 'quota_annual_leave', 'quota_personal_leave']
    const payload = keys.map(k => ({ key: k, value: String(localConfig.value[k]) }))
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

.quota-body { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.quota-item { padding: 16px 10px; background: #f8fafc; border-radius: 10px; border: 1px solid #e2e8f0; text-align: center; }
.q-icon { font-size: 1.1rem; color: #1a2a3a; margin-bottom: 8px; opacity: 0.7; }
.q-data label { display: block; font-size: 0.7rem; font-weight: 700; color: #64748b; margin-bottom: 4px; }
.q-val-wrap { display: flex; align-items: baseline; justify-content: center; gap: 4px; }
.q-val-wrap input { width: 45px; background: transparent; border: none; font-size: 1.2rem; font-weight: 800; color: #1a2a3a; text-align: right; outline: none; }
.q-val-wrap span { font-size: 0.65rem; font-weight: 600; color: #94a3b8; }
</style>
