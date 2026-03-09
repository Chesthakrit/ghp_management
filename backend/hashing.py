"""
ไฟล์จัดการการเข้ารหัสรหัสผ่าน (Password Hashing)
ทำหน้าที่ส่องรหัสผ่านให้เป็นรหัสที่อ่านไม่ออกเพื่อความปลอดภัย
"""

from passlib.context import CryptContext

# สร้าง pwd_context โดยระบุอัลกอริทึมที่ใช้คือ "bcrypt"
# bcrypt เป็นมาตรฐานสากลที่นิยมใช้เนื่องจากมีความปลอดภัยสูงและยากต่อการสุ่มเดา
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Hash:
    """
    Class รวบรวมฟังก์ชันเกี่ยวกับความปลอดภัยของรหัสผ่าน
    """
    
    # ฟังก์ชัน bcrypt - ใช้สำหรับเปลี่ยนรหัสผ่านธรรมดาให้กลายเป็นข้อความเข้ารหัส (Hashing)
    # ใช้บ่อยที่สุดในตอนที่ผู้ใช้สมัครสมาชิก หรือเปลี่ยนรหัสผ่านใหม่
    def bcrypt(password: str):
        return pwd_context.hash(password)

    # ฟังก์ชัน verify - ใช้สำหรับตรวจสอบรหัสผ่าน
    # ทำงานโดยนำรหัสผ่านที่ผู้ใช้พิมพ์เข้ามา (plain_password) 
    # ไปเทียบกับรหัสผ่านที่ผ่านการเข้ารหัสและเก็บอยู่ในเบส (hashed_password)
    # จะส่งกลับเป็น True ถ้าตรงกัน และ False ถ้าไม่ตรงกัน
    def verify(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)
