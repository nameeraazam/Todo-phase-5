"""
SQLModel model for the Task entity in the AI Todo Chatbot application.
Updated with advanced features: priority, status, recurrence, search vector.
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from sqlalchemy import Column, Index, text
from sqlalchemy.dialects.postgresql import TSVECTOR

from .enums import Priority, TaskStatus


class TaskBase(SQLModel):
    """Base schema for Task with common fields."""
    title: str = Field(min_length=1, max_length=500)
    description: Optional[str] = Field(default=None, max_length=5000)
    priority: Priority = Field(default=Priority.MEDIUM)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    due_date: Optional[datetime] = Field(default=None)
    user_id: int = Field(foreign_key="user.id", index=True)
    
    # Recurrence fields
    rrule_string: Optional[str] = Field(default=None, max_length=500, description="iCalendar RRULE for recurring tasks")
    is_recurring_instance: bool = Field(default=False)
    parent_recurring_task_id: Optional[int] = Field(default=None, foreign_key="task.id")


class Task(TaskBase, table=True):
    """Task model representing a user's to-do item with advanced features."""
    __tablename__ = "task"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None, index=True)
    
    # Search vector for full-text search (PostgreSQL)
    search_vector: Optional[bytes] = Field(default=None, sa_column=Column(TSVECTOR))
    
    # Relationships
    user: "User" = Relationship(back_populates="tasks", sa_relationship_kwargs={"lazy": "joined"})
    tags: List["Tag"] = Relationship(back_populates="tasks", link_model="TaskTag")
    reminders: List["Reminder"] = Relationship(back_populates="task")
    child_recurring_tasks: List["Task"] = Relationship(
        back_populates="parent_recurring_task",
        sa_relationship_kwargs={"lazy": "select"}
    )
    parent_recurring_task: Optional["Task"] = Relationship(
        back_populates="child_recurring_tasks",
        sa_relationship_kwargs={"lazy": "select", "remote_side": "Task.id"}
    )


class TaskCreate(SQLModel):
    """Schema for creating a new task."""
    title: str = Field(min_length=1, max_length=500)
    description: Optional[str] = Field(default=None, max_length=5000)
    priority: Priority = Field(default=Priority.MEDIUM)
    due_date: Optional[datetime] = Field(default=None)
    rrule_string: Optional[str] = Field(default=None, max_length=500)
    tag_ids: Optional[List[int]] = Field(default=None)


class TaskUpdate(SQLModel):
    """Schema for updating a task."""
    title: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = Field(default=None, max_length=5000)
    priority: Optional[Priority] = Field(default=None)
    status: Optional[TaskStatus] = Field(default=None)
    due_date: Optional[datetime] = Field(default=None)
    rrule_string: Optional[str] = Field(default=None, max_length=500)
    tag_ids: Optional[List[int]] = Field(default=None)


class TaskRead(SQLModel):
    """Schema for reading task data with relationships."""
    id: int
    title: str
    description: Optional[str]
    priority: Priority
    status: TaskStatus
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    user_id: int
    rrule_string: Optional[str]
    is_recurring_instance: bool
    parent_recurring_task_id: Optional[int]
    tag_ids: Optional[List[int]] = None
    
    class Config:
        from_attributes = True


# Index definitions (to be created via migrations)
# These are documented here for reference:
# - idx_task_user_id: ON task(user_id)
# - idx_task_due_date: ON task(due_date)
# - idx_task_priority: ON task(priority)
# - idx_task_status: ON task(status)
# - idx_task_search_vector: ON task USING GIN(search_vector)
# - idx_task_recurring_parent: ON task(parent_recurring_task_id)
