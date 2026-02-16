from passlib.context import CryptContext

# บอกระบบว่าให้ใช้วิธีเข้ารหัสแบบ "bcrypt" (ซึ่งเป็นมาตรฐานที่นิยมที่สุดตอนนี้)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Hash:
    # ฟังก์ชันสำหรับเข้ารหัส (ใช้ตอนสมัครสมาชิก)
    def bcrypt(password: str):
        return pwd_context.hash(password)

    # ฟังก์ชันสำหรับตรวจสอบรหัส (ใช้ตอน Login)
    # มันจะเทียบรหัสที่กรอกมา กับรหัสที่ถูกเข้ารหัสในฐานข้อมูลว่าตรงกันไหม
    def verify(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)