"""
Alembic migrations for the AI Todo Chatbot application.
Advanced Features Migration Script

This migration adds support for:
- Priority and TaskStatus enums
- Recurring tasks (rrule_string, parent_recurring_task_id, is_recurring_instance)
- Tags and TaskTag junction table
- Reminders
- Task Events
- Full-text search vector for tasks
- Updated indexes for performance

Run with: alembic upgrade head
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime

# Revision identifiers
revision = '002_advanced_features'
down_revision = '001_initial'  # Assuming initial migration exists
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema with advanced features."""
    
    # Step 1: Create enums
    print("Creating enums...")
    
    # Create priority enum
    priority_enum = postgresql.ENUM('low', 'medium', 'high', 'urgent', name='priority')
    priority_enum.create(op.get_bind())
    
    # Create task_status enum
    task_status_enum = postgresql.ENUM('pending', 'in_progress', 'completed', 'cancelled', name='taskstatus')
    task_status_enum.create(op.get_bind())
    
    # Create reminder_status enum
    reminder_status_enum = postgresql.ENUM('pending', 'delivered', 'failed', 'cancelled', name='reminderstatus')
    reminder_status_enum.create(op.get_bind())
    
    # Step 2: Update Task table with new columns
    print("Updating Task table...")
    
    op.add_column('task', sa.Column('priority', priority_enum, nullable=False, server_default='medium'))
    op.add_column('task', sa.Column('status', task_status_enum, nullable=False, server_default='pending'))
    op.add_column('task', sa.Column('rrule_string', sa.String(length=500), nullable=True))
    op.add_column('task', sa.Column('is_recurring_instance', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('task', sa.Column('parent_recurring_task_id', sa.Integer(), nullable=True))
    op.add_column('task', sa.Column('search_vector', postgresql.TSVECTOR(), nullable=True))
    
    # Add foreign key for self-referential recurring tasks
    op.create_foreign_key(
        'fk_task_parent_recurring',
        'task', 'task',
        ['parent_recurring_task_id'], ['id']
    )
    
    # Step 3: Create Tag table
    print("Creating Tag table...")
    
    op.create_table(
        'tag',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=False, server_default='#000000'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'user_id', name='uq_tag_name_user')
    )
    
    # Create indexes for Tag table
    op.create_index('ix_tag_user_id', 'tag', ['user_id'])
    op.create_index('ix_tag_name_user', 'tag', ['name', 'user_id'])
    
    # Step 4: Create TaskTag junction table
    print("Creating TaskTag junction table...")
    
    op.create_table(
        'task_tag',
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['task_id'], ['task.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('task_id', 'tag_id')
    )
    
    # Create indexes for TaskTag table
    op.create_index('ix_tasktag_task_id', 'task_tag', ['task_id'])
    op.create_index('ix_tasktag_tag_id', 'task_tag', ['tag_id'])
    
    # Step 5: Create Reminder table
    print("Creating Reminder table...")
    
    op.create_table(
        'reminder',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('trigger_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('relative_offset', sa.String(length=20), nullable=True),
        sa.Column('delivery_channels', sa.String(length=200), nullable=False, server_default='["in_app"]'),
        sa.Column('status', reminder_status_enum, nullable=False, server_default='pending'),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['task_id'], ['task.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for Reminder table
    op.create_index('ix_reminder_task_id', 'reminder', ['task_id'])
    op.create_index('ix_reminder_user_id', 'reminder', ['user_id'])
    op.create_index('ix_reminder_trigger_time', 'reminder', ['trigger_time'])
    op.create_index('ix_reminder_status', 'reminder', ['status'])
    
    # Step 6: Create TaskEvent table
    print("Creating TaskEvent table...")
    
    op.create_table(
        'task_event',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('source', sa.String(length=255), nullable=False),
        sa.Column('event_id', sa.String(length=36), nullable=False),
        sa.Column('spec_version', sa.String(length=10), nullable=False, server_default='1.0'),
        sa.Column('time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('data', sa.Text(), nullable=False),
        sa.Column('published', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_id', name='uq_task_event_id')
    )
    
    # Create indexes for TaskEvent table
    op.create_index('ix_task_event_event_type', 'task_event', ['event_type'])
    op.create_index('ix_task_event_time', 'task_event', ['time'])
    op.create_index('ix_task_event_published', 'task_event', ['published', 'time'])
    
    # Step 7: Create indexes on Task table for performance
    print("Creating Task indexes...")
    
    op.create_index('ix_task_due_date', 'task', ['due_date'])
    op.create_index('ix_task_priority', 'task', ['priority'])
    op.create_index('ix_task_status', 'task', ['status'])
    op.create_index('ix_task_completed_at', 'task', ['completed_at'])
    op.create_index('ix_task_recurring_parent', 'task', ['parent_recurring_task_id'])
    
    # Create GIN index for full-text search
    op.create_index('ix_task_search_vector', 'task', ['search_vector'], postgresql_using='gin')
    
    # Step 8: Create trigger function for auto-updating search_vector
    print("Creating search vector trigger...")
    
    op.execute("""
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
    """)
    
    # Create trigger
    op.execute("""
        CREATE TRIGGER trigger_update_search_vector
        BEFORE INSERT OR UPDATE ON task
        FOR EACH ROW
        EXECUTE FUNCTION update_task_search_vector();
    """)
    
    # Step 9: Update existing tasks with default search_vector
    print("Updating existing tasks with search vector...")
    
    op.execute("""
        UPDATE task 
        SET search_vector = 
            setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
            setweight(to_tsvector('english', COALESCE(description, '')), 'B')
        WHERE search_vector IS NULL;
    """)
    
    print("Migration completed successfully!")


def downgrade() -> None:
    """Downgrade database schema by removing advanced features."""
    
    # Drop trigger
    op.execute("DROP TRIGGER IF EXISTS trigger_update_search_vector ON task")
    op.execute("DROP FUNCTION IF EXISTS update_task_search_vector()")
    
    # Drop TaskEvent table
    op.drop_index('ix_task_event_published', table_name='task_event')
    op.drop_index('ix_task_event_time', table_name='task_event')
    op.drop_index('ix_task_event_event_type', table_name='task_event')
    op.drop_table('task_event')
    
    # Drop Reminder table
    op.drop_index('ix_reminder_status', table_name='reminder')
    op.drop_index('ix_reminder_trigger_time', table_name='reminder')
    op.drop_index('ix_reminder_user_id', table_name='reminder')
    op.drop_index('ix_reminder_task_id', table_name='reminder')
    op.drop_table('reminder')
    
    # Drop TaskTag table
    op.drop_index('ix_tasktag_tag_id', table_name='task_tag')
    op.drop_index('ix_tasktag_task_id', table_name='task_tag')
    op.drop_table('task_tag')
    
    # Drop Tag table
    op.drop_index('ix_tag_name_user', table_name='tag')
    op.drop_index('ix_tag_user_id', table_name='tag')
    op.drop_table('tag')
    
    # Drop Task indexes
    op.drop_index('ix_task_search_vector', table_name='task')
    op.drop_index('ix_task_recurring_parent', table_name='task')
    op.drop_index('ix_task_completed_at', table_name='task')
    op.drop_index('ix_task_status', table_name='task')
    op.drop_index('ix_task_priority', table_name='task')
    op.drop_index('ix_task_due_date', table_name='task')
    
    # Remove Task columns
    op.drop_constraint('fk_task_parent_recurring', 'task', type_='foreignkey')
    op.drop_column('task', 'search_vector')
    op.drop_column('task', 'parent_recurring_task_id')
    op.drop_column('task', 'is_recurring_instance')
    op.drop_column('task', 'rrule_string')
    op.drop_column('task', 'status')
    op.drop_column('task', 'priority')
    
    # Drop enums
    op.execute("DROP TYPE IF EXISTS reminderstatus")
    op.execute("DROP TYPE IF EXISTS taskstatus")
    op.execute("DROP TYPE IF EXISTS priority")
