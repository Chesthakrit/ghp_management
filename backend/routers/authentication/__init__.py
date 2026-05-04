from fastapi import APIRouter
from .login import router as login_router
from .registration import router as registration_router

router = APIRouter(prefix="/auth")
router.include_router(login_router)
router.include_router(registration_router)
