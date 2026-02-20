<template>
  <div class="register-wrapper">
    <div class="register-card">

      <div class="register-header">
        <h2 class="register-title">New Employee Registration</h2>
        <p class="register-subtitle">All fields are required. Please fill in exactly as per official documents.</p>
      </div>

      <div class="register-body">

        <!-- Account Information -->
        <div class="form-section">
          <h3 class="section-title">Account Information</h3>
          <div class="input-grid">
            <div class="field-group">
              <label>Username <span class="req">*</span></label>
              <input type="text" v-model="formData.username" placeholder="Login username" class="custom-input" autocomplete="off" />
            </div>
            <div class="field-group">
              <label>Nickname</label>
              <input type="text" v-model="formData.nickname" placeholder="Nickname (optional)" class="custom-input" />
            </div>
            <div class="field-group">
              <label>Password <span class="req">*</span></label>
              <div class="password-wrap">
                <input :type="showPass ? 'text' : 'password'" v-model="formData.password" placeholder="Password" class="custom-input" autocomplete="new-password" />
                <span class="eye-toggle" @click="showPass = !showPass">{{ showPass ? '▲' : '▼' }}</span>
              </div>
            </div>
            <div class="field-group">
              <label>Confirm Password <span class="req">*</span></label>
              <div class="password-wrap">
                <input :type="showPass2 ? 'text' : 'password'" v-model="formData.confirmPassword" placeholder="Confirm Password" class="custom-input" autocomplete="new-password" />
                <span class="eye-toggle" @click="showPass2 = !showPass2">{{ showPass2 ? '▲' : '▼' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Personal Information -->
        <div class="form-section">
          <h3 class="section-title">Personal Information</h3>
          <div class="input-grid">
            <div class="field-group">
              <label>First Name <span class="req">*</span></label>
              <input type="text" v-model="formData.firstName" placeholder="First Name" class="custom-input" />
            </div>
            <div class="field-group">
              <label>Last Name <span class="req">*</span></label>
              <input type="text" v-model="formData.lastName" placeholder="Last Name" class="custom-input" />
            </div>
            <div class="field-group">
              <label>Date of Birth <span class="req">*</span></label>
              <input type="date" v-model="formData.birthDate" class="custom-input" />
            </div>
            <div class="field-group">
              <label>Phone Number <span class="req">*</span></label>
              <input type="tel" v-model="formData.phone" placeholder="Phone Number" class="custom-input" />
            </div>
          </div>
        </div>

        <!-- Documents & Nationality -->
        <div class="form-section">
          <h3 class="section-title">Documents &amp; Nationality</h3>
          <div class="input-grid">
            <div class="field-group" style="grid-column: 1 / -1">
              <label>ID Card / Passport / Foreign Document Number <span class="req">*</span></label>
              <input type="text" v-model="formData.idCard" placeholder="Enter document number exactly as printed" class="custom-input" />
            </div>
            <div class="field-group">
              <label>Nationality <span class="req">*</span></label>
              <select v-model="formData.nationality" class="custom-input select-input">
                <option value="" disabled>Select Nationality</option>
                <option value="Thai">Thai</option>
                <option value="Myanmar">Myanmar</option>
                <option value="Cambodian">Cambodian</option>
                <option value="Lao">Lao</option>
                <option value="Vietnamese">Vietnamese</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Photos & Documents Upload -->
        <div class="form-section">
          <h3 class="section-title">Photos &amp; Documents Upload</h3>
          <div class="upload-grid">
            <div class="upload-item">
              <label class="upload-label">Portrait Photo <span class="req">*</span></label>
              <div class="upload-box" @click="$refs.photoInput.click()" :class="{ 'has-file': previewPhoto }">
                <img v-if="previewPhoto" :src="previewPhoto" class="preview-img" />
                <div v-else class="upload-placeholder">
                  <span class="upload-icon">+</span>
                  <span>Click to upload photo</span>
                  <span class="upload-hint">JPG, PNG (max 5MB)</span>
                </div>
              </div>
              <input ref="photoInput" type="file" accept="image/*" style="display:none" @change="handlePhotoChange" />
              <span class="file-name" v-if="formData.photo">{{ formData.photo.name }}</span>
            </div>
            <div class="upload-item">
              <label class="upload-label">ID / Passport / Work Permit Document <span class="req">*</span></label>
              <div class="upload-box" @click="$refs.idDocInput.click()" :class="{ 'has-file': previewIdDoc }">
                <img v-if="previewIdDoc" :src="previewIdDoc" class="preview-img" />
                <div v-else class="upload-placeholder">
                  <span class="upload-icon">+</span>
                  <span>Click to upload document</span>
                  <span class="upload-hint">JPG, PNG, PDF (max 5MB)</span>
                </div>
              </div>
              <input ref="idDocInput" type="file" accept="image/*,application/pdf" style="display:none" @change="handleIdDocChange" />
              <span class="file-name" v-if="formData.idDoc">{{ formData.idDoc.name }}</span>
            </div>
          </div>
        </div>

        <div class="action-buttons">
          <button class="save-button" @click="handleRegister" :disabled="isSaving">
            {{ isSaving ? 'Saving...' : 'Save Employee Data' }}
          </button>
          <button class="cancel-button" @click="$emit('go-to-login')">Cancel</button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import axios from 'axios'
import Swal from 'sweetalert2'

defineEmits(['go-to-login'])

const showPass  = ref(false)
const showPass2 = ref(false)
const isSaving  = ref(false)
const previewPhoto  = ref(null)
const previewIdDoc  = ref(null)

const formData = reactive({
  username: '',
  nickname: '',
  password: '',
  confirmPassword: '',
  firstName: '',
  lastName: '',
  birthDate: '',
  phone: '',
  idCard: '',
  nationality: '',
  photo: null,
  idDoc: null,
})

const handlePhotoChange = (e) => {
  const file = e.target.files[0]
  if (!file) return
  formData.photo = file
  previewPhoto.value = URL.createObjectURL(file)
}

const handleIdDocChange = (e) => {
  const file = e.target.files[0]
  if (!file) return
  formData.idDoc = file
  if (file.type.startsWith('image/')) {
    previewIdDoc.value = URL.createObjectURL(file)
  } else {
    previewIdDoc.value = null // PDF — no preview
  }
}

const handleRegister = async () => {
  // ── Frontend validation ────────────────────
  const required = {
    'Username':     formData.username,
    'Password':     formData.password,
    'First Name':   formData.firstName,
    'Last Name':    formData.lastName,
    'Date of Birth':formData.birthDate,
    'Phone':        formData.phone,
    'ID/Passport':  formData.idCard,
    'Nationality':  formData.nationality,
  }
  const missing = Object.entries(required).filter(([, v]) => !v || !String(v).trim())
  if (missing.length) {
    Swal.fire('Incomplete Form', `Please fill in: ${missing.map(([k]) => k).join(', ')}`, 'warning')
    return
  }
  if (formData.password !== formData.confirmPassword) {
    Swal.fire('Password Mismatch', 'Passwords do not match', 'error')
    return
  }
  if (!formData.photo) {
    Swal.fire('Missing Photo', 'Please upload a portrait photo', 'warning')
    return
  }
  if (!formData.idDoc) {
    Swal.fire('Missing Document', 'Please upload ID / Passport / Work Permit document', 'warning')
    return
  }

  isSaving.value = true
  try {
    // Step 1: Create user record
    const payload = {
      username:       formData.username.trim(),
      nickname:       formData.nickname.trim() || null,
      password:       formData.password,
      first_name:     formData.firstName.trim(),
      last_name:      formData.lastName.trim(),
      birth_date:     formData.birthDate,
      phone:          formData.phone.trim(),
      id_card_number: formData.idCard.trim(),
      nationality:    formData.nationality,
      role:           'employee',
    }

    const resp = await axios.post('http://127.0.0.1:8000/users/', payload)
    const userId = resp.data.id

    // Step 2: Upload files
    const fd = new FormData()
    fd.append('photo',  formData.photo)
    fd.append('id_doc', formData.idDoc)
    await axios.post(`http://127.0.0.1:8000/users/${userId}/upload`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    await Swal.fire({
      icon: 'success',
      title: 'Registration Successful!',
      text: 'Employee data saved. Please login.',
      timer: 2000,
      showConfirmButton: false,
    })

    // Reset form
    Object.assign(formData, {
      username: '', nickname: '', password: '', confirmPassword: '',
      firstName: '', lastName: '', birthDate: '', phone: '',
      idCard: '', nationality: '', photo: null, idDoc: null,
    })
    previewPhoto.value = null
    previewIdDoc.value = null

  } catch (error) {
    const detail = error.response?.data?.detail || 'Something went wrong'
    Swal.fire('Registration Failed', detail, 'error')
  } finally {
    isSaving.value = false
  }
}
</script>

<style scoped>
.register-wrapper {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 100vh;
  padding: 30px 20px;
  background: #f2f4f6;
}

.register-card {
  background: white;
  border-radius: 16px;
  padding: 36px 40px;
  width: 100%;
  max-width: 820px;
  box-shadow: 0 8px 32px rgba(26,42,58,0.12);
}

.register-header {
  text-align: center;
  margin-bottom: 28px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e8ecef;
}
.register-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1a2a3a;
  margin: 0 0 6px 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.register-subtitle { color: #7a9bb0; font-size: 0.88rem; margin: 0; }

.form-section { margin-bottom: 28px; }
.section-title {
  font-size: 0.82rem;
  font-weight: 700;
  color: #1a2a3a;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  border-bottom: 2px solid #e8ecef;
  padding-bottom: 8px;
  margin-bottom: 18px;
}

.input-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
@media (max-width: 600px) { .input-grid { grid-template-columns: 1fr; } }

.field-group { display: flex; flex-direction: column; gap: 5px; }
.field-group label {
  font-size: 0.75rem;
  font-weight: 700;
  color: #4a6070;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.req { color: #8b3a3a; }

.custom-input {
  width: 100%;
  padding: 10px 14px;
  border-radius: 8px;
  border: 1px solid #ccd6de;
  box-sizing: border-box;
  font-family: inherit;
  font-size: 0.9rem;
  color: #1a2a3a;
  background: #f7f9fa;
  transition: border-color 0.15s;
}
.custom-input:focus { outline: none; border-color: #2e4057; background: white; }
.select-input { cursor: pointer; }

.password-wrap { position: relative; }
.password-wrap .custom-input { padding-right: 40px; }
.eye-toggle {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  color: #7a9bb0;
  font-size: 0.75rem;
  user-select: none;
}

/* Upload boxes */
.upload-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
@media (max-width: 600px) { .upload-grid { grid-template-columns: 1fr; } }

.upload-item { display: flex; flex-direction: column; gap: 8px; }
.upload-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: #4a6070;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.upload-box {
  border: 2px dashed #ccd6de;
  border-radius: 10px;
  height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  overflow: hidden;
  background: #f7f9fa;
  transition: border-color 0.2s, background 0.2s;
}
.upload-box:hover, .upload-box.has-file { border-color: #2e4057; background: #edf1f4; }
.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: #7a9bb0;
  font-size: 0.85rem;
}
.upload-icon {
  font-size: 2rem;
  font-weight: 300;
  line-height: 1;
  color: #4a6070;
}
.upload-hint { font-size: 0.72rem; color: #b0c4d0; }
.preview-img { width: 100%; height: 100%; object-fit: cover; }
.file-name { font-size: 0.75rem; color: #4a6070; word-break: break-all; }

/* Buttons */
.action-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 32px;
  padding-top: 20px;
  border-top: 1px solid #e8ecef;
}
.save-button {
  padding: 12px 36px;
  background: #1a2a3a;
  color: #a8bcc8;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  transition: background 0.2s, color 0.2s;
}
.save-button:hover:not(:disabled) { background: #243447; color: #fff; }
.save-button:disabled { opacity: 0.5; cursor: not-allowed; }
.cancel-button {
  padding: 12px 28px;
  background: transparent;
  color: #4a6070;
  border: 1px solid #ccd6de;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.15s;
}
.cancel-button:hover { background: #f2f4f6; }
</style>
