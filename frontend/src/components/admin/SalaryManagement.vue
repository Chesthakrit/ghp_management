<template>
  <div class="salary-management-container">
    <div class="section-card">
      <div class="section-header">
        <h2 class="header-title">💰 Salary Grade Settings</h2>
        <p class="header-subtitle">Define min-max salary range and payment type for each job title.</p>
      </div>

      <div class="hr-settings-grid salary-main-grid">
        <!-- Left: Select Department & Job Title -->
        <div class="salary-selection-pane">
          <label class="form-label-sm">Select Department & Job Title</label>
          <div class="hr-list salary-accordion">
            <div v-for="d in departments" :key="d.id" class="salary-dept-group">
              <div class="hr-list-item dept-header" :class="{ 'is-expanded': expandedDepts.includes(d.id) }" @click="toggleDeptExpansion(d.id)">
                <div class="dept-title-wrapper">
                  <span class="toggle-icon">{{ expandedDepts.includes(d.id) ? '▼' : '▶' }}</span>
                  <span class="hr-label dept-name-label">{{ d.name }}</span>
                </div>
              </div>
              <div v-if="expandedDepts.includes(d.id)" class="jt-nested-list">
                <div v-for="jt in jobTitles.filter(j => j.department_id === d.id)" :key="jt.id" class="hr-list-item jt-item" :class="{ selected: salarySelectedJT?.id === jt.id }" @click="selectJobTitle(jt, d.id)">
                  <span class="hr-label">{{ jt.name }}</span>
                  <div class="salary-preview-right">
                    <div v-if="jt.min_salary_monthly > 0 || jt.max_salary_monthly > 0" class="salary-tag monthly">{{ (jt.min_salary_monthly || 0).toLocaleString() }} - {{ (jt.max_salary_monthly || 0).toLocaleString() }} M</div>
                    <div v-if="jt.min_salary_daily > 0 || jt.max_salary_daily > 0" class="salary-tag daily">{{ (jt.min_salary_daily || 0).toLocaleString() }} - {{ (jt.max_salary_daily || 0).toLocaleString() }} D</div>
                  </div>
                </div>
                <div v-if="!jobTitles.filter(j => j.department_id === d.id).length" class="no-data-hint-sm">No job titles defined</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right: Set Salary Details -->
        <div class="salary-details-pane">
          <div v-if="salarySelectedJT" class="section-card detail-config-card">
            <h3 class="detail-title">Position: {{ salarySelectedJT.name }}</h3>
            <div class="salary-dual-config">
              <div class="salary-config-card monthly-card">
                <h4 class="config-type-label">🏢 Monthly Salary</h4>
                <div class="form-grid config-grid">
                  <div class="form-group"><label>Min</label><input type="number" v-model.number="salarySelectedJT.min_salary_monthly" class="form-input" /></div>
                  <div class="form-group"><label>Max</label><input type="number" v-model.number="salarySelectedJT.max_salary_monthly" class="form-input" /></div>
                </div>
              </div>
              <div class="salary-config-card daily-card">
                <h4 class="config-type-label">☀️ Daily Wage</h4>
                <div class="form-grid config-grid">
                  <div class="form-group"><label>Min</label><input type="number" v-model.number="salarySelectedJT.min_salary_daily" class="form-input" /></div>
                  <div class="form-group"><label>Max</label><input type="number" v-model.number="salarySelectedJT.max_salary_daily" class="form-input" /></div>
                </div>
              </div>
            </div>
            <div class="detail-actions">
              <button class="btn-primary" @click="saveSalarySettings" :disabled="isSaving">{{ isSaving ? 'Saving...' : 'Save Settings' }}</button>
            </div>
          </div>
          <div v-else class="hr-empty-hint">Please select a job title to edit.</div>
        </div>
      </div>

      <!-- BOTTOM: Global Payroll Configuration -->
      <div class="salary-global-fullwidth">
         <div class="section-header">
            <h3>⚙️ Global Payroll Configuration</h3>
            <p class="global-subtitle">System-wide parameters for calculating daily earnings and overtime.</p>
         </div>
         
         <div class="global-settings-horizontal-flex">
            <div class="settings-category-group common-group">
              <h4 class="category-title">🌍 Common</h4>
              <div v-for="s in payrollSettings.filter(cfg => cfg.key.startsWith('common'))" :key="s.key" class="global-setting-item">
                <div class="setting-info"><label class="setting-label">{{ formatSettingLabel(s.key) }}</label></div>
                <div class="setting-action"><input type="number" step="0.1" v-model.number="s.value" class="form-input-sm" @change="savePayrollSetting(s)" /></div>
              </div>
            </div>
            <div class="settings-category-group monthly-group">
              <h4 class="category-title">🏢 Monthly</h4>
              <div v-for="s in payrollSettings.filter(cfg => cfg.key.startsWith('monthly'))" :key="s.key" class="global-setting-item">
                <div class="setting-info"><label class="setting-label">{{ formatSettingLabel(s.key) }}</label></div>
                <div class="setting-action"><input type="number" step="0.1" v-model.number="s.value" class="form-input-sm" @change="savePayrollSetting(s)" /></div>
              </div>
            </div>
            <div class="settings-category-group daily-group">
              <h4 class="category-title">☀️ Daily</h4>
              <div v-for="s in payrollSettings.filter(cfg => cfg.key.startsWith('daily'))" :key="s.key" class="global-setting-item">
                <div class="setting-info"><label class="setting-label">{{ formatSettingLabel(s.key) }}</label></div>
                <div class="setting-action"><input type="number" step="0.1" v-model.number="s.value" class="form-input-sm" @change="savePayrollSetting(s)" /></div>
              </div>
            </div>
         </div>
      </div>
    </div>
  </div>
</template>


<script setup>
import { ref, onMounted, defineEmits } from 'vue'
import api from '../../api'
import Swal from 'sweetalert2'

const props = defineProps({
  departments: { type: Array, default: () => [] },
  jobTitles: { type: Array, default: () => [] }
})

const emit = defineEmits(['refresh'])

const expandedDepts = ref([])
const salarySelectedJT = ref(null)
const salarySelectedDeptId = ref(null)
const payrollSettings = ref([])
const isSaving = ref(false)

onMounted(() => {
  fetchPayrollSettings()
})

const toggleDeptExpansion = (deptId) => {
  if (expandedDepts.value.includes(deptId)) {
    expandedDepts.value = expandedDepts.value.filter(id => id !== deptId)
  } else {
    expandedDepts.value.push(deptId)
  }
}

const selectJobTitle = (jt, deptId) => {
  salarySelectedJT.value = { ...jt }
  salarySelectedDeptId.value = deptId
}

const fetchPayrollSettings = async () => {
  try {
    const res = await api.get('/payroll/settings')
    payrollSettings.value = res.data
  } catch (e) {
    console.error('Failed to fetch payroll settings', e)
  }
}

const formatSettingLabel = (key) => {
  const cleanKey = key.replace(/^(common_|monthly_|daily_)/, '')
  return cleanKey.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
}

const savePayrollSetting = async (setting) => {
  try {
    await api.put(`/payroll/settings/${setting.key}`, { value: setting.value })
    Swal.fire({
      icon: 'success',
      title: 'Updated',
      text: `${formatSettingLabel(setting.key)} updated successfully`,
      timer: 1500,
      showConfirmButton: false
    })
  } catch (e) {
    Swal.fire('Error', 'Failed to update setting', 'error')
  }
}

const saveSalarySettings = async () => {
  if (!salarySelectedJT.value) return
  isSaving.value = true
  try {
    await api.put(`/hr/job-titles/${salarySelectedJT.value.id}`, {
      name: salarySelectedJT.value.name,
      department_id: salarySelectedDeptId.value,
      min_salary_monthly: salarySelectedJT.value.min_salary_monthly,
      max_salary_monthly: salarySelectedJT.value.max_salary_monthly,
      min_salary_daily: salarySelectedJT.value.min_salary_daily,
      max_salary_daily: salarySelectedJT.value.max_salary_daily
    })
    Swal.fire({
      icon: 'success',
      title: 'Saved',
      text: `Salary settings for ${salarySelectedJT.value.name} saved`,
      timer: 1500,
      showConfirmButton: false
    })
    emit('refresh')
  } catch (e) {
    Swal.fire('Error', 'Failed to save salary settings', 'error')
  } finally {
    isSaving.value = false
  }
}
</script>

<style scoped>
/* Base Containers */
.salary-management-container {
  padding: 0;
}

.section-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
  margin-bottom: 24px;
}

.section-header {
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 15px;
  margin-bottom: 15px;
}

.header-title {
  margin: 0;
  font-size: 1.25rem;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-subtitle {
  font-size: 0.85rem; 
  color: #64748b; 
  margin-top: 4px;
}

/* Grid Layout */
.salary-main-grid {
  margin-top: 20px;
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 24px;
  align-items: start;
}

/* LEFT: Selection Pane */
.salary-selection-pane {
  background: #f8fafc;
  border-radius: 10px;
  padding: 16px;
  border: 1px solid #e2e8f0;
}

.dept-title-wrapper {
  display: flex; 
  align-items: center; 
  gap: 8px;
}

.dept-name-label {
  font-weight: 700;
}

.form-label-sm {
  font-size: 0.75rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  margin-bottom: 12px;
  display: block;
}

.salary-accordion {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.dept-header {
  background: white;
  border: 1px solid #e2e8f0;
  padding: 12px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dept-header:hover {
  border-color: #3b82f6;
}

.dept-header.is-expanded {
  background: #eff6ff;
  border-color: #3b82f6;
}

.jt-nested-list {
  padding-left: 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 6px;
}

.jt-item {
  background: white;
  border: 1px solid #f1f5f9;
  padding: 10px 14px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.88rem;
  transition: all 0.2s;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.jt-item:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}

.jt-item.selected {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}

.jt-item.selected .hr-label {
  color: white;
}

.hr-label {
  font-weight: 500;
}

/* Salary Tags */
.salary-preview-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.salary-tag {
  font-size: 0.65rem;
  font-weight: 800;
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: uppercase;
}

.salary-tag.monthly {
  background: #dcfce7;
  color: #166534;
}

.salary-tag.daily {
  background: #fef9c3;
  color: #854d0e;
}

.jt-item.selected .salary-tag {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

/* RIGHT: Details Pane */
.detail-config-card {
  border-style: dashed; 
  background: #f8fafc; 
  padding: 20px; 
  border-radius: 12px;
}

.detail-title {
  margin-bottom: 20px; 
  color: #1a2a3a;
}

.monthly-card {
  margin-bottom: 20px; 
  padding: 15px; 
  background: white; 
  border-radius: 8px; 
  border: 1px solid #e2e8f0;
}

.daily-card {
  padding: 15px; 
  background: white; 
  border-radius: 8px; 
  border: 1px solid #e2e8f0;
}

.config-type-label {
  font-size: 0.75rem; 
  color: #64748b; 
  text-transform: uppercase;
  margin: 0;
}

.config-grid {
  display: grid; 
  grid-template-columns: 1fr 1fr; 
  gap: 15px; 
  margin-top: 10px;
}

.detail-actions {
  margin-top: 25px; 
  display: flex; 
  justify-content: flex-end;
}

/* Global Config Section */
.salary-global-fullwidth {
  margin-top: 40px; 
  border-top: 1px solid #e2e8f0; 
  padding-top: 30px;
}

.global-subtitle {
  font-size: 0.8rem; 
  color: #64748b;
}

.global-settings-horizontal-flex {
  display: flex; 
  gap: 20px; 
  flex-wrap: wrap; 
  margin-top: 20px;
}

.settings-category-group {
  flex: 1; 
  min-width: 280px;
}

.category-title {
  font-size: 0.75rem;
  text-transform: uppercase;
  color: #64748b;
  letter-spacing: 0.05em;
  border-left: 3px solid #3b82f6;
  padding-left: 10px;
  margin-bottom: 12px;
}

.global-setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  margin-bottom: 8px;
  transition: all 0.2s;
}

.global-setting-item:hover {
  border-color: #3b82f6;
  background: #f8fafc;
}

.setting-label {
  font-size: 0.88rem;
  font-weight: 600;
  color: #1e293b;
}

.form-input-sm {
  width: 80px;
  padding: 6px 10px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  text-align: right;
  font-weight: 700;
  color: #3b82f6;
  font-family: inherit;
}

.form-group label {
  display: block;
  font-size: 0.75rem;
  color: #64748b;
  margin-bottom: 6px;
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #dde3e8;
  border-radius: 8px;
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.2s;
}

.btn-primary {
  background: #1a2a3a;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-primary:hover {
  background: #243447;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.hr-empty-hint {
  height: 300px;
  background: #f1f5f9;
  border: 2px dashed #cbd5e1;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  font-style: italic;
}

@media (max-width: 1024px) {
  .salary-main-grid {
    grid-template-columns: 1fr;
  }
}
</style>

