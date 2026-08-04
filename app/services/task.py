"""Task service – business rules around tasks."""

from math import ceil
from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.task import Task, TaskPriority, TaskStatus
from app.repositories.task import TaskRepository
from app.schemas.task import TaskCreate, TaskListResponse, TaskRead, TaskUpdate


class TaskService:
    """Business logic for task CRUD, filtering and ownership checks."""

    def __init__(self, db: Session) -> None:
        self.task_repo = TaskRepository(db)

    def create(self, owner_id: int, data: TaskCreate) -> Task:
        return self.task_repo.create(
            title=data.title,
            description=data.description,
            priority=TaskPriority(data.priority.value),
            status=TaskStatus(data.status.value),
            owner_id=owner_id,
        )

    def get_by_id(self, task_id: int, owner_id: int) -> Task:
        task = self.task_repo.get_by_id_and_owner(task_id, owner_id)
        if task is None:
            # Do not reveal whether the task exists for another user
            raise NotFoundException(message="Task not found")
        return task

    def update(self, task_id: int, owner_id: int, data: TaskUpdate) -> Task:
        task = self.get_by_id(task_id, owner_id)
        update_data = data.model_dump(exclude_unset=True)

        # Convert enum values if present
        if "priority" in update_data and update_data["priority"] is not None:
            update_data["priority"] = TaskPriority(update_data["priority"].value)
        if "status" in update_data and update_data["status"] is not None:
            update_data["status"] = TaskStatus(update_data["status"].value)

        return self.task_repo.update(task, **update_data)

    def delete(self, task_id: int, owner_id: int) -> None:
        task = self.get_by_id(task_id, owner_id)
        self.task_repo.delete(task)

    def list(
        self,
        owner_id: int,
        *,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        size: int = 20,
    ) -> TaskListResponse:
        status_enum = TaskStatus(status) if status else None
        priority_enum = TaskPriority(priority) if priority else None

        items, total = self.task_repo.list_by_owner(
            owner_id,
            status=status_enum,
            priority=priority_enum,
            search=search,
            page=page,
            size=size,
        )

        pages = ceil(total / size) if size > 0 else 0

        return TaskListResponse(
            items=[TaskRead.model_validate(t) for t in items],
            total=total,
            page=page,
            size=size,
            pages=pages,
        )
