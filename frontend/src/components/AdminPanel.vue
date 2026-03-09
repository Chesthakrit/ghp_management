<template>
  <div class="admin-panel">

    <!-- ─── Sidebar (Desktop / iPad) ─── -->
    <aside class="sidebar" :class="{ 'sidebar-open': sidebarOpen }">
      <div class="sidebar-logo">
        <span>Admin Panel</span>
        <!-- Mobile: close X -->
        <button class="sidebar-close-btn" @click="sidebarOpen = false">✕</button>
      </div>
      <nav class="sidebar-nav">
        <!-- 1 Admin Profile Page -->
        <button 
          class="nav-item" 
          @click="$emit('go-to-profile'); sidebarOpen = false"
        >
          <i class="fas fa-id-card-alt"></i> Back to Profile
        </button>

        <!-- 2 User Management -->
        <button
          v-if="isAdmin || hasPerm('page.usermanagement')"
          :class="['nav-item', { active: activeTab === 'users' }]"
          @click="activeTab = 'users'; sidebarOpen = false"
        >
          <i class="fas fa-users-cog"></i> User Management
        </button>


        <!-- 4 HR Settings -->
        <button
          v-if="isAdmin || hasPerm('page.hr')"
          :class="['nav-item', { active: activeTab === 'hr' }]"
          @click="activeTab = 'hr'; sidebarOpen = false"
        >
          <i class="fas fa-sliders-h"></i> HR Settings
        </button>

        <!-- 5 Salary Settings -->
        <button
          v-if="isAdmin || hasPerm('page.salary')"
          :class="['nav-item', { active: activeTab === 'salary' }]"
          @click="activeTab = 'salary'; sidebarOpen = false"
        >
          <i class="fas fa-money-check-alt"></i> Salary Settings
        </button>

        <!-- 6 Access Control -->
        <button
          v-if="isAdmin || hasPerm('page.access')"
          :class="['nav-item', { active: activeTab === 'access' }]"
          @click="activeTab = 'access'; sidebarOpen = false"
        >
          <i class="fas fa-user-shield"></i> Access Control
        </button>
      </nav>
      <button class="logout-sidebar-btn" @click="$emit('logout')">
        <i class="fas fa-door-open"></i> Logout System
      </button>
    </aside>

    <!-- Mobile Overlay -->
    <div v-if="sidebarOpen" class="sidebar-overlay" @click="sidebarOpen = false"></div>

    <!-- ─── Main Content Area ─── -->
    <div class="main-wrapper">
      
      <!-- Mobile Top Bar -->
      <div class="mobile-topbar">
        <button class="mobile-menu-btn" @click="sidebarOpen = true">☰</button>
        <span class="mobile-title">
          {{ 
            activeTab === 'users' ? 'User Management' : 
            activeTab === 'hr' ? 'HR Settings' : 
            activeTab === 'salary' ? 'Salary Settings' : 
            activeTab === 'access' ? 'Access Control' : 'Dashboard'
          }}
        </span>
        <button class="mobile-logout-btn" @click="$emit('logout')" title="Logout">🚪</button>
      </div>

      <main class="admin-content">

      <!-- TAB: Users -->
      <div v-if="activeTab === 'users'">
        <UserManagement 
          @go-to-identity="(id) => $emit('go-to-identity', id)"
          @view-profile="(id) => $emit('view-profile', id)"
        />
      </div>


      <!-- TAB: HR Settings -->
      <div v-if="activeTab === 'hr'">
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
                v-model="rawDepartments"
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
                      :model-value="rawJobTitles.filter(j => j.department_id === d.id)"
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
                       <div class="skill-main-row" @click="expandedDuties.includes(duty.id) ? expandedDuties = expandedDuties.filter(id => id !== duty.id) : expandedDuties.push(duty.id)" style="cursor: pointer;">
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
                    <div class="skill-main-row" @click="expandedDuties.includes(duty.id) ? expandedDuties = expandedDuties.filter(id => id !== duty.id) : expandedDuties.push(duty.id)" style="cursor: pointer;">
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
      </div>

      <!-- TAB: Salary Settings -->
      <div v-if="activeTab === 'salary'">
        <div class="section-card">
          <div class="section-header">
            <h2>💰 Salary Grade Settings</h2>
            <p style="font-size: 0.85rem; color: #64748b; margin-top: 4px;">Define min-max salary range and payment type for each job title.</p>
          </div>

          <div class="hr-settings-grid" style="margin-top: 20px;">
            <!-- Left: Select Department & Job Title (Accordion Style) -->
            <div class="salary-selection-pane">
              <label class="form-label-sm">Select Department & Job Title</label>
              
              <div class="hr-list salary-accordion">
                <div v-for="d in rawDepartments" :key="d.id" class="salary-dept-group">
                  <!-- Department Header -->
                  <div 
                    class="hr-list-item dept-header" 
                    :class="{ 'is-expanded': expandedDepts.includes(d.id) }"
                    @click="toggleDeptExpansion(d.id)"
                  >
                    <div style="display: flex; align-items: center; gap: 8px;">
                      <span class="toggle-icon">{{ expandedDepts.includes(d.id) ? '▼' : '▶' }}</span>
                      <span class="hr-label" style="font-weight: 700;">{{ d.name }}</span>
                    </div>
                  </div>

                  <!-- Job Titles Nested -->
                  <div v-if="expandedDepts.includes(d.id)" class="jt-nested-list">
                    <div 
                      v-for="jt in rawJobTitles.filter(j => j.department_id === d.id)" 
                      :key="jt.id" 
                      class="hr-list-item jt-item"
                      :class="{ selected: salarySelectedJT?.id === jt.id }"
                      @click="salarySelectedJT = jt; salarySelectedDeptId = d.id"
                    >
                      <span class="hr-label">{{ jt.name }}</span>
                      
                      <!-- Salary Preview Aligned Right -->
                      <div class="salary-preview-right">
                        <div v-if="jt.min_salary_monthly > 0 || jt.max_salary_monthly > 0" class="salary-tag monthly">
                          {{ (jt.min_salary_monthly || 0).toLocaleString() }} - {{ (jt.max_salary_monthly || 0).toLocaleString() }} M
                        </div>
                        <div v-if="jt.min_salary_daily > 0 || jt.max_salary_daily > 0" class="salary-tag daily">
                          {{ (jt.min_salary_daily || 0).toLocaleString() }} - {{ (jt.max_salary_daily || 0).toLocaleString() }} D
                        </div>
                      </div>
                    </div>
                    <div v-if="!rawJobTitles.filter(j => j.department_id === d.id).length" class="no-data-hint-sm">
                      No job titles defined
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Right: Set Salary Details -->
            <div class="salary-details-pane">
              <div v-if="salarySelectedJT" class="section-card" style="border-style: dashed; background: #f8fafc;">
                <h3 style="margin-bottom: 20px; color: #1a2a3a;">Settings: {{ salarySelectedJT.name }}</h3>
                
                <div class="salary-dual-config">
                  <!-- Monthly Section -->
                  <div class="salary-config-card" style="margin-bottom: 20px; padding: 15px; background: white; border-radius: 8px; border: 1px solid #e2e8f0;">
                    <h4 style="font-size: 0.75rem; color: #64748b; text-transform: uppercase; margin-bottom: 15px; display: flex; align-items: center; gap: 8px;">
                      🏢 Monthly Salary Configuration
                    </h4>
                    <div class="form-grid">
                      <div class="form-group">
                        <label>Minimum Monthly</label>
                        <input type="number" v-model.number="salarySelectedJT.min_salary_monthly" class="form-input" placeholder="0" />
                      </div>
                      <div class="form-group">
                        <label>Maximum Monthly</label>
                        <input type="number" v-model.number="salarySelectedJT.max_salary_monthly" class="form-input" placeholder="0" />
                      </div>
                    </div>
                  </div>

                  <!-- Daily Section -->
                  <div class="salary-config-card" style="padding: 15px; background: white; border-radius: 8px; border: 1px solid #e2e8f0;">
                    <h4 style="font-size: 0.75rem; color: #64748b; text-transform: uppercase; margin-bottom: 15px; display: flex; align-items: center; gap: 8px;">
                      ☀️ Daily Wage Configuration
                    </h4>
                    <div class="form-grid">
                      <div class="form-group">
                        <label>Minimum Daily</label>
                        <input type="number" v-model.number="salarySelectedJT.min_salary_daily" class="form-input" placeholder="0" />
                      </div>
                      <div class="form-group">
                        <label>Maximum Daily</label>
                        <input type="number" v-model.number="salarySelectedJT.max_salary_daily" class="form-input" placeholder="0" />
                      </div>
                    </div>
                  </div>
                </div>

                <div class="skill-based-hint" style="margin-top: 30px; padding: 15px; background: #fff; border-radius: 8px; border: 1px solid #e2e8f0;">
                  <h4 style="font-size: 0.8rem; color: #1e293b; margin-bottom: 8px;">ℹ️ Skill-Based Calculation Rule</h4>
                  <p style="font-size: 0.75rem; color: #64748b; line-height: 1.5;">
                    Salary will be automatically calculated based on the employee's skill performance for this job title.
                    (Specific calculation rules will be implemented later.)
                  </p>
                </div>

                <div style="margin-top: 25px; display: flex; justify-content: flex-end;">
                  <button class="btn-primary" @click="saveSalarySettings" :disabled="isSaving">
                    {{ isSaving ? 'Saving...' : 'Save Salary Settings' }}
                  </button>
                </div>
              </div>
              <div v-else class="hr-empty-hint" style="height: 200px; display: flex; align-items: center; justify-content: center; background: #f1f5f9; border-radius: 12px; border: 2px dashed #cbd5e1;">
                Please select a job title on the left to manage salary settings.
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- TAB: Access Control -->
      <div v-if="activeTab === 'access'">
        <AccessManagement />
      </div>

      </main>
    </div>

    <!-- ─── Edit Duty (Skill) Modal ─── -->
    <div v-if="showDutyModal" class="modal-overlay" @click.self="closeDutyModal">
      <div class="modal-box jd-modal">
        <h3>Skill Details</h3>
        
        <div class="form-group" style="margin-top: 20px;">
          <label>Skill Name</label>
          <input v-model="selectedDuty.name" class="form-input" />
        </div>
        
        <div class="form-group" style="margin-top: 15px;">
          <label>Category / Tag</label>
          <select v-model="selectedDuty.category_id" class="form-input">
            <option :value="null">None / Uncategorized</option>
            <option v-for="cat in dutyCategories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
          </select>
        </div>

        <div class="form-group" style="margin-top: 15px;">
          <label>Description / Details</label>
          <textarea v-model="selectedDuty.description" class="form-input" rows="3" placeholder="Explain what this skill requires..."></textarea>
        </div>

        <!-- Sub-Skill Checklist Management -->
        <div class="sub-skills-section" style="margin-top: 25px; border-top: 1px solid #eee; padding-top: 20px;">
          <label style="font-size: 0.8rem; font-weight: 700; color: #1e293b;">เพิ่มสกิลย่อย (CHECKLIST)</label>
          <div class="add-sub-skill-form" style="display: flex; gap: 10px; margin-top: 10px;">
            <input 
              v-model="newSubDutyName" 
              class="form-input" 
              placeholder="ชื่อสกิลย่อย..." 
              @keyup.enter="addSubDuty"
            />
            <button class="btn-primary" style="padding: 0 20px;" @click="addSubDuty">เพิ่ม</button>
          </div>

          <div class="sub-skills-list-admin" style="margin-top: 15px;">
             <div v-for="sub in selectedDuty.sub_duties" :key="sub.id" class="sub-skill-admin-item">
                <span>{{ sub.name }}</span>
                <button class="btn-delete-sm" @click="removeSubDuty(sub.id)">🗑️</button>
             </div>
             <div v-if="!selectedDuty.sub_duties?.length" class="no-data-hint">
               ยังไม่มีสกิลย่อย
             </div>
          </div>
        </div>

        <div class="modal-actions mt-20" style="display: flex; gap: 10px;">
          <button class="btn-cancel" style="flex: 1;" @click="closeDutyModal">Cancel</button>
          <button class="btn-primary" style="flex: 1;" @click="saveDutyDetails">Save Details</button>
        </div>
      </div>
    </div>

    <!-- ─── Edit Job Duties (JD) Modal ─── -->
    <div v-if="showJDModal" class="modal-overlay" @click.self="closeJDModal">
      <div class="modal-box jd-modal">
        <h3>Skills for {{ selectedJT?.name }}</h3>
        
        <p style="color: #64748b; font-size: 0.9em; margin-bottom: 15px;">
          Select the skills required for this job title from the central library.
        </p>

        <div class="hr-list jd-list" style="max-height: 400px; overflow-y: auto;">
          <label v-for="duty in dutiesPool" :key="duty.id" class="hr-list-item" style="cursor: pointer; display: flex; align-items: center; justify-content: flex-start; gap: 10px;">
            <input type="checkbox" v-model="selectedJT_duties" :value="duty.id" style="width: 18px; height: 18px;" />
            <span class="hr-label" style="font-weight: normal;">{{ duty.name }}</span>
          </label>
          <div v-if="dutiesPool.length === 0" class="no-data-hint">
            The skills library is empty. Please add skills first.
          </div>
        </div>

        <div class="modal-actions mt-20" style="display: flex; gap: 10px;">
          <button class="btn-cancel" style="flex: 1;" @click="closeJDModal">Cancel</button>
          <button class="btn-primary" style="flex: 1;" @click="saveJT_Duties">Save Assignments</button>
        </div>
      </div>
    </div>


  </div>

  <!-- ─── Edit Page Access Modal ─── -->
  <div v-if="showPageAccessModal" class="modal-overlay" @click.self="showPageAccessModal = false">
    <div class="modal-box jd-modal">
      <h3>Page Access for {{ selectedJT?.name }}</h3>
      
      <p style="color: #64748b; font-size: 0.9em; margin-bottom: 20px;">
        Select the pages that employees in this position can access.
      </p>

      <div class="hr-list jd-list" style="max-height: 400px; overflow-y: auto; padding: 10px;">
        <label v-for="perm in pagePermissions" :key="perm.id" class="hr-list-item" style="cursor: pointer; display: flex; align-items: center; justify-content: flex-start; gap: 15px; padding: 12px; border-radius: 8px; transition: background 0.2s;">
          <input type="checkbox" v-model="selectedJT_permissions" :value="perm.id" style="width: 20px; height: 20px;" />
          <div style="display: flex; flex-direction: column;">
            <span class="hr-label" style="font-weight: 600; font-size: 0.95rem;">{{ perm.name }}</span>
            <span style="font-size: 0.75rem; color: #94a3b8;">Key: {{ perm.id }}</span>
          </div>
        </label>
        <div v-if="pagePermissions.length === 0" class="no-data-hint">
          No page permissions defined in the system.
        </div>
      </div>

      <div class="modal-actions mt-20" style="display: flex; gap: 10px;">
        <button class="btn-cancel" style="flex: 1;" @click="showPageAccessModal = false">Cancel</button>
        <button class="btn-primary" style="flex: 1;" @click="saveJT_Permissions">Save Page Access</button>
      </div>
    </div>
  </div>


</template>


<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import api from '../api'
import Swal from 'sweetalert2'
import draggable from 'vuedraggable'
import AccessManagement from './AccessManagement.vue'
import UserManagement from './UserManagement.vue'

const apiBase = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

const emit = defineEmits(['logout', 'go-to-identity', 'go-to-profile', 'view-profile'])

const activeTab = ref('users')
const sidebarOpen = ref(false)
const currentUser = ref(null)
const isLoading = ref(false)
const isSaving = ref(false)

const isAdmin = computed(() => {
  const role = (currentUser.value?.role || '').toLowerCase()
  const uname = (currentUser.value?.username || '').toLowerCase()
  return role === 'admin' || uname === 'admin'
})

const hasPerm = (p) => {
  if (isAdmin.value) return true
  return (currentUser.value?.permissions || []).includes(p)
}

// Set active tab based on first available permission
watch(currentUser, (newVal) => {
  if (newVal) {
    if (isAdmin.value || hasPerm('page.usermanagement')) activeTab.value = 'users'
    else if (hasPerm('page.hr')) activeTab.value = 'hr'
    else if (hasPerm('page.salary')) activeTab.value = 'salary'
    else if (hasPerm('page.access')) activeTab.value = 'access'
  }
}, { immediate: true })

const departments = ref([])       
const rawDepartments = ref([])    
const rawJobTitles = ref([])      
const jobTitlesByDept = ref({})

// For HR Settings Tab management
const newDept = ref({ name: '', value: '' })
const newJobTitle = ref({ name: '', level: 1, department_id: null })
const selectedDeptId = ref(null)
const editingDept = ref(null)

const showJDModal = ref(false)
const selectedJT = ref(null)
const editingJT = ref(null)
const dutiesPool = ref([])
const newDutyName = ref('')
const selectedJT_duties = ref([])

const showDutyModal = ref(false)
const selectedDuty = ref({ id: null, name: '', description: '', category_id: null })
const dutyCategories = ref([])
const newDutyCategoryName = ref('')
const editingDutyCategory = ref(null)

const showPageAccessModal = ref(false)
const selectedJT_permissions = ref([])
const pagePermissions = ref([])

const newSubDutyName = ref('')
const expandedDepts = ref([])
const expandedCats = ref([])
const expandedDuties = ref([])
const expandedJTs = ref([])

const toggleDeptExpansion = (id) => {
  if (expandedDepts.value.includes(id)) {
    expandedDepts.value = expandedDepts.value.filter(itemId => itemId !== id)
  } else {
    expandedDepts.value.push(id)
  }
}

const toggleJTExpansion = (id) => {
  if (expandedJTs.value.includes(id)) {
    expandedJTs.value = expandedJTs.value.filter(itemId => itemId !== id)
  } else {
    expandedJTs.value.push(id)
  }
}

const fetchHRData = async () => {
  try {
    const [deptsRes, jobsRes, dutiesRes, catsRes] = await Promise.all([
      api.get('/hr/departments'),
      api.get('/hr/job-titles'),
      api.get('/hr/duties'),
      api.get('/hr/duty-categories')
    ])
    dutiesPool.value = dutiesRes.data
    dutyCategories.value = catsRes.data
    // Sort departments by display_order explicitly
    const sortedDepts = [...deptsRes.data].sort((a, b) => (a.display_order || 100) - (b.display_order || 100))
    
    departments.value = sortedDepts.map(d => ({ 
      ...d,
      label: d.name
    }))
    rawDepartments.value = [...sortedDepts] // เก็บแยกสำหรับ drag-and-drop
    
    // Sort job titles by display_order explicitly
    const sortedJobs = [...jobsRes.data].sort((a, b) => (a.display_order || 100) - (b.display_order || 100))

    // Convert flat job titles list to a grouped object for existing logic compatibility
    const grouped = {}
    sortedJobs.forEach(job => {
      // Find the department value (slug) for this title
      const deptObj = departments.value.find(d => d.id === job.department_id)
      if (deptObj) {
        if (!grouped[deptObj.value]) grouped[deptObj.value] = []
        grouped[deptObj.value].push(job.name)
      }
    })
    jobTitlesByDept.value = grouped
    
    // If we have job title objects (raw from API) we might need them for the management UI
    rawJobTitles.value = sortedJobs

    // Fetch Page Permissions
    await fetchPermissions()
  } catch (e) {
    console.error('Error fetching HR data:', e)
  }
}

// ─── Drag & Drop: อัปเดต rawJobTitles เมื่อลาก job title ใน dept นั้น ───
const updateJTOrder = (newList, deptId) => {
  // แทนที่รายการเดิมของ dept นี้ด้วยลำดับใหม่
  const others = rawJobTitles.value.filter(j => j.department_id !== deptId)
  rawJobTitles.value = [...others, ...newList]
}

// ─── Drag & Drop: บันทึกลำดับแผนกใหม่ไปยัง Backend ───
const saveDeptOrder = async () => {
  try {
    const items = rawDepartments.value.map((d, index) => ({ id: d.id, display_order: index + 1 }))
    await api.put('/hr/departments/reorder', { items })
    // sync กลับไปยัง departments dropdown ด้วย
    departments.value = rawDepartments.value.map(d => ({ ...d, label: d.name }))
  } catch (e) {
    console.error('Failed to save department order', e)
  }
}

// ─── Drag & Drop: บันทึกลำดับ job titles ใหม่ไปยัง Backend ───
const saveJTOrder = async (deptId) => {
  try {
    const deptJTs = rawJobTitles.value.filter(j => j.department_id === deptId)
    const items = deptJTs.map((jt, index) => ({ id: jt.id, display_order: index + 1 }))
    await api.put('/hr/job-titles/reorder', { items })
  } catch (e) {
    console.error('Failed to save job title order', e)
  }
}

const fetchPermissions = async () => {
  try {
    const res = await api.get('/permissions/')
    pagePermissions.value = res.data.filter(p => p.id.startsWith('page.'))
  } catch (e) {
    console.error('Failed to fetch permissions', e)
  }
}

const fetchData = async () => {
  isLoading.value = true
  try {
    await fetchHRData() // Fetch departments/jobs first
    
    // Fetch current user info to know who is viewing
    const meRes = await api.get('/users/me')
    currentUser.value = meRes.data
  } catch (e) {
    console.error(e)
    Swal.fire('Error', 'Failed to load data', 'error')
  } finally {
    isLoading.value = false
  }
}

// HR Management Actions
const saveDept = async () => {
  if (!newDept.value.name) return
  try {
    // Generate value automatically: lowercase and replace spaces with underscore
    const value = newDept.value.name.toLowerCase().trim().replace(/\s+/g, '_')
    await api.post('/hr/departments', {
      name: newDept.value.name,
      value: value
    })
    newDept.value = { name: '', value: '' }
    await fetchHRData()
    Swal.fire({ icon: 'success', title: 'Department Added', timer: 1000, showConfirmButton: false })
  } catch (e) {
    Swal.fire('Error', e.response?.data?.detail || 'Failed to add department', 'error')
  }
}

const startEditDept = (dept) => {
  editingDept.value = { ...dept }
}

const updateDept = async () => {
  if (!editingDept.value) return
  if (!editingDept.value.name) {
    Swal.fire('Error', 'Department name cannot be empty', 'warning')
    return
  }
  try {
    const value = editingDept.value.name.toLowerCase().trim().replace(/\s+/g, '_')
    await api.put(`/hr/departments/${editingDept.value.id}`, {
      name: editingDept.value.name,
      value: value
    })
    editingDept.value = null
    await fetchHRData()
    Swal.fire({ icon: 'success', title: 'Department Updated', timer: 1000, showConfirmButton: false })
  } catch (e) {
    Swal.fire('Error', e.response?.data?.detail || 'Failed to update department', 'error')
  }
}

const deleteDept = async (id) => {
  const result = await Swal.fire({
    title: 'Delete Department?',
    text: 'This will also remove all job titles linked to it.',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#d33'
  })
  if (!result.isConfirmed) return
  try {
    await api.delete(`/hr/departments/${id}`)
    await fetchHRData()
    Swal.fire('Deleted', 'Department removed', 'success')
  } catch (e) {
    Swal.fire('Error', e.response?.data?.detail || 'Failed to delete', 'error')
  }
}

const saveJT = async () => {
  if (!newJobTitle.value.name || !selectedDeptId.value) return
  try {
    await api.post('/hr/job-titles', {
      name: newJobTitle.value.name,
      level: newJobTitle.value.level || 1,
      department_id: selectedDeptId.value
    })
    newJobTitle.value.name = ''
    newJobTitle.value.level = 1
    await fetchHRData()
    Swal.fire({ icon: 'success', title: 'Job Title Added', timer: 1000, showConfirmButton: false })
  } catch (e) {
    Swal.fire('Error', e.response?.data?.detail || 'Failed to add job title', 'error')
  }
}

const startEditJT = (jt) => {
  editingJT.value = { ...jt }
}

const updateJT = async () => {
  if (!editingJT.value) return
  if (!editingJT.value.name) {
    Swal.fire('Error', 'Job name cannot be empty', 'warning')
    return
  }

  try {
    await api.put(`/hr/job-titles/${editingJT.value.id}`, {
      name: editingJT.value.name
    })
    editingJT.value = null
    await fetchHRData()
    Swal.fire({ icon: 'success', title: 'Updated Successfully', timer: 1000, showConfirmButton: false })
  } catch (e) {
    Swal.fire('Error', e.response?.data?.detail || 'Failed to update job title', 'error')
  }
}

const deleteJT = async (id) => {
  try {
    await api.delete(`/hr/job-titles/${id}`)
    await fetchHRData()
    Swal.fire({ icon: 'success', title: 'Deleted', timer: 1000, showConfirmButton: false })
  } catch (e) {
    Swal.fire('Error', e.response?.data?.detail || 'Failed to delete', 'error')
  }
}

const openJDModal = (jt) => {
  selectedJT.value = jt
  selectedJT_duties.value = (jt.duties || []).map(d => d.id)
  showJDModal.value = true
}

const closeJDModal = () => {
  showJDModal.value = false
  selectedJT.value = null
  selectedJT_duties.value = []
}

const saveJT_Duties = async () => {
  if (!selectedJT.value) return
  try {
    await api.put(`/hr/job-titles/${selectedJT.value.id}/duties`, {
      duty_ids: selectedJT_duties.value
    })
    await fetchHRData()
    closeJDModal()
    Swal.fire({ icon: 'success', title: 'Skills updated', timer: 1000, showConfirmButton: false })
  } catch (e) {
    Swal.fire('Error', e.response?.data?.detail || 'Failed to update skills', 'error')
  }
}

// Global Skills Library management
const saveNewDuty = async () => {
  if (!newDutyName.value) return
  try {
    await api.post('/hr/duties', { name: newDutyName.value })
    newDutyName.value = ''
    await fetchHRData()
    Swal.fire({ icon: 'success', title: 'Added', timer: 1000, showConfirmButton: false })
  } catch (e) {
    Swal.fire('Error', e.response?.data?.detail || 'Failed to add duty', 'error')
  }
}

const saveNewDutyWithCat = async (catId) => {
  if (!newDutyName.value) return
  try {
    await api.post('/hr/duties', { 
      name: newDutyName.value,
      category_id: catId
    })
    newDutyName.value = ''
    selectedDeptId.value = null
    await fetchHRData()
    Swal.fire({ icon: 'success', title: 'Added', timer: 1000, showConfirmButton: false })
  } catch (e) {
    Swal.fire('Error', e.response?.data?.detail || 'Failed to add duty', 'error')
  }
}

const deleteDutyFromPool = async (id) => {
  try {
    await api.delete(`/hr/duties/${id}`)
    await fetchHRData()
    Swal.fire({ icon: 'success', title: 'Deleted', timer: 1000, showConfirmButton: false })
  } catch (e) {
    Swal.fire('Error', e.response?.data?.detail || 'Failed to delete duty', 'error')
  }
}

const openDutyModal = (duty) => {
  selectedDuty.value = { 
    id: duty.id,
    name: duty.name,
    description: duty.description,
    category_id: duty.category_id || null,
    sub_duties: duty.sub_duties || []
  }
  showDutyModal.value = true
}

const addSubDuty = async () => {
  if (!newSubDutyName.value || !selectedDuty.value.id) return
  try {
    const res = await api.post('/hr/sub-duties', {
      name: newSubDutyName.value,
      duty_id: selectedDuty.value.id
    })
    if (!selectedDuty.value.sub_duties) selectedDuty.value.sub_duties = []
    selectedDuty.value.sub_duties.push(res.data)
    newSubDutyName.value = ''
    await fetchHRData() // Refresh pool to keep sync
  } catch (e) {
    Swal.fire('Error', 'Failed to add sub-skill', 'error')
  }
}

const removeSubDuty = async (subId) => {
  try {
    await api.delete(`/hr/sub-duties/${subId}`)
    selectedDuty.value.sub_duties = selectedDuty.value.sub_duties.filter(s => s.id !== subId)
    await fetchHRData()
  } catch (e) {
    Swal.fire('Error', 'Failed to delete sub-skill', 'error')
  }
}

const closeDutyModal = () => {
  showDutyModal.value = false
  selectedDuty.value = { id: null, name: '', description: '', category_id: null }
}

const saveDutyDetails = async () => {
  if (!selectedDuty.value.name) return
  try {
    await api.put(`/hr/duties/${selectedDuty.value.id}`, {
      name: selectedDuty.value.name,
      description: selectedDuty.value.description,
      category_id: selectedDuty.value.category_id
    })
    await fetchHRData()
    closeDutyModal()
    Swal.fire({ icon: 'success', title: 'Saved successfully', timer: 1000, showConfirmButton: false })
  } catch (e) {
    Swal.fire('Error', e.response?.data?.detail || 'Failed to update detail', 'error')
  }
}

// Duty Categories Management
const saveDutyCategory = async () => {
  if (!newDutyCategoryName.value) return
  try {
    await api.post('/hr/duty-categories', { name: newDutyCategoryName.value })
    newDutyCategoryName.value = ''
    await fetchHRData()
    Swal.fire({ icon: 'success', title: 'Category Added', timer: 1000, showConfirmButton: false })
  } catch (e) {
    Swal.fire('Error', e.response?.data?.detail || 'Failed to add category', 'error')
  }
}

const startEditDutyCategory = (cat) => {
  editingDutyCategory.value = { ...cat }
}

const updateDutyCategory = async () => {
  if (!editingDutyCategory.value) return
  try {
    await api.put(`/hr/duty-categories/${editingDutyCategory.value.id}`, {
      name: editingDutyCategory.value.name
    })
    editingDutyCategory.value = null
    await fetchHRData()
    Swal.fire({ icon: 'success', title: 'Category Updated', timer: 1000, showConfirmButton: false })
  } catch (e) {
    Swal.fire('Error', e.response?.data?.detail || 'Failed to update category', 'error')
  }
}

const deleteDutyCategory = async (id) => {
  const result = await Swal.fire({
    title: 'Delete Category?',
    text: 'This will not delete the skills in this category, but they will become uncategorized.',
    icon: 'warning',
    showCancelButton: true
  })
  if (!result.isConfirmed) return
  try {
    await api.delete(`/hr/duty-categories/${id}`)
    await fetchHRData()
    Swal.fire('Deleted', 'Category removed', 'success')
  } catch (e) {
    Swal.fire('Error', e.response?.data?.detail || 'Failed to delete category', 'error')
  }
}

const openEdit = (user) => {
  editingUser.value = user
  form.value = {
    first_name: user.first_name || '',
    last_name: user.last_name || '',
    department: user.employee_profile?.department || '',
    job_title: user.employee_profile?.job_title || '',
    role: user.role || '',
    is_active: user.is_active,
    hire_date: user.employee_profile?.hire_date || '',
    employment_status: user.employee_profile?.employment_status || 'intern',
    salary_type: user.employee_profile?.salary_type || 'monthly',
  }
  showModal.value = true
}

const openEditIdentity = (user) => {
  emit('go-to-identity', user.id)
}

const closeModal = () => {
  showModal.value = false
  editingUser.value = null
}

const saveUser = async () => {
  isSaving.value = true
  try {
    // 1. Update Personal Info + Role
    const userRes = await api.put(
      `/users/${editingUser.value.id}`,
      {
        role: form.value.role,
        is_active: form.value.is_active,
        first_name: form.value.first_name,
        last_name: form.value.last_name,
      }
    )

    // 2. Update Company Info (EmployeeProfile)
    // The backend returns user object (UserOut) which includes updated employee_profile
    const finalUpdateRes = await api.put(
      `/users/${editingUser.value.id}/profile`,
      {
        department: form.value.department,
        job_title: form.value.job_title,
        hire_date: form.value.hire_date,
        employment_status: form.value.employment_status,
        salary_type: form.value.salary_type,
      }
    )

    // Update local list with the MOST RECENT user object from server
    const updatedUser = finalUpdateRes.data
    const idx = users.value.findIndex(u => u.id === editingUser.value.id)
    if (idx !== -1) {
      // Ensure we don't lose existing fields by replacing the whole object
      users.value[idx] = updatedUser
    }

    Swal.fire({ icon: 'success', title: 'Saved successfully!', timer: 1500, showConfirmButton: false })
    closeModal()
    // Explicitly refresh data to be 100% sure sync is perfect
    fetchData()
  } catch (e) {
    console.error(e)
    Swal.fire('Error', e.response?.data?.detail || 'Save failed', 'error')
  } finally {
    isSaving.value = false
  }
}

const deleteUser = async (user) => {
  const result = await Swal.fire({
    title: 'Delete Employee?',
    html: `<b>${user.first_name || user.username} ${user.last_name || ''}</b> will be permanently removed.`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonText: 'Delete',
    cancelButtonText: 'Cancel',
    confirmButtonColor: '#1a2a3a',
    reverseButtons: true,
  })
  if (!result.isConfirmed) return

  try {
    await api.delete(`/users/${user.id}`)
    users.value = users.value.filter(u => u.id !== user.id)
  } catch (e) {
    Swal.fire('Error', e.response?.data?.detail || 'Failed to delete user', 'error')
  }
}

// Salary Settings Logic
const salarySelectedDeptId = ref(null)
const salarySelectedJT = ref(null)

const saveSalarySettings = async () => {
  if (!salarySelectedJT.value) return
  isSaving.value = true
  try {
    await api.put(`/hr/job-titles/${salarySelectedJT.value.id}`, {
      min_salary_monthly: salarySelectedJT.value.min_salary_monthly,
      max_salary_monthly: salarySelectedJT.value.max_salary_monthly,
      min_salary_daily: salarySelectedJT.value.min_salary_daily,
      max_salary_daily: salarySelectedJT.value.max_salary_daily
    })
    await fetchHRData()
    Swal.fire({
      icon: 'success',
      title: 'Success',
      text: `Salary settings for ${salarySelectedJT.value.name} updated successfully.`,
      timer: 1500,
      showConfirmButton: false
    })
  } catch (e) {
    Swal.fire('Error', 'Failed to save salary settings', 'error')
  } finally {
    isSaving.value = false
  }
}

const openPageAccessModal = (jt) => {
  selectedJT.value = jt
  try {
    selectedJT_permissions.value = jt.permissions ? JSON.parse(jt.permissions) : []
  } catch (e) {
    selectedJT_permissions.value = []
  }
  showPageAccessModal.value = true
}

const saveJT_Permissions = async () => {
  try {
    await api.put(`/hr/job-titles/${selectedJT.value.id}`, {
      permissions: JSON.stringify(selectedJT_permissions.value)
    })
    await fetchHRData()
    Swal.fire({ icon: 'success', title: 'Page access updated', timer: 1500, showConfirmButton: false })
    showPageAccessModal.value = false
  } catch (e) {
    Swal.fire('Error', 'Failed to save permissions', 'error')
  }
}

onMounted(fetchData)
</script>

<style scoped>
/* ─── Color Palette ─────────────────────────────────────
  Dark  : #1a2a3a   Navy
  Mid   : #243447   Hover/Active
  Shade : #2e4057   Borders in dark areas
  Muted : #4a6070   Muted text
  Light : #e8ecef   Light tint
  Pale  : #f2f4f6   Page background
──────────────────────────────────────────────────────── */

/* ═══════════ LAYOUT ═══════════ */
.admin-panel {
  display: flex;
  min-height: 100vh;
  background: #f2f4f6;
  font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
  position: relative;
}

/* ═══════════ SIDEBAR ═══════════ */
.sidebar {
  width: 240px;
  background: #1a2a3a;
  color: #a8bcc8;
  display: flex;
  flex-direction: column;
  padding: 20px 0;
  flex-shrink: 0;
  transition: transform 0.25s ease;
  z-index: 200;
}
.sidebar-logo {
  padding: 0 20px 20px;
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #fff;
  border-bottom: 1px solid #2e4057;
  margin-bottom: 12px;
  text-transform: uppercase;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.sidebar-close-btn {
  display: none;
  background: transparent;
  border: none;
  color: #7a9bb0;
  font-size: 1.1rem;
  cursor: pointer;
  padding: 0 4px;
  line-height: 1;
}
.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 0 10px;
}
.nav-item {
  background: transparent;
  border: none;
  color: #7a9bb0;
  padding: 11px 14px;
  border-radius: 6px;
  text-align: left;
  cursor: pointer;
  font-size: 0.88rem;
  font-family: inherit;
  transition: all 0.15s;
  font-weight: 500;
}
.nav-item:hover { background: #243447; color: #c8d8e4; }
.nav-item.active { background: #243447; color: #fff; font-weight: 700; border-left: 3px solid #5a8ea8; }
.logout-sidebar-btn {
  margin: 20px 10px 0;
  background: transparent;
  border: 1px solid rgba(231, 76, 60, 0.4);
  color: #e74c3c;
  padding: 10px 14px;
  border-radius: 6px;
  cursor: pointer;
  font-family: inherit;
  font-size: 0.85rem;
  transition: all 0.2s;
  text-align: left;
  font-weight: 600;
}
.logout-sidebar-btn:hover { background: #e74c3c; color: #fff; }

/* Mobile Logout icon */
.mobile-logout-btn {
  background: transparent;
  border: none;
  color: #e74c3c;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
}

/* Mobile overlay behind sidebar */
.sidebar-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  z-index: 199;
}

/* ═══════════ MOBILE TOPBAR ═══════════ */
.mobile-topbar {
  display: none;
  align-items: center;
  justify-content: space-between;
  background: #1a2a3a;
  color: #fff;
  padding: 12px 16px;
  z-index: 100;
  flex-shrink: 0;
}
.mobile-menu-btn, .mobile-back-btn {
  background: transparent;
  border: none;
  color: #a8bcc8;
  font-size: 1.3rem;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.15s;
  line-height: 1;
}
.mobile-menu-btn:hover, .mobile-back-btn:hover { background: #243447; color: #fff; }
.mobile-title {
  font-size: 0.88rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

/* Main Wrapper helps with mobile topbar + scrolling */
.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  height: 100vh;
}

/* ═══════════ MAIN CONTENT ═══════════ */
.admin-content {
  flex: 1;
  padding: 28px;
  overflow-y: auto;
  min-width: 0;
}

/* ═══════════ STATS ═══════════ */
.stats-row {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.stat-card {
  background: white;
  border-radius: 8px;
  padding: 14px 20px;
  border: 1px solid #dde3e8;
  min-width: 90px;
  text-align: center;
  flex: 1;
}
.stat-number { font-size: 1.7rem; font-weight: 700; color: #1a2a3a; }
.stat-label  { font-size: 0.74rem; color: #7a9bb0; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.05em; }

/* ═══════════ SECTION CARD ═══════════ */
.section-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #dde3e8;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 10px;
}
.section-header h2 { margin: 0; font-size: 0.9rem; font-weight: 700; color: #1a2a3a; letter-spacing: 0.04em; text-transform: uppercase; }
.search-row { display: flex; gap: 8px; flex-wrap: wrap; }
.search-input, .filter-select {
  padding: 8px 12px;
  border: 1px solid #ccd6de;
  border-radius: 6px;
  font-family: inherit;
  font-size: 0.88rem;
  background: #f7f9fa;
  color: #1a2a3a;
}
.search-input:focus, .filter-select:focus { outline: none; border-color: #4a6070; background: white; }
.search-input { width: 200px; }

/* ═══════════ SORT CONTROLS ═══════════ */
.controls-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: flex-end;
}
.sort-row {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.sort-label {
  font-size: 0.72rem;
  color: #7a9bb0;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.sort-btn {
  padding: 5px 11px;
  border: 1px solid #ccd6de;
  border-radius: 20px;
  background: #f7f9fa;
  color: #4a6070;
  font-size: 0.78rem;
  font-family: inherit;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  gap: 4px;
}
.sort-btn:hover { background: #e8ecef; border-color: #4a6070; color: #1a2a3a; }
.sort-btn.active {
  background: #1a2a3a;
  border-color: #1a2a3a;
  color: #c8d8e4;
  font-weight: 700;
}
.sort-btn.clear { border-color: #c0a0a0; color: #8b3a3a; background: transparent; }
.sort-btn.clear:hover { background: #8b3a3a; color: #fff; border-color: #8b3a3a; }
.sort-arrow { font-size: 0.85rem; font-weight: 700; }

/* Sortable table headers */
.sortable-th {
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
}
.sortable-th:hover { background: #e8ecef !important; color: #1a2a3a; }
.sortable-th.sorted { background: #dde3e8 !important; color: #1a2a3a; }
.th-arrow { margin-left: 4px; font-size: 0.8rem; color: #7a9bb0; }
.sortable-th.sorted .th-arrow { color: #1a2a3a; font-weight: 700; }

/* ═══════════ TABLE ═══════════ */
.table-wrapper { overflow-x: auto; -webkit-overflow-scrolling: touch; }
.user-table { width: 100%; border-collapse: collapse; min-width: 360px; }
.user-table th {
  text-align: left;
  padding: 9px 12px;
  background: #f2f4f6;
  font-size: 0.72rem;
  color: #4a6070;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  border-bottom: 1px solid #dde3e8;
  white-space: nowrap;
}
.user-table td { padding: 11px 12px; border-bottom: 1px solid #edf0f2; vertical-align: middle; font-size: 0.87rem; color: #2c3e50; }
.user-table tr:hover td { background: #f7f9fa; }

/* Responsive column helpers */
.show-mobile  { display: none; } /* hidden by default; shown only on mobile */

/* Name cell */
.name-cell { display: flex; align-items: center; gap: 10px; }
.avatar {
  width: 40px; height: 40px;
  border-radius: 50%;
  background: #1a2a3a;
  color: #a8bcc8;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.76rem; font-weight: 700;
  flex-shrink: 0;
  overflow: hidden;
  transition: box-shadow 0.15s;
}
.avatar.has-photo { cursor: pointer; }
.avatar.has-photo:hover { box-shadow: 0 0 0 2px #2e4057, 0 0 0 4px #a8bcc8; }
.avatar.large { width: 50px; height: 50px; font-size: 0.88rem; }
.avatar-img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }

.name-info { display: flex; flex-direction: column; gap: 2px; }
.name-info.clickable-name { cursor: pointer; }
.name-info.clickable-name:hover .name-text { color: #3b82f6; text-decoration: underline; }
.name-text  { font-size: 0.87rem; color: #1a2a3a; font-weight: 500; }
.nickname-text { font-size: 0.74rem; color: #7a9bb0; }
.username-sub  { font-size: 0.73rem; color: #7a9bb0; }
.job-title-sub { font-size: 0.73rem; color: #4a6070; font-style: italic; }
.username-cell { color: #7a9bb0; font-size: 0.83rem; }
.no-data { color: #b0c4d0; }

/* Badges */
.dept-badge {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.72rem;
  font-weight: 600;
  background: #e8ecef;
  color: #2e4057;
  border: 1px solid #ccd6de;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  white-space: nowrap;
}
.dept-badge.sm { font-size: 0.66rem; padding: 2px 6px; }

.emp-status-badge { padding: 3px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; white-space: nowrap; }
.emp-status-badge.intern    { background: #e8ecef; color: #4a6070; border: 1px solid #ccd6de; }
.emp-status-badge.permanent { background: #2e4057; color: #c8d8e4; border: 1px solid #2e4057; }
.emp-status-badge.terminated{ background: #1a2a3a; color: #7a9bb0; border: 1px solid #1a2a3a; }

.date-cell { font-size: 0.82rem; color: #7a9bb0; white-space: nowrap; }

.role-badge {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.72rem;
  font-weight: 700;
  background: #e8ecef;
  color: #1a2a3a;
  border: 1px solid #ccd6de;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

/* Action buttons (emoji+icon style) */
.action-cell { display: flex; gap: 4px; align-items: center; }
.btn-edit, .btn-id-card {
  background: #1a2a3a; color: #a8bcc8;
  border: none; padding: 7px 9px;
  border-radius: 5px; cursor: pointer;
  font-size: 1rem; line-height: 1;
  transition: background 0.15s;
}
.btn-edit:hover, .btn-id-card:hover { background: #243447; color: #fff; }
.btn-delete {
  background: transparent; color: #8b3a3a;
  border: 1px solid #c0a0a0; padding: 7px 9px;
  border-radius: 5px; cursor: pointer;
  font-size: 1rem; line-height: 1;
  transition: all 0.15s;
}
.btn-delete:hover { background: #8b3a3a; color: #fff; border-color: #8b3a3a; }

.admin-lock-badge {
  background: #f2f4f6;
  color: #7a9bb0;
  border: 1px solid #ccd6de;
  padding: 4px 8px;
  border-radius: 5px;
  font-size: 0.7rem;
  white-space: nowrap;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.lock-hint  { color: #7a9bb0; font-size: 0.74rem; margin-top: 4px; }
.empty-row  { text-align: center; color: #b0c4d0; padding: 40px !important; font-size: 0.88rem; }
.loading    { text-align: center; padding: 40px; color: #7a9bb0; font-size: 0.88rem; }

/* ═══════════ MODAL ═══════════ */
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(26,42,58,0.5);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
  padding: 16px;
}
.modal-box {
  background: white;
  border-radius: 10px;
  padding: 24px;
  width: 100%; max-width: 540px;
  max-height: 90vh; overflow-y: auto;
  border: 1px solid #dde3e8;
}
.modal-box h3 { margin: 0 0 14px; font-size: 0.9rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em; color: #1a2a3a; }
.modal-user-info {
  display: flex; align-items: center; gap: 12px;
  padding: 10px; background: #f2f4f6;
  border-radius: 7px; margin-bottom: 18px;
  border: 1px solid #dde3e8;
}
.modal-user-info strong { display: block; color: #1a2a3a; font-size: 0.92rem; }
.modal-user-info span   { font-size: 0.8rem; color: #7a9bb0; }
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}
.form-group { display: flex; flex-direction: column; gap: 5px; }
.form-group label { font-size: 0.73rem; color: #4a6070; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; }
.form-input {
  padding: 9px 10px;
  border: 1px solid #ccd6de; border-radius: 6px;
  font-family: inherit; font-size: 0.88rem;
  background: #f7f9fa; color: #1a2a3a;
  width: 100%; box-sizing: border-box;
}
.form-input:focus    { outline: none; border-color: #2e4057; background: white; }
.form-input:disabled { background: #edf0f2; color: #7a9bb0; cursor: not-allowed; }
.modal-actions {
  display: flex; justify-content: flex-end; gap: 8px;
  margin-top: 20px; padding-top: 14px;
  border-top: 1px solid #edf0f2;
}
.btn-cancel {
  background: #f2f4f6; border: 1px solid #ccd6de; padding: 9px 18px;
  border-radius: 6px; cursor: pointer;
  font-family: inherit; font-size: 0.88rem; color: #4a6070;
  transition: background 0.15s;
}
.btn-cancel:hover { background: #e8ecef; }
/* Sub Skills Styling */
.sub-skill-admin-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f8fafc;
  border-radius: 6px;
  margin-bottom: 6px;
  border: 1px solid #e2e8f0;
  font-size: 0.9rem;
}

.btn-save {
  background: #1a2a3a; color: #a8bcc8; border: none;
  padding: 9px 22px; border-radius: 6px; cursor: pointer;
  font-family: inherit; font-weight: 700; font-size: 0.88rem;
  letter-spacing: 0.03em; transition: background 0.15s;
}

.btn-save:hover:not(:disabled) { background: #243447; color: #fff; }
.btn-save:disabled { opacity: 0.4; cursor: not-allowed; }

/* ═══════════ PHOTO POPUP ═══════════ */
.photo-popup-overlay {
  position: fixed; inset: 0;
  background: rgba(26,42,58,0.65);
  backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
  z-index: 2000;
}
.photo-popup-box {
  position: relative;
  background: white;
  border-radius: 10px;
  padding: 8px;
  box-shadow: 0 20px 60px rgba(26,42,58,0.4);
  max-width: 320px; width: 90vw;
}
.popup-img { width: 100%; border-radius: 6px; display: block; }
.popup-close {
  position: absolute; top: -10px; right: -10px;
  width: 28px; height: 28px; border-radius: 50%;
  background: #1a2a3a; color: #a8bcc8;
  border: none; font-size: 1.1rem; line-height: 1;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: background 0.15s;
}
.popup-close:hover { background: #243447; color: #fff; }

/* HR Settings Section */
.hr-settings-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
.hr-form-add {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  background: #fff;
  padding: 12px;
  border-radius: 10px;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
}
.hr-input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #dde3e8;
  border-radius: 8px;
  font-size: 0.88rem;
  outline: none;
}
.hr-input:focus { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.1); }
.hr-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.hr-list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fff;
  border: 1px solid #edf0f2;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}
.hr-list-item:hover { border-color: #3b82f6; background: #f8fbff; }
.hr-list-item.selected { border-color: #3b82f6; background: #eff6ff; box-shadow: 0 4px 12px rgba(59,130,246,0.1); }
.hr-item-main { display: flex; flex-direction: column; }
.hr-label { font-weight: 600; font-size: 0.92rem; color: #1a2a3a; }
.hr-sublabel { font-size: 0.75rem; color: #7a9bb0; }
.btn-delete-sm {
  background: transparent;
  border: none;
  font-size: 1.1rem;
  cursor: pointer;
  opacity: 0.4;
  transition: opacity 0.2s;
}
.btn-delete-sm:hover { opacity: 1; color: #e74c3c; }

.hr-empty-hint {
  text-align: center;
  padding: 40px 20px;
  color: #7a9bb0;
  font-style: italic;
  font-size: 0.9rem;
  background: #fff;
  border-radius: 10px;
  border: 2px dashed #dde3e8;
}

/* Salary Tab Specific */
.salary-selection-pane {
  background: white;
  padding: 10px;
}
.salary-accordion {
  margin-top: 10px;
}
.salary-dept-group {
  margin-bottom: 5px;
}
.dept-header {
  background: #f8fafc !important;
  border-left: 4px solid #cbd5e1;
  padding: 10px 16px !important;
  transition: all 0.2s;
}
.dept-header:hover {
  background: #f1f5f9 !important;
}
.dept-header.is-expanded {
  border-left-color: #3b82f6;
  background: #f1f5f9 !important;
}
.jt-nested-list {
  padding: 5px 0 5px 20px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.jt-item {
  padding: 8px 12px !important;
  border-radius: 6px !important;
  font-size: 0.85rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.salary-preview-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  text-align: right;
}
.salary-tag {
  font-size: 0.65rem;
  font-weight: 700;
  line-height: 1.2;
}
.salary-tag.monthly { color: #059669; }
.salary-tag.daily { color: #d97706; }
.no-data-hint-sm {
  font-size: 0.75rem;
  color: #94a3b8;
  padding: 8px 12px;
  font-style: italic;
}

.form-label-sm {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #64748b;
  margin-bottom: 8px;
  display: block;
}
.salary-type-toggle {
  display: flex;
  background: #f1f5f9;
  padding: 4px;
  border-radius: 8px;
  gap: 4px;
}
.toggle-btn {
  flex: 1;
  border: none;
  background: transparent;
  padding: 8px;
  font-size: 0.85rem;
  border-radius: 6px;
  cursor: pointer;
  color: #64748b;
  font-family: inherit;
  transition: all 0.2s;
}
.toggle-btn.active {
  background: white;
  color: #1a2a3a;
  font-weight: 600;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.no-data-hint { text-align: center; padding: 20px; color: #b0c4d0; font-size: 0.82rem; }
.btn-primary {
  background: #1a2a3a;
  color: #fff;
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
}
.btn-primary:hover { background: #243447; }

/* HR Settings & Job Duties Modal Extras */
.hr-actions { display: flex; align-items: center; }
.btn-primary-sm {
  background: #243447; color: white; border: none; padding: 4px 10px; border-radius: 6px; 
  font-size: 0.75rem; cursor: pointer; transition: background 0.2s;
}
.btn-primary-sm:hover { background: #1a2a3a; }
.jd-modal { max-width: 500px; }
.jd-text { font-weight: 400; font-size: 0.88rem; }
.mt-10 { margin-top: 10px; }
.mt-20 { margin-top: 20px; }
.mr-2 { margin-right: 8px; }

/* ══════════════ ORG TREE (COMPACT) ══════════════ */
.org-struct-card { overflow: visible; }
.org-tree { display: flex; flex-direction: column; gap: 15px; margin-top: 10px; }
.org-dept-block { background: #f8fafc; border-radius: 10px; border: 1px solid #e2e8f0; padding: 12px; }
.dept-row { display: flex; justify-content: space-between; align-items: center; padding-bottom: 8px; border-bottom: 1px dashed #cbd5e1; margin-bottom: 8px; }
.dept-title { font-weight: 700; color: #1e293b; font-size: 0.95rem; }
.toggle-icon { font-size: 0.7rem; color: #64748b; width: 12px; display: inline-block; }
.jt-container { padding-left: 20px; display: flex; flex-direction: column; gap: 5px; }
.jt-row { padding: 6px 10px; border-radius: 6px; transition: background 0.2s; }
.jt-row:hover { background: #fff; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
.jt-name { font-size: 0.88rem; color: #475569; }
.jt-block-nested { padding: 2px 0; border-bottom: 1px solid rgba(0,0,0,0.02); }
.jt-block-nested:last-child { border-bottom: none; }
.jt-main-row { padding: 6px 10px; border-radius: 6px; transition: background 0.2s; }
.jt-main-row:hover { background: #fff; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
.jt-skill-preview { background: #fdfdfd; padding: 4px 0 8px 25px; margin-bottom: 4px; }
.jt-skill-list { display: flex; flex-direction: column; gap: 2px; }
.jt-skill-item { font-size: 0.78rem; color: #64748b; position: relative; padding-left: 12px; }
.jt-skill-item::before { content: '-'; position: absolute; left: 0; color: #cbd5e1; }
.view-mode-row { display: flex; justify-content: space-between; align-items: center; width: 100%; }
.edit-mode-row { display: flex; gap: 6px; align-items: center; width: 100%; }

/* Buttons & Inputs (Extra Small) */
.hr-input-sm { padding: 4px 10px; border: 1px solid #ccd6de; border-radius: 4px; font-size: 0.8rem; flex: 1; }
.btn-primary-xs { background: #1a2a3a; color: white; border: none; padding: 4px 10px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; cursor: pointer; }
.btn-cancel-xs { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; padding: 3px 10px; border-radius: 4px; font-size: 0.75rem; cursor: pointer; }

/* Icon-style Buttons */
.action-icon-btn { background: transparent; border: none; cursor: pointer; opacity: 0.5; font-size: 0.9rem; transition: opacity 0.2s; padding: 4px; }
.action-icon-btn:hover { opacity: 1; }
.action-icon-btn.delete:hover { color: #ef4444; }

/* Action Pille (Small buttons for Access/Skills) */
.btn-action-pill { background: #f1f5f9; color: #475569; border: 1px solid #e2e8f0; padding: 2px 10px; border-radius: 12px; font-size: 0.72rem; font-weight: 600; cursor: pointer; margin-right: 4px; transition: all 0.2s; }
.btn-action-pill:hover { background: #1a2a3a; color: #fff; border-color: #1a2a3a; }

/* Ghost Add Button */
.btn-ghost-add { background: transparent; border: 1px dashed #cbd5e1; color: #64748b; padding: 6px 12px; border-radius: 6px; width: 100%; text-align: left; font-size: 0.8rem; cursor: pointer; transition: all 0.2s; margin-top: 5px; }
.btn-ghost-add:hover { background: #fff; border-color: #3b82f6; color: #3b82f6; }
.quick-add-jt { display: flex; gap: 8px; align-items: center; margin-top: 5px; }
.quick-add-actions { display: flex; gap: 4px; }

/* ══════════════ SKILL LIBRARY (HIERARCHICAL) ══════════════ */
.skill-mgmt-card { overflow: visible; }
.skill-block-nested { border-bottom: 1px solid #f1f5f9; padding: 4px 0; }
.skill-block-nested:last-child { border-bottom: none; }
.skill-main-row { display: flex; justify-content: space-between; align-items: center; padding: 8px 10px; border-radius: 6px; transition: background 0.2s; }
.skill-main-row:hover { background: #fff; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
.toggle-icon-sm { font-size: 0.6rem; color: #94a3b8; width: 10px; display: inline-block; }
.skill-details-area { background: #fff; padding: 12px; border-radius: 8px; margin: 4px 10px 10px 20px; border: 1px solid #edf2f7; }
.skill-desc-text { font-size: 0.82rem; color: #64748b; margin-bottom: 8px; line-height: 1.4; }
.sub-skills-mini-list { display: flex; flex-direction: column; gap: 4px; border-top: 1px dashed #e2e8f0; padding-top: 8px; margin-top: 4px; }
.sub-skill-pill { background: transparent; color: #475569; border: none; padding: 2px 0; border-radius: 0; font-size: 0.75rem; font-weight: 500; display: flex; align-items: center; gap: 8px; }
.sub-skill-pill::before { content: '•'; color: #3b82f6; font-size: 1.1rem; line-height: 1; }

/* ═══════════════════════════════════════════════════════
   RESPONSIVE — Tablet + Mobile  (≤ 1024px)
   Sidebar เป็น slide-in drawer สำหรับทุกขนาด ≤ 1024px
═══════════════════════════════════════════════════════ */
@media (max-width: 1024px) {

  /* --- Sidebar: slide-in drawer --- */
  .sidebar {
    position: fixed;
    top: 0; left: 0; bottom: 0;
    width: 260px;
    transform: translateX(-100%);
    box-shadow: 4px 0 28px rgba(0,0,0,0.3);
    z-index: 300;
  }
  .sidebar.sidebar-open { transform: translateX(0); }
  .sidebar-close-btn  { display: block; }
  .sidebar-overlay    { display: block; }

  /* --- Show topbar (hamburger + title + back) --- */
  .mobile-topbar { display: flex; }

  /* --- Main content full width --- */
  .admin-content { padding: 20px; }

  /* --- Stats flexible --- */
  .stats-row { flex-wrap: wrap; gap: 10px; }
  .stat-card { padding: 12px 16px; flex: 1; min-width: 80px; }
  .stat-number { font-size: 1.5rem; }

  /* --- Hide lower-priority table columns on tablet --- */
  .hide-tablet { display: none !important; }
  .search-input { width: 160px; }
}

/* ═══════════════════════════════════════════
   RESPONSIVE — Mobile only  (≤ 640px)
   เพิ่มเติมจาก tablet: ซ่อน column มากขึ้น,
   modal เป็น bottom sheet, table compact
═══════════════════════════════════════════ */
@media (max-width: 640px) {

  /* Drawer narrower on small phone */
  .sidebar { width: 265px; }

  /* Tighter padding */
  .admin-content { padding: 16px; }

  /* --- Stats: 2-per-row grid --- */
  .stats-row { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 14px; }
  .stat-card { padding: 10px 12px; min-width: 0; }
  .stat-number { font-size: 1.3rem; }
  .stat-label  { font-size: 0.64rem; }

  /* Section card */
  .section-card { padding: 12px; }
  .section-header { flex-direction: column; align-items: flex-start; gap: 8px; margin-bottom: 12px; }
  .section-header h2 { font-size: 0.82rem; }

  /* Search full width */
  .search-row { width: 100%; }
  .search-input { flex: 1; min-width: 0; width: auto; }
  .filter-select { flex: 0 0 auto; font-size: 0.82rem; padding: 7px 8px; }

  /* Sort controls full width */
  .controls-row { align-items: flex-start; width: 100%; }
  .sort-row { width: 100%; }
  .sort-btn { font-size: 0.74rem; padding: 5px 10px; }

  /* Hide more columns on mobile */
  .hide-mobile { display: none !important; }

  /* Show inline mobile data */
  .show-mobile { display: block !important; }

  /* Table compact */
  .user-table td { padding: 9px 8px; font-size: 0.82rem; }
  .user-table th { padding: 7px 8px; font-size: 0.64rem; }

  /* Avatar smaller */
  .avatar { width: 36px; height: 36px; font-size: 0.68rem; }

  /* Action buttons compact */
  .btn-edit, .btn-id-card, .btn-delete { padding: 7px 8px; font-size: 0.95rem; }
  .action-cell { gap: 3px; }

  /* Modal: bottom sheet */
  .modal-overlay { padding: 0; align-items: flex-end; }
  .modal-box {
    border-radius: 18px 18px 0 0;
    max-width: 100%;
    max-height: 88vh;
    padding: 20px 16px 28px;
  }
  .form-grid { grid-template-columns: 1fr; gap: 12px; }
  .modal-actions { flex-direction: column-reverse; gap: 8px; }
  .btn-cancel, .btn-save { width: 100%; text-align: center; padding: 12px; }
}

/* ─── Drag & Drop ─── */
.drag-handle,
.drag-handle-jt {
  cursor: grab;
  color: #94a3b8;
  font-size: 1.1rem;
  padding: 0 4px;
  user-select: none;
  line-height: 1;
  flex-shrink: 0;
  transition: color 0.15s;
}
.drag-handle:hover,
.drag-handle-jt:hover {
  color: #3b82f6;
}
.drag-handle:active,
.drag-handle-jt:active {
  cursor: grabbing;
}
.drag-ghost {
  opacity: 0.45;
  background: #e0f2fe !important;
  border: 2px dashed #38bdf8 !important;
  border-radius: 8px;
}
</style>
