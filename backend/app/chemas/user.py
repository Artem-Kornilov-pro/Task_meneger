from pydantic import BaseModel, EmailStr, StringConstraints, ConfigDict, Field
from typing import Optional
from typing_extensions import Annotated  # важно для Pydantic v2

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


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT токен доступа", example="your.jwt.token.here")
    token_type: str = Field(..., description="Тип токена", example="bearer")
    class Config:
        from_attributes = True  # <<< ВАЖНО



# Модель для тела запроса
class TokenRequest(BaseModel):
    token: str