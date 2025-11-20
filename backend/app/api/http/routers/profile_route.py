"""FastAPI router for profile endpoints.

GET /profile/me
PUT /profile/me
などをここに定義していく予定。
"""

from fastapi import APIRouter

router = APIRouter(prefix="/profile", tags=["Profile"])
