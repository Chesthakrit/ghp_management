# --------------------------------------------------------------------------------
# ไฟล์: backend/debug_register.py
# หน้าที่: สคริปต์สำหรับทดสอบการสมัครสมาชิก (Register) โดยไม่ต้องใช้หน้าเว็บ
# --------------------------------------------------------------------------------
# รายละเอียด:
# - ใช้สำหรับเช็คว่า API ทำงานถูกต้องไหม
# - ยิง Request ไปที่ http://127.0.0.1:8000/users/ เพื่อจำลองการส่งข้อมูล
# - ช่วยให้รู้ว่ามีปัญหาที่ "หลังบ้าน" (Backend) หรือ "หน้าบ้าน" (Frontend)
# --------------------------------------------------------------------------------
import requests

url = "http://127.0.0.1:8000/users/"

payload_1 = {
    "username": "testuser1",
    "email": "test1@example.com",
    "password": "password",
    "id_card_number": ""  # First user with empty ID card
}

payload_2 = {
    "username": "testuser2",
    "email": "test2@example.com",
    "password": "password",
    "id_card_number": ""  # Second user with empty ID card (Should fail if Unique=True considers "" as value)
}

try:
    print("Registering User 1...")
    r1 = requests.post(url, json=payload_1)
    print(f"User 1: {r1.status_code} {r1.text}")

    print("\nRegistering User 2...")
    r2 = requests.post(url, json=payload_2)
    print(f"User 2: {r2.status_code} {r2.text}")

except Exception as e:
    print(f"Error: {e}")
