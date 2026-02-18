"""
APScheduler initialization and configuration for the AI Todo Chatbot application.
Handles scheduled jobs for recurring task generation and reminder delivery.
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


# Global scheduler instance
_scheduler: Optional[AsyncIOScheduler] = None


def create_scheduler(db_url: str) -> AsyncIOScheduler:
    """Create and configure the APScheduler instance.
    
    Args:
        db_url: Database URL for job store persistence
        
    Returns:
        Configured AsyncIOScheduler instance
    """
    global _scheduler
    
    # Configure job stores - SQLAlchemy for persistence
    jobstores = {
        'default': SQLAlchemyJobStore(url=db_url)
    }
    
    # Configure executors
    executors = {
        'default': ThreadPoolExecutor(20)
    }
    
    # Job defaults
    job_defaults = {
        'coalesce': False,
        'max_instances': 3,
        'misfire_grace_time': 60  # 1 minute grace for missed runs
    }
    
    # Create scheduler
    _scheduler = AsyncIOScheduler(
        jobstores=jobstores,
        executors=executors,
        job_defaults=job_defaults,
        timezone='UTC'
    )
    
    logger.info("APScheduler initialized with SQLAlchemy job store")
    return _scheduler


def get_scheduler() -> Optional[AsyncIOScheduler]:
    """Get the global scheduler instance.
    
    Returns:
        AsyncIOScheduler instance or None if not initialized
    """
    return _scheduler


def start_scheduler():
    """Start the scheduler if not already running."""
    global _scheduler
    
    if _scheduler is None:
        logger.warning("Scheduler not initialized. Call create_scheduler() first.")
        return
    
    if not _scheduler.running:
        _scheduler.start()
        logger.info("APScheduler started")


def shutdown_scheduler(wait: bool = True):
    """Shutdown the scheduler.
    
    Args:
        wait: Whether to wait for running jobs to complete
    """
    global _scheduler
    
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=wait)
        logger.info("APScheduler shutdown complete")
        _scheduler = None


def add_job(func, trigger: str, **trigger_args) -> str:
    """Add a job to the scheduler.
    
    Args:
        func: Function to execute
        trigger: Trigger type ('interval', 'cron', 'date')
        **trigger_args: Trigger-specific arguments
        
    Returns:
        Job ID
    """
    if _scheduler is None:
        logger.error("Scheduler not initialized")
        return None
    
    job = _scheduler.add_job(
        func,
        trigger=trigger,
        **trigger_args,
        replace_existing=True
    )
    
    logger.info(f"Job added: {job.id} ({trigger})")
    return job.id


def remove_job(job_id: str):
    """Remove a job from the scheduler.
    
    Args:
        job_id: ID of job to remove
    """
    if _scheduler and job_id:
        try:
            _scheduler.remove_job(job_id)
            logger.info(f"Job removed: {job_id}")
        except Exception as e:
            logger.warning(f"Failed to remove job {job_id}: {e}")


# Example scheduled jobs (to be implemented in respective services)

def recurring_task_generation_job():
    """Job to generate recurring task instances.
    
    This job runs every minute and:
    1. Finds all recurring tasks due for instance generation
    2. Creates new task instances for each
    3. Updates next_run timestamps
    """
    from ..services.recurring_task_service import RecurringTaskService
    
    logger.debug("Running recurring task generation job")
    
    try:
        service = RecurringTaskService()
        service.generate_due_instances()
        logger.info("Recurring task generation completed")
    except Exception as e:
        logger.error(f"Recurring task generation failed: {e}")


def reminder_dispatch_job():
    """Job to dispatch due reminders.
    
    This job runs every 30 seconds and:
    1. Finds all reminders with trigger_time <= now
    2. Delivers notifications through configured channels
    3. Updates reminder status
    """
    from ..services.reminder_service import ReminderService
    
    logger.debug("Running reminder dispatch job")
    
    try:
        service = ReminderService()
        service.dispatch_due_reminders()
        logger.info("Reminder dispatch completed")
    except Exception as e:
        logger.error(f"Reminder dispatch failed: {e}")


def initialize_scheduled_jobs():
    """Initialize all scheduled jobs.
    
    Call this after creating the scheduler to set up:
    - Recurring task generation (every minute)
    - Reminder dispatch (every 30 seconds)
    """
    if _scheduler is None:
        logger.error("Scheduler not initialized")
        return
    
    # Recurring task generation - runs every minute
    add_job(
        func=recurring_task_generation_job,
        trigger='interval',
        seconds=60,
        id='recurring_task_generation',
        name='Generate recurring task instances'
    )
    
    # Reminder dispatch - runs every 30 seconds
    add_job(
        func=reminder_dispatch_job,
        trigger='interval',
        seconds=30,
        id='reminder_dispatch',
        name='Dispatch due reminders'
    )
    
    logger.info("Scheduled jobs initialized")
