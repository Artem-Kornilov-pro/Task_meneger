from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from backend.app.api import ping
from backend.app.api import auth

from backend.app.db.session import engine
from backend.app.models import user, task, task_category, task_status, category, reminder, user_settings  # эти импорты нужны, чтобы модели были зарегистрированы
from backend.app.db.base import Base



# Удалить все таблицы
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)



app = FastAPI(
    title="Моя система задач",
    version="1.0.0",
    description="""
    # Добро пожаловать в API управления задачами!

    Здесь вы можете:

    - Регистрировать пользователей
    - Авторизовываться и получать токены
    - Управлять задачами и категориями
    - Работать с приоритетами и статусами

    **Важно:** все защищённые маршруты требуют передачи JWT токена в заголовке `Authorization: Bearer <token>`.
    
    ---
    
    ✨ Для примера вы можете использовать пользователя `testuser` с паролем `testpassword`.
            Саша, если ты это читаешь, то ты - КРАСАВЧИК
    """)

# Добавляем CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Можно ограничить домен, если нужно
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ping.router, tags=["server"])
app.include_router(auth.router, tags=["auth"])


#Для запуска проекта использовать :  uvicorn backend.app.main:app --reload

"""# 1. Остановить все контейнеры
docker stop $(docker ps -aq)

# 2. Удалить все контейнеры
docker rm $(docker ps -aq)

# 3. Запустить Redis в новом контейнере
docker run --name redis -p 6379:6379 -d redis

# 4. Проверить, что Redis работает
docker ps   # Должен быть запущен контейнер redis
docker logs redis   # Посмотреть логи, если есть ошибки

# 5. Проверить подключение
docker exec -it redis redis-cli ping"""