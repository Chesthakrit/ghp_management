from fastapi import APIRouter
from .departments import router as dept_router
from .job_titles import router as jt_router
from .skills_duties import router as skills_router
from .evaluations import router as eval_router

router = APIRouter(prefix="/hr")
router.include_router(dept_router)
router.include_router(jt_router)
router.include_router(skills_router)
router.include_router(eval_router)
