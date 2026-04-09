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

          <!-- ช่วงเวลาอ้างอิงจากบริษัท (ดึงจาก DB) -->
          <div class="rules-summary">
             <div class="rule-item">
               <span class="dot std"></span>
               Standard: <strong>{{ configs.ot_normal_start || '17:00' }} - {{ configs.ot_normal_end || '22:00' }}</strong>
             </div>
             <div class="rule-item">
               <span class="dot sp"></span>
               Special: <strong>{{ configs.ot_special_start || '22:00' }} - {{ configs.ot_special_end || '06:00' }}</strong>
             </div>
          </div>

          <!-- แบบฟอร์มกรอกข้อมูล -->
          <div class="form-grid">
            <div class="form-group full">
              <label>วันที่ขอ (Date)</label>
              <input type="date" v-model="otForm.request_date" class="form-input" />
              
              <!-- ปุ่มกดดึงเวลาจริง (ปลาบปลื้มใจแน่นอนครับ) -->
              <div v-if="actualDayLog?.check_out_time" class="actual-info-row">
                <span>เลิกงานจริง: <strong>{{ formatActualTime(actualDayLog.check_out_time) }}</strong></span>
                <button class="btn-text-action" @click="useActualTime">
                  <i class="fas fa-magic"></i> ใช้เวลาเลิกงานจริง
                </button>
              </div>
            </div>

            <div class="form-group">
              <label>เวลาเริ่ม (Start)</label>
              <input type="time" v-model="otForm.start_time" 
                     :class="['form-input', { 'error': !isStartTimeValid }]" />
            </div>
            
            <div class="form-group">
              <label>เวลาสิ้นสุด (End)</label>
              <input type="time" v-model="otForm.end_time" 
                     :class="['form-input', { 'error': !isEndTimeValid }]" />
            </div>
          </div>

          <!-- ข้อความแจ้งเตือนถ้ากรอกนอกช่วงเวลา -->
          <p v-if="!isStartTimeValid || !isEndTimeValid" class="warning-text">
            * กรุณาเลือกเวลาในช่วง {{ configs.ot_normal_start || '17:00' }} ถึง {{ configs.ot_special_end || '06:00' }}
          </p>

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
              Total: <strong>{{ otSummary.total }}</strong> hrs.
            </div>
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn-cancel" @click="$emit('close')">Cancel</button>
          <button class="btn-submit" @click="submitOTRequest" :disabled="isSubmitting">
            {{ isSubmitting ? 'Sending...' : 'Request OT' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import api from '../../api'

const props = defineProps({
  isOpen: Boolean,
  requesterName: String,
  attendanceLogs: { type: Array, default: () => [] } 
})

const emit = defineEmits(['close', 'submitted'])

// --- 1. State ---
const configs = ref({}) 
const otForm = ref({
  request_date: new Date().toISOString().split('T')[0],
  start_time: '17:30',
  end_time: '20:30',
  reason: ''
})
const isSubmitting = ref(false)
const actualDayLog = ref(null) // เก็บ Log จริงของวันที่เลือก

// --- 2. Watchers & Actions ---
// ค้นหา Log จริงเมื่อเปลี่ยนวันที่
watch(() => otForm.value.request_date, (newDate) => {
  if (!newDate) {
    actualDayLog.value = null
    return
  }
  actualDayLog.value = props.attendanceLogs.find(l => l.date === newDate) || null
}, { immediate: true })

// ฟังก์ชันดึงเวลาเลิกงานจริงมาใส่ในฟอร์ม
const useActualTime = () => {
  if (actualDayLog.value?.check_out_time) {
    const checkOut = new Date(actualDayLog.value.check_out_time)
    const hh = String(checkOut.getHours()).padStart(2, '0')
    const mm = String(checkOut.getMinutes()).padStart(2, '0')
    
    otForm.value.start_time = configs.value.ot_normal_start || '17:00'
    otForm.value.end_time = `${hh}:${mm}`
  }
}

// --- 3. Fetch Logic (ดึงค่าจาก DB มาเก็บไว้แบบที่นายสั่ง) ---
const fetchOTRules = async () => {
  try {
    const res = await api.get('/attendance/ot-rules')
    configs.value = res.data
  } catch (e) {
    console.warn('Using default OT rules.')
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
  const min = timeToMin(configs.value.ot_normal_start || '17:00')
  const max = timeToMin(configs.value.ot_special_end || '06:00')
  const cur = timeToMin(time)
  
  if (min > max) return cur >= min || cur <= max
  return cur >= min && cur <= max
}

const otSummary = computed(() => {
  const { start_time, end_time, request_date } = otForm.value
  if (!start_time || !end_time) return { total: '0.0', std: '0.0', sp: '0.0' }
  
  const startMin = timeToMin(start_time)
  const endMin = timeToMin(end_time)
  
  // กฎเวลาจาก Config (ถ้าไม่มีใช้ 17:00 - 22:00 - 06:00)
  const normStart = timeToMin(configs.value.ot_normal_start || '17:00')
  const normEnd = timeToMin(configs.value.ot_normal_end || '22:00')
  const specEnd = timeToMin(configs.value.ot_special_end || '06:00')

  // คำนวณชั่วโมงทั้งหมด (รองรับข้ามคืน)
  let totalMin = endMin - startMin
  if (totalMin <= 0) totalMin += 1440
  
  const isWeekend = [0, 6].includes(new Date(request_date).getDay())
  
  // ถ้าเป็นวันหยุด (Weekend) ให้เป็น Special ทั้งหมด
  if (isWeekend) {
    return {
      total: (totalMin / 60).toFixed(1),
      std: '0.0',
      sp: (totalMin / 60).toFixed(1)
    }
  }

  // --- ลอจิกการ "ผ่าช่วง" สำหรับวันทำงานปกติ ---
  let stdMin = 0
  let spMin = 0
  
  // จำลองเวลาเป็นจุดๆ ใน 24-48 ชม. เพื่อให้คำนวณช่วงรอยต่อได้ง่าย
  for (let m = 0; m < totalMin; m++) {
    const current = (startMin + m) % 1440
    
    // ตรวจสอบว่านาทีนี้อยู่ในช่วง Standard (Normal Start -> Normal End) หรือไม่
    // หมายเหตุ: ลอจิกนี้รองรับกรณี Normal End อยู่หลังเที่ยงคืนด้วย
    const isInStandard = (normStart < normEnd) 
      ? (current >= normStart && current < normEnd)
      : (current >= normStart || current < normEnd)
      
    if (isInStandard) {
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

// --- 4. Watcher (Reset form when opened) ---
watch(() => props.isOpen, (val) => {
  if (val) {
    fetchOTRules()
    otForm.value.start_time = configs.value.ot_normal_start || '17:30'
    otForm.value.end_time = configs.value.ot_special_end || '22:30'
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
</style>
