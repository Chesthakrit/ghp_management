"""
ไฟล์สคริปต์สำหรับทดสอบระบบการเข้าสู่ระบบ (Login Verification)
รวมถึงกรณีการใส่ข้อมูลถูกต้อง, รหัสผิด และไม่มีผู้ใช้งานในระบบ
"""
import urllib.request
import urllib.parse
import json
import ssl

# ยกเว้นการตรวจสอบ SSL สำหรับการรันบน Localhost หากจำเป็น
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE_URL = "http://127.0.0.1:8000"

def login(username, password):
    url = f"{BASE_URL}/auth/login"
    data = urllib.parse.urlencode({
        "username": username,
        "password": password
    }).encode("utf-8")
    
    req = urllib.request.Request(url, data=data, method="POST")
    # ตั้งค่า Header สำหรับการส่งข้อมูลแบบ Form Data
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            status = response.getcode()
            response_body = response.read().decode("utf-8")
            return status, json.loads(response_body)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")
    except Exception as e:
        return 0, str(e)

# ฟังก์ชันสร้างผู้ใช้งานทดสอบ (เพื่อให้มั่นใจว่ามีข้อมูลให้ Login ได้)
def register_test_user():
    url = f"{BASE_URL}/users/"
    # สร้างรหัสเวลาเพื่อใช้เป็นข้อมูลที่ไม่ซ้ำกัน
    import time
    unique_id = int(time.time())
    
    # ข้อมูลสำหรับสมัครสมาชิกรูปแบบ JSON
    payload = {
        "username": f"verifylogin_{unique_id}",
        "email": f"verify_{unique_id}@test.com",
        "password": "correct_password",
        "role": "employee",
        "id_card_number": f"ID_{unique_id}", # Ensure unique
        "first_name": f"Test{unique_id}",
        "last_name": f"User{unique_id}"
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), method="POST")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            return payload["username"], payload["password"]
    except urllib.error.HTTPError as e:
        print(f"Register Failed: {e.read().decode('utf-8')}")
        return None, None

print("--- Starting Login Verification ---")

# ขั้นตอนที่ 1: สร้างผู้ใช้สำหรับการทดสอบ
print("\n[Step 1] Creating Test User...")
username, password = register_test_user()

if username:
    print(f"User created: {username} / {password}")

    # ขั้นตอนที่ 2: ทดสอบกรณีล็อกอินสำเร็จ (รหัสผ่านถูกต้อง)
    print("\n[Step 2] Testing Valid Login...")
    status, result = login(username, password)
    if status == 200 and "access_token" in result:
        print("✅ Success: Login passed with correct credentials.")
        print(f"   Token: {result['access_token'][:20]}...")
    else:
        print(f"❌ Failed: Expected 200, got {status} - {result}")

    # ขั้นตอนที่ 3: ทดสอบกรณีรหัสผ่านผิด
    print("\n[Step 3] Testing Invalid Password...")
    status, result = login(username, "wrong_password")
    if status == 404: # ระบบหลังบ้านจะตอบกลับเป็น 404 กรณีรหัสผ่านหรือไอดีไม่ถูกต้อง
        print("✅ Success: Login rejected with wrong password (404).")
    else:
        print(f"❌ Failed: Expected 404, got {status} - {result}")

    # ขั้นตอนที่ 4: ทดสอบกรณีไม่มีผู้ใช้งานนี้ในระบบ
    print("\n[Step 4] Testing Non-existent User...")
    status, result = login(username + "_fake", password)
    if status == 404:
        print("✅ Success: Login rejected for unknown user (404).")
    else:
        print(f"❌ Failed: Expected 404, got {status} - {result}")

else:
    print("Skipping login tests due to registration failure.")
