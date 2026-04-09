<template>
  <div class="attendance-settings-container">
    <div class="header-banner">
      <h2><i class="fas fa-business-time"></i> Time & Leave Settings</h2>
      <p class="subtitle">Configure standard working hours, optional shift configurations, and leave quotas.</p>
    </div>

    <!-- 1. WORKING HOURS -->
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
            <small class="hint">Allow checking in late without penalty.</small>
          </div>
          <div class="form-group">
            <label>Check-out Time</label>
            <input type="time" class="form-input" v-model="config.check_out_time" />
          </div>
        </div>
      </div>
    </div>

    <!-- 2. LOCATION MANAGEMENT (NEW) -->
    <div class="settings-card location-mgmt">
      <div class="card-header">
        <h3><i class="fas fa-map-marked-alt"></i> Location Management</h3>
        <div class="location-tabs">
          <button :class="['loc-tab-btn', { active: activeLocTab === 'fixed' }]" @click="activeLocTab = 'fixed'">Fixed Locations</button>
          <button :class="['loc-tab-btn', { active: activeLocTab === 'onsite' }]" @click="activeLocTab = 'onsite'">On-site Projects</button>
        </div>
      </div>
      <div class="card-body">
        
        <!-- Fixed Locations Tab -->
        <div v-if="activeLocTab === 'fixed'" class="loc-content-fade">
          <div class="loc-actions-header">
            <p class="section-desc">เพิ่ม/จัดการสถานที่ประจำของบริษัท เช่น สำนักงานใหญ่ หรือโรงงานสาขาต่างๆ</p>
            <button class="btn-add-loc" @click="openAddLocModal('fixed')"><i class="fas fa-plus"></i> Add Fixed Location</button>
          </div>
          
          <div class="locations-grid">
            <div v-for="loc in fixedLocations" :key="loc.id" class="location-item-card">
              <div class="loc-card-icon"><i class="fas fa-industry"></i></div>
              <div class="loc-card-info">
                <span class="loc-name">{{ loc.name }}</span>
                <span class="loc-coords">{{ loc.lat.toFixed(4) }}, {{ loc.lon.toFixed(4) }}</span>
                <span class="loc-radius">Radius: {{ loc.radius }}m</span>
              </div>
              <button class="loc-delete-btn" @click="deleteLocation(loc.id)"><i class="fas fa-trash"></i></button>
            </div>
            <div v-if="fixedLocations.length === 0" class="empty-state-simple">
              <i class="fas fa-map-marker-alt"></i>
              <span>No fixed locations added.</span>
            </div>
          </div>
        </div>

        <!-- On-site Projects Tab -->
        <div v-if="activeLocTab === 'onsite'" class="loc-content-fade">
          <div class="loc-actions-header">
            <p class="section-desc">จัดการสถานที่หน้างานหรือจุดปฏิบัติงานตามโปรเจกต์ (ข้อมูลเชื่อมโยงจากเมนูโครงการ)</p>
            <button class="btn-add-loc btn-onsite" @click="openAddLocModal('onsite')"><i class="fas fa-plus"></i> Link Project Location</button>
          </div>
          
          <div class="locations-grid">
            <div v-for="loc in onsiteLocations" :key="loc.id" class="location-item-card onsite">
              <div class="loc-card-icon"><i class="fas fa-hard-hat"></i></div>
              <div class="loc-card-info">
                <span class="loc-name">{{ loc.name }}</span>
                <span class="loc-coords">{{ loc.lat.toFixed(4) }}, {{ loc.lon.toFixed(4) }}</span>
                <span class="loc-radius">Radius: {{ loc.radius }}m</span>
              </div>
              <button class="loc-delete-btn" @click="deleteLocation(loc.id)"><i class="fas fa-trash"></i></button>
            </div>
            <div v-if="onsiteLocations.length === 0" class="empty-state-simple">
              <i class="fas fa-project-diagram"></i>
              <span>No onsite locations linked yet.</span>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- 3. OVERTIME RULES -->
    <div class="settings-card">
      <div class="card-header">
        <h3><i class="fas fa-business-time"></i> Overtime (OT) Rules</h3>
        <button class="btn-save btn-sm" @click="saveConfigs('ot')">Save OT Config</button>
      </div>
      <div class="card-body">
        <div class="ot-grid">
          <div class="ot-item">
            <span class="ot-title">Standard Overtime</span>
            <div class="time-range-box">
              <input type="time" class="form-input" v-model="config.ot_normal_start" />
              <span>to</span>
              <input type="time" class="form-input" v-model="config.ot_normal_end" />
            </div>
          </div>
          <div class="ot-item special">
            <span class="ot-title">Special Overtime</span>
            <div class="time-range-box">
              <input type="time" class="form-input" v-model="config.ot_special_start" />
              <span>to</span>
              <input type="time" class="form-input" v-model="config.ot_special_end" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 4. LEAVE QUOTAS -->
    <div class="settings-card">
      <div class="card-header">
        <h3><i class="fas fa-calendar-times"></i> Leave Quotas (Days/Year)</h3>
        <button class="btn-save btn-sm" @click="saveConfigs('leaves')">Save Quotas</button>
      </div>
      <div class="card-body">
         <div class="leave-grid">
           <div class="leave-item">
             <div class="leave-icon sick"><i class="fas fa-briefcase-medical"></i></div>
             <div class="leave-info"><label>Sick Leave</label><input type="number" class="form-input small" v-model="config.quota_sick_leave" /></div>
           </div>
           <div class="leave-item">
             <div class="leave-icon vacation"><i class="fas fa-umbrella-beach"></i></div>
             <div class="leave-info"><label>Annual Leave</label><input type="number" class="form-input small" v-model="config.quota_annual_leave" /></div>
           </div>
           <div class="leave-item">
             <div class="leave-icon personal"><i class="fas fa-user-clock"></i></div>
             <div class="leave-info"><label>Personal Leave</label><input type="number" class="form-input small" v-model="config.quota_personal_leave" /></div>
           </div>
         </div>
      </div>
    </div>

    <!-- 5. PUBLIC HOLIDAYS -->
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
        <table class="holiday-table">
          <thead>
            <tr><th width="150">Date</th><th>Holiday Name</th><th width="80">Action</th></tr>
          </thead>
          <tbody>
            <tr v-for="hol in holidays" :key="hol.id">
              <td><input type="date" class="form-input" v-model="hol.date" @change="updateHoliday(hol)" /></td>
              <td><input type="text" class="form-input" v-model="hol.name" @change="updateHoliday(hol)" /></td>
              <td><button class="btn-icon delete" @click="deleteHoliday(hol)"><i class="fas fa-trash-alt"></i></button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import api from '../../api'
import Swal from 'sweetalert2'

const config = ref({
  check_in_time: '08:00', check_out_time: '17:00', late_grace_period_mins: '15',
  ot_normal_start: '17:00', ot_normal_end: '22:00', ot_special_start: '22:00', ot_special_end: '06:00',
  quota_sick_leave: '30', quota_annual_leave: '6', quota_personal_leave: '3'
})

const activeLocTab = ref('fixed')
const locations = ref([])
const holidays = ref([])
const selectedYear = ref(new Date().getFullYear())

const fixedLocations = computed(() => locations.value.filter(l => l.is_fixed))
const onsiteLocations = computed(() => locations.value.filter(l => !l.is_fixed))

const fetchConfigs = async () => {
  try {
    const res = await api.get('/attendance/settings')
    res.data.forEach(item => { if (config.value[item.key] !== undefined) config.value[item.key] = item.value })
  } catch (err) { console.error(err) }
}

const fetchLocations = async () => {
  try {
    const res = await api.get('/attendance/locations')
    locations.value = res.data
  } catch (err) { console.error(err) }
}

const openAddLocModal = async (type) => {
  const { value: formValues } = await Swal.fire({
    title: type === 'fixed' ? 'Add Fixed Location' : 'Link On-site Project',
    html:
      `<input id="loc-name" class="swal2-input" placeholder="Location Name">` +
      `<input id="loc-lat" type="number" step="0.000001" class="swal2-input" placeholder="Latitude (e.g. 13.7563)">` +
      `<input id="loc-lon" type="number" step="0.000001" class="swal2-input" placeholder="Longitude (e.g. 100.5018)">` +
      `<input id="loc-radius" type="number" class="swal2-input" placeholder="Radius (meters) - default 100" value="100">`,
    focusConfirm: false,
    showCancelButton: true,
    preConfirm: () => {
      return {
        name: document.getElementById('loc-name').value,
        lat: parseFloat(document.getElementById('loc-lat').value),
        lon: parseFloat(document.getElementById('loc-lon').value),
        radius: parseInt(document.getElementById('loc-radius').value),
        is_fixed: type === 'fixed'
      }
    }
  })

  if (formValues && formValues.name && !isNaN(formValues.lat)) {
    try {
      await api.post('/attendance/locations', formValues)
      Swal.fire({ icon: 'success', title: 'Location Added', toast: true, position: 'top-end', showConfirmButton: false, timer: 1500 })
      fetchLocations()
    } catch (err) { Swal.fire('Error', 'Failed to add location', 'error') }
  }
}

const deleteLocation = async (id) => {
  const res = await Swal.fire({ title: 'Delete Location?', icon: 'warning', showCancelButton: true })
  if (res.isConfirmed) {
    try {
      await api.delete(`/attendance/locations/${id}`)
      fetchLocations()
    } catch (err) { Swal.fire('Error', 'Failed to delete', 'error') }
  }
}

const saveConfigs = async (type) => {
  try {
    let keys = []
    if (type === 'hours') keys = ['check_in_time', 'check_out_time', 'late_grace_period_mins']
    if (type === 'ot') keys = ['ot_normal_start', 'ot_normal_end', 'ot_special_start', 'ot_special_end']
    if (type === 'leaves') keys = ['quota_sick_leave', 'quota_annual_leave', 'quota_personal_leave']
    const payload = keys.map(k => ({ key: k, value: String(config.value[k]) }))
    await api.put('/attendance/settings', payload)
    Swal.fire({ toast: true, position: 'top-end', icon: 'success', title: 'Saved!', timer: 2000, showConfirmButton: false })
  } catch (err) { Swal.fire('Error', 'Save failed', 'error') }
}

const fetchHolidays = async () => {
  try {
    const res = await api.get(`/attendance/holidays/${selectedYear.value}`)
    holidays.value = res.data || []
  } catch (err) { console.error(err) }
}

const addHoliday = async () => {
  const { value: formValues } = await Swal.fire({
    title: 'Add Holiday',
    html: `<input id="h-date" type="date" class="swal2-input"> <input id="h-name" class="swal2-input" placeholder="Holiday Name">`,
    showCancelButton: true,
    preConfirm: () => ({ date: document.getElementById('h-date').value, name: document.getElementById('h-name').value })
  })
  if (formValues?.date) {
    await api.post('/attendance/holidays', { year: selectedYear.value, ...formValues })
    fetchHolidays()
  }
}

watch(selectedYear, fetchHolidays)
onMounted(() => { fetchConfigs(); fetchLocations(); fetchHolidays(); })

const availableYears = computed(() => {
  const y = new Date().getFullYear(); return [y-1, y, y+1]
})
</script>

<style scoped>
.attendance-settings-container { display: flex; flex-direction: column; gap: 24px; padding: 10px; }
.header-banner { background: white; padding: 24px; border-radius: 16px; border: 1px solid #e2e8f0; }
.header-banner h2 { margin: 0; color: #1e293b; display: flex; align-items: center; gap: 12px; }
.subtitle { color: #64748b; margin-top: 8px; }

.settings-card { background: white; border-radius: 16px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
.card-header { background: #f8fafc; padding: 16px 24px; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
.card-header h3 { margin: 0; font-size: 1.1rem; color: #334155; display: flex; align-items: center; gap: 10px; }
.card-body { padding: 24px; }

/* Location Tabs */
.location-tabs { display: flex; background: #f1f5f9; padding: 4px; border-radius: 10px; gap: 4px; }
.loc-tab-btn { border: none; background: none; padding: 8px 16px; border-radius: 8px; font-weight: 700; color: #64748b; cursor: pointer; transition: 0.2s; }
.loc-tab-btn.active { background: white; color: #3b82f6; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }

.loc-actions-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 10px; }
.section-desc { color: #64748b; font-size: 0.9rem; margin: 0; max-width: 60%; }
.btn-add-loc { background: #10b981; color: white; border: none; padding: 10px 18px; border-radius: 10px; font-weight: 700; cursor: pointer; }
.btn-add-loc.btn-onsite { background: #6366f1; }

.locations-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
.location-item-card { display: flex; align-items: center; gap: 16px; padding: 16px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; position: relative; }
.location-item-card.onsite { border-left: 4px solid #6366f1; }
.loc-card-icon { width: 44px; height: 44px; background: #e0f2fe; color: #3b82f6; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; }
.onsite .loc-card-icon { background: #eef2ff; color: #6366f1; }
.loc-card-info { display: flex; flex-direction: column; gap: 2px; }
.loc-name { font-weight: 800; color: #1e293b; font-size: 0.95rem; }
.loc-coords { font-size: 0.8rem; color: #64748b; font-family: monospace; }
.loc-radius { font-size: 0.75rem; color: #10b981; font-weight: 700; }
.loc-delete-btn { position: absolute; top: 12px; right: 12px; background: transparent; border: none; color: #94a3b8; cursor: pointer; }
.loc-delete-btn:hover { color: #ef4444; }

.form-row { display: flex; gap: 24px; flex-wrap: wrap; }
.form-group { display: flex; flex-direction: column; gap: 8px; flex: 1; min-width: 200px; }
.form-input { padding: 10px 14px; border: 1px solid #cbd5e1; border-radius: 10px; font-size: 0.95rem; }
.btn-save { background: #3b82f6; color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: 700; cursor: pointer; }

.ot-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.ot-item { background: #f8fafc; padding: 20px; border-radius: 14px; border: 1px solid #e2e8f0; }
.ot-item.special { background: #fffbeb; border-color: #fce38a; }
.ot-title { font-weight: 800; display: block; margin-bottom: 12px; }
.time-range-box { display: flex; align-items: center; gap: 10px; }

.leave-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.leave-item { display: flex; align-items: center; gap: 12px; padding: 16px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; }
.leave-icon { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; }
.leave-icon.sick { background: #ef4444; }
.leave-icon.vacation { background: #10b981; }
.leave-icon.personal { background: #f59e0b; }

.holiday-table { width: 100%; border-collapse: collapse; }
.holiday-table th { text-align: left; padding: 12px; background: #f1f5f9; font-size: 0.8rem; font-weight: 700; border-bottom: 2px solid #e2e8f0; }
.holiday-table td { padding: 12px; border-bottom: 1px solid #f1f5f9; }

.empty-state-simple { text-align: center; padding: 30px; color: #94a3b8; font-size: 0.9rem; display: flex; flex-direction: column; gap: 8px; }

@media (max-width: 768px) {
  .ot-grid, .leave-grid { grid-template-columns: 1fr; }
  .loc-actions-header { flex-direction: column; align-items: flex-start; }
  .section-desc { max-width: 100%; }
}
</style>
