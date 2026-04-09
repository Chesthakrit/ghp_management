<template>
  <div class="access-management">
    <!-- Mode Switcher -->
    <div class="mode-switcher">
      <button 
        :class="['mode-btn', { active: activeMode === 'org' }]" 
        @click="activeMode = 'org'"
      >
        <i class="fas fa-sitemap"></i> Organization (แผนก/ตำแหน่ง)
      </button>
      <button 
        :class="['mode-btn', { active: activeMode === 'user' }]" 
        @click="activeMode = 'user'"
      >
        <i class="fas fa-user-shield"></i> Individual ID (รายบุคคล)
      </button>
    </div>

    <div class="access-grid">
      <!-- Left: Sidebar Tree -->
      <div class="jt-sidebar card">
        <h3 class="selection-title">
          <i :class="activeMode === 'org' ? 'fas fa-building' : 'fas fa-users'"></i>
          {{ activeMode === 'org' ? 'Structure Tree' : 'User Selection' }}
        </h3>
        
        <div v-if="isLoading" class="loading-state">Loading...</div>
        
        <!-- Organization Tree Mode -->
        <div v-else-if="activeMode === 'org'" class="org-tree">
          <div v-for="dept in departments" :key="dept.id" class="org-node">
            <!-- Section Header (Selectable & Expandable) -->
            <div 
              class="tree-header dept-tree-header" 
              :class="{ active: selectedType === 'dept' && selectedDept?.id === dept.id }"
              @click="selectDept(dept)"
            >
               <div class="header-main">
                  <span class="tree-toggle" @click.stop="toggleDeptExpansion(dept.id)">
                    {{ expandedDepts.includes(dept.id) ? '▼' : '▶' }}
                  </span>
                  <i class="fas fa-building node-icon"></i>
                  <span class="node-name">{{ dept.name }}</span>
               </div>
               <span class="node-badge" title="Group Access">Group</span>
            </div>

            <!-- Job Titles (Nested) -->
            <div v-if="expandedDepts.includes(dept.id)" class="tree-children">
              <div 
                v-for="jt in jobTitles.filter(j => j.department_id === dept.id)" 
                :key="jt.id"
                class="tree-item jt-tree-item"
                :class="{ active: selectedType === 'jt' && selectedJT?.id === jt.id }"
                @click="selectJobTitle(jt)"
              >
                  <i class="fas fa-user-tag node-icon-sm"></i>
                  <span class="node-name-sm">{{ jt.name }}</span>
              </div>
              <div v-if="!jobTitles.filter(j => j.department_id === dept.id).length" class="no-data-hint">
                Empty
              </div>
            </div>
          </div>
        </div>

        <!-- User Selection Mode -->
        <div v-else class="user-selection-list">
          <div 
            v-for="u in allUsers" 
            :key="u.id"
            class="user-item"
            :class="{ active: selectedUser?.id === u.id }"
            @click="selectUser(u)"
          >
            <div class="user-info">
              <span class="u-name">{{ u.first_name }} {{ u.last_name }}</span>
              <span class="u-id">ID: @{{ u.username }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Permissions Grid -->
      <div class="permissions-content card">
        <!-- Placeholder States -->
        <div v-if="!hasSelection" class="no-selection-state">
          <i :class="placeholderIcon"></i>
          <p>{{ placeholderText }}</p>
        </div>
        
        <div v-else>
          <!-- Header -->
          <div class="content-header">
            <div class="header-titles">
               <span class="selection-badge">{{ activeMode === 'org' ? (selectedType === 'dept' ? 'Section' : 'Position') : 'User' }}</span>
               <h3>{{ selectionName }}</h3>
            </div>
            
            <button class="btn-primary" @click="savePermissions" :disabled="isSaving">
              {{ isSaving ? 'Saving...' : '💾 Save Changes' }}
            </button>
          </div>

          <!-- Info Banner -->
          <div class="info-banner" v-if="activeMode === 'org' && selectedType === 'dept'">
             <i class="fas fa-info-circle"></i>
             EVERYONE in the <strong>{{ selectedDept?.name }}</strong> section will inherit any permissions set here.
          </div>

          <!-- Permission Layout -->
          <div v-for="section in permissionLayout" :key="section.title" class="perm-section">
            <div class="section-badge">{{ section.badge || 'Module' }}</div>
            <div class="accordion-header" @click="section.expanded = !section.expanded">
              <h4><i :class="section.icon"></i> {{ section.title }}</h4>
              <span class="toggle-icon">{{ section.expanded ? '▼' : '▶' }}</span>
            </div>
            
            <div v-if="section.expanded" class="section-content-area">
              <div class="perm-row-main">
                <label class="switch-label">
                  <input type="checkbox" v-model="selectedPerms" :value="section.pageId" />
                  <span class="slider"></span>
                  <span class="label-text">Enable Full Access to {{ section.title }}</span>
                </label>
              </div>

              <!-- Granular Actions -->
              <div v-if="activeMode === 'org'" class="granular-actions" :class="{ disabled: !selectedPerms.includes(section.pageId) }">
                <div v-for="action in section.actions" :key="action.id" class="action-item">
                  <label class="chk-container">
                    <input type="checkbox" v-model="selectedPerms" :value="action.id" :disabled="!selectedPerms.includes(section.pageId)" />
                    <span class="checkmark"></span>
                    <span class="action-label">{{ action.label }}</span>
                  </label>
                </div>
              </div>
              
              <!-- Individual Mode Hint -->
              <div v-else class="id-mode-hint">
                <p v-if="selectedPerms.includes(section.pageId)" class="hint-active">
                  <i class="fas fa-check-circle"></i> Granted specifically to this User ID.
                </p>
                <p v-else class="hint-normal">
                  Calculated based on Section/Position rules.
                </p>
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

const activeMode = ref('org')
const selectedType = ref(null) // 'dept' or 'jt'
const selectedDept = ref(null)
const selectedJT = ref(null)
const selectedUser = ref(null)

const expandedDepts = ref([])
const selectedPerms = ref([])
const allUsers = ref([])
const isLoading = ref(true)
const isSaving = ref(false)

const permissionLayout = ref([
  {
    title: 'User Management',
    pageId: 'page.usermanagement',
    icon: 'fas fa-users-cog',
    expanded: true,
    actions: [
      { id: 'action.user.add', label: 'Add Employee' },
      { id: 'action.user.edit_id', label: 'Identity Card' },
      { id: 'action.user.edit_profile', label: 'Edit Info' },
      { id: 'action.user.delete', label: 'Delete User' },
      { id: 'action.user.view_profile', label: 'View Profile' }
    ]
  },
  {
    title: 'HR Settings',
    pageId: 'page.hr',
    icon: 'fas fa-sitemap',
    expanded: true,
    actions: [
      { id: 'action.hr.add_dept', label: 'Add Dept' },
      { id: 'action.hr.add_jt', label: 'Add Post' },
      { id: 'action.hr.edit_name', label: 'Names' },
      { id: 'action.hr.delete', label: 'Remove' }
    ]
  },
  {
    title: 'Time & Leave',
    pageId: 'page.time_leave',
    icon: 'fas fa-clock',
    expanded: true,
    actions: [
      { id: 'action.time.edit_hours', label: 'Hours' },
      { id: 'action.time.edit_ot', label: 'OT' },
      { id: 'action.time.edit_leave', label: 'Quota' },
      { id: 'action.time.edit_holiday', label: 'Holidays' }
    ]
  },
  {
    title: 'Attendance Dashboard',
    pageId: 'page.attendance_dash',
    icon: 'fas fa-chart-line',
    badge: 'Analytics',
    expanded: false,
    actions: []
  },
  {
    title: 'Salary Management',
    pageId: 'page.salary',
    icon: 'fas fa-money-check-alt',
    expanded: false,
    actions: []
  }
])

// Computed for dynamic UI
const hasSelection = computed(() => {
   if (activeMode.value === 'org') return !!(selectedDept.value || selectedJT.value)
   return !!selectedUser.value
})

const selectionName = computed(() => {
   if (activeMode.value === 'org') {
      return selectedType.value === 'dept' ? selectedDept.value?.name : selectedJT.value?.name
   }
   return selectedUser.value ? `${selectedUser.value.first_name} ${selectedUser.value.last_name}` : ''
})

const placeholderIcon = computed(() => {
   if (activeMode.value === 'org') return 'fas fa-sitemap'
   return 'fas fa-user-shield'
})

const placeholderText = computed(() => {
   if (activeMode.value === 'org') return 'Select a Section or Job Position to manage group access.'
   return 'Select an Employee ID to manage individual override access.'
})

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
    const res = await api.get('/users/')
    allUsers.value = res.data
  } catch (e) {
    console.error('Failed to load users', e)
  } finally {
    isLoading.value = false
  }
}

const selectDept = (dept) => {
  selectedType.value = 'dept'
  selectedDept.value = dept
  selectedJT.value = null
  selectedUser.value = null
  try {
    selectedPerms.value = dept.permissions ? JSON.parse(dept.permissions) : []
  } catch (e) {
    selectedPerms.value = []
  }
}

const selectJobTitle = (jt) => {
  selectedType.value = 'jt'
  selectedJT.value = jt
  selectedDept.value = null
  selectedUser.value = null
  try {
    selectedPerms.value = jt.permissions ? JSON.parse(jt.permissions) : []
  } catch (e) {
    selectedPerms.value = []
  }
}

const selectUser = async (user) => {
  selectedUser.value = user
  selectedJT.value = null
  selectedDept.value = null
  selectedType.value = null
  try {
    const res = await api.get(`/access-control/user/${user.id}`)
    selectedPerms.value = res.data.map(a => a.page_id)
  } catch (e) {
    console.error(e)
    selectedPerms.value = []
  }
}

const savePermissions = async () => {
  isSaving.value = true
  try {
    const permsJson = JSON.stringify(selectedPerms.value)
    if (activeMode.value === 'org') {
      if (selectedType.value === 'dept') {
         await api.put(`/hr/departments/${selectedDept.value.id}`, { permissions: permsJson })
      } else {
         await api.put(`/hr/job-titles/${selectedJT.value.id}`, { permissions: permsJson })
      }
    } else {
      const currentGranted = await api.get(`/access-control/user/${selectedUser.value.id}`)
      const previouslyGrantedIds = currentGranted.data.map(a => a.page_id)
      const toGrant = selectedPerms.value.filter(p => !previouslyGrantedIds.includes(p))
      const toRevoke = previouslyGrantedIds.filter(p => !selectedPerms.value.includes(p))
      
      await Promise.all([
        ...toGrant.map(p => api.post(`/access-control/grant?user_id=${selectedUser.value.id}&page_id=${p}&can_edit=true`)),
        ...toRevoke.map(p => api.delete(`/access-control/revoke?user_id=${selectedUser.value.id}&page_id=${p}`))
      ])
    }
    Swal.fire({ icon: 'success', title: 'Updated Successfully', timer: 1000, showConfirmButton: false })
    emit('refresh')
  } catch (e) {
    Swal.fire('Error', 'Failed to update access', 'error')
  } finally {
    isSaving.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.access-management { height: 100%; display: flex; flex-direction: column; gap: 20px; }

.mode-switcher {
  display: flex; gap: 10px; padding: 6px; background: #f1f5f9; border-radius: 14px; align-self: flex-start;
  margin-bottom: 5px;
}
.mode-btn {
  padding: 10px 22px; border: none; background: transparent; color: #64748b; border-radius: 10px; cursor: pointer; font-weight: 700; transition: all 0.2s; display: flex; align-items: center; gap: 8px; font-size: 0.9rem;
}
.mode-btn.active { background: white; color: #1e293b; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }

.access-grid { display: grid; grid-template-columns: 310px 1fr; gap: 24px; flex: 1; min-height: 0; }
.card { background: white; border-radius: 16px; border: 1px solid #e2e8f0; display: flex; flex-direction: column; min-height: 0; box-shadow: 0 1px 4px rgba(0,0,0,0.03); }

.jt-sidebar { padding: 24px; overflow-y: auto; background: #fff; }
.selection-title { font-size: 0.85rem; font-weight: 850; color: #94a3b8; margin-bottom: 24px; display: flex; align-items: center; gap: 10px; text-transform: uppercase; letter-spacing: 0.08em; }

/* Org Tree Visuals (Matching HR Settings Style) */
.org-tree { display: flex; flex-direction: column; gap: 12px; }
.tree-header { 
   background: #475569; color: white; padding: 14px 18px; border-radius: 10px; cursor: pointer; display: flex; align-items: center; justify-content: space-between; transition: all 0.2s;
   box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06); border: 1px solid transparent;
}
.tree-header:hover { background: #334155; transform: translateY(-1px); }
.tree-header.active { background: #1e293b; border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.3); }

.header-main { display: flex; align-items: center; gap: 14px; }
.tree-toggle { width: 14px; font-size: 0.75rem; color: #cbd5e1; cursor: pointer; transition: transform 0.2s; }
.node-icon { font-size: 1rem; color: #94a3b8; }
.node-name { font-weight: 700; font-size: 1rem; letter-spacing: 0.02em; }
.node-badge { font-size: 0.65rem; padding: 3px 8px; background: rgba(255,255,255,0.15); border-radius: 6px; color: #f1f5f9; font-weight: 800; text-transform: uppercase; }

.tree-children { 
   margin-top: -6px; padding: 12px 10px 8px 30px; background: #f8fafc; border-radius: 0 0 10px 10px; border: 1px solid #e2e8f0; border-top: none;
   display: flex; flex-direction: column; gap: 6px; 
}
.tree-item { 
   padding: 10px 15px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; gap: 12px; transition: all 0.2s; background: white; border: 1px solid #e2e8f0;
}
.tree-item:hover { background: #f1f5f9; border-color: #cbd5e1; padding-left: 18px; }
.tree-item.active { background: #1e293b; color: white; border-color: #1e293b; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
.node-icon-sm { font-size: 0.85rem; color: #64748b; }
.active .node-icon-sm { color: #94a3b8; }
.node-name-sm { font-weight: 600; font-size: 0.9rem; }

.user-selection-list { display: flex; flex-direction: column; gap: 10px; }
.user-item { padding: 14px 18px; background: white; border: 1px solid #e2e8f0; border-radius: 12px; cursor: pointer; transition: all 0.2s; }
.user-item:hover { transform: translateX(5px); border-color: #1e293b; }
.user-item.active { background: #1e293b; color: white; border-color: #1e293b; }

.permissions-content { padding: 32px; overflow-y: auto; }
.no-selection-state { height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #94a3b8; text-align: center; }
.no-selection-state i { font-size: 3.5rem; margin-bottom: 24px; opacity: 0.15; }

.content-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 35px; padding-bottom: 24px; border-bottom: 2px solid #f1f5f9; }
.selection-badge { font-size: 0.65rem; padding: 4px 10px; background: #1e293b; color: white; border-radius: 6px; font-weight: 800; text-transform: uppercase; margin-bottom: 10px; display: inline-block; }
.content-header h3 { font-size: 1.35rem; font-weight: 850; color: #1e293b; margin: 0; }

.info-banner { background: #eff6ff; border-radius: 12px; padding: 14px 20px; color: #1e40af; font-size: 0.9rem; display: flex; align-items: center; gap: 12px; margin-bottom: 30px; font-weight: 600; border-left: 5px solid #2563eb; }

.perm-section { background: #f8fafc; border-radius: 20px; padding: 28px; margin-bottom: 24px; border: 1px solid #e2e8f0; transition: all 0.3s; }
.perm-section:hover { border-color: #cbd5e1; box-shadow: 0 4px 12px rgba(0,0,0,0.02); }
.section-badge { display: inline-block; padding: 4px 12px; background: #e2e8f0; border-radius: 100px; font-size: 0.65rem; font-weight: 850; color: #475569; margin-bottom: 15px; text-transform: uppercase; }

.accordion-header { display: flex; justify-content: space-between; align-items: center; cursor: pointer; }
.accordion-header h4 { margin: 0; font-size: 1.1rem; font-weight: 850; color: #1e293b; display: flex; align-items: center; gap: 12px; }
.toggle-icon { font-size: 0.75rem; color: #94a3b8; }

.section-content-area { margin-top: 25px; }
.perm-row-main { padding: 20px; background: white; border-radius: 16px; border: 1px solid #e2e8f0; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }

.switch-label { display: flex; align-items: center; gap: 16px; cursor: pointer; }
.label-text { font-weight: 850; font-size: 1rem; color: #1e293b; }
.switch-label input { opacity: 0; width: 0; height: 0; }
.slider { position: relative; width: 50px; height: 28px; background-color: #cbd5e1; border-radius: 34px; transition: .3s; }
.slider:before { position: absolute; content: ""; height: 22px; width: 22px; left: 3px; bottom: 3px; background-color: white; border-radius: 50%; transition: .3s; }
input:checked + .slider { background-color: #10b981; }
input:checked + .slider:before { transform: translateX(22px); }

.granular-actions { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.granular-actions.disabled { opacity: 0.35; pointer-events: none; filter: grayscale(1); }
.action-item { background: white; padding: 16px; border-radius: 12px; border: 1px solid #e2e8f0; transition: border 0.2s; }
.action-item:hover { border-color: #1e293b; }
.chk-container { display: flex; align-items: center; gap: 12px; cursor: pointer; font-size: 0.92rem; font-weight: 750; color: #475569; position: relative; padding-left: 32px; }
.chk-container input { position: absolute; opacity: 0; }
.checkmark { position: absolute; left: 0; top: 50%; transform: translateY(-50%); height: 20px; width: 20px; background: #fff; border: 2px solid #cbd5e1; border-radius: 6px; }
input:checked ~ .checkmark { background: #1e293b; border-color: #1e293b; }
.checkmark:after { content: ""; position: absolute; display: none; left: 6px; top: 2px; width: 5px; height: 10px; border: solid white; border-width: 0 2.5px 2.5px 0; transform: rotate(45deg); }
input:checked ~ .checkmark:after { display: block; }

.id-mode-hint { margin-top: 15px; padding: 16px; background: white; border-radius: 12px; border: 1.5px dashed #cbd5e1; }
.hint-active { color: #059669; font-weight: 800; font-size: 0.9rem; display: flex; align-items: center; gap: 8px; }
.hint-normal { color: #94a3b8; font-size: 0.88rem; font-style: italic; }

.btn-primary { background: #1e293b; color: white; border: none; padding: 14px 35px; border-radius: 14px; font-weight: 850; cursor: pointer; transition: all 0.3s; font-size: 1rem; }
.btn-primary:hover { border-radius: 10px; transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.15); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
