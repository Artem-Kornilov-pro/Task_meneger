from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session
from backend.app.chemas.user import UserProfileCreate, UserProfileOut, UserProfileUpdate
from backend.app.models.user import User
from backend.app.models.user_profile import UserProfile

from backend.app.db.session import get_db
    
from backend.app.core.dependencies import get_current_user




router = APIRouter()



@router.post("/profile", response_model=UserProfileOut, summary="Создать профиль пользователя")
def create_profile( 
    profile: UserProfileCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Создание нового профиля для текущего пользователя.

    Этот эндпоинт позволяет авторизованному пользователю создать собственный профиль,
    содержащий личную информацию, такую как полное имя, дату рождения, локацию и описание (био).
    Данные профиля сохраняются в таблицу `user_profiles` и связываются с пользователем по `user_id`.

    Аргументы:
        profile (UserProfileCreate): Входная модель данных профиля, содержащая пользовательскую информацию.
        current_user (dict): Зависимость, предоставляющая `user_id` текущего авторизованного пользователя.
        db (Session): Сессия базы данных для выполнения операций сохранения.

    Возвращает:
        UserProfileOut: Объект созданного профиля.

    Исключения:
        HTTPException: 400 Bad Request — если профиль для пользователя уже существует.
    """
    user_id = current_user["user_id"]

    # Проверка: существует ли уже профиль для этого пользователя
    existing_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Профиль пользователя уже существует"
        )

    # Создание нового профиля
    new_profile = UserProfile(user_id=user_id, **profile.dict())
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return new_profile


@router.get("/profile", response_model=UserProfileOut, summary="Получить профиль текущего пользователя")
def get_my_profile(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Получение профиля текущего пользователя.

    Эндпоинт предназначен для получения полной информации о профиле пользователя,
    авторизованного с помощью JWT-токена. На основе `user_id`, извлечённого из токена,
    выполняется запрос к базе данных для получения связанных с этим пользователем
    данных из таблицы `user_profiles`.

    Аргументы:
        current_user (dict): Зависимость, предоставляющая информацию об авторизованном пользователе из токена.
        db (Session): Сессия базы данных SQLAlchemy.

    Возвращает:
        UserProfileOut: Объект профиля пользователя с такими полями, как имя, дата рождения, пол и другая информация.

    Исключения:
        HTTPException: 404 Not Found — если профиль пользователя не найден.
    """
    user_id = current_user["user_id"]

    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль пользователя не найден"
        )

    return profile


@router.patch("/profile", response_model=UserProfileOut, summary="Обновить профиль пользователя")
def update_profile(
    profile_update: UserProfileUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Частичное обновление профиля текущего пользователя.

    Позволяет авторизованному пользователю обновить отдельные поля его профиля, такие как имя, локация, био и т.д.
    Только предоставленные в запросе поля будут обновлены. Идентификация пользователя выполняется на основе `user_id` из токена.

    Аргументы:
        profile_update (UserProfileUpdate): Модель с необязательными полями для обновления профиля.
        current_user (dict): Зависимость, предоставляющая `user_id` авторизованного пользователя.
        db (Session): Сессия базы данных SQLAlchemy.

    Возвращает:
        UserProfileOut: Обновлённый профиль пользователя с учётом внесённых изменений.

    Исключения:
        HTTPException: 404 Not Found — если профиль пользователя не найден.
    """
    user_id = current_user["user_id"]

    # Найти существующий профиль
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль пользователя не найден"
        )

    # Обновить только переданные поля
    update_data = profile_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)

    db.commit()
    db.refresh(profile)

    return profile



@router.delete("/profile", summary="Удалить профиль текущего пользователя", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Удаление профиля текущего пользователя.

    Эндпоинт предназначен для удаления профиля, связанного с текущим авторизованным пользователем.
    Авторизация осуществляется через токен, из которого извлекается `user_id`.

    Аргументы:
        current_user (dict): Зависимость, предоставляющая информацию об авторизованном пользователе.
        db (Session): Сессия базы данных SQLAlchemy.

    Возвращает:
        None: HTTP 204 No Content при успешном удалении.

    Исключения:
        HTTPException: 404 Not Found — если профиль не найден.
    """
    user_id = current_user["user_id"]

    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль не найден"
        )

    db.delete(profile)
    db.commit()
    return None