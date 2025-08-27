from typing import Optional
from sqlmodel import Session as DBSession, null, select
from app.models.sql_model import Organization


class OrganizationStore:
    """Class to handle organization operations"""

    def __init__(self, db_session: DBSession):
        self.db = db_session

    def get_organization(self, organization_id: str) -> Optional[Organization]:
        """
        Get organization by ID

        Args:
            organization_id: The organization identifier

        Returns:
            Organization object or None if not found
        """
        statement = select(Organization).where(
            Organization.id == organization_id,
            Organization.deleted_at == null(),
        )
        return self.db.exec(statement).first()

    def get_organization_by_name(self, name: str) -> Optional[Organization]:
        """
        Get organization by name

        Args:
            name: The organization name

        Returns:
            Organization object or None if not found
        """
        statement = select(Organization).where(
            Organization.name == name, Organization.deleted_at == null()
        )
        return self.db.exec(statement).first()
