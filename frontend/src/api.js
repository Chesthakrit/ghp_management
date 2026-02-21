/**
 * api.js — Axios instance กลาง
 * 
 * ใช้ VITE_API_BASE จากไฟล์ .env
 * ถ้าต้องการให้มือถือเข้าได้ → แก้ค่า VITE_API_BASE ใน .env เป็น IP เครื่องคุณ
 * เช่น: VITE_API_BASE=http://192.168.1.100:8000
 */
import axios from 'axios'

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000',
})

// Interceptor: ใส่ Authorization Token อัตโนมัติทุก Request
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token')
    if (token) {
        config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
})

export default api
