"""
ระบบรับ-ส่งข้อมูลกับเครื่องสแกน ZKTeco ผ่าน ADMS Push Protocol
"""

import re
import logging
from datetime import datetime

from fastapi import APIRouter, Request, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from database import get_db
from models.attendance import AttendanceLog, AttendanceConfig, OTRequest
from models.users import User, EmployeeProfile
from utils.attendance_utils import calculate_attendance_status

# ─── Logger ───────────────────────────────────────────────────────────────────
logger = logging.getLogger("zkteco")
logger.setLevel(logging.DEBUG)
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(_handler)

# ─── Router ───────────────────────────────────────────────────────────────────
router = APIRouter(prefix="/iclock", tags=["ZKTeco ADMS"])

_DOUBLE_SCAN_SECS = 120   # ระยะเวลาขั้นต่ำระหว่างสแกน (วินาที) เพื่อกันสแกนซ้ำ


# ─── Internal Helpers ─────────────────────────────────────────────────────────

def _find_user_by_pin(pin: str, db: Session):
    """
    ค้นหา User จาก PIN ของเครื่องสแกน
    ลำดับ: scan_id ในโปรไฟล์ → User.id โดยตรง → สร้างใหม่อัตโนมัติ
    """
    pin_str  = pin.strip()
    user_id  = int(pin_str) if pin_str.isdigit() else None

    # 1. หาจาก EmployeeProfile.scan_id ก่อน
    profile = db.query(EmployeeProfile).filter(EmployeeProfile.scan_id == pin_str).first()
    if profile:
        return db.query(User).filter(User.id == profile.user_id).first()

    # 2. หาจาก User.id โดยตรง
    if user_id is not None:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            return user

    return None


def _parse_attlog_line(line: str):
    """
    แยกข้อมูล pin และ scan_time_str จาก 1 บรรทัดของ ATTLOG payload
    รองรับทั้งรูปแบบ rtlog (key=value) และ ATTLOG แบบเก่า (tab-separated)
    """
    if "pin=" in line and "time=" in line:
        data = {}
        for part in line.split("\t"):
            if "=" in part:
                k, v = part.split("=", 1)
                data[k.strip()] = v.strip()
        return data.get("pin"), data.get("time")

    parts = re.split(r"\s+", line) if "\t" not in line else line.split("\t")
    if len(parts) >= 2:
        return parts[0], parts[1]

    return None, None


def _process_attlog(body: str, db: Session):
    """ประมวลผล ATTLOG payload และบันทึกเวลาเข้า/ออกงาน"""
    configs  = {c.key: c.value for c in db.query(AttendanceConfig).all()}
    success  = 0

    for line in body.strip().splitlines():
        line = line.strip()
        if not line:
            continue

        pin, scan_time_str = _parse_attlog_line(line)
        if not pin or not scan_time_str:
            continue

        try:
            scan_time = datetime.strptime(scan_time_str, "%Y-%m-%d %H:%M:%S")
            scan_date = scan_time.date()

            user = _find_user_by_pin(pin, db)
            if not user:
                logger.warning(f"Cannot resolve user for PIN: {pin}")
                continue

            log = db.query(AttendanceLog).filter(
                AttendanceLog.user_id == user.id,
                AttendanceLog.date    == scan_date,
            ).first()

            if not log:
                # ─ Check-in ─
                status_val, late_mins = calculate_attendance_status(user.id, scan_time, configs)
                db.add(AttendanceLog(
                    user_id         = user.id,
                    date            = scan_date,
                    check_in_time   = scan_time,
                    actual_check_in = scan_time,
                    site_name       = "Factory",
                    status          = status_val,
                    late_minutes    = late_mins,
                    note            = "Scanned via ZKTeco (Auto)",
                ))
            else:
                # ─ Check-out (ถ้าห่างกันเกิน _DOUBLE_SCAN_SECS) ─
                last_time = log.actual_check_out or log.actual_check_in or log.check_in_time
                if (scan_time - last_time).total_seconds() > _DOUBLE_SCAN_SECS:
                    # 1. บันทึกเวลาจริงไว้เสมอเพื่อเป็นหลักฐาน
                    log.actual_check_out = scan_time
                    log.site_name        = "Factory"

                    # 2. ตรวจสอบเงื่อนไข Cutoff (17:00)
                    normal_out_str = configs.get("check_out_time", "17:00")
                    normal_out_h, normal_out_m = map(int, normal_out_str.split(":"))
                    normal_out_time = scan_time.replace(hour=normal_out_h, minute=normal_out_m, second=0, microsecond=0)

                    # เช็คว่ามี OT ที่อนุมัติแล้วในวันนั้นหรือไม่
                    approved_ot = db.query(OTRequest).filter(
                        OTRequest.user_id == user.id,
                        OTRequest.request_date == scan_date,
                        OTRequest.status == "approved"
                    ).first()

                    if not approved_ot:
                        # ถ้าไม่มี OT และสแกนหลังเวลาเลิกงานปกติ -> ตัดจบที่เวลาเลิกงานปกติ
                        if scan_time > normal_out_time:
                            log.check_out_time = normal_out_time
                            log.note = f"Scanned out at {scan_time.strftime('%H:%M')} (No OT: Cutoff applied)"
                        else:
                            log.check_out_time = scan_time
                            log.note = "Scanned out via ZKTeco (Auto)"
                    else:
                        # ถ้ามี OT ให้บันทึกตามจริง (ลอจิก OT จะไปคำนวณแยกที่ตาราง OT อีกที)
                        log.check_out_time = scan_time
                        log.note = f"Scanned out via ZKTeco (OT Approved until {approved_ot.end_time})"

            success += 1

        except Exception as e:
            logger.error(f"Error processing line '{line}': {e}")

    db.commit()
    logger.info(f"Successfully processed {success} ATTLOG records.")


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/cdata")
async def get_cdata(SN: str = None, options: str = None):
    """Handshake ตอนเครื่องสแกนเปิดเครื่องหรือเชื่อมต่อใหม่"""
    logger.info(f"Device connected (GET /cdata): SN={SN}, options={options}")
    body = (
        f"GET OPTION FROM: {SN}\r\n"
        "Stamp=9999\r\nOpStamp=9999\r\nErrorDelay=60\r\nDelay=10\r\n"
        "TransTimes=00:00;14:00\r\nTransInterval=1\r\nTransFlag=1111000000\r\n"
        "Realtime=1\r\nEncrypt=0\r\n"
    )
    return Response(content=body, media_type="text/plain")


@router.post("/registry")
async def post_registry(request: Request, SN: str = None):
    """Firmware บางรุ่นส่ง POST /registry เพื่อลงทะเบียน"""
    body = await request.body()
    logger.info(f"Device registry: SN={SN}, body={body.decode('utf-8', errors='ignore')}")
    return Response(content="RegistryCode=OK\r\n", media_type="text/plain")


@router.post("/push")
async def post_push(request: Request, SN: str = None):
    """Firmware ใหม่ (เช่น SenseFace) ใช้ /push ส่งข้อมูลบางส่วน"""
    body = await request.body()
    logger.info(f"Device PUSH: SN={SN}, body={body.decode('utf-8', errors='ignore')}")
    return Response(content="OK\r\n", media_type="text/plain")


@router.get("/ping")
async def get_ping(SN: str = None):
    """Firmware ใหม่ส่ง Ping เพื่อเช็คว่า Server ยังออนไลน์อยู่"""
    return Response(content="OK\r\n", media_type="text/plain")


@router.get("/getrequest")
async def get_request(SN: str = None):
    """เครื่องสแกน Poll เข้ามาถามว่ามีคำสั่งใหม่ไหม"""
    return Response(content="OK\r\n", media_type="text/plain")


@router.post("/cdata")
async def post_cdata(
    request: Request,
    SN: str = None,
    table: str = None,
    db: Session = Depends(get_db),
):
    """รับข้อมูลการสแกนจากเครื่อง (ATTLOG, rtlog, rtstate ฯลฯ)"""
    body_bytes = await request.body()
    body_str   = body_bytes.decode("utf-8", errors="ignore")

    logger.info(f"Received data from SN={SN}, table={table}")
    logger.debug(f"Payload:\n{body_str}")

    if table in ("ATTLOG", "rtlog"):
        _process_attlog(body_str, db)

    return Response(content="OK\n", media_type="text/plain")


@router.post("/devicecmd")
async def post_devicecmd(request: Request, SN: str = None):
    """รับผลลัพธ์ของคำสั่งที่ส่งไปยังเครื่อง"""
    body = await request.body()
    logger.info(f"Device command response from SN={SN}: {body.decode('utf-8', errors='ignore')}")
    return Response(content="OK\r\n", media_type="text/plain")
