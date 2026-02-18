# Research: Advanced Todo Features

**Feature**: 003-advanced-todo-features  
**Date**: 2026-02-17  
**Purpose**: Resolve technical unknowns and establish best practices for implementation

---

## Phase 0: Outline & Research

### Research Tasks Identified

1. **Recurring Task Pattern Implementation** - Research best practices for recurring task scheduling
2. **Reminder Delivery System** - Research notification delivery patterns and timing
3. **Priority and Tag Data Modeling** - Research efficient storage and querying patterns
4. **Full-Text Search Implementation** - Research search strategies for PostgreSQL
5. **Event-Driven Architecture with Kafka** - Research Kafka integration patterns for task events
6. **Dapr Integration for Distributed Runtime** - Research Dapr service invocation and pub/sub patterns
7. **Task Scheduler Design** - Research background job scheduling for recurring tasks and reminders

---

## Research Findings

### 1. Recurring Task Pattern Implementation

**Decision**: Use iCalendar RFC 5545 RRULE syntax for recurrence pattern storage

**Rationale**:
- Industry standard for recurring events (used by Google Calendar, Outlook, Apple Calendar)
- Supports all required patterns: daily, weekly, monthly, yearly, custom intervals
- Handles edge cases like "last Monday of month", "every 3rd Friday"
- Python libraries available: `dateutil.rrule`, `icalendar`
- Stores as simple string: `FREQ=WEEKLY;BYDAY=MO` (every Monday)

**Alternatives Considered**:
- Custom JSON schema: More flexible but requires custom parsing logic
- Separate recurrence tables: More normalized but complex queries for instance generation
- Cron expressions: Limited support for complex patterns like "3rd Monday"

**Implementation Approach**:
- Store `rrule_string` field on Task model
- Use `python-dateutil.rrule` for parsing and calculating next occurrences
- Background scheduler queries for due recurring tasks every minute
- Generate new instance at scheduled time, mark with `parent_recurring_task_id`

**Edge Case Handling**:
- Monthly on 31st in 30-day month: Skip month or use last day (configurable)
- Timezone handling: Store all dates in UTC, convert to user timezone for display
- Series modification: Support "this instance only" vs "all future instances"

---

### 2. Reminder Delivery System

**Decision**: Multi-channel notification system with in-app as primary, extensible architecture for email/SMS/push

**Rationale**:
- In-app notifications provide immediate feedback within existing UI
- Extensible architecture allows adding channels without core logic changes
- Reminder preferences stored per-user, per-task
- Delivery attempts logged for reliability tracking

**Implementation Approach**:
- `Reminder` model with: task_id, trigger_time, delivery_channels, status
- Background scheduler checks for due reminders every 30 seconds
- Notification service publishes `reminder.due` event
- Notification consumers handle channel-specific delivery
- Retry logic with exponential backoff for failed deliveries

**Delivery Channels**:
- Phase 1: In-app (stored in database, fetched by frontend)
- Future: Email (SMTP), SMS (Twilio), Push (Firebase Cloud Messaging)

**Edge Case Handling**:
- Failed delivery: Retry up to 3 times with 5-minute intervals
- User timezone changes: Recalculate trigger times on timezone update
- Past-due reminders: Deliver immediately upon user's next login

---

### 3. Priority and Tag Data Modeling

**Decision**: Enum-based priority, many-to-many tags with junction table

**Rationale**:
- Priority as ENUM ensures data integrity and efficient querying
- Tags as separate table enables reusability and efficient filtering
- Junction table supports multiple tags per task
- Indexes on priority and tag_id for fast filtering

**Implementation Approach**:
- Priority: SQLAlchemy/SQLModel Enum field (LOW, MEDIUM, HIGH, URGENT)
- Tags: `Tag` table (id, name, user_id) + `TaskTag` junction table (task_id, tag_id)
- Unique constraint on (name, user_id) to prevent duplicate tags per user
- Cascade delete: deleting tag removes junction entries, not tasks

**Query Optimization**:
- Index on `Task.priority` for sorting
- Index on `TaskTag.tag_id` for filtering
- Composite index on `(task_id, tag_id)` for junction lookups
- Full-text search index includes priority name for natural language queries

---

### 4. Full-Text Search Implementation

**Decision**: PostgreSQL full-text search with tsvector/tsquery, GIN index

**Rationale**:
- Built into PostgreSQL (no additional infrastructure)
- Supports stemming, ranking, weighted searches
- Sufficient for 10,000 tasks per user at sub-500ms response
- Can extend to dedicated search service (Elasticsearch) if needed at scale

**Implementation Approach**:
- Add `search_vector` column (tsvector type) to Task table
- Trigger auto-updates search_vector on title/description changes
- GIN index on search_vector for fast lookups
- Search query: `to_tsquery('english', search_terms)`
- Ranking: `ts_rank_cd(search_vector, query)` for result ordering

**Advanced Features**:
- Filter by priority, tags, due date range using WHERE clauses
- Sort by relevance, due date, priority, creation date
- Highlighting: `ts_headline()` for search result snippets

**Edge Case Handling**:
- Special characters: Sanitize input, escape tsquery syntax
- Empty results: Return empty list with helpful suggestions
- Very broad searches: Limit to 100 results, require more specific query

---

### 5. Event-Driven Architecture with Kafka

**Decision**: Kafka for event streaming with exactly-once semantics, Dapr pub/sub abstraction

**Rationale**:
- Kafka provides durable, scalable event streaming
- At-least-once delivery guarantee meets requirement (FR-013)
- Dapr pub/sub abstraction simplifies Kafka integration
- Event sourcing enables audit trail and future analytics
- Decouples task operations from notification, analytics, integrations

**Event Schema** (CloudEvents specification):
```json
{
  "specversion": "1.0",
  "type": "task.created",
  "source": "/tasks/{task_id}",
  "id": "{uuid}",
  "time": "ISO8601 timestamp",
  "data": {
    "task_id": "uuid",
    "user_id": "uuid",
    "title": "string",
    "priority": "HIGH",
    "due_date": "ISO8601 or null",
    "tags": ["tag1", "tag2"]
  }
}
```

**Event Types**:
- `task.created`, `task.updated`, `task.completed`, `task.deleted`
- `reminder.due`, `reminder.delivered`, `reminder.failed`
- `recurring.instance.generated`, `recurring.series.modified`

**Implementation Approach**:
- Dapr sidecar configured with Kafka pub/sub component
- Backend publishes events via Dapr publish API (`/v1.0/publish/{pubsubname}/{topic}`)
- Event consumers subscribe to topics via Dapr subscription API
- Idempotent consumers track processed event IDs to handle duplicates

**Kafka Topics**:
- `tasks.events` - All task lifecycle events
- `reminders.events` - Reminder-related events
- `recurring.events` - Recurring task events

**Edge Case Handling**:
- Kafka downtime: Buffer events in database, replay when available
- Message backpressure: Implement consumer rate limiting, scale consumers
- Duplicate events: Idempotency key in event metadata, track processed IDs

---

### 6. Dapr Integration for Distributed Runtime

**Decision**: Dapr sidecar pattern for service invocation, pub/sub, and state management

**Rationale**:
- Simplifies distributed system patterns (service discovery, retries, circuit breaking)
- Language-agnostic APIs work with Python backend
- Pub/sub abstraction works with Kafka, RabbitMQ, Azure Service Bus
- State management provides consistent key-value storage abstraction
- Built-in observability (tracing, metrics)

**Dapr Components**:
1. **Pub/Sub**: Kafka component for event streaming
2. **State Store**: PostgreSQL component for distributed state
3. **Service Invocation**: HTTP/gRPC calls between services with retries

**Implementation Approach**:
- Dapr sidecar container in same pod as backend (Kubernetes)
- Backend calls Dapr APIs on `localhost:3500` (HTTP) or `localhost:50001` (gRPC)
- Dapr handles service discovery, load balancing, retries automatically
- State stored as key-value: `task:{task_id}`, `user:{user_id}:settings`

**Dapr Configuration** (Kubernetes):
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka:9092"
```

**Service-to-Service Communication**:
- Use Dapr service invocation: `POST http://localhost:3500/v1.0/invoke/{app-id}/method/{method-name}`
- Dapr handles retries, timeouts, circuit breaking
- mTLS between services automatically enabled

**Edge Case Handling**:
- Dapr sidecar unavailable: Fallback to direct Kafka/DB calls (degraded mode)
- State conflicts: Optimistic concurrency with etag
- Network partitions: Circuit breaker opens, fail gracefully

---

### 7. Task Scheduler Design

**Decision**: APScheduler with persistent job store in PostgreSQL

**Rationale**:
- APScheduler integrates well with FastAPI/Python
- Persistent job store survives server restarts
- Supports cron-like scheduling and interval-based jobs
- Lightweight compared to Celery/Redis for this use case

**Implementation Approach**:
- `AsyncIOScheduler` for async FastAPI compatibility
- `SQLAlchemyJobStore` for persistence in PostgreSQL
- Two scheduler jobs:
  1. **Recurring Task Generator** (runs every minute): Find recurring tasks due for instance generation
  2. **Reminder Dispatcher** (runs every 30 seconds): Find reminders due for delivery

**Job Store Tables**:
- `apscheduler_jobs` - Managed by APScheduler
- Custom queries for recurring tasks: `WHERE rrule_string IS NOT NULL AND next_run <= NOW()`
- Custom queries for reminders: `WHERE trigger_time <= NOW() AND status = 'pending'`

**Scalability Considerations**:
- Single scheduler instance for consistency (avoid duplicate instance generation)
- For horizontal scaling: Use Redis lock to ensure only one scheduler active
- Future: Migrate to distributed scheduler (Celery Beat with Redis) if needed

**Edge Case Handling**:
- Server downtime: Scheduler catches up on missed runs when restarted
- Long-running jobs: Timeout after 5 minutes, log warning
- Duplicate detection: Check if instance already exists before creating

---

## Technology Stack Summary

| Component | Technology | Justification |
|-----------|-----------|---------------|
| **Backend Framework** | FastAPI | Existing stack, async support, automatic OpenAPI docs |
| **ORM** | SQLModel | Existing stack, type-safe, SQLAlchemy compatibility |
| **Database** | PostgreSQL | Existing stack, JSONB support, full-text search |
| **Event Streaming** | Kafka + Dapr | Scalable, durable, Dapr abstraction simplifies integration |
| **Task Scheduling** | APScheduler | Python-native, persistent, integrates with FastAPI |
| **Recurrence Parsing** | python-dateutil | Industry standard, handles complex RRULE patterns |
| **Search** | PostgreSQL FTS | Built-in, sufficient performance, no new infrastructure |
| **Priority Storage** | SQLAlchemy Enum | Type-safe, efficient queries |
| **Tag Storage** | Many-to-many junction table | Flexible, efficient filtering |
| **Notifications** | In-app (extensible) | Immediate feedback, architecture supports future channels |

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Kubernetes Cluster                       │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Backend Pod                              │   │
│  │  ┌─────────────┐    ┌─────────────┐                  │   │
│  │  │   FastAPI   │◄──►│   Dapr      │                  │   │
│  │  │   App       │    │   Sidecar   │                  │   │
│  │  │  (uvicorn)  │    │  (localhost)│                  │   │
│  │  └─────────────┘    └──────┬──────┘                  │   │
│  │         │                  │                          │   │
│  │         │                  │                          │   │
│  └─────────┼──────────────────┼──────────────────────────┘   │
│            │                  │                              │
│            │                  │                              │
│            ▼                  ▼                              │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │   PostgreSQL    │  │     Kafka       │                   │
│  │   (database)    │  │  (event bus)    │                   │
│  │  - tasks        │  │  - tasks.events │                   │
│  │  - reminders    │  │  - reminders.ev │                   │
│  │  - tags         │  │  - recurring.ev │                   │
│  │  - events       │  │                 │                   │
│  └─────────────────┘  └─────────────────┘                   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Frontend Pod                             │   │
│  │  ┌─────────────┐                                     │   │
│  │  │    React    │                                     │   │
│  │  │   (nginx)   │                                     │   │
│  │  └─────────────┘                                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Next Steps

1. **Data Model Design**: Create detailed entity-relationship diagram based on research
2. **API Contract Definition**: Define OpenAPI endpoints for all new operations
3. **Event Schema Specification**: Finalize CloudEvents schema for all event types
4. **Dapr Component Configuration**: Create Kubernetes manifests for Dapr components
5. **Helm Chart Updates**: Add Kafka, Dapr, scheduler components to Helm chart
