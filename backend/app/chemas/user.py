from pydantic import BaseModel, EmailStr, StringConstraints, ConfigDict, Field
from typing import Optional
from typing_extensions import Annotated  # важно для Pydantic v2
from datetime import date
from enum import Enum
# 💡 Используем Annotated + StringConstraints вместо устаревшего constr
UsernameType = Annotated[str, StringConstraints(min_length=3, max_length=30)]
PasswordType = Annotated[str, StringConstraints(min_length=6)]

class UserCreate(BaseModel):
    email: EmailStr
    username: UsernameType
    password: PasswordType



class UserOut(BaseModel):
    id: int
    email: str
    username: str
    class Config:
        from_attributes = True  # <<< ВАЖНО

class LoginRequest(BaseModel):
    username: UsernameType
    password: PasswordType


class LogInTokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT токен доступа", example="your.acsess.jwt.token.here")
    refresh_token: str = Field(..., description="JWT токен доступа", example="your.refresh.jwt.token.here")
    token_type: str = Field(..., description="Тип токена", example="bearer")
    class Config:
        from_attributes = True  # <<< ВАЖНО


# Модель для тела запроса
class TokenRequest(BaseModel):
    token: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., title="Refresh Token", example="your.refresh.token.here")

class AccessTokenResponse(BaseModel):
    access_token: str = Field(..., title="Access Token", example="new.access.token.here")
    token_type: str = Field(default="bearer", title="Token Type", example="bearer")


class UserOutMe(BaseModel):
    id: int = Field(..., example=1, title="User ID")
    email: EmailStr = Field(..., example="user@example.com", title="Email")
    username: str = Field(..., example="johndoe", title="Username")
    class Config:
        from_attributes = True  # <<< ВАЖНО


class GenderEnum(str, Enum):
    male = "male"
    female = "female"


class UserProfileCreate(BaseModel):
    full_name: str = Field(..., title="Full Name", example="Kornilov Artemiy Alexandrovich")
    gender: GenderEnum = Field(..., title="Gender", example="male")
    birth_date: date = Field(..., title="Date of Birth", example="1990-01-01")
    location: str = Field(..., title="Location", example="Kursk")
    bio: Optional[str] = Field(None, title="Biography", example="Software engineer and musician.")

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, title="Full Name", example="John Doe")
    gender: Optional[GenderEnum] = Field(None, title="Gender", example="male")
    birth_date: Optional[date] = Field(None, title="Date of Birth", example="1990-01-01")
    location: Optional[str] = Field(None, title="Location", example="New York")
    bio: Optional[str] = Field(None, title="Biography", example="Software engineer and musician.")

class UserProfileOut(UserProfileUpdate):
    user_id: int
    