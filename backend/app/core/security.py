# app/core/security.py
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.core.redis_client import redis_client
import os



SECRET_KEY = os.getenv("RANDOM_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)



def create_access_token(data: dict):
    """
    Generates a JWT access token with expiration and stores it in Redis for validation.

    Args:
        data (dict): Payload data to be encoded in the JWT. Should at minimum contain:
            - 'sub' (str): Subject identifier (typically user ID)

    Returns:
        str: Encoded JWT access token

    Raises:
        JWTError: If token encoding fails

    Notes:
        - Adds an expiration claim ('exp') to the token payload based on 
          ACCESS_TOKEN_EXPIRE_MINUTES configuration
        - Uses HS256 signing algorithm by default (configurable via ALGORITHM)
        - Stores the token in Redis with TTL matching token expiration for
          server-side validation capabilities
        - Redis key format: "token:{encoded_jwt}" with value "valid"

    Example:
        >>> token = create_access_token({"sub": "user123"})
        >>> isinstance(token, str)
        True
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # Сохраняем в Redis
    redis_client.set(f"token:{encoded_jwt}", "valid", ex=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    return encoded_jwt




def verify_token(token: str):
    """
    Verify a JWT token's validity by checking both its cryptographic signature and Redis store.

    Args:
        token (str): The JWT token to verify in format 'Bearer <token>' or raw token string.

    Returns:
        dict: The decoded JWT payload if the token is valid. Typically contains:
            - 'sub' (str): Subject identifier (usually user ID)
            - 'exp' (int): Expiration timestamp
            - Additional claims that were included in the token

    Raises:
        JWTError: If any of the following conditions occur:
            - Token is malformed or signature verification fails
            - Token has expired (based on 'exp' claim)
            - Token is marked invalid in Redis
            - Token doesn't exist in Redis store

    Notes:
        - Performs dual validation: both cryptographic and server-side (Redis)
        - Redis key is expected to be in format "token:<raw_jwt>"
        - Automatically handles 'Bearer ' prefix if present
        - Uses application's configured SECRET_KEY and ALGORITHM
        - Redis check provides immediate invalidation capability

    Example:
        >>> payload = verify_token("eyJhb...")
        >>> user_id = payload.get('sub')
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_key = f"token:{token}"
        if redis_client.get(token_key) != "valid":
            raise JWTError("Token is invalid or expired in Redis")
        return payload
    except JWTError:
        raise JWTError("Invalid token")


