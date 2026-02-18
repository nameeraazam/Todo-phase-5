"""
SQLModel junction table for Task-Tag many-to-many relationship.
"""

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class TaskTagBase(SQLModel):
    """Base schema for TaskTag junction table."""
    task_id: int = Field(foreign_key="task.id", primary_key=True, index=True)
    tag_id: int = Field(foreign_key="tag.id", primary_key=True, index=True)


class TaskTag(TaskTagBase, table=True):
    """Junction table for many-to-many relationship between Task and Tag."""
    __tablename__ = "task_tag"
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Composite primary key (task_id, tag_id) ensures no duplicate associations
    # Indexes on both columns for efficient lookups in both directions
    # CASCADE DELETE on both foreign keys


class TaskTagCreate(SQLModel):
    """Schema for creating a task-tag association."""
    task_id: int
    tag_id: int


class TaskTagRead(SQLModel):
    """Schema for reading task-tag association."""
    task_id: int
    tag_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
