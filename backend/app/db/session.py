# app/db/session.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from pathlib import Path

# Загрузка .env с родительских директорий
BASE_DIR = Path(__file__).resolve().parents[2]  # поднимаемся до tasks_meneger/
dotenv_path = BASE_DIR / ".env"
load_dotenv(dotenv_path)

# Получаем строку подключения из .env
DATABASE_URL = os.getenv("POSTGRES_CONN")

# Создаём engine с пулом соединений
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

# Создаём sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Функция получения и возврата сессии
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
