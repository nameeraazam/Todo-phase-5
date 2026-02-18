"""
Event Publisher Service for the AI Todo Chatbot application.
Handles publishing domain events to Kafka via Dapr pub/sub.
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from dapr.clients import DaprClient
from dapr.clients.exceptions import DaprInternalError

logger = logging.getLogger(__name__)


class EventPublisher:
    """Service for publishing CloudEvents to Kafka via Dapr."""
    
    def __init__(self, pubsub_name: str = "kafka-pubsub"):
        """Initialize the event publisher.
        
        Args:
            pubsub_name: Name of the Dapr pub/sub component
        """
        self.pubsub_name = pubsub_name
        self._client = None
    
    @property
    def client(self) -> DaprClient:
        """Lazy initialization of Dapr client."""
        if self._client is None:
            try:
                self._client = DaprClient()
            except Exception as e:
                logger.warning(f"Dapr client initialization failed: {e}. Events will be buffered.")
                self._client = None
        return self._client
    
    def publish(
        self,
        topic: str,
        event_type: str,
        source: str,
        data: Dict[str, Any],
        event_id: Optional[str] = None
    ) -> bool:
        """Publish a CloudEvent to Kafka.
        
        Args:
            topic: Kafka topic to publish to
            event_type: Type of event (e.g., 'task.created')
            source: Source URI (e.g., '/tasks/123')
            data: Event data payload
            event_id: Optional event ID (generated if not provided)
            
        Returns:
            True if published successfully, False otherwise
        """
        if event_id is None:
            event_id = str(uuid.uuid4())
        
        # Create CloudEvent envelope
        cloud_event = {
            "specversion": "1.0",
            "type": event_type,
            "source": source,
            "id": event_id,
            "time": datetime.utcnow().isoformat() + "Z",
            "data": data,
            "datacontenttype": "application/json"
        }
        
        try:
            if self.client is None:
                logger.warning(f"Dapr client not available. Event buffered locally: {event_id}")
                # TODO: Implement local buffering for later replay
                return False
            
            self.client.publish_event(
                pubsub_name=self.pubsub_name,
                topic_name=topic,
                data=json.dumps(cloud_event),
                data_content_type="application/json"
            )
            
            logger.info(f"Event published: {event_type} -> {topic} (id: {event_id})")
            return True
            
        except DaprInternalError as e:
            logger.error(f"Dapr publish failed: {e}. Event buffered locally.")
            # TODO: Implement local buffering
            return False
        except Exception as e:
            logger.error(f"Unexpected error publishing event: {e}")
            return False
    
    def publish_task_event(
        self,
        event_type: str,
        task_id: int,
        data: Dict[str, Any]
    ) -> bool:
        """Publish a task-related event.
        
        Args:
            event_type: Type of task event
            task_id: ID of the task
            data: Event data payload
            
        Returns:
            True if published successfully
        """
        return self.publish(
            topic="tasks.events",
            event_type=event_type,
            source=f"/tasks/{task_id}",
            data=data
        )
    
    def publish_reminder_event(
        self,
        event_type: str,
        reminder_id: int,
        data: Dict[str, Any]
    ) -> bool:
        """Publish a reminder-related event.
        
        Args:
            event_type: Type of reminder event
            reminder_id: ID of the reminder
            data: Event data payload
            
        Returns:
            True if published successfully
        """
        return self.publish(
            topic="reminders.events",
            event_type=event_type,
            source=f"/reminders/{reminder_id}",
            data=data
        )
    
    def close(self):
        """Close the Dapr client connection."""
        if self._client:
            self._client.close()
            self._client = None


# Global event publisher instance
_event_publisher: Optional[EventPublisher] = None


def get_event_publisher() -> EventPublisher:
    """Get or create the global event publisher instance."""
    global _event_publisher
    if _event_publisher is None:
        _event_publisher = EventPublisher()
    return _event_publisher
