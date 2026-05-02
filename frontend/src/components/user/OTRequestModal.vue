<template>
  <div v-if="isOpen" class="modal-overlay" @click="$emit('close')">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3><i class="fas fa-business-time"></i> OT Request</h3>
        <button class="close-btn" @click="$emit('close')"><i class="fas fa-times"></i></button>
      </div>
      
      <div class="modal-body">
        <div class="ot-form">
          <!-- ข้อมูลพนักงาน -->
          <div class="info-card">
            <span class="label">ผู้ขอโอที (Requester)</span>
            <span class="value">{{ requesterName }}</span>
          </div>

          <!-- แบบฟอร์มกรอกข้อมูล -->
          <div class="form-grid">
            <div class="form-group full">
              <label>วันที่ขอ (Date)</label>
              <input type="date" v-model="otForm.request_date" class="form-input" />
              
              <!-- ปุ่มกดดึงเวลาจริง (ปลาบปลื้มใจแน่นอนครับ) -->
              <div v-if="actualDayLog?.actual_check_out" class="actual-info-row">
                <span>เลิกงานจริง: <strong>{{ formatActualTime(actualDayLog.actual_check_out) }}</strong></span>
                <button class="btn-text-action" @click="useActualTime">
                  <i class="fas fa-magic"></i> ใช้เวลาเลิกงานจริง (ปัดเศษ 30 นาที)
                </button>
              </div>
            </div>

            <div class="form-group">
              <label>เวลาเริ่ม (Start)</label>
              <div class="time-picker-custom">
                <select v-model="startTime.h" class="time-select">
                  <option v-for="h in hourOptions" :key="'sh'+h" :value="h">{{ h }}</option>
                </select>
                <span class="sep">:</span>
                <select v-model="startTime.m" class="time-select">
                  <option value="00">00</option>
                  <option value="30">30</option>
                </select>
              </div>
            </div>
            
            <div class="form-group">
              <label>เวลาสิ้นสุด (End)</label>
              <div class="time-picker-custom">
                <select v-model="endTime.h" class="time-select">
                  <option v-for="h in hourOptions" :key="'eh'+h" :value="h">{{ h }}</option>
                </select>
                <span class="sep">:</span>
                <select v-model="endTime.m" class="time-select">
                  <option value="00">00</option>
                  <option value="30">30</option>
                </select>
              </div>
            </div>
          </div>

          <!-- ข้อความแจ้งเตือนถ้ากรอกนอกช่วงเวลา -->
          <p v-if="!isStartTimeValid || !isEndTimeValid" class="warning-text">
            * เวลาที่เลือกไม่อยู่ในช่วงที่บริษัทกำหนดให้ทำโอทีได้
          </p>

          <!-- ข้อความแจ้งเตือนนาทีไม่ตรงรอบ -->
          <p v-if="!isTimeStepValid && otForm.end_time" class="warning-text">
            * กรุณาเลือกเวลาเป็นรอบ 00 หรือ 30 นาทีเท่านั้น
          </p>

          <!-- ข้อความแจ้งเตือนช่วงเวลาที่อนุญาตให้ขอ (Request Window) -->
          <div v-if="!isInRequestWindow && !isLoadingRules" class="request-window-alert">
            <i class="fas fa-exclamation-triangle"></i>
            <div>
              <strong>หมดเวลาส่งคำขอ OT</strong>
              <p>บริษัทกำหนดให้ส่งคำขอได้เฉพาะช่วงเวลา {{ configs.ot_request_start_time || '08:00' }} - {{ configs.ot_request_end_time || '16:00' }} เท่านั้น</p>
            </div>
          </div>

          <div class="form-group full">
            <label>เหตุผล (Reason)</label>
            <textarea v-model="otForm.reason" class="form-input" placeholder="ระบุเหตุผลในการทำโอที..."></textarea>
          </div>

          <!-- ส่วนสรุปชั่วโมงคำนวณอัตโนมัติ -->
          <div class="calculation-card">
            <div class="calc-row">
              <span>Standard OT:</span>
              <span class="hours">{{ otSummary.std }} hrs.</span>
            </div>
            <div class="calc-row">
              <span>Special OT:</span>
              <span class="hours special">{{ otSummary.sp }} hrs.</span>
            </div>
            <div class="calc-total">
              Total: <strong>{{ otCalculated.total }}</strong> hrs.
            </div>
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn-cancel" @click="$emit('close')">Cancel</button>
          <button class="btn-submit" @click="submitOTRequest" :disabled="isSubmitting || !isInRequestWindow || !isTimeStepValid">
            {{ isSubmitting ? 'Sending...' : 'Request OT' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import axios from 'axios'

const props = defineProps({
  isOpen: Boolean,
  user: Object,
  attendanceLogs: { type: Array, default: () => [] } 
})

const emit = defineEmits(['close', 'submitted'])

const otForm = ref({
  request_date: new Date().toISOString().split('T')[0],
  start_time: '17:00',
  end_time: '19:00',
  reason: ''
})

const startTime = ref({ h: '17', m: '00' })
const endTime = ref({ h: '19', m: '00' })

// --- 2. Initial Data & Rules ---
const isSubmitting = ref(false)
const isLoadingRules = ref(true)
const actualDayLog = ref(null) 
const configs = ref({})

// --- 3. Computed & Logic ---
const requesterName = computed(() => `${props.user?.first_name || ''} ${props.user?.last_name || ''}`)

const hourOptions = computed(() => {
  const start = parseInt(configs.value.ot_normal_start?.split(':')[0] || '17')
  const end = parseInt(configs.value.ot_normal_end?.split(':')[0] || '22')
  const options = []
  if (start <= end) {
    for (let i = start; i <= end; i++) options.push(String(i).padStart(2, '0'))
  } else {
    for (let i = start; i < 24; i++) options.push(String(i).padStart(2, '0'))
    for (let i = 0; i <= end; i++) options.push(String(i).padStart(2, '0'))
  }
  return options
})

// Sync Dropdown -> otForm
watch([startTime, endTime], () => {
  otForm.value.start_time = `${startTime.value.h}:${startTime.value.m}`
  otForm.value.end_time = `${endTime.value.h}:${endTime.value.m}`
}, { deep: true })

// --- 2. Watchers & Actions ---
// ค้นหา Log จริงเมื่อเปลี่ยนวันที่
watch(() => otForm.value.request_date, (newDate) => {
  if (!newDate) {
    actualDayLog.value = null
    return
  }
  actualDayLog.value = props.attendanceLogs.find(l => l.date === newDate) || null
}, { immediate: true })

// ฟังก์ชันดึงเวลาเลิกงานจริงมาใส่ในฟอร์ม (พร้อมปัดเศษลง 30 นาที)
const useActualTime = () => {
  if (actualDayLog.value?.actual_check_out) {
    const checkOut = new Date(actualDayLog.value.actual_check_out)
    const hh = String(checkOut.getHours()).padStart(2, '0')
    let mm = checkOut.getMinutes()
    
    // ปัดเศษนาทีลง
    const mmStr = mm >= 30 ? '30' : '00'
    
    startTime.value = { h: configs.value.ot_normal_start?.split(':')[0] || '17', m: '00' }
    endTime.value = { h: hh, m: mmStr }
  }
}

// --- 3. Fetch Logic (ดึงค่าจาก DB มาเก็บไว้แบบที่นายสั่ง) ---
const fetchOTRules = async () => {
  try {
    isLoadingRules.value = true
    const res = await api.get('/attendance/ot-rules')
    configs.value = res.data
  } catch (e) {
    console.warn('Using default OT rules.')
  } finally {
    isLoadingRules.value = false
  }
}

onMounted(() => {
  fetchOTRules()
})

// ช่วยแสดงผลเวลาจริงบน UI
const formatActualTime = (isoStr) => {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  return d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', hour12: false })
}

// --- 3. Calculation Logic ---
const timeToMin = (timeStr) => {
  if (!timeStr) return 0
  const [h, m] = timeStr.split(':').map(Number)
  return h * 60 + m
}

const isStartTimeValid = computed(() => validateTime(otForm.value.start_time))
const isEndTimeValid = computed(() => validateTime(otForm.value.end_time))

function validateTime(time) {
  if (!time) return true
  const cur = timeToMin(time)
  
  // ช่วงเย็น/ดึก (Evening/Midnight)
  const normS = timeToMin(configs.value.ot_normal_start || '17:00')
  const specE = timeToMin(configs.value.ot_special_end || '06:00')
  
  // ช่วงเช้า (Morning)
  const mornS = timeToMin(configs.value.ot_morning_start || '05:00')
  const mornE = timeToMin(configs.value.ot_morning_end || '08:00')
  
  // เช็คช่วงเย็น (ข้ามคืน)
  const isInEveningRange = (normS > specE) ? (cur >= normS || cur <= specE) : (cur >= normS && cur <= specE)
  
  // เช็คช่วงเช้า
  const isInMorningRange = (cur >= mornS && cur <= mornE)
  
  return isInEveningRange || isInMorningRange
}

const otCalculated = computed(() => {
  const { start_time, end_time, request_date } = otForm.value
  if (!start_time || !end_time) return { total: '0.0', std: '0.0', sp: '0.0' }
  
  const startMin = timeToMin(start_time)
  const endMin = timeToMin(end_time)
  
  // กฎเวลาจาก Config
  const normStart = timeToMin(configs.value.ot_normal_start || '17:00')
  const normEnd = timeToMin(configs.value.ot_normal_end || '22:00')
  
  const mornStart = timeToMin(configs.value.ot_morning_start || '05:00')
  const mornEnd = timeToMin(configs.value.ot_morning_end || '08:00')

  // คำนวณชั่วโมงทั้งหมด (รองรับข้ามคืน)
  let totalMin = endMin - startMin
  if (totalMin <= 0) totalMin += 1440
  
  const isWeekend = [0, 6].includes(new Date(request_date).getDay())
  
  if (isWeekend) {
    return { total: (totalMin / 60).toFixed(1), std: '0.0', sp: (totalMin / 60).toFixed(1) }
  }

  let stdMin = 0
  let spMin = 0
  
  for (let m = 0; m < totalMin; m++) {
    const current = (startMin + m) % 1440
    
    // ช่วง Standard ปกติ (เย็น)
    const isInEveningStandard = (normStart < normEnd) 
      ? (current >= normStart && current < normEnd)
      : (current >= normStart || current < normEnd)
      
    // ช่วง Standard ใหม่ (เช้า)
    const isInMorningStandard = (current >= mornStart && current < mornEnd)
      
    if (isInEveningStandard || isInMorningStandard) {
      stdMin++
    } else {
      spMin++
    }
  }

  return {
    total: (totalMin / 60).toFixed(1),
    std: (stdMin / 60).toFixed(1),
    sp: (spMin / 60).toFixed(1)
  }
})

// ตรวจสอบว่าตอนนี้อยู่ในช่วงเวลาที่อนุญาตให้กดขอหรือไม่
const isInRequestWindow = computed(() => {
  const start = configs.value.ot_request_start_time || '08:00'
  const end = configs.value.ot_request_end_time || '16:00'
  
  const now = new Date()
  const currentMin = now.getHours() * 60 + now.getMinutes()
  
  const timeToMinLocal = (t) => {
    const [h, m] = t.split(':').map(Number)
    return h * 60 + m
  }
  
  const startMin = timeToMinLocal(start)
  const endMin = timeToMinLocal(end)
  
  if (startMin <= endMin) {
    return currentMin >= startMin && currentMin <= endMin
  } else {
    // กรณีข้ามคืน
    return currentMin >= startMin || currentMin <= endMin
  }
})

// ตรวจสอบว่านาทีลงท้ายด้วย 00 หรือ 30 หรือไม่
const isTimeStepValid = computed(() => {
  if (!otForm.value.start_time || !otForm.value.end_time) return false
  const sMin = parseInt(otForm.value.start_time.split(':')[1])
  const eMin = parseInt(otForm.value.end_time.split(':')[1])
  return [0, 30].includes(sMin) && [0, 30].includes(eMin)
})

// --- 4. Watcher (Reset form when opened) ---
watch(() => props.isOpen, (val) => {
  if (val) {
    fetchOTRules()
    const today = new Date().toISOString().split('T')[0]
    otForm.value = { request_date: today, start_time: '17:00', end_time: '19:00', reason: '' }
    startTime.value = { h: '17', m: '00' }
    endTime.value = { h: '19', m: '00' }
  }
})

// --- 5. Submit ---
const submitOTRequest = async () => {
  if (!otForm.value.reason.trim()) return alert('กรุณาระบุเหตุผลในการทำโอที')
  
  isSubmitting.value = true
  try {
    const summary = otSummary.value
    await api.post('/attendance/ot-requests', {
      ...otForm.value,
      standard_hours: parseFloat(summary.std),
      special_hours: parseFloat(summary.sp)
    })
    alert('✅ ส่งคำขอเรียบร้อยแล้ว')
    emit('submitted')
    emit('close')
  } catch (e) {
    alert(e.response?.data?.detail || 'ขอโอทีไม่สำเร็จ')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center; z-index: 9999;
  padding: 16px; /* กันชนขอบจอ */
}

.modal-content {
  background: white; width: calc(100% - 32px); max-width: 380px; border-radius: 20px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15); animation: zoomIn 0.3s ease-out;
  max-height: 90vh; display: flex; flex-direction: column; overflow: hidden;
  box-sizing: border-box; margin: auto;
}

@keyframes zoomIn { from { transform: scale(0.95); opacity: 0; } to { transform: scale(1); opacity: 1; } }

.modal-header {
  padding: 20px 24px; border-bottom: 1px solid #f1f5f9;
  display: flex; justify-content: space-between; align-items: center;
  box-sizing: border-box;
}

.modal-header h3 { margin: 0; color: #0f172a; font-size: 1.1rem; display: flex; align-items: center; gap: 10px; }
.close-btn { background: none; border: none; font-size: 1.2rem; color: #94a3b8; cursor: pointer; }

.modal-body { 
  padding: 24px 30px 24px 24px; /* ปรับให้ขยับกลับมาทางขวามากขึ้น (30px) เพื่อความสมดุล */
  overflow-y: auto;
  box-sizing: border-box;
  width: 100%;
}
.ot-form { 
  display: flex; 
  flex-direction: column; 
  gap: 20px; 
  width: 100%; 
  box-sizing: border-box; 
}

.info-card { background: #f0fdf4; padding: 14px 20px; border-radius: 16px; border: 1px solid #dcfce7; display: flex; flex-direction: column; gap: 4px; box-sizing: border-box; width: 100%; }
.info-card .label { font-size: 0.75rem; color: #166534; font-weight: 700; text-transform: uppercase; }
.info-card .value { font-size: 1.1rem; color: #064e3b; font-weight: 800; }

.rules-summary { background: #f0f9ff; padding: 14px 18px; border-radius: 12px; border: 1px solid #e0f2fe; display: flex; flex-direction: column; gap: 6px; box-sizing: border-box; width: 100%; }
.rule-item { font-size: 0.8rem; color: #0369a1; display: flex; align-items: center; gap: 8px; }
.dot { width: 8px; height: 8px; border-radius: 50%; }
.dot.std { background: #0ea5e9; }
.dot.morn { background: #f59e0b; }
.dot.sp { background: #22c55e; }

.form-grid { 
  display: grid; 
  grid-template-columns: 1fr 1fr; 
  gap: 32px; /* เพิ่มระยะห่างระหว่างช่องซ้าย-ขวาให้มากขึ้น */
  width: 100%; 
  box-sizing: border-box;
}

/* Responsive Grid สำหรับหน้าจอเล็ก */
@media (max-width: 400px) {
  .form-grid { grid-template-columns: 1fr; gap: 16px; }
}

.form-group { 
  width: 100%; 
  box-sizing: border-box; 
  display: flex; 
  flex-direction: column; 
  align-items: center; /* จัดทุกอย่างในกลุ่มฟอร์มให้เข้ากึ่งกลาง */
}
.form-group.full { grid-column: span 1; }
@media (min-width: 401px) {
  .form-group.full { grid-column: span 2; }
}

.form-group label { 
  display: block; 
  font-size: 0.7rem; /* ย่อขนาดลงเล็กน้อย */
  font-weight: 800; 
  color: #64748b; 
  margin-bottom: 8px; 
  text-align: center; 
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.form-input {
  width: 95%; /* ปรับความกว้างให้ดูสมดุลเมื่ออยู่กึ่งกลาง */
  padding: 10px 14px; border: 2px solid #e2e8f0; border-radius: 12px;
  font-size: 0.95rem; color: #1e293b; transition: all 0.2s;
  box-sizing: border-box;
  box-shadow: 0 1px 2px rgba(0,0,0,0.02);
  text-align: center; /* จัดข้อความข้างใน (ถ้า Browser รองรับ) ให้เข้ากึ่งกลางด้วย */
}
.form-input:focus { border-color: #3b82f6; outline: none; box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1); }
.form-input.error { border-color: #ef4444; background: #fff1f2; }

textarea.form-input { min-height: 80px; resize: none; width: 95%; text-align: left; }

.warning-text { font-size: 0.7rem; color: #ef4444; margin: -12px 0 12px 0; font-weight: 600; }

.calculation-card { background: #fafafa; border: 2px dashed #e2e8f0; border-radius: 16px; padding: 16px; margin-top: 4px; box-sizing: border-box; width: 100%; }
.calc-row { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 0.85rem; color: #64748b; }
.hours { font-weight: 800; color: #0ea5e9; }
.hours.special { color: #22c55e; }
.calc-total { border-top: 1px solid #e2e8f0; padding-top: 8px; margin-top: 8px; text-align: center; color: #0f172a; font-size: 1rem; }

.modal-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 16px; box-sizing: border-box; width: 100%; }
.btn-cancel { padding: 12px; background: #f1f5f9; border: none; border-radius: 12px; font-weight: 700; color: #64748b; cursor: pointer; transition: 0.2s; font-size: 0.95rem; }
.btn-submit { padding: 12px; background: #0ea5e9; border: none; border-radius: 12px; font-weight: 700; color: white; cursor: pointer; transition: 0.2s; font-size: 0.95rem; box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3); }
.btn-submit:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(14, 165, 233, 0.4); background: #0284c7; }
.btn-submit:disabled { opacity: 0.6; transform: none; cursor: not-allowed; }

/* สไตล์ปุ่มดึงเวลาจริง */
.actual-info-row {
  margin-top: 10px;
  width: 95%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8fafc;
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px dashed #3498db66;
  font-size: 0.8rem;
  color: #475569;
}

.btn-text-action {
  background: white;
  border: 1px solid #3498db;
  color: #3498db;
  font-weight: 800;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 8px;
  transition: 0.2s;
  font-size: 0.75rem;
}

.btn-text-action:hover {
  background: #3498db;
  color: white;
  box-shadow: 0 4px 10px rgba(52, 152, 219, 0.2);
}

/* Alert สำหรับช่วงเวลาที่ไม่อนุญาตให้ขอ OT */
.request-window-alert {
  background: #fff1f2;
  border: 1px solid #fda4af;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  gap: 12px;
  align-items: flex-start;
  color: #9f1239;
  margin-bottom: 10px;
}
.request-window-alert i { font-size: 1.2rem; margin-top: 2px; }
.request-window-alert strong { display: block; font-size: 0.95rem; margin-bottom: 2px; }
.request-window-alert p { margin: 0; font-size: 0.8rem; line-height: 1.4; opacity: 0.9; }

/* Custom Time Picker Styles */
.time-picker-custom {
  display: flex;
  align-items: center;
  gap: 5px;
}
.time-select {
  flex: 1;
  padding: 10px 5px;
  border: 1.5px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 700;
  text-align: center;
  background-color: #fff;
  cursor: pointer;
  appearance: none; /* Hide default arrow to make it cleaner */
  -webkit-appearance: none;
}
.time-select:focus {
  border-color: #3b82f6;
  outline: none;
}
.time-picker-custom .sep {
  font-weight: 900;
  color: #64748b;
}

.step-info {
  font-size: 0.72rem;
  color: #64748b;
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 5px;
}
.step-info i { color: #3b82f6; }
</style>
