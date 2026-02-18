"""
SQLModel model for the Reminder entity in the AI Todo Chatbot application.
Reminders notify users about upcoming or overdue tasks.
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import validator

from .enums import ReminderStatus


class ReminderBase(SQLModel):
    """Base schema for Reminder with common fields."""
    task_id: int = Field(foreign_key="task.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    trigger_time: datetime = Field(description="Absolute time when reminder should fire")
    relative_offset: Optional[str] = Field(
        default=None, 
        max_length=20,
        description="ISO 8601 duration (e.g., -PT1H for 1 hour before due date)"
    )
    delivery_channels: str = Field(
        default='["in_app"]',
        max_length=200,
        description="JSON array of delivery channels: in_app, email, sms, push"
    )


class Reminder(ReminderBase, table=True):
    """Reminder model representing a notification scheduled for a task."""
    __tablename__ = "reminder"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    status: ReminderStatus = Field(default=ReminderStatus.PENDING, index=True)
    delivered_at: Optional[datetime] = Field(default=None)
    retry_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    task: "Task" = Relationship(back_populates="reminders", sa_relationship_kwargs={"lazy": "joined"})
    user: "User" = Relationship(sa_relationship_kwargs={"lazy": "joined"})


class ReminderCreate(SQLModel):
    """Schema for creating a new reminder."""
    trigger_time: datetime
    relative_offset: Optional[str] = None
    delivery_channels: Optional[List[str]] = Field(default=["in_app"])
    
    class Config:
        json_schema_extra = {
            "example": {
                "trigger_time": "2026-02-23T16:00:00Z",
                "relative_offset": "-PT1H",
                "delivery_channels": ["in_app"]
            }
        }


class ReminderUpdate(SQLModel):
    """Schema for updating a reminder."""
    trigger_time: Optional[datetime] = None
    relative_offset: Optional[str] = None
    delivery_channels: Optional[List[str]] = None
    status: Optional[ReminderStatus] = None


class ReminderRead(SQLModel):
    """Schema for reading reminder data."""
    id: int
    task_id: int
    user_id: int
    trigger_time: datetime
    relative_offset: Optional[str]
    delivery_channels: str
    status: ReminderStatus
    delivered_at: Optional[datetime]
    retry_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ReminderWithTask(ReminderRead):
    """Extended reminder schema with task details."""
    task_title: Optional[str] = None
    task_due_date: Optional[datetime] = None
