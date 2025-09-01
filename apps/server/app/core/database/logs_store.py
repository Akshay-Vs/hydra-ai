from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlmodel import Session, select, desc

from app.models.enums import LogLevelEnum
from app.models.sql_model import Log


class LogStore:
    """Class to handle log operations using Log model"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def create_log(
        self,
        service_name: str,
        level: LogLevelEnum,
        message: str,
        organization_id: str,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        structured_data: Optional[Dict[str, Any]] = None,
        embedding: Optional[str] = None,
        timestamp: Optional[datetime] = None,
    ) -> Log:
        """
        Create a new log entry

        Args:
            service_name: Name of the service
            level: Log level
            message: Log message
            organization_id: Organization identifier
            trace_id: Optional trace ID
            span_id: Optional span ID
            structured_data: Optional structured data dictionary
            embedding: Optional vector embedding
            timestamp: Optional timestamp (defaults to now)

        Returns:
            Created Log object
        """
        log = Log(
            service_name=service_name,
            level=level,
            message=message,
            organization_id=organization_id,
            trace_id=trace_id,
            span_id=span_id,
            structured_data=structured_data,
            embedding=embedding,
            timestamp=timestamp or datetime.now(),
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def bulk_create_logs(self, logs_data: List[Dict]) -> List[Log]:
        """
        Bulk create multiple logs

        Args:
            logs_data: List of log dictionaries

        Returns:
            List of created Log objects
        """
        logs = [Log(**data) for data in logs_data]
        self.db.add_all(logs)
        self.db.commit()
        for log in logs:
            self.db.refresh(log)
        return logs

    def get_log(self, log_id: str) -> Optional[Log]:
        """Get log by ID"""
        return self.db.get(Log, log_id)

    def get_logs_by_service(
        self,
        service_name: str,
        organization_id: str,
        level: Optional[LogLevelEnum] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000,
    ) -> List[Log]:
        """
        Get logs for a specific service within time range

        Args:
            service_name: Service name to filter by
            organization_id: Organization identifier
            level: Optional log level filter
            start_time: Optional start time filter
            end_time: Optional end time filter
            limit: Maximum number of records to return

        Returns:
            List of Log objects
        """
        statement = select(Log).where(
            Log.service_name == service_name,
            Log.organization_id == organization_id,
        )

        if level:
            statement = statement.where(Log.level == level)
        if start_time:
            statement = statement.where(Log.timestamp >= start_time)
        if end_time:
            statement = statement.where(Log.timestamp <= end_time)

        statement = statement.order_by(desc(Log.timestamp)).limit(limit)
        return list(self.db.exec(statement).all())

    def get_logs_by_trace(self, trace_id: str, organization_id: str) -> List[Log]:
        """
        Get all logs for a specific trace

        Args:
            trace_id: Trace ID to filter by
            organization_id: Organization identifier

        Returns:
            List of Log objects
        """
        statement = (
            select(Log)
            .where(
                Log.trace_id == trace_id,
                Log.organization_id == organization_id,
            )
            .order_by(str(Log.timestamp))
        )
        return list(self.db.exec(statement).all())

    def search_logs_by_message(
        self,
        search_term: str,
        organization_id: str,
        service_name: Optional[str] = None,
        limit: int = 100,
    ) -> List[Log]:
        """
        Search logs by message content

        Args:
            search_term: Term to search for in messages
            organization_id: Organization identifier
            service_name: Optional service filter
            limit: Maximum number of records

        Returns:
            List of matching Log objects
        """
        statement = select(Log).where(
            Log.organization_id == organization_id,
            Log.message.__contains__(search_term),
        )

        if service_name:
            statement = statement.where(Log.service_name == service_name)

        statement = statement.order_by(desc(Log.timestamp)).limit(limit)
        return list(self.db.exec(statement).all())

    def delete_old_logs(self, organization_id: str, older_than: datetime) -> int:
        """
        Delete logs older than specified date

        Args:
            organization_id: Organization identifier
            older_than: Delete logs older than this date

        Returns:
            Number of logs deleted
        """
        statement = select(Log).where(
            Log.organization_id == organization_id,
            Log.timestamp < older_than,
        )
        logs = self.db.exec(statement).all()
        count = len(logs)

        for log in logs:
            self.db.delete(log)

        self.db.commit()
        return count
