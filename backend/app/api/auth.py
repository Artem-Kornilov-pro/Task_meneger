# app/api/v1/endpoints/auth.py

from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.app.chemas.user import UserCreate, UserOut, LoginRequest, TokenResponse, TokenRequest, AccessTokenResponse, RefreshTokenRequest, UserOutMe
from backend.app.models.user import User
from backend.app.db.session import get_db
from backend.app.core.security import hash_password, create_access_token, verify_password
    
from backend.app.core.redis_client import redis_client
from backend.app.core.security import verify_token  # твоя функция для декодирования токена, нужна чтобы проверить токен
from typing import Optional


# Описываем, что нам нужен токен через OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  # путь на получение токена можешь поставить любой


router = APIRouter()


@router.post("/register", response_model=UserOut)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Регистрация нового пользователя в системе.

    Принимает данные нового пользователя (email, имя пользователя и пароль), 
    выполняет проверку на уникальность email и имени пользователя в базе данных. 
    В случае успешной проверки создаёт нового пользователя, хэширует его пароль, 
    сохраняет данные в базе данных и возвращает информацию о зарегистрированном пользователе, 
    исключая чувствительные поля.

    Аргументы:
        user_in (UserCreate): Входные данные для регистрации нового пользователя:
            - email: адрес электронной почты (должен быть уникальным),
            - username: имя пользователя (должно быть уникальным),
            - password: пароль (будет захэширован перед сохранением).
        db (Session): Зависимость сессии базы данных для выполнения операций сохранения и проверки.

    Возвращает:
        UserOut: Объект пользователя без чувствительных данных, соответствующий модели ответа.

    Исключения:
        HTTPException: 
            - 400 Bad Request — если пользователь с указанным email или именем пользователя уже существует.

    Примечания:
        - Пароль пользователя перед сохранением обязательно хэшируется с использованием безопасного алгоритма (например, bcrypt).
        - Перед регистрацией выполняется проверка на уникальность email и username.
        - Возвращается объект нового пользователя, отфильтрованный через схему UserOut, чтобы скрыть приватные данные (например, хэш пароля).
    """


    existing_user = db.query(User).filter(
        (User.email == user_in.email) | (User.username == user_in.username)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )

    hashed_pw = hash_password(user_in.password)
    new_user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=hashed_pw
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user



@router.post("/login", response_model=TokenResponse)
def login(user_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Аутентификация пользователя и генерация JWT токена доступа.

    Принимает учётные данные пользователя (имя пользователя и пароль), 
    проверяет их на соответствие данным в базе данных. 
    В случае успешной аутентификации создаёт JWT токен, который можно использовать для доступа к защищённым маршрутам.

    Аргументы:
        user_data (LoginRequest): Учётные данные пользователя, содержащие:
            - username: уникальное имя пользователя,
            - password: пароль в открытом виде (будет проверяться через хэш).
        db (Session): Сессия базы данных для выполнения поиска пользователя и проверки пароля.

    Возвращает:
        dict: Словарь с данными:
            - access_token (str): JWT токен для аутентифицированных запросов,
            - token_type (str): Тип токена, всегда "bearer".

    Исключения:
        HTTPException:
            - 400 Bad Request — если имя пользователя не существует или пароль неверный.

    Примечания:
        - Пароль проверяется с использованием безопасного метода верификации (например, bcrypt).
        - Сгенерированный JWT токен включает ID пользователя в поле 'sub'.
        - Для доступа к защищённым маршрутам необходимо указывать токен в заголовке Authorization.
        - Обычно токен имеет срок действия, который задаётся при его создании.
    """
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": str(user.id)})
    resp = TokenResponse(access_token=access_token,
                          token_type="bearer")
    return resp




@router.delete("/logout")
async def logout(token_request: TokenRequest):
    """
    Удаляет токен из Redis.

    Этот эндпоинт принимает токен в теле запроса и удаляет его из хранилища Redis,
    если он существует. Используется для выхода пользователя из системы.

    Параметры:
    - token_request (TokenRequest): Модель запроса с полем токена.

    Ответы:
    - 200: Токен успешно удалён.
    - 404: Токен не найден в Redis.
    """
    token = token_request.token
    redis_key = f"token:{token}"

    if redis_client.exists(redis_key):
        redis_client.delete(redis_key)
        return {"detail": "Token deleted successfully"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token not found")
    


@router.post("/refresh", response_model=AccessTokenResponse, summary="Обновить access токен по refresh токену")
def refresh_access_token(data: RefreshTokenRequest):
    """
    🔁 Обновление access токена на основе предоставленного refresh токена.

    проверка refresh токена и генерация нового access токена.
    """
    # Заглушка: не проверяет токен, просто возвращает фиктивный access_token
    if not data.refresh_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Refresh токен отсутствует")
    
    return AccessTokenResponse(
        access_token="mocked.new.access.token.123456",
        token_type="bearer"
    )






@router.get(
    "/me",
    response_model=UserOutMe,
    summary="Получить текущего пользователя (токен вводится вручную)"
)
def get_current_user(authorization: Optional[str] = Header(None, description="JWT токен формата: Bearer <token>")):
    """
    👤 Заглушка: возвращает пользователя, если передан заголовок Authorization.

    **Пример:**
    ```
    Authorization: Bearer eyJhbGciOi...
    ```
    """
    if not authorization:
        # Здесь может быть raise HTTPException, но пока заглушка
        return UserOutMe(id=0, email="anonymous@example.com", username="anonymous")

    return UserOutMe(
        id=1,
        email="user@example.com",
        username="johndoe"
    )