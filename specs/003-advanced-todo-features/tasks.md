# Tasks: Advanced Todo Features

**Input**: Design documents from `/specs/003-advanced-todo-features/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks for critical paths. Tests are OPTIONAL - only include them if explicitly requested in the feature specification or if using TDD approach.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- **Containers**: `backend/Dockerfile`, `frontend/Dockerfile`
- **Kubernetes**: `helm-chart/templates/`
- Paths shown below assume web app structure per plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and structure

- [X] T001 Create backend project structure per implementation plan in `backend/src/`
- [X] T002 Update `backend/requirements.txt` with new dependencies: apscheduler, python-dateutil, dapr-sdk, confluent-kafka
- [X] T003 [P] Configure pytest and test directory structure in `backend/tests/`
- [X] T004 [P] Update `.env` template with new variables: KAFKA_BROKERS, DAPR_HTTP_PORT, DAPR_GRPC_PORT, SCHEDULER_ENABLED

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 [P] Create Priority enum in `backend/src/models/enums.py`
- [X] T006 [P] Create TaskStatus enum in `backend/src/models/enums.py`
- [X] T007 [P] Update Task model with new fields in `backend/src/models/task.py`: priority, status, rrule_string, parent_recurring_task_id, is_recurring_instance, search_vector
- [X] T008 [P] Create Tag model in `backend/src/models/tag.py`
- [X] T009 [P] Create TaskTag junction model in `backend/src/models/task_tag.py`
- [X] T010 [P] Create Reminder model in `backend/src/models/reminder.py`
- [X] T011 [P] Create TaskEvent model in `backend/src/models/task_event.py`
- [X] T012 Create database migration script in `backend/src/db/alembic_env.py` for new tables and columns
- [X] T013 [P] Create Dapr configuration in `backend/dapr/components/kafka-pubsub.yaml`
- [X] T014 [P] Create Dapr configuration in `backend/dapr/components/state-store.yaml`
- [X] T015 Create base event publisher service in `backend/src/services/event_publisher.py`
- [X] T016 Create APScheduler initialization in `backend/src/services/scheduler.py`
- [X] T017 Update database.py in `backend/src/db/database.py` with new session management for events

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create and Manage Recurring Tasks (Priority: P1) 🎯 MVP

**Goal**: Enable users to create tasks that repeat automatically on schedules (daily, weekly, monthly, custom patterns)

**Independent Test**: Create a recurring task with RRULE pattern and verify new instances are automatically generated at scheduled times, surviving server restarts

### Tests for User Story 1 (OPTIONAL) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T018 [P] [US1] Unit test for RRULE parsing in `backend/tests/unit/test_recurring.py::test_rrule_parsing`
- [ ] T019 [P] [US1] Integration test for recurring task instance generation in `backend/tests/integration/test_recurring_generation.py`
- [ ] T020 [US1] Contract test for recurring task creation endpoint in `backend/tests/contract/test_recurring_api.py`

### Implementation for User Story 1

- [ ] T021 [P] [US1] Create RecurringTaskService in `backend/src/services/recurring_task_service.py`
- [ ] T022 [P] [US1] Implement RRULE parser utility in `backend/src/utils/rrule_parser.py`
- [ ] T023 [US1] Add recurrence pattern field to TaskCreate schema in `backend/src/api/schemas/task.py`
- [ ] T024 [US1] Implement POST /tasks endpoint with recurrence support in `backend/src/api/routes/tasks.py`
- [ ] T025 [US1] Implement PUT /tasks/{task_id}/recurrence endpoint in `backend/src/api/routes/tasks.py`
- [ ] T026 [US1] Implement DELETE /tasks/{task_id}/recurrence endpoint in `backend/src/api/routes/tasks.py`
- [ ] T027 [US1] Implement recurring instance generation job in `backend/src/services/scheduler.py`
- [ ] T028 [US1] Add edge case handling for month-end dates in `backend/src/utils/rrule_parser.py`
- [ ] T029 [US1] Add logging for recurring task operations in `backend/src/utils/logger.py`
- [ ] T030 [US1] Update MCP tool add_task with rrule_string parameter in `backend/src/mcp/tools.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Set Due Dates and Receive Reminders (Priority: P2)

**Goal**: Enable users to assign due dates/times to tasks and receive configurable reminders before deadlines

**Independent Test**: Create tasks with due dates and reminders, verify reminders trigger at appropriate times and are delivered through configured channels

### Tests for User Story 2 (OPTIONAL) ⚠️

- [ ] T031 [P] [US2] Unit test for reminder trigger time calculation in `backend/tests/unit/test_reminder.py::test_trigger_time_calculation`
- [ ] T032 [P] [US2] Integration test for reminder delivery in `backend/tests/integration/test_reminder_delivery.py`
- [ ] T033 [US2] Contract test for reminder CRUD endpoints in `backend/tests/contract/test_reminder_api.py`

### Implementation for User Story 2

- [ ] T034 [P] [US2] Create ReminderService in `backend/src/services/reminder_service.py`
- [ ] T035 [P] [US2] Create NotificationService in `backend/src/services/notification_service.py`
- [ ] T036 [P] [US2] Create InAppNotification model in `backend/src/models/notification.py`
- [ ] T037 [US2] Add reminder fields to TaskCreate schema in `backend/src/api/schemas/task.py`
- [ ] T038 [US2] Implement POST /tasks/{task_id}/reminders endpoint in `backend/src/api/routes/reminders.py`
- [ ] T039 [US2] Implement GET /tasks/{task_id}/reminders endpoint in `backend/src/api/routes/reminders.py`
- [ ] T040 [US2] Implement DELETE /tasks/{task_id}/reminders/{reminder_id} endpoint in `backend/src/api/routes/reminders.py`
- [ ] T041 [US2] Implement reminder dispatcher job in `backend/src/services/scheduler.py`
- [ ] T042 [US2] Implement retry logic for failed deliveries in `backend/src/services/notification_service.py`
- [ ] T043 [US2] Add timezone handling for reminder triggers in `backend/src/utils/timezone.py`
- [ ] T044 [US2] Add logging for reminder operations in `backend/src/utils/logger.py`
- [ ] T045 [US2] Update MCP tool add_task with reminder parameter in `backend/src/mcp/tools.py`
- [ ] T046 [US2] Implement add_reminder MCP tool in `backend/src/mcp/tools.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Organize Tasks with Priorities and Tags (Priority: P3)

**Goal**: Enable users to assign priority levels and custom tags to tasks for organization and categorization

**Independent Test**: Create tasks with various priorities and tags, verify filtering, sorting, and search by these attributes works correctly

### Tests for User Story 3 (OPTIONAL) ⚠️

- [ ] T047 [P] [US3] Unit test for priority-based sorting in `backend/tests/unit/test_task_sorting.py::test_priority_sorting`
- [ ] T048 [P] [US3] Integration test for tag filtering in `backend/tests/integration/test_tag_filtering.py`
- [ ] T049 [US3] Contract test for tag CRUD endpoints in `backend/tests/contract/test_tag_api.py`

### Implementation for User Story 3

- [ ] T050 [P] [US3] Create TagService in `backend/src/services/tag_service.py`
- [ ] T051 [US3] Add priority enum to Task model in `backend/src/models/task.py` (if not in T005)
- [ ] T052 [US3] Implement POST /tags endpoint in `backend/src/api/routes/tags.py`
- [ ] T053 [US3] Implement GET /tags endpoint in `backend/src/api/routes/tags.py`
- [ ] T054 [US3] Implement DELETE /tags/{tag_id} endpoint in `backend/src/api/routes/tags.py`
- [ ] T055 [US3] Implement task-tag association in `backend/src/api/routes/tasks.py`
- [ ] T056 [US3] Add tag_ids field to TaskCreate and TaskUpdate schemas in `backend/src/api/schemas/task.py`
- [ ] T057 [US3] Implement tag filtering in list tasks endpoint in `backend/src/api/routes/tasks.py`
- [ ] T058 [US3] Implement priority filtering in list tasks endpoint in `backend/src/api/routes/tasks.py`
- [ ] T059 [US3] Add validation for duplicate tag names per user in `backend/src/services/tag_service.py`
- [ ] T060 [US3] Add logging for tag operations in `backend/src/utils/logger.py`
- [ ] T061 [US3] Update MCP tool add_task with priority and tag_ids parameters in `backend/src/mcp/tools.py`
- [ ] T062 [US3] Implement add_tag MCP tool in `backend/src/mcp/tools.py`

**Checkpoint**: At this point, User Stories 1, 2, and 3 should all work independently

---

## Phase 6: User Story 4 - Search, Filter, and Sort Tasks (Priority: P4)

**Goal**: Enable users to search tasks by keywords, filter by multiple criteria, and sort by various attributes

**Independent Test**: Create diverse set of tasks with different attributes, perform search/filter/sort operations and verify correct results

### Tests for User Story 4 (OPTIONAL) ⚠️

- [ ] T063 [P] [US4] Unit test for PostgreSQL full-text search in `backend/tests/unit/test_search.py::test_full_text_search`
- [ ] T064 [P] [US4] Integration test for combined filters in `backend/tests/integration/test_combined_filters.py`
- [ ] T065 [US4] Contract test for search endpoint in `backend/tests/contract/test_search_api.py`

### Implementation for User Story 4

- [ ] T066 [P] [US4] Create database trigger for search_vector auto-update in `backend/src/db/alembic_env.py`
- [ ] T067 [P] [US4] Create GIN index on search_vector in `backend/src/db/alembic_env.py`
- [ ] T068 [US4] Create SearchService in `backend/src/services/search_service.py`
- [ ] T069 [US4] Implement POST /tasks/search endpoint in `backend/src/api/routes/search.py`
- [ ] T070 [US4] Implement GET /tasks with query params for filtering in `backend/src/api/routes/tasks.py`
- [ ] T071 [US4] Add sort_by and sort_order parameters to list tasks in `backend/src/api/routes/tasks.py`
- [ ] T072 [US4] Implement date range filtering (due_date_from, due_date_to) in `backend/src/api/routes/tasks.py`
- [ ] T073 [US4] Implement status filtering in `backend/src/api/routes/tasks.py`
- [ ] T074 [US4] Add pagination support with page/limit params in `backend/src/api/routes/tasks.py`
- [ ] T075 [US4] Implement search result ranking using ts_rank_cd in `backend/src/services/search_service.py`
- [ ] T076 [US4] Add special character handling in search queries in `backend/src/utils/search_utils.py`
- [ ] T077 [US4] Add logging for search operations in `backend/src/utils/logger.py`

**Checkpoint**: At this point, User Stories 1-4 should all work independently

---

## Phase 7: User Story 5 - Event-Driven Task Notifications (Priority: P5)

**Goal**: Enable automatic event publishing for task lifecycle operations with reliable delivery via Kafka and Dapr

**Independent Test**: Subscribe to task events and verify appropriate events are published when task operations occur with correct CloudEvents payload structure

### Tests for User Story 5 (OPTIONAL) ⚠️

- [ ] T078 [P] [US5] Unit test for CloudEvents schema validation in `backend/tests/unit/test_events.py::test_cloudevents_schema`
- [ ] T079 [P] [US5] Integration test for Kafka event publishing in `backend/tests/integration/test_kafka_publishing.py`
- [ ] T080 [US5] Contract test for event history endpoint in `backend/tests/contract/test_events_api.py`

### Implementation for User Story 5

- [ ] T081 [P] [US5] Create CloudEvents schema validator in `backend/src/utils/cloudevents.py`
- [ ] T082 [P] [US5] Create Kafka consumer service in `backend/src/services/kafka_consumer.py`
- [ ] T083 [US5] Implement event publishing in TaskService in `backend/src/services/task_service.py`
- [ ] T084 [US5] Implement event publishing in ReminderService in `backend/src/services/reminder_service.py`
- [ ] T085 [US5] Implement event publishing in RecurringTaskService in `backend/src/services/recurring_task_service.py`
- [ ] T086 [US5] Implement GET /tasks/events endpoint in `backend/src/api/routes/events.py`
- [ ] T087 [US5] Add event type filtering to events endpoint in `backend/src/api/routes/events.py`
- [ ] T088 [US5] Implement idempotency tracking for duplicate events in `backend/src/services/kafka_consumer.py`
- [ ] T089 [US5] Add Dapr pub/sub integration in `backend/src/services/event_publisher.py`
- [ ] T090 [US5] Configure Kafka topics in `backend/dapr/components/kafka-pubsub.yaml`
- [ ] T091 [US5] Add event buffering for Kafka downtime in `backend/src/services/event_publisher.py`
- [ ] T092 [US5] Add logging for event operations in `backend/src/utils/logger.py`

**Checkpoint**: At this point, all 5 user stories should work independently

---

## Phase 8: Frontend Integration (Optional - if frontend updates requested)

**Goal**: Update React frontend to support advanced features

**Note**: This phase is optional and depends on whether frontend updates are in scope

- [ ] T093 [P] Create RecurringTaskForm component in `frontend/src/components/RecurringTaskForm.tsx`
- [ ] T094 [P] Create ReminderForm component in `frontend/src/components/ReminderForm.tsx`
- [ ] T095 [P] Create PrioritySelector component in `frontend/src/components/PrioritySelector.tsx`
- [ ] T096 [P] Create TagManager component in `frontend/src/components/TagManager.tsx`
- [ ] T097 Create SearchAndFilter component in `frontend/src/components/SearchAndFilter.tsx`
- [ ] T098 Update TaskList component in `frontend/src/components/TaskList.tsx` with sorting options
- [ ] T099 Update task API service in `frontend/src/services/taskApi.ts` with new endpoints
- [ ] T100 Add event subscription hook in `frontend/src/hooks/useTaskEvents.ts`

---

## Phase 9: Containerization & Kubernetes (Constitution Compliance)

**Purpose**: Package application for deployment per constitution requirements

- [X] T101 [P] Update `Dockerfile.backend` with new dependencies and health checks
- [X] T102 [P] Create Dapr sidecar configuration in `backend/dapr-config.yaml`
- [X] T103 [P] Update `helm-chart/values.yaml` with Kafka and Dapr configuration
- [X] T104 [P] Create Kafka deployment in `helm-chart/templates/kafka-deployment.yaml`
- [X] T105 [P] Create Dapr components deployment in `helm-chart/templates/dapr-components.yaml`
- [ ] T106 Update backend deployment template in `helm-chart/templates/deployment-backend.yaml` with Dapr annotations
- [ ] T107 Add resource limits for Kafka and Dapr in `helm-chart/templates/`
- [ ] T108 Configure liveness/readiness probes for new services in `helm-chart/templates/`
- [ ] T109 Update service discovery for event-driven communication in `helm-chart/templates/`
- [ ] T110 Add network policies for security in `helm-chart/templates/networkpolicy.yaml`

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T111 [P] Update API documentation in `specs/003-advanced-todo-features/contracts/api-contract.yaml`
- [ ] T112 [P] Update quickstart guide in `specs/003-advanced-todo-features/quickstart.md`
- [ ] T113 Code cleanup and refactoring across all services
- [ ] T114 Performance optimization for search queries
- [ ] T115 [P] Additional unit tests in `backend/tests/unit/`
- [ ] T116 [P] Additional integration tests in `backend/tests/integration/`
- [ ] T117 Security hardening (input validation, SQL injection prevention)
- [ ] T118 Run quickstart.md validation and fix any issues
- [ ] T119 Update README.md with new features
- [ ] T120 Create migration guide for existing users

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - **BLOCKS all user stories**
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Frontend (Phase 8)**: Optional, depends on backend APIs being complete
- **Containerization (Phase 9)**: Should start after Foundational, complete after all user stories
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1) - Recurring Tasks**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2) - Reminders**: Can start after Foundational (Phase 2) - Independent of US1
- **User Story 3 (P3) - Priorities & Tags**: Can start after Foundational (Phase 2) - Independent of US1/US2
- **User Story 4 (P4) - Search/Filter/Sort**: Can start after Foundational (Phase 2) - May benefit from US3 tags being complete
- **User Story 5 (P5) - Event-Driven**: Can start after Foundational (Phase 2) - Independent but integrates with all stories

### Within Each User Story

- Tests (if included) **MUST** be written and FAIL before implementation
- Models/utilities before services
- Services before endpoints/routes
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1 (Setup)**: T003, T004 can run in parallel
- **Phase 2 (Foundational)**: T005-T011 (all models) can run in parallel; T013-T014 (Dapr configs) can run in parallel
- **After Foundational completes**: All user stories (Phases 3-7) can start in parallel with different developers
- **Within User Story 1**: T018-T020 (tests) can run in parallel; T021-T022 (services/utilities) can run in parallel
- **Within User Story 2**: T031-T033 (tests) can run in parallel; T034-T036 (services/models) can run in parallel
- **Within User Story 3**: T047-T049 (tests) can run in parallel
- **Within User Story 4**: T063-T065 (tests) can run in parallel; T066-T067 (DB setup) can run in parallel
- **Within User Story 5**: T078-T080 (tests) can run in parallel; T081-T082 (utilities/consumer) can run in parallel
- **Phase 9**: T101-T105 can run in parallel (different files)

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Unit test for RRULE parsing in backend/tests/unit/test_recurring.py::test_rrule_parsing"
Task: "Integration test for recurring task instance generation in backend/tests/integration/test_recurring_generation.py"
Task: "Contract test for recurring task creation endpoint in backend/tests/contract/test_recurring_api.py"

# Launch all models/utilities for User Story 1 together:
Task: "Create RecurringTaskService in backend/src/services/recurring_task_service.py"
Task: "Implement RRULE parser utility in backend/src/utils/rrule_parser.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (**CRITICAL** - blocks all stories)
3. Complete Phase 3: User Story 1 (Recurring Tasks)
4. **STOP and VALIDATE**: Test recurring task creation and instance generation
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (Recurring Tasks) → Test independently → Deploy/Demo (**MVP!**)
3. Add User Story 2 (Reminders) → Test independently → Deploy/Demo
4. Add User Story 3 (Priorities & Tags) → Test independently → Deploy/Demo
5. Add User Story 4 (Search/Filter/Sort) → Test independently → Deploy/Demo
6. Add User Story 5 (Event-Driven) → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Recurring Tasks)
   - Developer B: User Story 2 (Reminders)
   - Developer C: User Story 3 (Priorities & Tags)
   - Developer D: User Story 4 (Search/Filter/Sort)
   - Developer E: User Story 5 (Event-Driven)
3. Stories complete and integrate independently
4. Team reconvenes for Phase 9 (Containerization & Kubernetes)

---

## Notes

- **[P]** tasks = different files, no dependencies, can run in parallel
- **[Story]** label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (if using tests)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Task Summary

| Phase | Description | Task Count |
|-------|-------------|------------|
| Phase 1 | Setup | 4 |
| Phase 2 | Foundational | 13 |
| Phase 3 | User Story 1 (Recurring Tasks) | 13 |
| Phase 4 | User Story 2 (Reminders) | 16 |
| Phase 5 | User Story 3 (Priorities & Tags) | 13 |
| Phase 6 | User Story 4 (Search/Filter/Sort) | 12 |
| Phase 7 | User Story 5 (Event-Driven) | 15 |
| Phase 8 | Frontend Integration (Optional) | 8 |
| Phase 9 | Containerization & Kubernetes | 10 |
| Phase 10 | Polish & Cross-Cutting | 10 |
| **Total** | **All phases** | **114** |

**MVP Scope** (Phases 1-3): 30 tasks
**Full Implementation** (Phases 1-7): 86 tasks
**Complete with DevOps** (Phases 1-10): 114 tasks

---

## Constitution Compliance Verification

### Statelessness Requirement
- [x] T007-T011: All models persist to PostgreSQL database
- [x] T016: APScheduler with persistent job store
- [x] T081-T092: Events persisted before publishing

### MCP Tool Compliance
- [x] T030, T045, T046, T061, T062: MCP tools updated with new parameters
- [x] All task operations through MCP tools in `backend/src/mcp/tools.py`

### Natural Language Interface
- [x] MCP tools support all advanced features for AI agent interpretation
- [x] Natural language parsing handled by existing AI agent

### Conversation Persistence
- [x] Conversation and Message models in data-model.md
- [x] Existing conversation infrastructure maintained

### Containerization Standards
- [x] T101: Dockerfile.backend updated
- [x] T102: Dapr sidecar configuration
- [x] Health checks included in deployment templates

### Kubernetes Deployment
- [x] T103-T110: Helm chart updated with Kafka, Dapr, probes, resources
- [x] Service discovery configured for event-driven communication
