"""Task repository – pure data access with filtering and pagination."""

from typing import Optional, Tuple

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.task import Task, TaskPriority, TaskStatus


class TaskRepository:
    """Encapsulates all database operations related to tasks."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, task_id: int) -> Optional[Task]:
        return self.db.get(Task, task_id)

    def get_by_id_and_owner(self, task_id: int, owner_id: int) -> Optional[Task]:
        stmt = select(Task).where(Task.id == task_id, Task.owner_id == owner_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def create(
        self,
        *,
        title: str,
        description: Optional[str],
        priority: TaskPriority,
        status: TaskStatus,
        owner_id: int,
    ) -> Task:
        task = Task(
            title=title,
            description=description,
            priority=priority,
            status=status,
            owner_id=owner_id,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def update(self, task: Task, **kwargs) -> Task:
        for key, value in kwargs.items():
            if value is not None and hasattr(task, key):
                setattr(task, key, value)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        self.db.delete(task)
        self.db.commit()

    def list_by_owner(
        self,
        owner_id: int,
        *,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        search: Optional[str] = None,
        page: int = 1,
        size: int = 20,
    ) -> Tuple[list[Task], int]:
        """Return a page of tasks belonging to the given owner together with the total count."""
        filters = [Task.owner_id == owner_id]

        if status is not None:
            filters.append(Task.status == status)
        if priority is not None:
            filters.append(Task.priority == priority)
        if search:
            pattern = f"%{search}%"
            filters.append(
                or_(Task.title.ilike(pattern), Task.description.ilike(pattern))
            )

        # Total count
        count_stmt = select(func.count()).select_from(Task).where(*filters)
        total = self.db.execute(count_stmt).scalar_one()

        # Paginated results
        offset = (page - 1) * size
        stmt = (
            select(Task)
            .where(*filters)
            .order_by(Task.created_at.desc())
            .offset(offset)
            .limit(size)
        )
        items = list(self.db.execute(stmt).scalars().all())

        return items, total
