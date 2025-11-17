from fastapi import APIRouter
from app.api.http.schemas.auth import RegisterRequest

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
async def register(request: RegisterRequest):
    return {"message": "User registered successfully"}
