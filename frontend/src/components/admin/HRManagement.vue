<template>
  <div class="hr-management-container">
    <div class="hr-settings-grid">
      <!-- 1 & 2. Unified Organization Structure (Compact) -->
      <div class="section-card org-struct-card">
        <div class="section-header">
          <h2>🏢 Organization & Job Titles</h2>
        </div>
        
        <!-- Global Add Dept -->
        <div class="hr-form-add main-add" v-if="hasPerm('action.hr.add_dept')">
          <input v-model="newDept.name" placeholder="New Department Name (e.g. Finance)" class="hr-input" @keyup.enter="saveDept" />
          <button class="btn-primary" @click="saveDept">+ Add Dept</button>
        </div>

        <div class="org-tree">
          <draggable
            v-model="localDepartments"
            item-key="id"
            handle=".drag-handle"
            animation="200"
            ghost-class="drag-ghost"
            @end="saveDeptOrder"
          >
            <template #item="{ element: d }">
            <div class="org-dept-block">
              <!-- Dept Header -->
              <div class="dept-row">
                <div v-if="editingDept?.id === d.id" class="edit-mode-row">
                  <input v-model="editingDept.name" class="hr-input-sm" />
                  <button class="btn-primary-xs" @click="updateDept">Save</button>
                  <button class="btn-cancel-xs" @click="editingDept = null">Cancel</button>
                </div>
                <div v-else class="view-mode-row" @click="toggleDeptExpansion(d.id)" style="cursor: pointer;">
                  <div style="display: flex; align-items: center; gap: 8px;">
                    <span class="drag-handle" @click.stop title="ลากเพื่อเรียงลำดับ">≡</span>
                    <span class="toggle-icon">{{ expandedDepts.includes(d.id) ? '▼' : '▶' }}</span>
                    <span class="dept-title">{{ d.name }}</span>
                  </div>
                  <div class="dept-actions" @click.stop>
                    <button v-if="hasPerm('action.hr.edit_name')" class="action-icon-btn" @click="startEditDept(d)" title="Edit Dept">✏️</button>
                    <button v-if="hasPerm('action.hr.delete')" class="action-icon-btn delete" @click="deleteDept(d.id)" title="Delete Dept">🗑️</button>
                  </div>
                </div>
              </div>

              <!-- Job Titles List under Dept -->
              <div v-if="expandedDepts.includes(d.id)" class="jt-container">
                <draggable
                  :model-value="localJobTitles.filter(j => j.department_id === d.id)"
                  @update:model-value="val => updateJTOrder(val, d.id)"
                  item-key="id"
                  handle=".drag-handle-jt"
                  animation="200"
                  ghost-class="drag-ghost"
                  @end="evt => saveJTOrder(d.id)"
                >
                  <template #item="{ element: jt }">
                  <div class="jt-block-nested">
                    <div v-if="editingJT?.id === jt.id" class="edit-mode-row">
                      <input v-model="editingJT.name" class="hr-input-sm" />
                      <button class="btn-primary-xs" @click="updateJT">Save</button>
                      <button class="btn-cancel-xs" @click="editingJT = null">Cancel</button>
                    </div>
                    <div v-else class="view-mode-row jt-main-row" @click="toggleJTExpansion(jt.id)" style="cursor: pointer;">
                      <div style="display: flex; align-items: center; gap: 6px;">
                        <span class="drag-handle-jt" @click.stop title="ลากเพื่อเรียงลำดับ">≡</span>
                        <span class="toggle-icon-sm">{{ expandedJTs.includes(jt.id) ? '▼' : '▶' }}</span>
                        <span class="jt-name">{{ jt.name }}</span>
                      </div>
                      <div class="jt-actions" @click.stop>
                        <button v-if="hasPerm('action.hr.manage_jt_skills')" class="btn-action-pill" @click="openJDModal(jt)">Skills</button>
                        <button v-if="isAdmin || hasPerm('page.access')" class="btn-action-pill" @click="openPageAccessModal(jt)">Access</button>
                        <button v-if="hasPerm('action.hr.edit_name')" class="action-icon-btn" @click="startEditJT(jt)">✏️</button>
                        <button v-if="hasPerm('action.hr.delete')" class="action-icon-btn delete" @click="deleteJT(jt.id)">🗑️</button>
                      </div>
                    </div>
                    <!-- Skill Preview under JT -->
                    <div v-if="expandedJTs.includes(jt.id)" class="jt-skill-preview">
                       <div v-if="jt.duties && jt.duties.length > 0" class="jt-skill-list">
                          <div v-for="duty in jt.duties" :key="duty.id" class="jt-skill-item">
                             {{ duty.name }}
                          </div>
                       </div>
                       <div v-else class="no-data-hint-sm" style="font-size: 0.7rem; color: #94a3b8; padding: 4px 10px;">
                          No skills assigned yet.
                       </div>
                    </div>
                  </div>
                  </template>
                </draggable>

                <!-- Quick Add JT for this Dept -->
                <div class="quick-add-jt" v-if="hasPerm('action.hr.add_jt')">
                  <input 
                    v-model="newJobTitle.name" 
                    v-if="selectedDeptId === d.id"
                    placeholder="Enter job title..." 
                    class="hr-input-sm"
                    @keyup.enter="saveJT"
                    autofocus
                  />
                  <button 
                    v-if="selectedDeptId !== d.id"
                    class="btn-ghost-add" 
                    @click="selectedDeptId = d.id; newJobTitle.name = ''"
                  >
                    + Add Job Title
                  </button>
                  <div v-else class="quick-add-actions">
                     <button class="btn-primary-xs" @click="saveJT">Add</button>
                     <button class="btn-cancel-xs" @click="selectedDeptId = null">Cancel</button>
                  </div>
                </div>
              </div>
            </div>
            </template>
          </draggable>
        </div>
      </div>

      <!-- 3 & 4. Unified Skills Management (Hierarchical) -->
      <div class="section-card skill-mgmt-card">
        <div class="section-header">
          <h2>📚 Skills & Category Library</h2>
        </div>
        
        <!-- Global Add Tag -->
        <div class="hr-form-add main-add" v-if="hasPerm('action.hr.add_tag')">
          <input v-model="newDutyCategoryName" placeholder="New Skill Tag (e.g. Software)" class="hr-input" @keyup.enter="saveDutyCategory" />
          <button class="btn-primary" @click="saveDutyCategory">+ Add Tag</button>
        </div>

        <div class="org-tree">
          <!-- Uncategorized Block -->
          <div v-if="dutiesPool.filter(d => !d.category_id).length > 0" class="org-dept-block uncategorized">
             <div class="dept-row" @click="toggleDeptExpansion('uncat_skill')" style="cursor: pointer;">
               <div style="display: flex; align-items: center; gap: 8px;">
                 <span class="toggle-icon">{{ expandedDepts.includes('uncat_skill') ? '▼' : '▶' }}</span>
                 <span class="dept-title">Uncategorized Skills</span>
               </div>
             </div>
             <div v-if="expandedDepts.includes('uncat_skill')" class="jt-container">
                <div v-for="duty in dutiesPool.filter(d => !d.category_id)" :key="duty.id" class="skill-block-nested">
                   <div class="skill-main-row" @click="toggleDutyExpansion(duty.id)" style="cursor: pointer;">
                      <div style="display: flex; align-items: center; gap: 8px;">
                         <span class="toggle-icon-sm">{{ expandedDuties.includes(duty.id) ? '▾' : '▸' }}</span>
                         <span class="jt-name">{{ duty.name }}</span>
                      </div>
                      <div class="jt-actions" @click.stop>
                         <button v-if="hasPerm('action.hr.edit_skill')" class="action-icon-btn" @click="openDutyModal(duty)">✏️</button>
                         <button v-if="hasPerm('action.hr.delete_skill')" class="action-icon-btn delete" @click="deleteDutyFromPool(duty.id)">🗑️</button>
                      </div>
                   </div>
                   <!-- Sub-skills & Desc -->
                   <div v-if="expandedDuties.includes(duty.id)" class="skill-details-area">
                      <p v-if="duty.description" class="skill-desc-text">{{ duty.description }}</p>
                      <div class="sub-skills-mini-list">
                         <div v-for="sub in duty.sub_duties" :key="sub.id" class="sub-skill-pill">{{ sub.name }}</div>
                      </div>
                   </div>
                </div>
             </div>
          </div>

          <!-- Categorized Blocks -->
          <div v-for="cat in dutyCategories" :key="cat.id" class="org-dept-block">
            <!-- Tag Header -->
            <div class="dept-row" @click="toggleDeptExpansion('cat_' + cat.id)" style="cursor: pointer;">
              <div v-if="editingDutyCategory?.id === cat.id" class="edit-mode-row" @click.stop>
                <input v-model="editingDutyCategory.name" class="hr-input-sm" />
                <button class="btn-primary-xs" @click="updateDutyCategory">Save</button>
                <button class="btn-cancel-xs" @click="editingDutyCategory = null">Cancel</button>
              </div>
              <div v-else class="view-mode-row">
                <div style="display: flex; align-items: center; gap: 8px;">
                  <span class="toggle-icon">{{ expandedDepts.includes('cat_' + cat.id) ? '▼' : '▶' }}</span>
                  <span class="dept-title">{{ cat.name }}</span>
                </div>
                <div class="dept-actions" @click.stop>
                  <button v-if="hasPerm('action.hr.edit_tag')" class="action-icon-btn" @click="startEditDutyCategory(cat)" title="Edit Tag">✏️</button>
                  <button v-if="hasPerm('action.hr.delete_tag')" class="action-icon-btn delete" @click="deleteDutyCategory(cat.id)" title="Delete Tag">🗑️</button>
                </div>
              </div>
            </div>

            <!-- Skills List under Tag -->
            <div v-if="expandedDepts.includes('cat_' + cat.id)" class="jt-container">
              <div v-for="duty in dutiesPool.filter(d => d.category_id === cat.id)" :key="duty.id" class="skill-block-nested">
                <div class="skill-main-row" @click="toggleDutyExpansion(duty.id)" style="cursor: pointer;">
                   <div style="display: flex; align-items: center; gap: 8px;">
                      <span class="toggle-icon-sm">{{ expandedDuties.includes(duty.id) ? '▾' : '▸' }}</span>
                      <span class="jt-name">{{ duty.name }}</span>
                   </div>
                   <div class="jt-actions" @click.stop>
                      <button v-if="hasPerm('action.hr.edit_skill')" class="action-icon-btn" @click="openDutyModal(duty)">✏️</button>
                      <button v-if="hasPerm('action.hr.delete_skill')" class="action-icon-btn delete" @click="deleteDutyFromPool(duty.id)">🗑️</button>
                   </div>
                </div>
                <!-- Sub-skills & Desc -->
                <div v-if="expandedDuties.includes(duty.id)" class="skill-details-area">
                   <p v-if="duty.description" class="skill-desc-text">{{ duty.description }}</p>
                   <div class="sub-skills-mini-list">
                      <div v-for="sub in duty.sub_duties" :key="sub.id" class="sub-skill-pill">{{ sub.name }}</div>
                   </div>
                </div>
              </div>

              <!-- Quick Add Skill for this Tag -->
              <div class="quick-add-jt" v-if="hasPerm('action.hr.add_skill')">
                <input 
                  v-model="newDutyName" 
                  v-if="editingDutyCategory?.id === null && selectedDeptId === 'tag_' + cat.id"
                  placeholder="Enter skill name..." 
                  class="hr-input-sm"
                  @keyup.enter="saveNewDutyWithCat(cat.id)"
                  autofocus
                />
                <button 
                  v-if="selectedDeptId !== 'tag_' + cat.id"
                  class="btn-ghost-add" 
                  @click="selectedDeptId = 'tag_' + cat.id; newDutyName = ''"
                >
                  + Add Skill to {{ cat.name }}
                </button>
                <div v-else class="quick-add-actions">
                   <button class="btn-primary-xs" @click="saveNewDutyWithCat(cat.id)">Add</button>
                   <button class="btn-cancel-xs" @click="selectedDeptId = null">Cancel</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ─── Modals (Skills, JD, Page Access) ─── -->
    <div v-if="showDutyModal" class="modal-overlay" @click.self="closeDutyModal">
      <div class="modal-box jd-modal">
        <h3>Skill Details</h3>
        <div class="form-group"><label>Skill Name</label><input v-model="selectedDuty.name" class="form-input" /></div>
        <div class="form-group"><label>Category / Tag</label>
          <select v-model="selectedDuty.category_id" class="form-input">
            <option :value="null">None / Uncategorized</option>
            <option v-for="cat in dutyCategories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
          </select>
        </div>
        <div class="form-group"><label>Description</label><textarea v-model="selectedDuty.description" class="form-input" rows="3"></textarea></div>
        <div class="sub-skills-section">
          <label>เพิ่มสกิลย่อย (CHECKLIST)</label>
          <div class="add-sub-skill-form">
            <input v-model="newSubDutyName" class="form-input" placeholder="ชื่อสกิลย่อย..." @keyup.enter="addSubDuty" />
            <button class="btn-primary" @click="addSubDuty">เพิ่ม</button>
          </div>
          <div class="sub-skills-list-admin">
             <div v-for="sub in selectedDuty.sub_duties" :key="sub.id" class="sub-skill-admin-item">
                <span>{{ sub.name }}</span>
                <button class="btn-delete-sm" @click="removeSubDuty(sub.id)">🗑️</button>
             </div>
          </div>
        </div>
        <div class="modal-actions"><button class="btn-cancel" @click="closeDutyModal">Cancel</button><button class="btn-primary" @click="saveDutyDetails">Save Details</button></div>
      </div>
    </div>

    <div v-if="showJDModal" class="modal-overlay" @click.self="closeJDModal">
      <div class="modal-box jd-modal">
        <h3>Skills for {{ selectedJT?.name }}</h3>
        <div class="hr-list jd-list" style="max-height: 400px; overflow-y: auto;">
          <label v-for="duty in dutiesPool" :key="duty.id" class="hr-list-item" style="cursor: pointer; display: flex; align-items: center; gap: 10px;">
            <input type="checkbox" v-model="selectedJT_duties" :value="duty.id" style="width: 18px; height: 18px;" />
            <span class="hr-label">{{ duty.name }}</span>
          </label>
        </div>
        <div class="modal-actions"><button class="btn-cancel" @click="closeJDModal">Cancel</button><button class="btn-primary" @click="saveJT_Duties">Save Assignments</button></div>
      </div>
    </div>

    <div v-if="showPageAccessModal" class="modal-overlay" @click.self="showPageAccessModal = false">
      <div class="modal-box jd-modal">
        <h3>Page Access for {{ selectedJT?.name }}</h3>
        <div class="hr-list jd-list" style="max-height: 400px; overflow-y: auto; padding: 10px;">
          <label v-for="perm in pagePermissions" :key="perm.id" class="hr-list-item" style="cursor: pointer; display: flex; align-items: center; gap: 15px;">
            <input type="checkbox" v-model="selectedJT_permissions" :value="perm.id" style="width: 20px; height: 20px;" />
            <div>
              <span class="hr-label">{{ perm.name }}</span>
              <div style="font-size: 0.75rem; color: #94a3b8;">Key: {{ perm.id }}</div>
            </div>
          </label>
        </div>
        <div class="modal-actions"><button class="btn-cancel" @click="showPageAccessModal = false">Cancel</button><button class="btn-primary" @click="saveJT_Permissions">Save Page Access</button></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import api from '../../api'
import Swal from 'sweetalert2'
import draggable from 'vuedraggable'

const props = defineProps({
  departments: { type: Array, default: () => [] },
  jobTitles: { type: Array, default: () => [] },
  currentUser: { type: Object, default: () => ({}) },
  isAdmin: { type: Boolean, default: false }
})

const emit = defineEmits(['refresh'])

// Local copies for sorting/UI
const localDepartments = ref([...props.departments])
const localJobTitles = ref([...props.jobTitles])

watch(() => props.departments, (newVal) => { localDepartments.value = [...newVal] })
watch(() => props.jobTitles, (newVal) => { localJobTitles.value = [...newVal] })

const hasPerm = (p) => {
  if (props.isAdmin) return true
  return (props.currentUser?.permissions || []).includes(p)
}

// All HR Logic (Refs & Methods)
const expandedDepts = ref([])
const expandedJTs = ref([])
const expandedDuties = ref([])
const selectedDeptId = ref(null)
const newDept = ref({ name: '' })
const editingDept = ref(null)
const newJobTitle = ref({ name: '', department_id: null })
const editingJT = ref(null)

const dutiesPool = ref([])
const dutyCategories = ref([])
const newDutyName = ref('')
const newDutyCategoryName = ref('')
const editingDutyCategory = ref(null)

const showDutyModal = ref(false)
const selectedDuty = ref({ id: null, name: '', description: '', category_id: null, sub_duties: [] })
const newSubDutyName = ref('')

const showJDModal = ref(false)
const selectedJT = ref(null)
const selectedJT_duties = ref([])

const showPageAccessModal = ref(false)
const pagePermissions = ref([])
const selectedJT_permissions = ref([])

onMounted(() => {
  fetchHRData()
  fetchPermissions()
})

const fetchHRData = async () => {
  try {
    const [dutiesRes, catsRes] = await Promise.all([
      api.get('/hr/duties'),
      api.get('/hr/duty-categories')
    ])
    dutiesPool.value = dutiesRes.data
    dutyCategories.value = catsRes.data
  } catch (e) { console.error(e) }
}

const fetchPermissions = async () => {
  try {
    const res = await api.get('/permissions/')
    pagePermissions.value = res.data.filter(p => p.id.startsWith('page.'))
  } catch (e) { console.error(e) }
}

// CRUD Methods
const toggleDeptExpansion = (id) => {
  if (expandedDepts.value.includes(id)) expandedDepts.value = expandedDepts.value.filter(i => i !== id)
  else expandedDepts.value.push(id)
}
const toggleJTExpansion = (id) => {
  if (expandedJTs.value.includes(id)) expandedJTs.value = expandedJTs.value.filter(i => i !== id)
  else expandedJTs.value.push(id)
}
const toggleDutyExpansion = (id) => {
  if (expandedDuties.value.includes(id)) expandedDuties.value = expandedDuties.value.filter(i => i !== id)
  else expandedDuties.value.push(id)
}

const saveDept = async () => {
  if (!newDept.value.name) return
  try {
    const value = newDept.value.name.toLowerCase().trim().replace(/\s+/g, '_')
    await api.post('/hr/departments', { name: newDept.value.name, value: value })
    newDept.value.name = ''
    emit('refresh')
  } catch (e) { Swal.fire('Error', 'Failed to add dept', 'error') }
}

const startEditDept = (dept) => { editingDept.value = { ...dept } }
const updateDept = async () => {
  if (!editingDept.value || !editingDept.value.name) return
  try {
    const value = editingDept.value.name.toLowerCase().trim().replace(/\s+/g, '_')
    await api.put(`/hr/departments/${editingDept.value.id}`, { name: editingDept.value.name, value: value })
    editingDept.value = null
    emit('refresh')
  } catch (e) { Swal.fire('Error', 'Failed to update dept', 'error') }
}

const deleteDept = async (id) => {
  const res = await Swal.fire({ title: 'Delete?', icon: 'warning', showCancelButton: true })
  if (!res.isConfirmed) return
  try {
    await api.delete(`/hr/departments/${id}`)
    emit('refresh')
  } catch (e) { Swal.fire('Error', 'Delete failed', 'error') }
}

const saveJT = async () => {
  if (!newJobTitle.value.name || !selectedDeptId.value) return
  try {
    await api.post('/hr/job-titles', { name: newJobTitle.value.name, department_id: selectedDeptId.value })
    newJobTitle.value.name = ''
    selectedDeptId.value = null
    emit('refresh')
  } catch (e) { Swal.fire('Error', 'Add JT failed', 'error') }
}

const startEditJT = (jt) => { editingJT.value = { ...jt } }
const updateJT = async () => {
  if (!editingJT.value || !editingJT.value.name) return
  try {
    await api.put(`/hr/job-titles/${editingJT.value.id}`, { name: editingJT.value.name, department_id: editingJT.value.department_id })
    editingJT.value = null
    emit('refresh')
  } catch (e) { Swal.fire('Error', 'Update JT failed', 'error') }
}

const deleteJT = async (id) => {
  const res = await Swal.fire({ title: 'Delete?', icon: 'warning', showCancelButton: true })
  if (!res.isConfirmed) return
  try {
    await api.delete(`/hr/job-titles/${id}`)
    emit('refresh')
  } catch (e) { Swal.fire('Error', 'Delete failed', 'error') }
}

const saveDeptOrder = async () => {
  try {
    const items = localDepartments.value.map((d, index) => ({ id: d.id, display_order: index + 1 }))
    await api.put('/hr/departments/reorder', { items })
    emit('refresh')
  } catch (e) { console.error(e) }
}

const updateJTOrder = (newList, deptId) => {
  const others = localJobTitles.value.filter(j => j.department_id !== deptId)
  localJobTitles.value = [...others, ...newList]
}

const saveJTOrder = async (deptId) => {
  try {
    const deptJTs = localJobTitles.value.filter(j => j.department_id === deptId)
    const items = deptJTs.map((jt, index) => ({ id: jt.id, display_order: index + 1 }))
    await api.put('/hr/job-titles/reorder', { items })
    emit('refresh')
  } catch (e) { console.error(e) }
}

const saveDutyCategory = async () => {
  if (!newDutyCategoryName.value) return
  try {
    await api.post('/hr/duty-categories', { name: newDutyCategoryName.value })
    newDutyCategoryName.value = ''
    await fetchHRData()
  } catch (e) { Swal.fire('Error', 'Add category failed', 'error') }
}
const startEditDutyCategory = (cat) => { editingDutyCategory.value = { ...cat } }
const updateDutyCategory = async () => {
  if (!editingDutyCategory.value) return
  try {
    await api.put(`/hr/duty-categories/${editingDutyCategory.value.id}`, { name: editingDutyCategory.value.name })
    editingDutyCategory.value = null
    await fetchHRData()
  } catch (e) { Swal.fire('Error', 'Update failed', 'error') }
}
const deleteDutyCategory = async (id) => {
  const res = await Swal.fire({ title: 'Delete?', icon: 'warning', showCancelButton: true })
  if (!res.isConfirmed) return
  try {
    await api.delete(`/hr/duty-categories/${id}`)
    await fetchHRData()
  } catch (e) { Swal.fire('Error', 'Delete failed', 'error') }
}

const saveNewDutyWithCat = async (catId) => {
  if (!newDutyName.value) return
  try {
    await api.post('/hr/duties', { name: newDutyName.value, category_id: catId })
    newDutyName.value = ''
    selectedDeptId.value = null
    await fetchHRData()
  } catch (e) { Swal.fire('Error', 'Add skill failed', 'error') }
}

// Duty Modal
const openDutyModal = (duty) => {
  selectedDuty.value = { ...duty, sub_duties: duty.sub_duties ? [...duty.sub_duties] : [] }
  showDutyModal.value = true
}
const closeDutyModal = () => { showDutyModal.value = false }
const saveDutyDetails = async () => {
  try {
    await api.put(`/hr/duties/${selectedDuty.value.id}`, {
      name: selectedDuty.value.name,
      description: selectedDuty.value.description,
      category_id: selectedDuty.value.category_id
    })
    closeDutyModal()
    await fetchHRData()
    emit('refresh')
  } catch (e) { Swal.fire('Error', 'Save failed', 'error') }
}
const deleteDutyFromPool = async (id) => {
  const res = await Swal.fire({ title: 'Delete?', icon: 'warning', showCancelButton: true })
  if (!res.isConfirmed) return
  try {
    await api.delete(`/hr/duties/${id}`)
    await fetchHRData()
    emit('refresh')
  } catch (e) { Swal.fire('Error', 'Delete failed', 'error') }
}

const addSubDuty = async () => {
  if (!newSubDutyName.value) return
  try {
    await api.post(`/hr/duties/${selectedDuty.value.id}/sub-duties`, { name: newSubDutyName.value })
    newSubDutyName.value = ''
    // Refresh sub duties list
    const res = await api.get(`/hr/duties/${selectedDuty.value.id}`)
    selectedDuty.value.sub_duties = res.data.sub_duties
  } catch (e) { Swal.fire('Error', 'Add sub skill failed', 'error') }
}
const removeSubDuty = async (id) => {
  try {
    await api.delete(`/hr/sub-duties/${id}`)
    selectedDuty.value.sub_duties = selectedDuty.value.sub_duties.filter(s => s.id !== id)
  } catch (e) { Swal.fire('Error', 'Delete failed', 'error') }
}

// JD Modal
const openJDModal = (jt) => {
  selectedJT.value = jt
  selectedJT_duties.value = jt.duties ? jt.duties.map(d => d.id) : []
  showJDModal.value = true
}
const closeJDModal = () => { showJDModal.value = false }
const saveJT_Duties = async () => {
  try {
    await api.put(`/hr/job-titles/${selectedJT.value.id}/duties`, { duty_ids: selectedJT_duties.value })
    closeJDModal()
    emit('refresh')
  } catch (e) { Swal.fire('Error', 'Save failed', 'error') }
}

// Permissions Modal
const openPageAccessModal = (jt) => {
  selectedJT.value = jt
  selectedJT_permissions.value = jt.permissions ? jt.permissions.map(p => p.id) : []
  showPageAccessModal.value = true
}
const saveJT_Permissions = async () => {
  try {
    await api.put(`/hr/job-titles/${selectedJT.value.id}/permissions`, { permission_ids: selectedJT_permissions.value })
    showPageAccessModal.value = false
    emit('refresh')
  } catch (e) { Swal.fire('Error', 'Save failed', 'error') }
}

</script>

<style scoped>
/* Copying essential HR styles */
.section-card { background: white; border-radius: 12px; padding: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); margin-bottom: 24px; }
.section-header h2 { margin: 0; font-size: 1.1rem; color: #1e293b; display: flex; align-items: center; gap: 10px; }
.hr-settings-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; align-items: start; }
.hr-form-add { display: flex; gap: 10px; margin-bottom: 20px; background: #fff; padding: 12px; border-radius: 10px; border: 1px solid #e2e8f0; }
.hr-input { flex: 1; padding: 10px 14px; border: 1px solid #dde3e8; border-radius: 8px; font-size: 0.88rem; outline: none; }
.org-tree { display: flex; flex-direction: column; gap: 15px; }
.org-dept-block { background: #f8fafc; border-radius: 10px; border: 1px solid #e2e8f0; padding: 12px; }
.dept-row { display: flex; justify-content: space-between; align-items: center; padding-bottom: 8px; border-bottom: 1px dashed #cbd5e1; margin-bottom: 8px; }
.dept-title { font-weight: 700; color: #1e293b; font-size: 0.95rem; }
.jt-container { padding-left: 20px; display: flex; flex-direction: column; gap: 5px; }
.jt-block-nested { padding: 4px 0; border-bottom: 1px solid rgba(0,0,0,0.02); }
.jt-main-row { padding: 8px 10px; border-radius: 6px; transition: background 0.2s; display: flex; justify-content: space-between; align-items: center; }
.jt-main-row:hover { background: #fff; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
.jt-name { font-size: 0.88rem; color: #444; }
.jt-skill-preview { background: #fff; padding: 8px; border-radius: 6px; margin: 4px 0 8px 25px; border: 1px solid #f1f5f9; }
.jt-skill-item { font-size: 0.78rem; color: #64748b; padding-left: 12px; position: relative; }
.jt-skill-item::before { content: '•'; position: absolute; left: 0; color: #3b82f6; }

/* Modals */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 2000; }
.modal-box { background: white; border-radius: 12px; padding: 24px; width: 90%; max-width: 500px; box-shadow: 0 20px 60px rgba(0,0,0,0.2); }
.form-group { margin-bottom: 15px; }
.form-group label { display: block; font-size: 0.75rem; color: #64748b; margin-bottom: 5px; text-transform: uppercase; font-weight: 700; }
.form-input { width: 100%; padding: 10px; border: 1px solid #dde3e8; border-radius: 8px; font-size: 0.9rem; }
.modal-actions { display: flex; gap: 10px; margin-top: 20px; }
.modal-actions button { flex: 1; }

/* Buttons */
.btn-primary { background: #1a2a3a; color: white; border: none; padding: 10px 16px; border-radius: 8px; font-weight: 600; cursor: pointer; }
.btn-cancel { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; padding: 10px; border-radius: 8px; cursor: pointer; }
.btn-action-pill { background: #f1f5f9; color: #475569; border: 1px solid #e2e8f0; padding: 2px 10px; border-radius: 12px; font-size: 0.72rem; font-weight: 600; cursor: pointer; margin-right: 4px; }
.btn-action-pill:hover { background: #1a2a3a; color: #fff; }
.action-icon-btn { background: transparent; border: none; cursor: pointer; opacity: 0.5; padding: 4px; }
.action-icon-btn:hover { opacity: 1; }
.btn-ghost-add { background: transparent; border: 1px dashed #cbd5e1; color: #64748b; padding: 8px; border-radius: 6px; width: 100%; text-align: left; font-size: 0.8rem; cursor: pointer; }

/* Drag & Drop */
.drag-handle, .drag-handle-jt { cursor: grab; color: #94a3b8; font-size: 1.1rem; padding: 0 4px; }
.drag-ghost { opacity: 0.45; background: #e0f2fe !important; border: 2px dashed #38bdf8 !important; }

/* Skills Section */
.skill-block-nested { border-bottom: 1px solid #f1f5f9; padding: 4px 0; }
.skill-main-row { display: flex; justify-content: space-between; align-items: center; padding: 8px 10px; border-radius: 6px; transition: background 0.2s; }
.skill-main-row:hover { background: #fff; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
.skill-details-area { background: #fff; padding: 12px; border-radius: 8px; margin: 4px 10px 10px 20px; border: 1px solid #edf2f7; }
.skill-desc-text { font-size: 0.82rem; color: #64748b; margin-bottom: 8px; }
.sub-skill-pill { font-size: 0.75rem; color: #475569; display: flex; align-items: center; gap: 8px; }
.sub-skill-pill::before { content: '•'; color: #3b82f6; }

/* Sub Skills Modal Section */
.sub-skills-section { margin-top: 20px; border-top: 1px solid #eee; padding-top: 15px; }
.add-sub-skill-form { display: flex; gap: 10px; margin-top: 10px; }
.sub-skill-admin-item { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: #f8fafc; border-radius: 6px; margin-bottom: 6px; border: 1px solid #e2e8f0; }

@media (max-width: 1024px) {
  .hr-settings-grid { grid-template-columns: 1fr; }
}
</style>
