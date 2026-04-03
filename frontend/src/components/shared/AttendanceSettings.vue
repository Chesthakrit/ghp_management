<template>
  <div class="attendance-settings-container">
    <div class="header-banner">
      <h2><i class="fas fa-business-time"></i> Time & Leave Settings</h2>
      <p class="subtitle">Configure standard working hours, optional shift configurations, and leave quotas.</p>
    </div>

    <!-- Working Hours Config -->
    <div class="settings-card">
      <div class="card-header">
        <h3><i class="fas fa-clock"></i> Standard Working Hours</h3>
        <button class="btn-save btn-sm" @click="saveConfigs('hours')">Save Config</button>
      </div>
      <div class="card-body">
        <div class="form-row">
          <div class="form-group">
            <label>Check-in Time</label>
            <input type="time" class="form-input" v-model="config.check_in_time" />
          </div>
          <div class="form-group">
            <label>Late Grace Period (mins)</label>
            <input type="number" class="form-input" v-model="config.late_grace_period_mins" />
            <small class="hint">Allow checking in late up to this without penalty.</small>
          </div>
          <div class="form-group">
            <label>Check-out Time</label>
            <input type="time" class="form-input" v-model="config.check_out_time" />
          </div>
        </div>
      </div>
    </div>

    <!-- Overtime Rules Config -->
    <div class="settings-card">
      <div class="card-header">
        <h3><i class="fas fa-business-time"></i> Overtime (OT) Rules</h3>
        <button class="btn-save btn-sm" @click="saveConfigs('ot')">Save OT Config</button>
      </div>
      <div class="card-body">
        <div class="ot-grid">
          <div class="ot-item">
            <div class="ot-header">
              <span class="ot-title">Standard Overtime</span>
            </div>
            <div class="form-group row-align">
              <label>Time Range</label>
              <div class="time-range-box">
                <input type="time" class="form-input" v-model="config.ot_normal_start" />
                <span class="separator">to</span>
                <input type="time" class="form-input" v-model="config.ot_normal_end" />
              </div>
            </div>
          </div>
          
          <div class="ot-item special">
            <div class="ot-header">
              <span class="ot-title">Special Overtime</span>
            </div>
            <div class="form-group row-align">
              <label>Time Range</label>
              <div class="time-range-box">
                <input type="time" class="form-input" v-model="config.ot_special_start" />
                <span class="separator">to</span>
                <input type="time" class="form-input" v-model="config.ot_special_end" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Leave Quota Config -->
    <div class="settings-card">
      <div class="card-header">
        <h3><i class="fas fa-calendar-times"></i> Leave Quotas (Days/Year)</h3>
        <button class="btn-save btn-sm" @click="saveConfigs('leaves')">Save Quotas</button>
      </div>
      <div class="card-body">
         <div class="leave-grid">
           <div class="leave-item">
             <div class="leave-icon sick"><i class="fas fa-briefcase-medical"></i></div>
             <div class="leave-info">
               <label>Sick Leave</label>
               <input type="number" class="form-input small" v-model="config.quota_sick_leave" />
             </div>
           </div>
           
           <div class="leave-item">
             <div class="leave-icon vacation"><i class="fas fa-umbrella-beach"></i></div>
             <div class="leave-info">
               <label>Annual Leave</label>
               <input type="number" class="form-input small" v-model="config.quota_annual_leave" />
             </div>
           </div>
           
           <div class="leave-item">
             <div class="leave-icon personal"><i class="fas fa-user-clock"></i></div>
             <div class="leave-info">
               <label>Personal Leave</label>
               <input type="number" class="form-input small" v-model="config.quota_personal_leave" />
             </div>
           </div>
         </div>
      </div>
    </div>

    <!-- Public Holidays Config -->
    <div class="settings-card">
      <div class="card-header">
        <div class="holiday-title-group">
          <h3><i class="fas fa-calendar-star"></i> Public Holidays</h3>
          <select class="form-input small year-selector" v-model="selectedYear">
            <option v-for="year in availableYears" :key="year" :value="year">{{ year }}</option>
          </select>
        </div>
        <button class="btn-save btn-sm" @click="addHoliday"><i class="fas fa-plus"></i> Add Holiday</button>
      </div>
      <div class="card-body">
        <p class="hint" style="margin-top: 0; margin-bottom: 16px;">Labor law requires configuring a minimum of 13 public holidays per calendar year.</p>
        
        <div class="holidays-list">
          <table class="holiday-table">
            <thead>
              <tr>
                <th width="150">Date</th>
                <th>Holiday Name</th>
                <th width="80">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="hol in holidays" :key="hol.id">
                <td>
                  <input type="date" class="form-input" v-model="hol.date" @change="updateHoliday(hol)" />
                </td>
                <td>
                  <input type="text" class="form-input" v-model="hol.name" @change="updateHoliday(hol)" />
                </td>
                <td>
                  <button class="btn-icon delete" @mousedown.prevent="deleteHoliday(hol)"><i class="fas fa-trash-alt"></i></button>
                </td>
              </tr>
              <tr v-if="holidays.length === 0">
                <td colspan="3" class="text-center" style="padding: 24px; color: #94a3b8; text-align: center;">No holidays configured for {{ selectedYear }}. Click 'Add Holiday' to begin.</td>
              </tr>
            </tbody>
          </table>
          <div class="holiday-summary">
            <span>Total Configured: <strong>{{ holidays.length }}</strong> / 13 Days Minimum</span>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import api from '../../api'
import Swal from 'sweetalert2'

const userPermissions = ref(JSON.parse(localStorage.getItem('user_permissions') || '[]'))
const dbUser = ref(JSON.parse(localStorage.getItem('user_data') || '{}'))

const isAdmin = computed(() => {
  return dbUser.value?.username === 'admin' || dbUser.value?.role?.name === 'admin'
})

const canEdit = (section) => {
  return true
}

const currentYear = new Date().getFullYear()

// Config Data
const config = ref({
  check_in_time: '08:00',
  check_out_time: '17:00',
  late_grace_period_mins: '15',
  ot_normal_start: '17:00',
  ot_normal_end: '22:00',
  ot_special_start: '22:00',
  ot_special_end: '06:00',
  quota_sick_leave: '30',
  quota_annual_leave: '6',
  quota_personal_leave: '3'
})

const fetchConfigs = async () => {
  try {
    const res = await api.get('/attendance/settings')
    if (res.data?.length > 0) {
      res.data.forEach(item => {
        if (config.value[item.key] !== undefined) {
          config.value[item.key] = item.value
        }
      })
    }
  } catch (err) {
    console.error("Failed to load configs", err)
  }
}

const saveConfigs = async (type) => {
  try {
    let keysToSave = []
    if (type === 'hours') keysToSave = ['check_in_time', 'check_out_time', 'late_grace_period_mins']
    if (type === 'ot') keysToSave = ['ot_normal_start', 'ot_normal_end', 'ot_special_start', 'ot_special_end']
    if (type === 'leaves') keysToSave = ['quota_sick_leave', 'quota_annual_leave', 'quota_personal_leave']

    const payload = keysToSave.map(k => ({ key: k, value: String(config.value[k]) }))
    await api.put('/attendance/settings', payload)
    
    let groupName = type === 'hours' ? 'Working Hours' : type === 'ot' ? 'Overtime Rules' : 'Leave Quotas'
    Swal.fire({
      toast: true, position: 'top-end',
      icon: 'success', title: `${groupName} Saved!`,
      timer: 2000, showConfirmButton: false
    })
  } catch (err) {
    Swal.fire('Error', 'Failed to save configurations', 'error')
    console.error(err)
  }
}

// ----- Holidays Logic -----
const selectedYear = ref(currentYear)
const availableYears = computed(() => {
  const years = []
  for (let i = currentYear - 5; i <= currentYear + 5; i++) {
    years.push(i)
  }
  return years
})

const holidays = ref([])

const fetchHolidays = async () => {
  try {
    const res = await api.get(`/attendance/holidays/${selectedYear.value}`)
    holidays.value = res.data || []
  } catch (err) {
    console.error("Failed to load holidays", err)
  }
}

// Reload when year changes
watch(selectedYear, fetchHolidays)

const addHoliday = async () => {
  const { value: formValues } = await Swal.fire({
    title: 'Add Public Holiday',
    html:
      `<input id="swal-date" type="date" class="swal2-input" value="${selectedYear.value}-01-01">` +
      `<input id="swal-name" type="text" class="swal2-input" placeholder="Holiday Name (e.g. New Year's Day)">`,
    focusConfirm: false,
    showCancelButton: true,
    preConfirm: () => {
      const date = document.getElementById('swal-date').value
      const name = document.getElementById('swal-name').value
      if (!date || !name) Swal.showValidationMessage('Please fill both fields')
      return { date, name }
    }
  })

  if (formValues) {
    try {
      await api.post('/attendance/holidays', {
        year: selectedYear.value,
        date: formValues.date,
        name: formValues.name
      })
      Swal.fire({ toast: true, position: 'top-end', icon: 'success', title: 'Holiday Added', timer: 1500, showConfirmButton: false })
      fetchHolidays()
    } catch (err) {
      Swal.fire('Error', 'Failed to add holiday', 'error')
    }
  }
}

const updateHoliday = async (hol) => {
  try {
    if (!hol.date || !hol.name) return
    await api.put(`/attendance/holidays/${hol.id}`, {
      year: selectedYear.value,
      date: hol.date,
      name: hol.name
    })
    Swal.fire({ toast: true, position: 'top-end', icon: 'success', title: 'Holiday updated', showConfirmButton: false, timer: 1500 })
  } catch (err) {
    console.error(err)
    Swal.fire('Error', 'Failed to update holiday', 'error')
  }
}

const deleteHoliday = async (hol) => {
  const res = await Swal.fire({
    title: 'Delete this holiday?',
    text: `Are you sure you want to remove "${hol.name}"?`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#ef4444',
    confirmButtonText: 'Yes, delete it'
  })
  if (res.isConfirmed) {
    try {
      await api.delete(`/attendance/holidays/${hol.id}`)
      Swal.fire({ toast: true, position: 'top-end', icon: 'success', title: 'Deleted', timer: 1500, showConfirmButton: false })
      fetchHolidays()
    } catch (err) {
      Swal.fire('Error', 'Failed to delete', 'error')
    }
  }
}

onMounted(() => {
  fetchConfigs()
  fetchHolidays()
})
</script>

<style scoped>
.attendance-settings-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.header-banner {
  background: white;
  padding: 24px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.header-banner h2 {
  margin: 0;
  color: #1e293b;
  font-size: 1.25rem;
  display: flex;
  align-items: center;
  gap: 10px;
}

.subtitle {
  margin: 8px 0 0 0;
  color: #64748b;
  font-size: 0.95rem;
}

.settings-card {
  background: white;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

.card-header {
  background: #f8fafc;
  padding: 16px 20px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.holiday-title-group {
  display: flex;
  align-items: center;
  gap: 16px;
}

.year-selector {
  width: auto;
  min-width: 100px;
  padding: 6px 12px;
  font-weight: 600;
  cursor: pointer;
}

.card-header h3 {
  margin: 0;
  font-size: 1.05rem;
  color: #334155;
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-body {
  padding: 24px;
}

.form-row {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
  min-width: 200px;
}

.form-group label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #475569;
}

.form-input {
  padding: 10px 14px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.95rem;
  outline: none;
  transition: border-color 0.2s;
  font-family: inherit;
}

.form-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input.small {
  width: 80px;
  text-align: center;
}

.hint {
  font-size: 0.75rem;
  color: #94a3b8;
}

.btn-save {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s;
}

.btn-save:hover {
  background: #2563eb;
}

.leave-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.leave-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
}

.leave-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
}

.leave-icon.sick { background: #ef4444; }
.leave-icon.vacation { background: #10b981; }
.leave-icon.personal { background: #f59e0b; }

.leave-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.leave-info label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #334155;
}

.holiday-table {
  width: 100%;
  border-collapse: collapse;
}

.holiday-table th {
  text-align: left;
  padding: 12px;
  background: #f1f5f9;
  font-size: 0.85rem;
  color: #475569;
  font-weight: 600;
  border-bottom: 2px solid #e2e8f0;
}

.holiday-table td {
  padding: 12px;
  border-bottom: 1px solid #e2e8f0;
  vertical-align: middle;
}

.holiday-table .form-input {
  width: 100%;
}

.btn-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: none;
  background: #fef2f2;
  color: #ef4444;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: 0.2s;
}

.btn-icon:hover {
  background: #fee2e2;
  color: #b91c1c;
}

.holiday-summary {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px dashed #cbd5e1;
  text-align: right;
  font-size: 0.95rem;
  color: #64748b;
}

.holiday-summary strong {
  color: #3b82f6;
  font-size: 1.1rem;
}

/* OT Rules Styles */
.ot-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.ot-item {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.2s;
}

.ot-item.special {
  background: #fffcf2;
  border-color: #fce38a;
}

.ot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  border-bottom: 2px dashed #cbd5e1;
  padding-bottom: 12px;
}

.ot-item.special .ot-header {
  border-bottom-color: #fde047;
}

.ot-title {
  font-weight: 700;
  color: #1e293b;
  font-size: 1.05rem;
}

.ot-rate-hint {
  font-size: 0.75rem;
  background: #e0f2fe;
  color: #0284c7;
  padding: 4px 8px;
  border-radius: 6px;
  font-weight: 700;
}

.ot-item.special .ot-rate-hint {
  background: #fef08a;
  color: #a16207;
}

.row-align {
  display: block;
}

.time-range-box {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 6px;
}

.time-range-box .form-input {
  flex: 1;
  text-align: center;
}

.separator {
  color: #94a3b8;
  font-size: 0.9rem;
  font-weight: 500;
}
</style>
