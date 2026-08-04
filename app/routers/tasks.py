"""Task CRUD endpoints (authenticated, owner-scoped)."""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, status

from app.dependencies import CurrentUser, get_task_service
from app.schemas.task import (
    TaskCreate,
    TaskListResponse,
    TaskPriorityEnum,
    TaskRead,
    TaskStatusEnum,
    TaskUpdate,
)
from app.services.task import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
)
def create_task(
    payload: TaskCreate,
    current_user: CurrentUser,
    service: Annotated[TaskService, Depends(get_task_service)],
) -> TaskRead:
    task = service.create(current_user.id, payload)
    return TaskRead.model_validate(task)


@router.get(
    "",
    response_model=TaskListResponse,
    summary="List tasks with filters and pagination",
    description=(
        "Returns only tasks belonging to the authenticated user. "
        "Supports filtering by status, priority and free-text search on title/description. "
        "Results are paginated."
    ),
)
def list_tasks(
    current_user: CurrentUser,
    service: Annotated[TaskService, Depends(get_task_service)],
    status: Optional[TaskStatusEnum] = Query(None, description="Filter by status"),
    priority: Optional[TaskPriorityEnum] = Query(None, description="Filter by priority"),
    search: Optional[str] = Query(
        None, min_length=1, max_length=100, description="Search in title and description"
    ),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> TaskListResponse:
    return service.list(
        current_user.id,
        status=status.value if status else None,
        priority=priority.value if priority else None,
        search=search,
        page=page,
        size=size,
    )


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    summary="Get a single task by ID",
)
def get_task(
    task_id: int,
    current_user: CurrentUser,
    service: Annotated[TaskService, Depends(get_task_service)],
) -> TaskRead:
    task = service.get_by_id(task_id, current_user.id)
    return TaskRead.model_validate(task)


@router.patch(
    "/{task_id}",
    response_model=TaskRead,
    summary="Update a task",
    description="Partially update title, description, priority or status.",
)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    current_user: CurrentUser,
    service: Annotated[TaskService, Depends(get_task_service)],
) -> TaskRead:
    task = service.update(task_id, current_user.id, payload)
    return TaskRead.model_validate(task)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
)
def delete_task(
    task_id: int,
    current_user: CurrentUser,
    service: Annotated[TaskService, Depends(get_task_service)],
) -> None:
    service.delete(task_id, current_user.id)
