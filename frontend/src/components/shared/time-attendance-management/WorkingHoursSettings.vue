<template>
  <div class="card">
    <div class="card-header">
      <h3><i class="fas fa-clock"></i> Standard Working Hours</h3>
      <button class="btn-primary-sm" @click="save">Save Settings</button>
    </div>
    <div class="card-body">
      <div class="form-row">
        <div class="field">
          <label>Check-in <span class="tag-24h">24H</span></label>
          <input type="text" class="input-modern" v-model="localConfig.check_in_time" placeholder="HH:mm" @blur="validateTime('check_in_time')" />
        </div>
        <div class="field">
          <label>Check-out <span class="tag-24h">24H</span></label>
          <input type="text" class="input-modern" v-model="localConfig.check_out_time" placeholder="HH:mm" @blur="validateTime('check_out_time')" />
        </div>
      </div>
      
      <div class="grace-periods-container">
        <label class="section-label">Grace Periods (Late Tiers)</label>
        <div class="grace-grid">
          <div class="grace-field">
            <div class="grace-tag t1">Tier 1</div>
            <div class="grace-input-wrap">
              <input type="number" v-model="localConfig.late_grace_period_mins" />
              <span>min</span>
            </div>
          </div>
          <div class="grace-field">
            <div class="grace-tag t2">Tier 2</div>
            <div class="grace-input-wrap">
              <input type="number" v-model="localConfig.late_grace_period_mins_t2" />
              <span>min</span>
            </div>
          </div>
          <div class="grace-field">
            <div class="grace-tag t3">Tier 3</div>
            <div class="grace-input-wrap">
              <input type="number" v-model="localConfig.late_grace_period_mins_t3" />
              <span>min</span>
            </div>
          </div>
        </div>
        <p class="help-text">Define allowed lateness levels before penalty status changes.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import Swal from 'sweetalert2'
import api from '../../../api'

const props = defineProps({
  modelValue: Object
})
const emit = defineEmits(['update:modelValue', 'saved'])

const localConfig = ref({ ...props.modelValue })

watch(() => props.modelValue, (newVal) => {
  localConfig.value = { ...newVal }
}, { deep: true })

const validateTime = (key) => {
  const val = localConfig.value[key]
  if (!val) return
  let clean = val.trim().replace(/[^0-9:]/g, '')
  if (clean.length === 4 && !clean.includes(':')) {
    clean = clean.slice(0, 2) + ':' + clean.slice(2)
  }
  const regex = /^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/
  if (!regex.test(clean)) {
    Swal.fire({ icon: 'error', title: 'รูปแบบเวลาไม่ถูกต้อง', text: 'กรุณากรอกเป็นรูปแบบ 24 ชม. (เช่น 08:30 หรือ 17:00)' })
    localConfig.value[key] = "08:00"
  } else {
    const [h, m] = clean.split(':')
    localConfig.value[key] = `${h.padStart(2, '0')}:${m.padStart(2, '0')}`
  }
  emit('update:modelValue', { ...localConfig.value })
}

const save = async () => {
  try {
    const keys = ['check_in_time', 'check_out_time', 'late_grace_period_mins', 'late_grace_period_mins_t2', 'late_grace_period_mins_t3']
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
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase; }
.input-modern { padding: 10px 12px; border: 1.5px solid #e2e8f0; border-radius: 8px; font-size: 0.9rem; outline: none; }
.tag-24h { font-size: 0.6rem; background: #1a2a3a; color: #fff; padding: 1px 4px; border-radius: 3px; margin-left: 4px; }
.btn-primary-sm { background: #1a2a3a; color: #fff; border: none; padding: 6px 14px; border-radius: 6px; font-size: 0.8rem; font-weight: 700; cursor: pointer; }

.grace-periods-container { padding-top: 16px; border-top: 1px dashed #e2e8f0; }
.section-label { display: block; font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 12px; }
.grace-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.grace-field { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px; display: flex; flex-direction: column; gap: 8px; }
.grace-tag { font-size: 0.65rem; font-weight: 800; padding: 2px 6px; border-radius: 4px; align-self: flex-start; text-transform: uppercase; }
.grace-tag.t1 { background: #fef9c3; color: #854d0e; }
.grace-tag.t2 { background: #ffedd5; color: #9a3412; }
.grace-tag.t3 { background: #fee2e2; color: #991b1b; }
.grace-input-wrap { display: flex; align-items: center; gap: 4px; }
.grace-input-wrap input { width: 100%; border: none; background: transparent; font-size: 1.1rem; font-weight: 800; color: #1a2a3a; outline: none; }
.grace-input-wrap span { font-size: 0.65rem; font-weight: 600; color: #94a3b8; }
.help-text { font-size: 0.7rem; color: #94a3b8; margin-top: 10px; font-style: italic; }
</style>
