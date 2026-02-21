from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import blacklist_token
from core.dependencies import get_current_user
from schemas.auth import RegisterRequest, UserResponse, TokenResponse
from services.auth_service import create_user, login_user

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/register", response_model=UserResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    user = create_user(db, request.username, request.password)
    if user is None:
        raise HTTPException(status_code=400, detail="Username already exists")
    return user
    
@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    token = login_user(db, form_data.username, form_data.password)
    if token is None:
        raise HTTPException(
            status_code=401,
            detail="Username or password is incorrect"
        )
    return TokenResponse(access_token=token)

@router.post("/logout")
def logout(
    token: str = Depends(oauth2_scheme),
    current_user: dict = Depends(get_current_user)
):
    blacklist_token(token)
    return {"message": "Logged out successfully"}

