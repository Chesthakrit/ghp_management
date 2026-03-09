/**
 * api.js — Axios instance กลาง
 * 
 * ใช้ VITE_API_BASE จากไฟล์ .env
 * ถ้าต้องการให้มือถือเข้าได้ → แก้ค่า VITE_API_BASE ใน .env เป็น IP เครื่องคุณ
 * เช่น: VITE_API_BASE=http://192.168.1.11:8000
 */
import axios from 'axios'

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000',
    timeout: 10000, // Increase to 10s for slower local networks
})

// Interceptor: ใส่ Authorization Token อัตโนมัติทุก Request
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token')
    if (token) {
        config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
})

// Interceptor: จัดการ Response (Error Handling)
api.interceptors.response.use(
    (response) => response,
    (error) => {
        // หากได้รับ 401 Unauthorized แสดงว่า Token หมดอายุหรือผิดพลาด
        if (error.response && error.response.status === 401) {
            console.warn('Session expired or invalid token.')
            localStorage.clear()
            // ถ้าไม่ใช้ window.location.reload() ทันที อาจจะทำให้เกิด loop ในบางกรณี
            // แต่สำหรับ App.vue นี้ การ reload จะช่วยให้ getInitialView() ทำงานใหม่
            window.location.reload()
        }
        return Promise.reject(error)
    }
)

export default api
