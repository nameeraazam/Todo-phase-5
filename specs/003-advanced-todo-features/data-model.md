# Data Model: Advanced Todo Features

**Feature**: 003-advanced-todo-features  
**Date**: 2026-02-17  
**Database**: PostgreSQL 14+

---

## Entity-Relationship Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                           User                                    │
├──────────────────────────────────────────────────────────────────┤
│ id: UUID (PK)                                                     │
│ email: VARCHAR(255) (UNIQUE, NOT NULL)                           │
│ hashed_password: VARCHAR(255) (NOT NULL)                         │
│ timezone: VARCHAR(50) DEFAULT 'UTC'                              │
│ created_at: TIMESTAMP WITH TIME ZONE                             │
│ updated_at: TIMESTAMP WITH TIME ZONE                             │
└──────────────────────────────────────────────────────────────────┘
                              │
                              │ 1:N
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                           Task                                    │
├──────────────────────────────────────────────────────────────────┤
│ id: UUID (PK)                                                     │
│ user_id: UUID (FK → User.id, INDEX)                              │
│ title: VARCHAR(500) (NOT NULL)                                   │
│ description: TEXT                                                 │
│ priority: ENUM('LOW','MEDIUM','HIGH','URGENT') DEFAULT 'MEDIUM'  │
│ status: ENUM('PENDING','IN_PROGRESS','COMPLETED','CANCELLED')    │
│ due_date: TIMESTAMP WITH TIME ZONE (INDEX)                       │
│ completed_at: TIMESTAMP WITH TIME ZONE                           │
│ created_at: TIMESTAMP WITH TIME ZONE                             │
│ updated_at: TIMESTAMP WITH TIME ZONE                             │
│ rrule_string: VARCHAR(500) (recurrence pattern)                  │
│ parent_recurring_task_id: UUID (FK → Task.id, self-reference)    │
│ is_recurring_instance: BOOLEAN DEFAULT FALSE                     │
│ search_vector: TSVECTOR (GIN INDEX for full-text search)         │
└──────────────────────────────────────────────────────────────────┘
                              │
                              │ 1:N
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                         Reminder                                  │
├──────────────────────────────────────────────────────────────────┤
│ id: UUID (PK)                                                     │
│ task_id: UUID (FK → Task.id, INDEX, CASCADE DELETE)              │
│ user_id: UUID (FK → User.id, INDEX)                              │
│ trigger_time: TIMESTAMP WITH TIME ZONE (INDEX)                   │
│ relative_offset: INTERVAL (e.g., '-1 hour', '-1 day')            │
│ delivery_channels: JSONB (e.g., ["in_app", "email"])             │
│ status: ENUM('PENDING','DELIVERED','FAILED','CANCELLED')         │
│ delivered_at: TIMESTAMP WITH TIME ZONE                           │
│ retry_count: INTEGER DEFAULT 0                                   │
│ created_at: TIMESTAMP WITH TIME ZONE                             │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                           Tag                                     │
├──────────────────────────────────────────────────────────────────┤
│ id: UUID (PK)                                                     │
│ user_id: UUID (FK → User.id, INDEX)                              │
│ name: VARCHAR(50) (NOT NULL)                                     │
│ color: VARCHAR(7) DEFAULT '#000000' (hex color)                  │
│ created_at: TIMESTAMP WITH TIME ZONE                             │
│ UNIQUE(name, user_id)                                            │
│ INDEX(name, user_id)                                             │
└──────────────────────────────────────────────────────────────────┘
                              │
                              │ N:M
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                         TaskTag                                   │
├──────────────────────────────────────────────────────────────────┤
│ task_id: UUID (FK → Task.id, PK, CASCADE DELETE)                 │
│ tag_id: UUID (FK → Tag.id, PK, CASCADE DELETE)                   │
│ created_at: TIMESTAMP WITH TIME ZONE                             │
│ INDEX(task_id, tag_id)                                           │
│ INDEX(tag_id, task_id)                                           │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                        TaskEvent                                  │
├──────────────────────────────────────────────────────────────────┤
│ id: UUID (PK)                                                     │
│ event_type: VARCHAR(50) (INDEX) (e.g., 'task.created')           │
│ source: VARCHAR(255) (e.g., '/tasks/{task_id}')                  │
│ event_id: UUID (UNIQUE) (CloudEvents id)                         │
│ spec_version: VARCHAR(10) DEFAULT '1.0'                          │
│ time: TIMESTAMP WITH TIME ZONE (INDEX)                           │
│ data: JSONB (CloudEvents data payload)                           │
│ published: BOOLEAN DEFAULT FALSE                                 │
│ published_at: TIMESTAMP WITH TIME ZONE                           │
│ created_at: TIMESTAMP WITH TIME ZONE                             │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                      Conversation                                 │
├──────────────────────────────────────────────────────────────────┤
│ id: UUID (PK)                                                     │
│ user_id: UUID (FK → User.id, INDEX)                              │
│ title: VARCHAR(255) (e.g., "Task Management Session")            │
│ created_at: TIMESTAMP WITH TIME ZONE                             │
│ updated_at: TIMESTAMP WITH TIME ZONE                             │
│ last_activity_at: TIMESTAMP WITH TIME ZONE                       │
└──────────────────────────────────────────────────────────────────┘
                              │
                              │ 1:N
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                       Message                                     │
├──────────────────────────────────────────────────────────────────┤
│ id: UUID (PK)                                                     │
│ conversation_id: UUID (FK → Conversation.id, INDEX)              │
│ role: ENUM('USER', 'ASSISTANT', 'SYSTEM')                        │
│ content: TEXT (NOT NULL)                                         │
│ metadata: JSONB (e.g., referenced task IDs, MCP tool calls)      │
│ created_at: TIMESTAMP WITH TIME ZONE                             │
└──────────────────────────────────────────────────────────────────┘
```

---

## Entity Definitions

### User

Represents an individual using the Todo Chatbot system.

**Fields**:
- `id`: Unique identifier (UUID)
- `email`: User's email address (unique, used for authentication)
- `hashed_password`: Bcrypt-hashed password
- `timezone`: User's timezone for scheduling (default: UTC)
- `created_at`: Account creation timestamp
- `updated_at`: Last profile update timestamp

**Relationships**:
- One-to-Many with Task (user owns multiple tasks)
- One-to-Many with Reminder (user receives reminders)
- One-to-Many with Tag (user creates tags)
- One-to-Many with Conversation (user has conversation history)

---

### Task

Represents a user's to-do item with optional recurrence, priority, and tags.

**Fields**:
- `id`: Unique identifier (UUID)
- `user_id`: Foreign key to User (INDEX for fast user filtering)
- `title`: Task title (max 500 chars, required)
- `description`: Detailed task description (optional)
- `priority`: Enum (LOW, MEDIUM, HIGH, URGENT), default MEDIUM
- `status`: Enum (PENDING, IN_PROGRESS, COMPLETED, CANCELLED)
- `due_date`: When task is due (timezone-aware, INDEX for date filtering)
- `completed_at`: When task was marked complete (nullable)
- `created_at`: Task creation timestamp
- `updated_at`: Last modification timestamp
- `rrule_string`: iCalendar RRULE for recurring tasks (e.g., "FREQ=WEEKLY;BYDAY=MO")
- `parent_recurring_task_id`: Self-reference to parent recurring task (nullable)
- `is_recurring_instance`: True if this is an instance of a recurring series
- `search_vector`: PostgreSQL TSVECTOR for full-text search (GIN INDEX)

**Validation Rules**:
- Title must be non-empty and under 500 characters
- If `is_recurring_instance` is True, `parent_recurring_task_id` must be set
- `completed_at` must be set when status changes to COMPLETED
- `rrule_string` must be valid iCalendar RRULE syntax if provided
- Due date must be in the future for new tasks (optional validation)

**State Transitions**:
```
PENDING → IN_PROGRESS (user starts task)
PENDING → COMPLETED (user completes directly)
PENDING → CANCELLED (user cancels)
IN_PROGRESS → COMPLETED (user completes)
IN_PROGRESS → CANCELLED (user cancels)
COMPLETED → PENDING (user reopens, if allowed)
CANCELLED → PENDING (user reopens, if allowed)
```

**Indexes**:
- `idx_task_user_id`: Fast user filtering
- `idx_task_due_date`: Date-based queries
- `idx_task_priority`: Priority sorting
- `idx_task_status`: Status filtering
- `idx_task_search_vector`: Full-text search (GIN)
- `idx_task_recurring_parent`: Find instances of recurring series

---

### Reminder

Represents a notification scheduled for a specific time relative to a task's due date.

**Fields**:
- `id`: Unique identifier (UUID)
- `task_id`: Foreign key to Task (CASCADE DELETE, INDEX)
- `user_id`: Foreign key to User (INDEX for user-specific queries)
- `trigger_time`: Absolute time when reminder should fire (INDEX)
- `relative_offset`: INTERVAL representing offset from due date (e.g., '-1 hour')
- `delivery_channels`: JSONB array (e.g., ["in_app"], ["in_app", "email"])
- `status`: Enum (PENDING, DELIVERED, FAILED, CANCELLED)
- `delivered_at`: When reminder was successfully delivered
- `retry_count`: Number of delivery attempts (max 3)
- `created_at`: Reminder creation timestamp

**Validation Rules**:
- `trigger_time` must be in the future
- `delivery_channels` must contain at least one channel
- `relative_offset` must be negative (before due date) or zero (at due date)
- Only one reminder per task per delivery channel

**Business Logic**:
- Reminder automatically cancelled if task is completed before trigger time
- Retry logic: 3 attempts with 5-minute exponential backoff on failure
- Timezone-aware: trigger_time adjusted if user changes timezone

---

### Tag

Represents a user-defined label for categorizing tasks.

**Fields**:
- `id`: Unique identifier (UUID)
- `user_id`: Foreign key to User (INDEX)
- `name`: Tag name (max 50 chars, case-insensitive per user)
- `color`: Hex color code for UI display (default: #000000)
- `created_at`: Tag creation timestamp

**Validation Rules**:
- Name must be unique per user (case-insensitive)
- Name must be 1-50 characters, alphanumeric + hyphens + underscores
- Color must be valid 6-digit hex code

**Constraints**:
- `UNIQUE(name, user_id)`: Prevent duplicate tags per user
- Maximum 100 tags per user (enforced at application layer)

---

### TaskTag

Junction table for many-to-many relationship between Task and Tag.

**Fields**:
- `task_id`: Foreign key to Task (CASCADE DELETE)
- `tag_id`: Foreign key to Tag (CASCADE DELETE)
- `created_at`: Association creation timestamp

**Constraints**:
- Primary key: (task_id, tag_id)
- `UNIQUE(task_id, tag_id)`: Prevent duplicate associations
- `INDEX(task_id, tag_id)`: Fast task-to-tag lookups
- `INDEX(tag_id, task_id)`: Fast tag-to-task lookups

---

### TaskEvent

Represents a domain event in the task lifecycle (for event sourcing and audit trail).

**Fields**:
- `id`: Unique identifier (UUID)
- `event_type`: Type of event (e.g., "task.created", "task.completed")
- `source`: Resource URI (e.g., "/tasks/{task_id}")
- `event_id`: CloudEvents specification ID (unique)
- `spec_version`: CloudEvents version (default: "1.0")
- `time`: Event timestamp (INDEX for chronological queries)
- `data`: JSONB payload containing event-specific data
- `published`: Whether event was published to Kafka
- `published_at`: When event was published
- `created_at`: Event record creation timestamp

**Event Types**:
- `task.created`: New task created
- `task.updated`: Task modified
- `task.completed`: Task marked complete
- `task.deleted`: Task removed
- `task.priority_changed`: Priority updated
- `reminder.due`: Reminder trigger time arrived
- `reminder.delivered`: Reminder successfully delivered
- `reminder.failed`: Reminder delivery failed
- `recurring.instance.generated`: New recurring instance created
- `recurring.series.modified`: Recurring series pattern changed

**CloudEvents Data Payload Example**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Submit timesheet",
  "priority": "HIGH",
  "due_date": "2026-02-20T17:00:00Z",
  "tags": ["work", "finance"],
  "previous_values": {
    "priority": "MEDIUM"
  }
}
```

---

### Conversation

Represents a session of interaction between user and AI chatbot.

**Fields**:
- `id`: Unique identifier (UUID)
- `user_id`: Foreign key to User (INDEX)
- `title`: Auto-generated or user-provided conversation title
- `created_at`: Conversation start timestamp
- `updated_at`: Last metadata update timestamp
- `last_activity_at`: Last message timestamp (INDEX for sorting)

**Business Logic**:
- Automatically created on first user message in a session
- Title auto-generated from first user message (truncated to 50 chars)
- Archived after 30 days of inactivity (configurable)

---

### Message

Represents a single message within a conversation.

**Fields**:
- `id`: Unique identifier (UUID)
- `conversation_id`: Foreign key to Conversation (INDEX)
- `role`: Enum (USER, ASSISTANT, SYSTEM)
- `content`: Message text (required)
- `metadata`: JSONB containing contextual information
- `created_at`: Message timestamp

**Metadata Structure**:
```json
{
  "referenced_task_ids": ["uuid1", "uuid2"],
  "mcp_tool_calls": [
    {
      "tool": "add_task",
      "parameters": {"task_text": "Buy groceries"},
      "result": {"task_id": "uuid"}
    }
  ],
  "intent": "create_task",
  "entities": {
    "task_title": "Buy groceries",
    "due_date": "tomorrow"
  }
}
```

---

## Database Indexes

### Performance-Critical Indexes

```sql
-- Task queries
CREATE INDEX idx_task_user_id ON Task(user_id);
CREATE INDEX idx_task_due_date ON Task(due_date);
CREATE INDEX idx_task_priority ON Task(priority);
CREATE INDEX idx_task_status ON Task(status);
CREATE INDEX idx_task_user_status ON Task(user_id, status);
CREATE INDEX idx_task_user_due_date ON Task(user_id, due_date);
CREATE INDEX idx_task_recurring_parent ON Task(parent_recurring_task_id);

-- Full-text search
CREATE INDEX idx_task_search_vector ON Task USING GIN(search_vector);

-- Reminder queries
CREATE INDEX idx_reminder_task_id ON Reminder(task_id);
CREATE INDEX idx_reminder_user_id ON Reminder(user_id);
CREATE INDEX idx_reminder_trigger_time ON Reminder(trigger_time);
CREATE INDEX idx_reminder_pending ON Reminder(status, trigger_time) WHERE status = 'PENDING';

-- Tag queries
CREATE INDEX idx_tag_user_id ON Tag(user_id);
CREATE INDEX idx_tag_name_user ON Tag(name, user_id);
CREATE INDEX idx_tasktag_task_id ON TaskTag(task_id);
CREATE INDEX idx_tasktag_tag_id ON TaskTag(tag_id);

-- Event queries
CREATE INDEX idx_event_type ON TaskEvent(event_type);
CREATE INDEX idx_event_time ON TaskEvent(time);
CREATE INDEX idx_event_published ON TaskEvent(published, time) WHERE published = FALSE;

-- Conversation queries
CREATE INDEX idx_conversation_user_id ON Conversation(user_id);
CREATE INDEX idx_conversation_last_activity ON Conversation(last_activity_at DESC);
CREATE INDEX idx_message_conversation_id ON Message(conversation_id);
CREATE INDEX idx_message_created_at ON Message(created_at);
```

---

## Database Triggers

### Auto-update search_vector on Task changes

```sql
CREATE OR REPLACE FUNCTION update_task_search_vector()
RETURNS TRIGGER AS $$
BEGIN
  NEW.search_vector := 
    setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'B') ||
    setweight(to_tsvector('english', COALESCE(NEW.priority::text, '')), 'C') ||
    setweight(to_tsvector('english', COALESCE(NEW.status::text, '')), 'D');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_search_vector
BEFORE INSERT OR UPDATE ON Task
FOR EACH ROW
EXECUTE FUNCTION update_task_search_vector();
```

---

## Migration Strategy

### Phase 1: Add new columns to existing Task table

```sql
-- Add priority column
ALTER TABLE Task ADD COLUMN priority VARCHAR(20) DEFAULT 'MEDIUM';
ALTER TABLE Task ADD COLUMN status VARCHAR(20) DEFAULT 'PENDING';

-- Add recurrence columns
ALTER TABLE Task ADD COLUMN rrule_string VARCHAR(500);
ALTER TABLE Task ADD COLUMN parent_recurring_task_id UUID REFERENCES Task(id);
ALTER TABLE Task ADD COLUMN is_recurring_instance BOOLEAN DEFAULT FALSE;

-- Add search vector
ALTER TABLE Task ADD COLUMN search_vector TSVECTOR;
CREATE INDEX idx_task_search_vector ON Task USING GIN(search_vector);
```

### Phase 2: Create new tables

```sql
-- Create Tag table
CREATE TABLE Tag (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES "User"(id) ON DELETE CASCADE,
  name VARCHAR(50) NOT NULL,
  color VARCHAR(7) DEFAULT '#000000',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(name, user_id)
);

-- Create TaskTag junction table
CREATE TABLE TaskTag (
  task_id UUID REFERENCES Task(id) ON DELETE CASCADE,
  tag_id UUID REFERENCES Tag(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (task_id, tag_id)
);

-- Create Reminder table
CREATE TABLE Reminder (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  task_id UUID REFERENCES Task(id) ON DELETE CASCADE,
  user_id UUID REFERENCES "User"(id),
  trigger_time TIMESTAMPTZ NOT NULL,
  relative_offset INTERVAL,
  delivery_channels JSONB DEFAULT '["in_app"]',
  status VARCHAR(20) DEFAULT 'PENDING',
  delivered_at TIMESTAMPTZ,
  retry_count INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create TaskEvent table
CREATE TABLE TaskEvent (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_type VARCHAR(50) NOT NULL,
  source VARCHAR(255) NOT NULL,
  event_id UUID UNIQUE NOT NULL,
  spec_version VARCHAR(10) DEFAULT '1.0',
  time TIMESTAMPTZ NOT NULL,
  data JSONB NOT NULL,
  published BOOLEAN DEFAULT FALSE,
  published_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Phase 3: Create Conversation and Message tables

```sql
-- Create Conversation table
CREATE TABLE Conversation (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES "User"(id) ON DELETE CASCADE,
  title VARCHAR(255),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  last_activity_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create Message table
CREATE TABLE Message (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID REFERENCES Conversation(id) ON DELETE CASCADE,
  role VARCHAR(20) NOT NULL,
  content TEXT NOT NULL,
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Data Retention Policy

- **Tasks**: Retained indefinitely until user deletes
- **Completed Tasks**: Archived after 1 year (configurable)
- **TaskEvents**: Detailed events retained for 90 days, aggregated statistics indefinitely
- **Conversations/Messages**: Retained for 1 year, then archived
- **Reminders**: Deleted when associated task is deleted

---

## Scalability Considerations

### Partitioning Strategy (Future)

When Task table exceeds 10M rows:
- Partition by `user_id` hash for multi-tenant isolation
- Or partition by `created_at` range for time-based retention

### Index Optimization

- Covering indexes for common queries (user_id + status + due_date)
- Partial indexes for filtered queries (e.g., only pending reminders)
- BRIN indexes for time-series data if partitioned

### Connection Pooling

- Use PgBouncer for connection pooling at scale
- Configure pool size based on backend replica count
