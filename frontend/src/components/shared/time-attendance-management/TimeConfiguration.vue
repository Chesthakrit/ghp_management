<template>
  <div class="attendance-settings-container">
    <div class="header-section">
      <div class="header-titles">
        <h2><i class="fas fa-business-time"></i> Time & Leave Settings</h2>
        <p class="subtitle">Configuration panel for attendance, location, and annual leave quotas.</p>
      </div>
      <div class="header-status">
        <span class="status-badge"><i class="fas fa-shield-alt"></i> Admin Control</span>
      </div>
    </div>

    <!-- 1. Schedule Ring Overview -->
    <TimeScheduleRing :config="config" />

    <div class="settings-grid">
      <!-- LEFT COLUMN -->
      <div class="settings-col">
        <!-- 2. WORKING HOURS -->
        <WorkingHoursSettings v-model="config" @saved="fetchConfigs" />

        <!-- 3. WORK DAY CONFIGURATION -->
        <WorkDaySettings v-model="config" @saved="fetchConfigs" />

        <!-- 4. LEAVE QUOTAS -->
        <LeaveQuotasSettings v-model="config" @saved="fetchConfigs" />
      </div>

      <!-- RIGHT COLUMN -->
      <div class="settings-col">
        <!-- 5. LOCATION MANAGEMENT -->
        <LocationManagement />

        <!-- 6. PUBLIC HOLIDAYS -->
        <HolidayManagement />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../../api'

// Sub-components
import TimeScheduleRing from './TimeScheduleRing.vue'
import WorkingHoursSettings from './WorkingHoursSettings.vue'
import WorkDaySettings from './WorkDaySettings.vue'
import LeaveQuotasSettings from './LeaveQuotasSettings.vue'
import LocationManagement from './LocationManagement.vue'
import HolidayManagement from './HolidayManagement.vue'

const config = ref({
  check_in_time: '08:00', 
  check_out_time: '17:00', 
  late_grace_period_mins: '5', 
  late_grace_period_mins_t2: '15', 
  late_grace_period_mins_t3: '30',
  quota_sick_leave: '30', 
  quota_annual_leave: '6', 
  quota_personal_leave: '3',
  work_day_0: 'work', work_day_1: 'work', work_day_2: 'work',
  work_day_3: 'work', work_day_4: 'work', work_day_5: 'off', work_day_6: 'off'
})

const fetchConfigs = async () => {
  try {
    const res = await api.get('/attendance/settings')
    res.data.forEach(item => { 
      if (config.value[item.key] !== undefined) config.value[item.key] = item.value 
    })
  } catch (err) { console.error(err) }
}

onMounted(() => { 
  fetchConfigs() 
})
</script>

<style scoped>
.attendance-settings-container {
  display: flex; flex-direction: column; gap: 24px; padding: 10px;
  font-family: 'Inter', -apple-system, sans-serif;
  color: #334155;
}

.header-section {
  display: flex; justify-content: space-between; align-items: flex-start;
  padding-bottom: 20px; border-bottom: 1px solid #e2e8f0;
}
.header-titles h2 { margin: 0; font-size: 1.5rem; font-weight: 800; color: #1a2a3a; display: flex; align-items: center; gap: 12px; }
.subtitle { margin: 4px 0 0; font-size: 0.9rem; color: #64748b; }
.status-badge { background: #f1f5f9; padding: 6px 14px; border-radius: 100px; font-size: 0.75rem; font-weight: 700; color: #1a2a3a; border: 1px solid #e2e8f0; }

.settings-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
@media (max-width: 1024px) { .settings-grid { grid-template-columns: 1fr; } }

.settings-col { display: flex; flex-direction: column; gap: 24px; }
</style>
