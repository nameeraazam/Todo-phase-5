"""
SQLModel model for the Tag entity in the AI Todo Chatbot application.
Tags allow users to categorize and organize tasks.
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime


class TagBase(SQLModel):
    """Base schema for Tag with common fields."""
    name: str = Field(min_length=1, max_length=50, description="Tag name, unique per user")
    color: str = Field(default="#000000", max_length=7, pattern=r"^#[0-9A-Fa-f]{6}$", description="Hex color code for UI display")


class Tag(TagBase, table=True):
    """Tag model representing a user-defined label for categorizing tasks."""
    __tablename__ = "tag"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: "User" = Relationship(back_populates="tags", sa_relationship_kwargs={"lazy": "joined"})
    tasks: List["Task"] = Relationship(back_populates="tags", link_model="TaskTag")
    
    # Unique constraint on (name, user_id) to prevent duplicate tags per user
    __table_args__ = (
        # Unique constraint will be created via migration
        # UNIQUE(name, user_id)
    )


class TagCreate(SQLModel):
    """Schema for creating a new tag."""
    name: str = Field(min_length=1, max_length=50)
    color: str = Field(default="#000000", max_length=7)


class TagUpdate(SQLModel):
    """Schema for updating a tag."""
    name: Optional[str] = Field(default=None, max_length=50)
    color: Optional[str] = Field(default=None, max_length=7)


class TagRead(SQLModel):
    """Schema for reading tag data."""
    id: int
    name: str
    color: str
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class TagWithTaskCount(TagRead):
    """Extended tag schema with task count."""
    task_count: int = 0
