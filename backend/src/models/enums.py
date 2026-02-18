"""
Enum definitions for the AI Todo Chatbot application.
Defines Priority and TaskStatus enumerations.
"""

from enum import Enum


class Priority(str, Enum):
    """Priority levels for tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, Enum):
    """Status values for tasks."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ReminderStatus(str, Enum):
    """Status values for reminders."""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SenderType(str, Enum):
    """Sender types for messages."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class EventType(str, Enum):
    """Event types for task events."""
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_COMPLETED = "task.completed"
    TASK_DELETED = "task.deleted"
    REMINDER_DUE = "reminder.due"
    REMINDER_DELIVERED = "reminder.delivered"
    REMINDER_FAILED = "reminder.failed"
    RECURRING_INSTANCE_GENERATED = "recurring.instance.generated"
    RECURRING_SERIES_MODIFIED = "recurring.series.modified"
