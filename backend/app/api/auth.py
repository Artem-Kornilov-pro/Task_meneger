# app/api/v1/endpoints/auth.py

from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError
from backend.app.chemas.user import UserCreate, UserOut, LoginRequest, LogInTokenResponse, TokenRequest
from backend.app.chemas.user import AccessTokenResponse, RefreshTokenRequest, UserOutMe

from backend.app.models.user import User
from backend.app.models.user_profile import UserProfile
from backend.app.db.session import get_db
from backend.app.core.security import hash_password, create_token, verify_password
    
from backend.app.core.redis_client import redis_client
from backend.app.core.security import verify_token  # твоя функция для декодирования токена, нужна чтобы проверить токен

from backend.app.core.dependencies import get_current_user

# Описываем, что нам нужен токен через OAuth2
#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  # путь на получение токена можешь поставить любой


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


@router.post("/login", response_model=LogInTokenResponse, summary="Авторизация пользователя")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Эндпоинт для авторизации пользователя. При успешной авторизации возвращает
    access и refresh токены для дальнейшей работы с защищенными ресурсами.

    Параметры:
    - form_data: OAuth2PasswordRequestForm
      - username: Имя пользователя, используемое для входа.
      - password: Пароль пользователя для проверки.
    - db: Сессия базы данных, необходимая для получения данных о пользователе.

    Возвращаемое значение:
    - LogInTokenResponse: Ответ, содержащий access_token, refresh_token и token_type.
    
    Исключения:
    - HTTPException (400): В случае неверного имени пользователя или пароля.
    
    Пример успешного ответа:
    {
        "access_token": "string",
        "refresh_token": "string",
        "token_type": "bearer"
    }
    """
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Неверное имя пользователя или пароль")

    access_token = create_token(data={"sub": str(user.id)}, token_type="access")
    refresh_token = create_token(data={"sub": str(user.id)}, token_type="refresh")

    return LogInTokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


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
    🔁 Обновляет access токен по действующему refresh токену.
    
    Проверяет:
    - подпись и срок действия refresh токена
    - наличие токена в Redis
    - корректность типа токена

    Возвращает новый access токен.
    """
    refresh_token = data.refresh_token.strip()

    if not refresh_token:
        raise HTTPException(status_code=400, detail="Refresh токен не предоставлен")

    try:
        # Проверка и расшифровка токена
        payload = verify_token(refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=400, detail="Передан не refresh токен")

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=400, detail="Не удалось извлечь user_id из токена")

        # Генерация нового access токена
        new_access_token = create_token({"sub": user_id}, token_type="access")

        return AccessTokenResponse(
            access_token=new_access_token,
            token_type="bearer"
        )

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Невалидный refresh токен: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка: {str(e)}")


# Создаем зависимость для получения токена из заголовков
def get_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Invalid token format")
    return authorization[7:]  # Возвращаем только сам токен без "Bearer "



@router.get("/me",response_model=UserOutMe, summary="Информация о текущем пользователе")
def get_me(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Получение информации о текущем авторизованном пользователе.

    Эндпоинт возвращает основные данные пользователя (ID, email, username) на основе ID,
    извлечённого из JWT-токена доступа. Запрос выполняется к базе данных по ID пользователя.

    Требуется передача токена доступа в заголовке Authorization формата: `Bearer <token>`.

    Возвращает:
        UserOut: Объект с основной информацией о пользователе без чувствительных данных
        (например, без хэша пароля).

    Исключения:
        - 401 Unauthorized — если токен недействителен или отсутствует.
        - 404 Not Found — если пользователь с таким ID не найден в базе данных.
    """
    user_id = current_user["user_id"]
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
    