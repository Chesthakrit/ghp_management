<template>
  <div class="access-management">
    <div class="access-grid">
      <!-- Left: Job Titles List (Accordion Style) -->

      <div class="jt-sidebar card">
        <h3 class="selection-title">📂 Organization Structure</h3>
        <div v-if="isLoading" class="loading-state">Loading...</div>
        <div v-else class="salary-accordion">
          <div v-for="dept in departments" :key="dept.id" class="org-dept-block">
            <!-- Department Header -->
            <div 
              class="dept-row dept-header-row" 
              :class="{ expanded: expandedDepts.includes(dept.id) }"
              @click="toggleDeptExpansion(dept.id)"
            >
              <div class="dept-title-content">
                <span class="toggle-icon">{{ expandedDepts.includes(dept.id) ? '▼' : '▶' }}</span>
                <span class="dept-title">{{ dept.name }}</span>
              </div>
            </div>

            <!-- Job Titles (Nested) -->
            <div v-if="expandedDepts.includes(dept.id)" class="jt-container">
              <div 
                v-for="jt in jobTitles.filter(j => j.department_id === dept.id)" 
                :key="jt.id"
                class="jt-block-nested"
                :class="{ active: selectedJT?.id === jt.id }"
                @click="selectJobTitle(jt)"
              >
                <div class="jt-main-row">
                   <span class="jt-name">{{ jt.name }}</span>
                </div>
              </div>
              <div v-if="!jobTitles.filter(j => j.department_id === dept.id).length" class="no-data-hint">
                No positions
              </div>
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
            <div class="accordion-header" @click="userSectionExpanded = !userSectionExpanded" style="display: flex; justify-content: space-between; align-items: center; cursor: pointer;">
              <h4 style="margin: 0;"><i class="fas fa-users-cog"></i> User Management Page</h4>
              <span class="toggle-icon">{{ userSectionExpanded ? '▼' : '▶' }}</span>
            </div>
            
            <div v-if="userSectionExpanded" style="margin-top: 15px;">
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
                    Edit Employee Identity
                  </label>
                </div>
                <div class="action-item">
                  <label class="chk-container">
                    <input type="checkbox" v-model="selectedPerms" value="action.user.edit_employment" :disabled="!selectedPerms.includes('page.usermanagement')" />
                    <span class="checkmark"></span>
                    Employment & Access Control
                  </label>
                </div>
                <div class="action-item">
                  <label class="chk-container">
                    <input type="checkbox" v-model="selectedPerms" value="action.user.delete" :disabled="!selectedPerms.includes('page.usermanagement')" />
                    <span class="checkmark"></span>
                    Delete Employee
                  </label>
                </div>
                <div class="action-item">
                  <label class="chk-container">
                    <input type="checkbox" v-model="selectedPerms" value="action.user.view_profile" :disabled="!selectedPerms.includes('page.usermanagement')" />
                    <span class="checkmark"></span>
                    View Profile Page
                  </label>
                </div>
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
import api from '../../api'
import Swal from 'sweetalert2'

const props = defineProps({
  departments: { type: Array, default: () => [] },
  jobTitles: { type: Array, default: () => [] },
  currentUser: { type: Object, default: null },
  isAdmin: { type: Boolean, default: false }
})

const emit = defineEmits(['refresh'])

const allPermissions = ref([])
const selectedJT = ref(null)
const selectedPerms = ref([])
const expandedDepts = ref([])
const userSectionExpanded = ref(true)
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
    const permsRes = await api.get('/permissions/')
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
    Swal.fire({ icon: 'success', title: 'Permissions Saved', timer: 1000, showConfirmButton: false })
    emit('refresh')
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

.selection-title {
  font-size: 0.95rem;
  font-weight: 800;
  color: #1a2a3a;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.salary-accordion {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.org-dept-block {
  border: 1px solid #f1f5f9;
  border-radius: 10px;
  overflow: hidden;
  background: #f8fafc;
}
.dept-row {
  background: white;
  padding: 12px 14px;
  border-bottom: 1px solid #f1f5f9;
}
.dept-header-row {
  cursor: pointer;
}
.dept-header-row:hover {
  background: #f1f5f9;
}
.dept-header.expanded {
  background: #f8fafc;
  border-bottom-color: #e2e8f0;
}
.dept-title-content {
  display: flex; 
  align-items: center; 
  gap: 8px;
}
.dept-title {
  font-weight: 700;
  color: #1e293b;
  font-size: 0.95rem;
}
.toggle-icon {
  font-size: 0.7rem;
  color: #94a3b8;
  width: 12px;
}
.jt-container {
  padding: 10px;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.jt-block-nested { 
  background: white;
  border: 1px solid #eef2f6;
  border-radius: 8px; 
  cursor: pointer; 
  transition: all 0.2s;
  overflow: hidden;
}
.jt-main-row {
  padding: 10px 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.jt-name {
  font-weight: 600;
  color: #334155;
  font-size: 0.88rem;
}
.jt-block-nested.active .jt-name {
  color: white;
}
.no-data-hint {
  font-size: 0.75rem;
  color: #94a3b8;
  padding: 8px 12px;
  font-style: italic;
}
.jt-block-nested:hover { background: #f1f5f9; border-color: #cbd5e1; }
.jt-block-nested.active { background: #1a2a3a; color: white; border-color: #1a2a3a; box-shadow: 0 4px 10px rgba(0,0,0,0.15); }

.permissions-content {
  padding: 28px;
  overflow-y: auto;
}
.no-jt-selected {
  height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #94a3b8;
}
.no-jt-selected i { font-size: 2.5rem; margin-bottom: 20px; opacity: 0.5; }

.content-header { 
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #f1f5f9;
}
.content-header h3 { font-size: 1.15rem; color: #1a2a3a; font-weight: 800; }
.highlight { color: #1a2a3a; text-decoration: underline; text-underline-offset: 4px; }

.perm-section { 
  background: #f8fafc; border-radius: 14px; padding: 24px; margin-bottom: 24px; border: 1px solid #e2e8f0;
}
.perm-section.muted { opacity: 0.8; }
.section-badge { display: inline-block; padding: 3px 10px; background: #e2e8f0; border-radius: 100px; font-size: 0.65rem; font-weight: 800; color: #475569; text-transform: uppercase; margin-bottom: 12px; }
.perm-section h4 { margin-bottom: 20px; font-size: 1rem; color: #1e293b; font-weight: 700; }

.perm-row.page-level { margin-bottom: 24px; padding: 16px; background: white; border-radius: 12px; border: 1px solid #dde3e8; display: flex; align-items: center; }

/* Switch Style */
.switch-label { display: flex; align-items: center; gap: 14px; cursor: pointer; position: relative; }
.label-text { font-weight: 700; color: #1e293b; font-size: 0.92rem; }
.switch-label input { opacity: 0; width: 0; height: 0; }
.slider { position: relative; width: 44px; height: 24px; background-color: #cbd5e1; border-radius: 34px; transition: .3s; }
.slider:before { position: absolute; content: ""; height: 18px; width: 18px; left: 3px; bottom: 3px; background-color: white; border-radius: 50%; transition: .3s; box-shadow: 0 1px 3px rgba(0,0,0,0.2); }
input:checked + .slider { background-color: #10b981; }
input:checked + .slider:before { transform: translateX(20px); }

.granular-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 5px; }
.granular-actions.disabled { opacity: 0.4; pointer-events: none; filter: grayscale(1); }
.action-item { background: white; padding: 14px; border-radius: 10px; border: 1px solid #e2e8f0; transition: all 0.2s; }
.action-item:hover { border-color: #1a2a3a; transform: translateY(-1px); box-shadow: 0 2px 8px rgba(0,0,0,0.05); }

.perm-grid-lite { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; }

/* Checkbox Style */
.chk-container, .chk-container-inline { 
  display: block; position: relative; padding-left: 32px; cursor: pointer; font-size: 0.88rem; color: #475569; user-select: none; font-weight: 600;
}
.chk-container input, .chk-container-inline input { position: absolute; opacity: 0; cursor: pointer; height: 0; width: 0; }
.checkmark { 
  position: absolute; top: 0; left: 0; height: 20px; width: 20px; background-color: #fff; border: 2px solid #cbd5e1; border-radius: 6px; transition: all 0.2s;
}
.chk-container:hover input ~ .checkmark, .chk-container-inline:hover input ~ .checkmark { border-color: #1a2a3a; }
.chk-container input:checked ~ .checkmark, .chk-container-inline input:checked ~ .checkmark { background-color: #1a2a3a; border-color: #1a2a3a; }
.checkmark:after { content: ""; position: absolute; display: none; }
.chk-container input:checked ~ .checkmark:after, .chk-container-inline input:checked ~ .checkmark:after { display: block; }
.chk-container .checkmark:after, .chk-container-inline .checkmark:after { left: 6px; top: 2px; width: 5px; height: 10px; border: solid white; border-width: 0 2.5px 2.5px 0; transform: rotate(45deg); }

.btn-primary { 
  background: #1a2a3a; color: white; border: none; padding: 12px 24px; border-radius: 10px; font-weight: 700; cursor: pointer; transition: all 0.2s; font-size: 0.95rem;
}
.btn-primary:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); background: #243447; }
.btn-primary:active { transform: translateY(0); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }

@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
.perm-section { animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
</style>
