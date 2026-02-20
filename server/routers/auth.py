from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.auth import RegisterRequest, UserResponse
from services.auth_service import create_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    user = create_user(db, request.username, request.password)
    if user is None:
        raise HTTPException(status_code=400, detail="Username already exists")
    return user