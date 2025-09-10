from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlmodel import Session, col, select, desc
from hydra_types.telemetry import Trace as TraceType, TraceEvent
from app.utils.now import now

from app.models.sql_model import Trace


class TraceStore:
    """Class to handle trace operations using Trace model"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def create_trace(
        self,
        trace_id: str,
        span_id: str,
        operation_name: str,
        start_time: datetime,
        service_name: str,
        service_version: str,
        organization_id: str,
        parent_span_id: Optional[str] = None,
        end_time: Optional[datetime] = None,
        duration_ms: Optional[float] = None,
        status: str = "OK",
        attributes: Optional[Dict[str, Any]] = None,
        events: Optional[List[TraceEvent]] = None,
    ) -> Trace:
        """
        Create a new trace entry

        Args:
            trace_id: Trace identifier
            span_id: Span identifier
            operation_name: Name of the operation
            start_time: Start timestamp
            service_name: Name of the service
            service_version: Version of the service
            organization_id: Organization identifier
            parent_span_id: Optional parent span ID
            end_time: Optional end timestamp
            duration_ms: Optional duration in milliseconds
            status: Status of the trace (defaults to "OK")
            attributes: Optional attributes dictionary
            events: Optional events list

        Returns:
            Created Trace object
        """
        trace = Trace(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            start_time=start_time,
            end_time=end_time,
            duration_ms=str(duration_ms),
            status=status,
            attributes=attributes,
            events=events,
            service_name=service_name,
            service_version=service_version,
            organization_id=organization_id,
        )
        self.db.add(trace)
        self.db.commit()
        self.db.refresh(trace)
        return trace

    def bulk_create_traces(
        self, traces_data: List[TraceType], organization_id: str
    ) -> List[Trace]:
        """
        Bulk create multiple traces

        Args:
            traces_data: List of trace dictionaries
            organization_id: Organization identifier

        Returns:
            List of created Trace objects
        """
        traces = [
            Trace(
                trace_id=data.trace_id,
                span_id=data.span_id,
                parent_span_id=data.parent_span_id,
                operation_name=data.operation_name,
                start_time=data.start_time,
                end_time=data.end_time,
                duration_ms=str(data.duration_ms),
                status=data.status,
                attributes=data.attributes,
                events=data.events,
                service_name=data.service_name,
                service_version=data.service_version,
                organization_id=organization_id,
            )
            for data in traces_data
        ]
        self.db.add_all(traces)
        self.db.commit()
        for trace in traces:
            self.db.refresh(trace)
        return traces

    def get_trace(self, trace_id: str) -> Optional[Trace]:
        """Get trace by ID"""
        return self.db.get(Trace, trace_id)

    def get_traces_by_service(
        self,
        service_name: str,
        organization_id: str,
        status: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000,
    ) -> List[Trace]:
        """
        Get traces for a specific service within time range

        Args:
            service_name: Service name to filter by
            organization_id: Organization identifier
            status: Optional status filter
            start_time: Optional start time filter (timestamp)
            end_time: Optional end time filter (timestamp)
            limit: Maximum number of records to return

        Returns:
            List of Trace objects
        """
        statement = select(Trace).where(
            Trace.service_name == service_name,
            Trace.organization_id == organization_id,
        )

        if status:
            statement = statement.where(Trace.status == status)
        if start_time:
            statement = statement.where(Trace.start_time >= start_time)
        if end_time:
            statement = statement.where(Trace.start_time <= end_time)

        statement = statement.order_by(desc(Trace.start_time)).limit(limit)
        return list(self.db.exec(statement).all())

    def get_traces_by_trace_id(
        self, trace_id: str, organization_id: str, limit: int = 100
    ) -> List[Trace]:
        """
        Get all traces (spans) for a specific trace ID

        Args:
            trace_id: Trace ID to filter by
            organization_id: Organization identifier

        Returns:
            List of Trace objects
        """
        statement = select(Trace).where(
            Trace.trace_id == trace_id,
            Trace.organization_id == organization_id,
        )
        statement = statement.order_by(desc(Trace.start_time)).limit(limit)
        return list(self.db.exec(statement).all())

    def get_child_spans(
        self, parent_span_id: str, organization_id: str, limit: int = 100
    ) -> List[Trace]:
        """
        Get all child spans for a specific parent span

        Args:
            parent_span_id: Parent span ID to filter by
            organization_id: Organization identifier

        Returns:
            List of child Trace objects
        """
        statement = select(Trace).where(
            Trace.parent_span_id == parent_span_id,
            Trace.organization_id == organization_id,
        )

        statement = statement.order_by(desc(Trace.start_time)).limit(limit)
        return list(self.db.exec(statement).all())

    def search_traces_by_operation(
        self,
        search_term: str,
        organization_id: str,
        service_name: Optional[str] = None,
        limit: int = 100,
    ) -> List[Trace]:
        """
        Search traces by operation name

        Args:
            search_term: Term to search for in operation names
            organization_id: Organization identifier
            service_name: Optional service filter
            limit: Maximum number of records

        Returns:
            List of matching Trace objects
        """
        statement = select(Trace).where(
            Trace.organization_id == organization_id,
            col(Trace.operation_name).contains(search_term),
        )

        if service_name:
            statement = statement.where(Trace.service_name == service_name)

        statement = statement.order_by(desc(Trace.start_time)).limit(limit)
        return list(self.db.exec(statement).all())

    def update_trace_end_time(
        self,
        trace_id: str,
        span_id: str,
        end_time: datetime,
        duration_ms: Optional[float] = None,
    ) -> Optional[Trace]:
        """
        Update trace end time and duration

        Args:
            trace_id: Trace ID
            span_id: Span ID
            end_time: End timestamp
            duration_ms: Optional duration in milliseconds

        Returns:
            Updated Trace object or None if not found
        """
        statement = select(Trace).where(
            Trace.trace_id == trace_id,
            Trace.span_id == span_id,
        )
        trace = self.db.exec(statement).first()
        if trace:
            trace.end_time = end_time
            if duration_ms is not None:
                trace.duration_ms = str(duration_ms)
            elif trace.start_time and end_time:
                # Calculate duration if not provided
                trace.duration_ms = str(end_time - trace.start_time)

            self.db.add(trace)
            self.db.commit()
            self.db.refresh(trace)
            return trace

        return None

    def update_trace_status(
        self, trace_id: str, span_id: str, status: str
    ) -> Optional[Trace]:
        """
        Update trace status

        Args:
            trace_id: Trace ID
            span_id: Span ID
            status: New status

        Returns:
            Updated Trace object or None if not found
        """
        statement = select(Trace).where(
            Trace.trace_id == trace_id,
            Trace.span_id == span_id,
        )
        trace = self.db.exec(statement).first()

        if trace:
            trace.status = status
            self.db.add(trace)
            self.db.commit()
            self.db.refresh(trace)
            return trace

        return None

    def delete_old_traces(self, organization_id: str, older_than: datetime) -> int:
        """
        Delete traces older than specified timestamp

        Args:
            organization_id: Organization identifier
            older_than: Delete traces older than this timestamp

        Returns:
            Number of traces deleted
        """
        statement = select(Trace).where(
            Trace.organization_id == organization_id,
            Trace.start_time < older_than,
        )
        traces = self.db.exec(statement).all()
        count = len(traces)

        for trace in traces:
            self.db.delete(trace)

        self.db.commit()
        return count

    def get_trace_statistics(
        self,
        organization_id: str,
        service_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Get trace statistics for analysis

        Args:
            organization_id: Organization identifier
            service_name: Optional service filter
            start_time: Optional start time filter
            end_time: Optional end time filter

        Returns:
            Dictionary with trace statistics
        """
        statement = select(Trace).where(Trace.organization_id == organization_id)

        if service_name:
            statement = statement.where(Trace.service_name == service_name)
        if start_time:
            statement = statement.where(Trace.start_time >= start_time)
        if end_time:
            statement = statement.where(Trace.start_time <= end_time)

        traces = list(self.db.exec(statement).all())

        if not traces:
            return {
                "total_traces": 0,
                "unique_trace_ids": 0,
                "avg_duration_ms": 0,
                "status_distribution": {},
                "service_distribution": {},
            }

        unique_trace_ids = len(set(trace.trace_id for trace in traces))
        durations = [
            trace.duration_ms for trace in traces if trace.duration_ms is not None
        ]
        avg_duration = (
            sum([int(duration) for duration in durations]) / len(durations)
            if durations
            else 0
        )

        status_dist = {}
        service_dist = {}

        for trace in traces:
            status_dist[trace.status] = status_dist.get(trace.status, 0) + 1
            service_dist[trace.service_name] = (
                service_dist.get(trace.service_name, 0) + 1
            )

        return {
            "total_traces": len(traces),
            "unique_trace_ids": unique_trace_ids,
            "avg_duration_ms": avg_duration,
            "status_distribution": status_dist,
            "service_distribution": service_dist,
        }
