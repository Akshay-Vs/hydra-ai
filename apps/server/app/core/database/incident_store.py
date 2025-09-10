from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlmodel import Session, select, desc

from app.models.enums import SeverityEnum, StatusEnum
from app.models.sql_model import Incident


class IncidentStore:
    """Class to handle incident operations using Incident model"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def create_incident(
        self,
        incident: Incident,
        organization_id: str,
    ) -> Incident:
        """
        Create a new incident

        Args:
            service_name: Name of the affected service
            severity: Incident severity
            title: Incident title
            organization_id: Organization identifier
            description: Optional description
            error_signature: Optional error signature for grouping
            embedding: Optional vector embedding
            context_data: Optional context data
            assigned_agent_id: Optional assigned agent ID
            confidence_score: Optional confidence score
            timestamp: Optional timestamp (defaults to now)

        Returns:
            Created Incident object
        """
        incident = Incident(
            service_name=incident.service_name,
            service_version=incident.service_version,
            severity=incident.severity,
            title=incident.title,
            organization_id=organization_id,
            description=incident.description,
            error_signature=incident.error_signature,
            embedding=incident.embedding,
            context_data=incident.context_data,
            assigned_agent_id=incident.assigned_agent_id,
            confidence_score=incident.confidence_score,
            timestamp=incident.timestamp or datetime.now(),
        )
        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)
        return incident

    def get_incident(self, incident_id: str) -> Optional[Incident]:
        """Get incident by ID"""
        return self.db.get(Incident, incident_id)

    def get_open_incidents(
        self,
        organization_id: str,
        service_name: Optional[str] = None,
        severity: Optional[SeverityEnum] = None,
        limit: int = 100,
    ) -> List[Incident]:
        """
        Get open incidents

        Args:
            organization_id: Organization identifier
            service_name: Optional service filter
            severity: Optional severity filter
            limit: Maximum number of records

        Returns:
            List of open Incident objects
        """
        statement = select(Incident).where(
            Incident.organization_id == organization_id,
            Incident.status == StatusEnum.OPEN,
        )

        if service_name:
            statement = statement.where(Incident.service_name == service_name)
        if severity:
            statement = statement.where(Incident.severity == severity)

        statement = statement.order_by(desc(Incident.timestamp)).limit(limit)
        return list(self.db.exec(statement).all())

    def update_incident_status(
        self,
        incident_id: str,
        status: StatusEnum,
        resolution_data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Update incident status

        Args:
            incident_id: Incident ID
            status: New status
            resolution_data: Optional resolution data

        Returns:
            True if updated successfully
        """
        incident = self.db.get(Incident, incident_id)
        if incident:
            old_status = incident.status
            incident.status = status

            if resolution_data:
                incident.resolution_data = resolution_data

            # Calculate resolution time if closing
            if old_status == StatusEnum.OPEN and status in [
                StatusEnum.RESOLVED,
                StatusEnum.CLOSED,
            ]:
                resolution_time = (datetime.now() - incident.timestamp).total_seconds()
                incident.resolution_time_seconds = int(resolution_time)

            self.db.add(incident)
            self.db.commit()
            return True
        return False

    def assign_incident_to_agent(self, incident_id: str, agent_id: str) -> bool:
        """
        Assign incident to an agent

        Args:
            incident_id: Incident ID
            agent_id: Agent ID

        Returns:
            True if assigned successfully
        """
        incident = self.db.get(Incident, incident_id)
        if incident:
            incident.assigned_agent_id = agent_id
            self.db.add(incident)
            self.db.commit()
            return True
        return False

    def get_similar_incidents(
        self,
        error_signature: str,
        organization_id: str,
        exclude_incident_id: Optional[str] = None,
        limit: int = 5,
    ) -> List[Incident]:
        """
        Get incidents with similar error signatures

        Args:
            error_signature: Error signature to match
            organization_id: Organization identifier
            exclude_incident_id: Optional incident ID to exclude
            limit: Maximum number of records

        Returns:
            List of similar Incident objects
        """
        statement = select(Incident).where(
            Incident.organization_id == organization_id,
            Incident.error_signature == error_signature,
        )

        if exclude_incident_id:
            statement = statement.where(Incident.incident_id != exclude_incident_id)

        statement = statement.order_by(desc(Incident.timestamp)).limit(limit)
        return list(self.db.exec(statement).all())

    def get_incident_statistics(
        self, organization_id: str, days: int = 30
    ) -> Dict[str, Any]:
        """
        Get incident statistics for the organization

        Args:
            organization_id: Organization identifier
            days: Number of days to look back

        Returns:
            Dictionary with incident statistics
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        statement = select(Incident).where(
            Incident.organization_id == organization_id,
            Incident.timestamp >= cutoff_date,
        )
        incidents = list(self.db.exec(statement).all())

        total_incidents = len(incidents)
        open_incidents = len([i for i in incidents if i.status == StatusEnum.OPEN])
        resolved_incidents = len(
            [i for i in incidents if i.status == StatusEnum.RESOLVED]
        )
        closed_incidents = len([i for i in incidents if i.status == StatusEnum.CLOSED])

        # Calculate average resolution time for resolved/closed incidents
        resolved_times = [
            i.resolution_time_seconds
            for i in incidents
            if i.resolution_time_seconds is not None
            and i.status in [StatusEnum.RESOLVED, StatusEnum.CLOSED]
        ]
        avg_resolution_time = (
            sum(resolved_times) / len(resolved_times) if resolved_times else 0
        )

        # Group by severity
        severity_counts = {}
        for incident in incidents:
            severity_counts[incident.severity.value] = (
                severity_counts.get(incident.severity.value, 0) + 1
            )

        return {
            "total_incidents": total_incidents,
            "open_incidents": open_incidents,
            "resolved_incidents": resolved_incidents,
            "closed_incidents": closed_incidents,
            "avg_resolution_time_seconds": avg_resolution_time,
            "severity_breakdown": severity_counts,
        }

    def auto_resolve_incident(
        self, incident_id: str, root_cause: str, resolution_data: Dict[str, Any]
    ) -> bool:
        """
        Auto-resolve an incident

        Args:
            incident_id: Incident ID
            root_cause: Root cause description
            resolution_data: Resolution data

        Returns:
            True if resolved successfully
        """
        incident = self.db.get(Incident, incident_id)
        if incident:
            incident.status = StatusEnum.RESOLVED
            incident.root_cause = root_cause
            incident.resolution_data = resolution_data
            incident.auto_resolved = True

            # Calculate resolution time
            resolution_time = (datetime.now() - incident.timestamp).total_seconds()
            incident.resolution_time_seconds = int(resolution_time)

            self.db.add(incident)
            self.db.commit()
            return True
        return False
