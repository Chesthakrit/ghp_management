<template>
    <div class="dashboard-container">
        <!-- แถบเมนูด้านบน (Navbar) -->
        <nav class="navbar">
            <div class="navbar-brand">GHP Management Platform</div>
            <div class="navbar-user">
                <span>Welcome, {{ username }}</span>
                <span v-if="roleName" class="role-badge">{{ roleName }}</span>
                
                <!-- ปุ่มเมนูสำหรับ Admin/Manager -->
                <div class="admin-menu" v-if="canManageUsers || canManageRoles">
                    <button @click="currentView = 'projects'" :class="{ active: currentView === 'projects' }">Projects</button>
                    <button v-if="canManageUsers" @click="emit('go-to-admin')" class="btn-admin-panel">⚙️ Admin Panel</button>
                </div>

                <button @click="logout" class="btn-logout">Logout</button>
            </div>
        </nav>

        <!-- ส่วนเนื้อหาหลัก (Content Area) -->
        <main class="dashboard-content">
            
            <!-- View: Projects -->
            <div v-if="currentView === 'projects'">
                <div class="content-header">
                    <h2>Construction Projects</h2>
                    <button class="btn-create">+ New Project</button>
                </div>

                <!-- Loading State -->
                <div v-if="isLoading" class="loading-spinner">
                    Loading...
                </div>

                <!-- Project Grid -->
                <div v-else-if="projects.length > 0" class="projects-grid">
                    <div v-for="project in projects" :key="project.id" class="project-card">
                        <div class="card-header">
                            <h3>{{ project.name }}</h3>
                            <span class="status-badge">Active</span>
                        </div>
                        <div class="card-body">
                            <p><strong>Customer:</strong> {{ project.customer }}</p>
                            <p><strong>Due Date:</strong> {{ project.due_date || 'N/A' }}</p>
                            <p class="description">{{ project.description }}</p>
                            <!-- Show Owner ID if Admin (or has permission) -->
                            <p v-if="canViewAllProjects" class="owner-info">Owner ID: {{ project.owner_id }}</p>
                        </div>
                        <div class="card-footer">
                            <button class="btn-view">View Details</button>
                        </div>
                    </div>
                </div>

                <!-- Empty State -->
                <div v-else class="empty-state">
                    <h3>No Projects Found</h3>
                    <p>Get started by creating a new project.</p>
                </div>
            </div>

            <!-- View: User Management -->
            <UserManagement v-if="currentView === 'users'" />

            <!-- View: Role Management -->
            <RoleManagement v-if="currentView === 'roles'" />

        </main>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import Swal from 'sweetalert2'
import UserManagement from './UserManagement.vue'
import RoleManagement from './RoleManagement.vue'

const emit = defineEmits(['go-to-login', 'go-to-admin'])

// --- Logic from Dashboard.js ---
const projects = ref([])
const isLoading = ref(false)

// User Info
const username = ref('')
const roleName = ref('')
const permissions = ref([])

// View State (projects, users, roles)
const currentView = ref('projects') 

// Permission Checks (Computed)
const canManageUsers = computed(() => permissions.value.includes('user.manage'))
const canManageRoles = computed(() => permissions.value.includes('role.manage'))
const canViewAllProjects = computed(() => permissions.value.includes('project.view_all'))

const fetchProjects = async () => {
    const token = localStorage.getItem('token')
    if (!token) {
        window.location.reload() 
        return
    }

    try {
        isLoading.value = true

        // 1. Decode Token ข้อมูลเบื้องต้น
        const payload = JSON.parse(atob(token.split('.')[1]))
        username.value = payload.sub
        
        // 2. ดึงข้อมูล User ล่าสุด (Role + Permissions)
        const userRes = await axios.get('http://127.0.0.1:8000/users/me', {
            headers: { Authorization: `Bearer ${token}` }
        })
        
        roleName.value = userRes.data.role
        permissions.value = userRes.data.permissions || []

        // 3. ดึงข้อมูล Projects
        const response = await axios.get('http://127.0.0.1:8000/projects/', {
            headers: {
                Authorization: `Bearer ${token}`
            }
        })
        projects.value = response.data

    } catch (error) {
        console.error('Error fetching data:', error)
        if (error.response && error.response.status === 401) {
            logout()
        }
    } finally {
        isLoading.value = false
    }
}

const logout = () => {
    localStorage.removeItem('token')
    window.location.reload() 
    
    Swal.fire({
        icon: 'success',
        title: 'Logged Out',
        timer: 1000,
        showConfirmButton: false
    })
}

// Initial Fetch
onMounted(() => {
    fetchProjects()
})
</script>

<style scoped>
/* --- Styles from Dashboard.css --- */
.dashboard-container {
    min-height: 100vh;
    background-color: #f5f7fa;
    color: #333;
    font-family: 'Kanit', sans-serif;
}

/* แถบเมนูด้านบน (Navbar) */
.navbar {
    background-color: #1a2a3a;
    color: white;
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.navbar-brand {
    font-size: 1.5rem;
    font-weight: bold;
    display: flex;
    align-items: center;
    gap: 10px;
}

.btn-admin-panel {
    background: rgba(52, 152, 219, 0.3);
    border: 1px solid #3498db !important;
    color: white;
}
.btn-admin-panel:hover {
    background: #3498db !important;
}

.btn-logout {
    background-color: transparent;
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-logout:hover {
    background-color: rgba(255, 255, 255, 0.1);
    border-color: white;
}

/* ส่วนเนื้อหาหลัก (Content Area) */
.dashboard-content {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
}

.content-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
}

.content-header h2 {
    font-size: 1.8rem;
    color: #1a2a3a;
    margin: 0;
}

.btn-create {
    background-color: #2ecc71;
    color: white;
    border: none;
    padding: 0.5rem 1.5rem;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
}

.navbar-user {
    display: flex;
    align-items: center;
    gap: 15px;
}

.role-badge {
    background-color: rgba(255, 255, 255, 0.2);
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.9rem;
}

.admin-menu {
    display: flex;
    gap: 10px;
    margin-right: 15px;
}

.admin-menu button {
    background: transparent;
    border: 1px solid rgba(255, 255, 255, 0.5);
    color: white;
    padding: 5px 10px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
}

.admin-menu button.active {
    background: white;
    color: #1a2a3a;
    font-weight: bold;
}

/* ตารางแสดงรายการโปรเจกต์ (Project Grid) */
.projects-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 2rem;
}

/* การ์ดโปรเจกต์ (Project Card) */
.project-card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    transition: transform 0.2s, box-shadow 0.2s;
    border-left: 5px solid #1a2a3a;
}

.project-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
}

.card-header h3 {
    font-size: 1.25rem;
    font-weight: 600;
    margin: 0;
    color: #2c3e50;
}

.status-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 15px;
    font-size: 0.8rem;
    background-color: #eab543;
    color: white;
}

.card-body p {
    margin: 0.5rem 0;
    color: #576574;
}

.description {
    color: #95a5a6;
    font-size: 0.9rem;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.owner-info {
    font-size: 0.8rem;
    color: #7f8c8d;
    margin-top: 10px !important;
}

.card-footer {
    margin-top: 1.5rem;
    padding-top: 1rem;
    border-top: 1px solid #eee;
    display: flex;
    justify-content: flex-end;
}

.btn-view {
    background-color: transparent;
    color: #3498db;
    border: 1px solid #3498db;
    padding: 0.4rem 1rem;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-view:hover {
    background-color: #3498db;
    color: white;
}

/* กรณีไม่มีข้อมูล (Empty State) */
.empty-state {
    text-align: center;
    padding: 4rem;
    color: #bdc3c7;
    grid-column: 1 / -1;
}

.empty-state h3 {
    margin-bottom: 0.5rem;
}

.loading-spinner {
    text-align: center;
    padding: 2rem;
    color: #666;
    grid-column: 1 / -1;
}
</style>
