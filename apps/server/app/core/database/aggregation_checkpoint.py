from datetime import datetime
from sqlmodel import Session, select
from typing import Optional
from app.utils.logging import create_logger
from app.utils.now import now

from app.models.sql_model import AggregationCheckpoint

logger = create_logger(__name__)


class AggregationCheckpointStore:
    def __init__(self, session: Session):
        self.session = session

    def _get_checkpoint(
        self, organization_id: str, field_name: str
    ) -> Optional[AggregationCheckpoint]:
        statement = select(AggregationCheckpoint).where(
            AggregationCheckpoint.organization_id == organization_id,
            AggregationCheckpoint.field_name == field_name,
        )
        result = self.session.exec(statement).first()
        logger.debug(f"Checkpoint result: {result}")
        return result

    def last_aggregated_at(self, organization_id: str, field_name: str) -> datetime:
        checkpoint = self._get_checkpoint(organization_id, field_name)

        if not checkpoint:
            create_checkpoint = self.create_checkpoint_if_missing(
                organization_id, field_name
            )
            return create_checkpoint.aggrigated_at

        logger.debug(f"Last aggregated at: {checkpoint.aggrigated_at}")
        return checkpoint.aggrigated_at

    def update_timestamp(
        self,
        organization_id: str,
        field_name: str,
        timestamp: Optional[datetime] = None,
    ) -> bool:
        logger.debug(f"Updating timestamp for {field_name}")

        # Use provided timestamp or current time
        update_time = timestamp if timestamp is not None else now()

        # Try to get existing checkpoint
        checkpoint = self._get_checkpoint(organization_id, field_name)

        if checkpoint:
            # Update existing checkpoint
            checkpoint.aggrigated_at = update_time
            self.session.add(checkpoint)
            self.session.commit()
        else:
            # Create new checkpoint if it doesn't exist
            checkpoint = AggregationCheckpoint(
                organization_id=organization_id,
                field_name=field_name,
                aggrigated_at=update_time,
            )
            self.session.add(checkpoint)
            self.session.commit()

        logger.debug(f"Updated timestamp for {field_name}")
        return True

    def create_checkpoint_if_missing(
        self, organization_id: str, field_name: str
    ) -> AggregationCheckpoint:
        checkpoint = self._get_checkpoint(organization_id, field_name)
        if checkpoint:
            return checkpoint
        checkpoint = AggregationCheckpoint(
            organization_id=organization_id, field_name=field_name, aggrigated_at=now()
        )
        self.session.add(checkpoint)
        self.session.commit()
        logger.debug(f"Created checkpoint: {checkpoint}")
        return checkpoint
