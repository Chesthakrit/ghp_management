
import os
import shutil
import psycopg2

# 1. Database Connection Info
DB_URL = "postgresql://postgres:1900@localhost/ghp_db"
UPLOAD_DIR = "uploads/attendance"

def reset_attendance_data():
    print("🚀 สั่งเริ่มการเคลียร์ข้อมูล Attendance...")
    
    # 2. ลบชุดข้อมูลใน Database (logs เท่านั้น)
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        # ลบเฉพาะข้อมูลการเข้างาน (คงค่าพนักงานและตั้งค่าไว้)
        cur.execute("DELETE FROM attendance_logs;")
        
        conn.commit()
        print("✅ ลบข้อมูลในตาราง attendance_logs เรียบร้อย!")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error DB: {e}")

    # 3. ลบไฟล์รูปภาพในโฟลเดอร์
    if os.path.exists(UPLOAD_DIR):
        try:
            for filename in os.listdir(UPLOAD_DIR):
                file_path = os.path.join(UPLOAD_DIR, filename)
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            print(f"✅ ลบไฟล์รูปภาพทั้งหมดใน {UPLOAD_DIR} เรียบร้อย!")
        except Exception as e:
            print(f"❌ Error Files: {e}")
    else:
        print("⚠️ ไม่พบโฟลเดอร์รูปภาพ ไม่ต้องลบไฟล์")

    print("\n✨ เคลียร์ข้อมูลสะอาดกริบ! พร้อมสำหรับการเริ่มทดสอบใหม่แล้วครับ")

if __name__ == "__main__":
    reset_attendance_data()
