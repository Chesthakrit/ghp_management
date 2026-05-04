from fastapi import APIRouter
from .accounts import router as accounts_router
from .profiles import router as profiles_router

router = APIRouter(prefix="/users")
router.include_router(accounts_router)
router.include_router(profiles_router)
