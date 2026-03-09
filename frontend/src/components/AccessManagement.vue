<template>
  <div class="access-management">
    <div class="access-grid">
      <!-- Left: Job Titles List (Accordion Style) -->
      <div class="jt-sidebar card">
        <h3>Job Titles</h3>
        <div v-if="isLoading" class="loading-state">Loading...</div>
        <div v-else class="dept-group" v-for="dept in rawDepartments" :key="dept.id">
          <!-- Department Header -->
          <div 
            class="dept-header" 
            :class="{ expanded: expandedDepts.includes(dept.id) }"
            @click="toggleDeptExpansion(dept.id)"
          >
            <span class="toggle-icon">{{ expandedDepts.includes(dept.id) ? '▼' : '▶' }}</span>
            <span class="dept-name">{{ dept.name }}</span>
          </div>

          <!-- Job Titles (Nested) -->
          <div v-if="expandedDepts.includes(dept.id)" class="jt-nested-list">
            <div 
              v-for="jt in rawJobTitles.filter(j => j.department_id === dept.id)" 
              :key="jt.id"
              class="jt-item"
              :class="{ active: selectedJT?.id === jt.id }"
              @click="selectJobTitle(jt)"
            >
              {{ jt.name }}
            </div>
            <div v-if="!rawJobTitles.filter(j => j.department_id === dept.id).length" class="no-data-hint">
              No positions
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Permissions Grid -->
      <div class="permissions-content card">
        <div v-if="!selectedJT" class="no-jt-selected">
          <i class="fas fa-arrow-left"></i>
          <p>Please select a Job Title to manage access rights.</p>
        </div>
        
        <div v-else>
          <div class="content-header">
            <h3>Access Rights for: <span class="highlight">{{ selectedJT.name }}</span></h3>
            <button class="btn-primary" @click="savePermissions" :disabled="isSaving">
              {{ isSaving ? 'Saving...' : '💾 Save Changes' }}
            </button>
          </div>

          <!-- Section: User Management -->
          <div class="perm-section">
            <div class="section-badge">Module</div>
            <h4><i class="fas fa-users-cog"></i> User Management Page</h4>
            <div class="perm-row page-level">
              <label class="switch-label">
                <input type="checkbox" v-model="selectedPerms" value="page.usermanagement" />
                <span class="slider"></span>
                <span class="label-text">Allow Access to User Management Page</span>
              </label>
            </div>

            <div class="granular-actions" :class="{ disabled: !selectedPerms.includes('page.usermanagement') }">
              <div class="action-item">
                <label class="chk-container">
                  <input type="checkbox" v-model="selectedPerms" value="action.user.edit_identity" :disabled="!selectedPerms.includes('page.usermanagement')" />
                  <span class="checkmark"></span>
                  Button: Edit Employee Identity
                </label>
              </div>
              <div class="action-item">
                <label class="chk-container">
                  <input type="checkbox" v-model="selectedPerms" value="action.user.edit_employment" :disabled="!selectedPerms.includes('page.usermanagement')" />
                  <span class="checkmark"></span>
                  Button: Employment & Access Control
                </label>
              </div>
              <div class="action-item">
                <label class="chk-container">
                  <input type="checkbox" v-model="selectedPerms" value="action.user.delete" :disabled="!selectedPerms.includes('page.usermanagement')" />
                  <span class="checkmark"></span>
                  Button: Delete Employee
                </label>
              </div>
              <div class="action-item">
                <label class="chk-container">
                  <input type="checkbox" v-model="selectedPerms" value="action.user.view_profile" :disabled="!selectedPerms.includes('page.usermanagement')" />
                  <span class="checkmark"></span>
                  Button: View Profile Page
                </label>
              </div>
            </div>
          </div>

          <!-- Section: HR Management -->
          <div class="perm-section">
            <div class="section-badge">Module</div>
            <div class="accordion-header" @click="hrSectionExpanded = !hrSectionExpanded" style="display: flex; justify-content: space-between; align-items: center; cursor: pointer;">
              <h4 style="margin: 0;"><i class="fas fa-sitemap"></i> HR Settings Page</h4>
              <span class="toggle-icon">{{ hrSectionExpanded ? '▼' : '▶' }}</span>
            </div>
            
            <div v-if="hrSectionExpanded" style="margin-top: 15px;">
              <div class="perm-row page-level">
                <label class="switch-label">
                  <input type="checkbox" v-model="selectedPerms" value="page.hr" />
                  <span class="slider"></span>
                  <span class="label-text">Allow Access to HR Settings Page</span>
                </label>
              </div>

              <div class="granular-actions" :class="{ disabled: !selectedPerms.includes('page.hr') }">
                <div class="action-item"><label class="chk-container">
                  <input type="checkbox" v-model="selectedPerms" value="action.hr.add_dept" :disabled="!selectedPerms.includes('page.hr')" /><span class="checkmark"></span>Add Department
                </label></div>
                <div class="action-item"><label class="chk-container">
                  <input type="checkbox" v-model="selectedPerms" value="action.hr.add_jt" :disabled="!selectedPerms.includes('page.hr')" /><span class="checkmark"></span>Add Job Title
                </label></div>
                <div class="action-item"><label class="chk-container">
                  <input type="checkbox" v-model="selectedPerms" value="action.hr.edit_name" :disabled="!selectedPerms.includes('page.hr')" /><span class="checkmark"></span>Edit Name (Dept / Job Title)
                </label></div>
                <div class="action-item"><label class="chk-container">
                  <input type="checkbox" v-model="selectedPerms" value="action.hr.delete" :disabled="!selectedPerms.includes('page.hr')" /><span class="checkmark"></span>Delete (Dept / Job Title)
                </label></div>
                <div class="action-item"><label class="chk-container">
                  <input type="checkbox" v-model="selectedPerms" value="action.hr.manage_jt_skills" :disabled="!selectedPerms.includes('page.hr')" /><span class="checkmark"></span>Assign Skills to Job Title
                </label></div>
                <div class="action-item"><label class="chk-container">
                  <input type="checkbox" v-model="selectedPerms" value="action.hr.add_tag" :disabled="!selectedPerms.includes('page.hr')" /><span class="checkmark"></span>Add Skill Tag
                </label></div>
                <div class="action-item"><label class="chk-container">
                  <input type="checkbox" v-model="selectedPerms" value="action.hr.edit_tag" :disabled="!selectedPerms.includes('page.hr')" /><span class="checkmark"></span>Edit Skill Tag Name
                </label></div>
                <div class="action-item"><label class="chk-container">
                  <input type="checkbox" v-model="selectedPerms" value="action.hr.delete_tag" :disabled="!selectedPerms.includes('page.hr')" /><span class="checkmark"></span>Delete Skill Tag
                </label></div>
                <div class="action-item"><label class="chk-container">
                  <input type="checkbox" v-model="selectedPerms" value="action.hr.add_skill" :disabled="!selectedPerms.includes('page.hr')" /><span class="checkmark"></span>Add New Skill
                </label></div>
                <div class="action-item"><label class="chk-container">
                  <input type="checkbox" v-model="selectedPerms" value="action.hr.edit_skill" :disabled="!selectedPerms.includes('page.hr')" /><span class="checkmark"></span>Edit Skill Info
                </label></div>
                <div class="action-item"><label class="chk-container">
                  <input type="checkbox" v-model="selectedPerms" value="action.hr.delete_skill" :disabled="!selectedPerms.includes('page.hr')" /><span class="checkmark"></span>Delete Skill
                </label></div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import api from '../api'
import Swal from 'sweetalert2'

const rawDepartments = ref([])
const rawJobTitles = ref([])
const allPermissions = ref([])
const selectedJT = ref(null)
const selectedPerms = ref([])
const expandedDepts = ref([])
const hrSectionExpanded = ref(true)
const isLoading = ref(true)
const isSaving = ref(false)

const toggleDeptExpansion = (id) => {
  if (expandedDepts.value.includes(id)) {
    expandedDepts.value = expandedDepts.value.filter(itemId => itemId !== id)
  } else {
    expandedDepts.value.push(id)
  }
}

const fetchData = async () => {
  isLoading.value = true
  try {
    const [deptsRes, jobsRes, permsRes] = await Promise.all([
      api.get('/hr/departments'),
      api.get('/hr/job-titles'),
      api.get('/permissions/')
    ])
    // Sort
    rawDepartments.value = deptsRes.data.sort((a,b) => (a.display_order||100)-(b.display_order||100))
    rawJobTitles.value = jobsRes.data.sort((a,b) => (a.display_order||100)-(b.display_order||100))
    allPermissions.value = permsRes.data
  } catch (e) {
    console.error('Failed to load access data', e)
  } finally {
    isLoading.value = false
  }
}

const selectJobTitle = (jt) => {
  selectedJT.value = jt
  try {
    selectedPerms.value = jt.permissions ? JSON.parse(jt.permissions) : []
  } catch (e) {
    selectedPerms.value = []
  }
}

const hasPageAccess = computed(() => {
  return selectedPerms.value.includes('page.usermanagement')
})

const hasHRAccess = computed(() => {
  return selectedPerms.value.includes('page.hr')
})

// Auto-uncheck granular if page access is lost
watch(hasPageAccess, (val) => {
  if (!val) {
    const granular = ['action.user.edit_identity', 'action.user.edit_employment', 'action.user.delete', 'action.user.view_profile']
    selectedPerms.value = selectedPerms.value.filter(p => !granular.includes(p))
  }
})

watch(hasHRAccess, (val) => {
  if (!val) {
    const granularHR = [
      'action.hr.add_dept', 'action.hr.add_jt', 'action.hr.edit_name', 'action.hr.delete',
      'action.hr.manage_jt_skills', 'action.hr.add_tag', 'action.hr.edit_tag', 'action.hr.delete_tag',
      'action.hr.add_skill', 'action.hr.edit_skill', 'action.hr.delete_skill'
    ]
    selectedPerms.value = selectedPerms.value.filter(p => !granularHR.includes(p))
  }
})

const savePermissions = async () => {
  if (!selectedJT.value) return
  isSaving.value = true
  try {
    await api.put(`/hr/job-titles/${selectedJT.value.id}`, {
      permissions: JSON.stringify(selectedPerms.value)
    })
    // Update local data
    const idx = rawJobTitles.value.findIndex(j => j.id === selectedJT.value.id)
    if (idx !== -1) {
      rawJobTitles.value[idx].permissions = JSON.stringify(selectedPerms.value)
    }
    Swal.fire({ icon: 'success', title: 'Permissions Saved', timer: 1000, showConfirmButton: false })
  } catch (e) {
    Swal.fire('Error', 'Failed to save permissions', 'error')
  } finally {
    isSaving.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.access-management {
  height: 100%;
}
.access-grid {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 20px;
  height: calc(100vh - 120px);
}
.card {
  background: white;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
}
.jt-sidebar {
  padding: 20px;
  overflow-y: auto;
}
.jt-sidebar h3 { font-size: 0.9rem; margin-bottom: 20px; color: #1e293b; text-transform: uppercase; letter-spacing: 0.05em; }
.dept-group { margin-bottom: 10px; }
.dept-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: #f8fafc;
  border-radius: 8px;
  cursor: pointer;
  border: 1px solid #e2e8f0;
  transition: all 0.2s;
}
.dept-header:hover {
  background: #f1f5f9;
}
.dept-header.expanded {
  background: #eff6ff;
  border-color: #3b82f6;
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
}
.toggle-icon {
  font-size: 0.7rem;
  color: #94a3b8;
  width: 12px;
}
.dept-name { 
  font-size: 0.75rem; 
  font-weight: 800; 
  color: #64748b; 
  text-transform: uppercase; 
}
.dept-header.expanded .dept-name {
  color: #1a2a3a;
}
.jt-nested-list {
  padding: 8px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-top: none;
  border-radius: 0 0 8px 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.jt-item { 
  padding: 8px 12px; 
  border-radius: 6px; 
  cursor: pointer; 
  font-size: 0.85rem; 
  color: #475569; 
  transition: all 0.2s;
}
.no-data-hint {
  font-size: 0.75rem;
  color: #94a3b8;
  padding: 8px 12px;
  font-style: italic;
}
.jt-item:hover { background: #f8fafc; color: #3b82f6; }
.jt-item.active { background: #eff6ff; color: #2563eb; font-weight: 700; box-shadow: inset 0 0 0 1px #bfdbfe; }

.permissions-content {
  padding: 24px;
  overflow-y: auto;
}
.no-jt-selected {
  height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #94a3b8;
}
.no-jt-selected i { font-size: 2rem; margin-bottom: 15px; }

.content-header { 
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; padding-bottom: 15px; border-bottom: 2px solid #f1f5f9;
}
.content-header h3 { font-size: 1.1rem; color: #1e293b; }
.highlight { color: #2563eb; text-decoration: underline; }

.perm-section { 
  background: #f8fafc; border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 1px solid #e2e8f0;
}
.perm-section.muted { opacity: 0.8; }
.section-badge { display: inline-block; padding: 2px 8px; background: #e2e8f0; border-radius: 4px; font-size: 0.65rem; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 10px; }
.perm-section h4 { margin-bottom: 15px; font-size: 0.95rem; color: #1e293b; }

.perm-row.page-level { margin-bottom: 20px; padding: 12px; background: white; border-radius: 10px; border: 1px solid #cbd5e1; }

/* Switch Style */
.switch-label { display: flex; align-items: center; gap: 12px; cursor: pointer; position: relative; }
.label-text { font-weight: 700; color: #1e293b; font-size: 0.9rem; }
.switch-label input { opacity: 0; width: 0; height: 0; }
.slider { position: relative; width: 42px; height: 22px; background-color: #cbd5e1; border-radius: 34px; transition: .4s; }
.slider:before { position: absolute; content: ""; height: 16px; width: 16px; left: 3px; bottom: 3px; background-color: white; border-radius: 50%; transition: .4s; }
input:checked + .slider { background-color: #10b981; }
input:checked + .slider:before { transform: translateX(20px); }

.granular-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-left: 10px; }
.granular-actions.disabled { opacity: 0.5; pointer-events: none; }
.action-item { background: white; padding: 12px; border-radius: 8px; border: 1px solid #e2e8f0; transition: border-color 0.2s; }
.action-item:hover { border-color: #94a3b8; }

.perm-grid-lite { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; }

/* Checkbox Style */
.chk-container, .chk-container-inline { 
  display: block; position: relative; padding-left: 30px; cursor: pointer; font-size: 0.85rem; color: #475569; user-select: none; font-weight: 500;
}
.chk-container input, .chk-container-inline input { position: absolute; opacity: 0; cursor: pointer; height: 0; width: 0; }
.checkmark { 
  position: absolute; top: 0; left: 0; height: 18px; width: 18px; background-color: #fff; border: 2px solid #cbd5e1; border-radius: 4px;
}
.chk-container:hover input ~ .checkmark, .chk-container-inline:hover input ~ .checkmark { background-color: #f1f5f9; }
.chk-container input:checked ~ .checkmark, .chk-container-inline input:checked ~ .checkmark { background-color: #2563eb; border-color: #2563eb; }
.checkmark:after { content: ""; position: absolute; display: none; }
.chk-container input:checked ~ .checkmark:after, .chk-container-inline input:checked ~ .checkmark:after { display: block; }
.chk-container .checkmark:after, .chk-container-inline .checkmark:after { left: 5px; top: 2px; width: 4px; height: 8px; border: solid white; border-width: 0 2px 2px 0; transform: rotate(45deg); }

.btn-primary { 
  background: #1a2a3a; color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: 700; cursor: pointer; transition: all 0.2s;
}
.btn-primary:hover { transform: translateY(-1px); box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

@keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
.perm-section { animation: fadeIn 0.3s ease-out; }
</style>
