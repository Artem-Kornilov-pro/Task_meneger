from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from backend.app.core.redis_client import redis_client
from fastapi import HTTPException, status
import os

# Конфигурация токенов
SECRET_KEY = os.getenv("RANDOM_SECRET", "fallback-secret")  # на случай, если переменная не установлена
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Настройка шифрования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Хеширует пароль"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Сравнивает хеш пароля и введённый пароль"""
    return pwd_context.verify(plain_password, hashed_password)

def create_token(data: dict, token_type: str = "access") -> str:
    """
    Создаёт JWT access или refresh токен и сохраняет его в Redis с TTL.

    Args:
        data (dict): payload токена (например, {"sub": user_id})
        token_type (str): 'access' или 'refresh'

    Returns:
        str: закодированный JWT
    """
    to_encode = data.copy()

    if token_type == "access":
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        ttl_seconds = ACCESS_TOKEN_EXPIRE_MINUTES * 60
    elif token_type == "refresh":
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        ttl_seconds = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недопустимый тип токена. Используй 'access' или 'refresh'."
        )

    to_encode.update({"exp": expire, "type": token_type})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # Сохраняем токен в Redis
    redis_client.set(f"token:{encoded_jwt}", "valid", ex=ttl_seconds)

    return encoded_jwt

def verify_token(token: str) -> dict:
    """
    Проверяет токен: сигнатуру, срок и наличие в Redis.

    Args:
        token (str): JWT-токен (может быть с префиксом Bearer)

    Returns:
        dict: payload токена (например, {'sub': 'user123', ...})

    Raises:
        JWTError: если токен недействителен или просрочен
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        redis_key = f"token:{token}"
        redis_status = redis_client.get(redis_key)

        if redis_status != "valid":
            raise JWTError("Token отсутствует или истёк в Redis")

        return payload

    except JWTError as e:
        raise JWTError(f"Невалидный токен: {e}")
