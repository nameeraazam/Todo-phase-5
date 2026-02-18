"""
Main models module for the AI Todo Chatbot application.
Imports all individual models and defines relationships.
Updated with advanced features models.
"""

from .enums import Priority, TaskStatus, ReminderStatus, SenderType, EventType
from .task import Task, TaskCreate, TaskRead, TaskUpdate
from .tag import Tag, TagCreate, TagRead, TagUpdate
from .task_tag import TaskTag, TaskTagCreate, TaskTagRead
from .reminder import Reminder, ReminderCreate, ReminderRead, ReminderUpdate
from .task_event import TaskEvent, TaskEventCreate, TaskEventRead, TaskEventFilter
from .conversation import Conversation, ConversationCreate, ConversationRead
from .message import Message, MessageCreate, MessageRead
from .user import User, UserCreate, UserRead

# Import SQLModel for convenience
from sqlmodel import SQLModel

# Define all models in __all__ for easy importing
__all__ = [
    "SQLModel",
    # Enums
    "Priority",
    "TaskStatus",
    "ReminderStatus",
    "SenderType",
    "EventType",
    # Task models
    "Task",
    "TaskCreate",
    "TaskRead",
    "TaskUpdate",
    # Tag models
    "Tag",
    "TagCreate",
    "TagRead",
    "TagUpdate",
    # TaskTag junction table
    "TaskTag",
    "TaskTagCreate",
    "TaskTagRead",
    # Reminder models
    "Reminder",
    "ReminderCreate",
    "ReminderRead",
    "ReminderUpdate",
    # TaskEvent models
    "TaskEvent",
    "TaskEventCreate",
    "TaskEventRead",
    "TaskEventFilter",
    # Conversation models
    "Conversation",
    "ConversationCreate",
    "ConversationRead",
    # Message models
    "Message",
    "MessageCreate",
    "MessageRead",
    # User models
    "User",
    "UserCreate",
    "UserRead"
]
