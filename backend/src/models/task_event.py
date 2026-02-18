"""
SQLModel model for the TaskEvent entity in the AI Todo Chatbot application.
TaskEvent stores domain events for event sourcing and audit trail.
"""

from sqlmodel import SQLModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import json

from .enums import EventType


class TaskEventBase(SQLModel):
    """Base schema for TaskEvent with common fields."""
    event_type: str = Field(max_length=50, index=True, description="Type of event (e.g., task.created)")
    source: str = Field(max_length=255, description="Resource URI (e.g., /tasks/{task_id})")
    event_id: str = Field(unique=True, description="CloudEvents specification ID (UUID)")
    spec_version: str = Field(default="1.0", max_length=10, description="CloudEvents version")
    time: datetime = Field(index=True, description="Event timestamp")
    data: str = Field(description="JSON payload containing event-specific data")


class TaskEvent(TaskEventBase, table=True):
    """TaskEvent model representing a domain event in the task lifecycle."""
    __tablename__ = "task_event"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    published: bool = Field(default=False, index=True)
    published_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @classmethod
    def create(cls, event_type: EventType, source: str, data: Dict[str, Any]) -> "TaskEvent":
        """Factory method to create a new TaskEvent with proper defaults."""
        return cls(
            event_type=event_type.value,
            source=source,
            event_id=str(uuid.uuid4()),
            spec_version="1.0",
            time=datetime.utcnow(),
            data=json.dumps(data),
            published=False
        )
    
    def get_data(self) -> Dict[str, Any]:
        """Parse and return the JSON data payload."""
        return json.loads(self.data) if self.data else {}


class TaskEventCreate(SQLModel):
    """Schema for creating a new task event."""
    event_type: str
    source: str
    event_id: Optional[str] = None
    spec_version: str = "1.0"
    data: Dict[str, Any]


class TaskEventRead(SQLModel):
    """Schema for reading task event data."""
    id: int
    event_type: str
    source: str
    event_id: str
    spec_version: str
    time: datetime
    data: Dict[str, Any]
    published: bool
    published_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class TaskEventFilter(SQLModel):
    """Schema for filtering task events."""
    event_type: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
