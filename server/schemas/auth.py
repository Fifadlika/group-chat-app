from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    """Request body for user registration."""
    password: str = Field(min_length=8, max_length=512)

class UserResponse(BaseModel):
    id: int
    username: str
    model_config = {"from_attributes": True}

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"