import requests
import datetime
import time

# URL ของ Backend ที่รันอยู่ (ปรับพอร์ตให้ตรงกับที่ FastAPI รัน ปกติ 8000 หรือ 8081)
BASE_URL = "http://localhost:8000"
SN = "TEST_DEVICE_001"

def test_handshake():
    """ทดสอบการเชื่อมต่อ (Handshake)"""
    print("\n--- Testing Handshake ---")
    url = f"{BASE_URL}/iclock/cdata"
    params = {"SN": SN, "options": "all"}
    try:
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_push_attendance():
    """ทดสอบการส่งข้อมูลการสแกน (Push Attendance Data)"""
    print("\n--- Testing Push Attendance (ATTLOG) ---")
    url = f"{BASE_URL}/iclock/cdata"
    params = {"SN": SN, "table": "ATTLOG"}
    
    # สร้างข้อมูลจำลอง (PIN=1, Time=Now)
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # รูปแบบ ZKTeco: PIN\tTime\tStatus\tVerify_Type\t...
    data = f"1\t{now_str}\t1\t15\t0\t0\t0\n"
    # ทดสอบส่งอีกคน (PIN=2)
    data += f"2\t{now_str}\t1\t15\t0\t0\t0\n"
    
    headers = {"Content-Type": "text/plain"}
    
    try:
        response = requests.post(url, params=params, data=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Starting ZKTeco ADMS Test on Localhost...")
    test_handshake()
    time.sleep(1)
    test_push_attendance()
