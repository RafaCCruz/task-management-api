"""Task-related Pydantic schemas."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class TaskPriorityEnum(str, Enum):
    """Task priority values exposed by the API."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskStatusEnum(str, Enum):
    """Task status values exposed by the API."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskBase(BaseModel):
    """Shared task fields."""

    title: str = Field(..., min_length=1, max_length=200, examples=["Implement login endpoint"])
    description: Optional[str] = Field(
        None, max_length=5000, examples=["Add JWT authentication with refresh tokens"]
    )
    priority: TaskPriorityEnum = Field(
        default=TaskPriorityEnum.MEDIUM, examples=[TaskPriorityEnum.HIGH]
    )
    status: TaskStatusEnum = Field(
        default=TaskStatusEnum.PENDING, examples=[TaskStatusEnum.PENDING]
    )


class TaskCreate(TaskBase):
    """Payload for creating a new task."""

    pass


class TaskUpdate(BaseModel):
    """Payload for partial task update. All fields optional."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    priority: Optional[TaskPriorityEnum] = None
    status: Optional[TaskStatusEnum] = None


class TaskRead(TaskBase):
    """Public task representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime


class TaskListResponse(BaseModel):
    """Paginated list of tasks."""

    items: List[TaskRead]
    total: int
    page: int
    size: int
    pages: int
