from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.task import Task
from backend.app.chemas.task import TaskCreate, TaskUpdate, TaskOut
from backend.app.core.dependencies import get_current_user

router = APIRouter()

# Create
@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """
Создать новую задачу.

Этот эндпоинт позволяет аутентифицированному пользователю создать новую задачу, указав название, описание, дедлайн и статус. 
Пользователь автоматически становится владельцем задачи. Возвращает созданную задачу с её ID и текущими параметрами.

- **title**: Название задачи (обязательно)
- **description**: Подробности задачи (необязательно)
- **due_date**: Дата и время дедлайна (необязательно)
- **status_id**: Идентификатор статуса задачи (необязательно)
"""

    user_id = int(current_user["user_id"])

    db_task = Task(**task.dict(), user_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# Get
@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """
    Получить задачу по её идентификатору.

    Этот эндпоинт возвращает подробную информацию о задаче по её ID. Если задача не найдена, возвращается ошибка 404.
    Доступен только для аутентифицированных пользователей.

    - **task_id**: Уникальный идентификатор задачи (целое число)
    """
    user_id = current_user["user_id"]

    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# Patch
@router.patch("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """
    Обновить параметры задачи (частично).

    Позволяет аутентифицированному пользователю изменить одну или несколько характеристик существующей задачи, таких как заголовок,
    описание, дедлайн или статус. Только переданные поля будут обновлены. Возвращает обновлённую задачу.

    - **task_id**: ID редактируемой задачи
    - **title / description / due_date / status_id**: Поля для частичного обновления
    """

    user_id = current_user["user_id"]

    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    for field, value in task_update.dict(exclude_unset=True).items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    return task

# Delete
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """
    Удалить задачу по ID.

    Удаляет задачу с указанным идентификатором. Доступ разрешён только аутентифицированным пользователям. 
    Если задача с таким ID не найдена — возвращается ошибка 404. После удаления тело ответа будет пустым (HTTP 204).

    - **task_id**: ID задачи, которую нужно удалить
    """

    user_id = current_user["user_id"]
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return None
