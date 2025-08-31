from typing import Dict, List
from typing_extensions import Optional
from sqlmodel import Session, false, select, true

from app.models.sql_model import Role


class RoleStore:
    """Class to handle role operations using Role model"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_role(self, organization_id: str, role_id: str) -> Optional[Dict]:
        """
        Get a specific role by ID for an organization

        Args:
            organization_id: The organization identifier
            role_id: The role identifier

        Returns:
            Dict with role data or None if not found
        """
        statement = select(Role).where(
            Role.id == role_id,
            Role.organization_id == organization_id,
        )
        role = self.db.exec(statement).first()
        return (
            {
                "id": role.id,
                "organization_id": role.organization_id,
                "name": role.name,
                "description": role.description,
                "is_default": role.is_default,
                "is_system": role.is_system,
                "level": role.level,
            }
            if role
            else None
        )

    def create_role(
        self,
        organization_id: str,
        name: str,
        description: Optional[str] = None,
        is_default: bool = False,
        is_system: bool = False,
        level: int = 0,
    ) -> Role:
        """
        Create a new role for an organization

        Args:
            organization_id: The organization identifier
            name: Role name
            description: Optional role description
            is_default: Whether this is a default role
            is_system: Whether this is a system role
            level: Role level

        Returns:
            Created Role object
        """
        role = Role(
            organization_id=organization_id,
            name=name,
            description=description,
            is_default=is_default,
            is_system=is_system,
            level=level,
        )
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    def update_role(
        self,
        role_id: str,
        organization_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_default: Optional[bool] = None,
        level: Optional[int] = None,
    ) -> bool:
        """
        Update role information

        Args:
            role_id: The role ID
            organization_id: The organization identifier
            name: New role name
            description: New role description
            is_default: New default status
            level: New role level

        Returns:
            True if updated successfully
        """
        statement = select(Role).where(
            Role.id == role_id,
            Role.organization_id == organization_id,
        )
        role = self.db.exec(statement).first()
        if role:
            if name is not None:
                role.name = name
            if description is not None:
                role.description = description
            if is_default is not None:
                role.is_default = is_default
            if level is not None:
                role.level = level

            self.db.add(role)
            self.db.commit()
            return True
        return False

    def delete_role(self, organization_id: str, role_id: str) -> bool:
        """
        Delete a role (only if it's not a system role)

        Args:
            organization_id: The organization identifier
            role_id: The role ID to delete

        Returns:
            Boolean indicating if deletion was successful
        """
        statement = select(Role).where(
            Role.id == role_id,
            Role.organization_id == organization_id,
            Role.is_system == false(),
        )
        role = self.db.exec(statement).first()
        if role:
            self.db.delete(role)
            self.db.commit()
            return True
        return False

    def get_all_organization_roles(
        self, organization_id: str, include_system: bool = True
    ) -> List[Dict]:
        """
        Get all roles for an organization

        Args:
            organization_id: The organization identifier
            include_system: Whether to include system roles

        Returns:
            List of role dictionaries
        """
        statement = select(Role).where(
            Role.organization_id == organization_id,
        )

        if not include_system:
            statement = statement.where(Role.is_system == false())

        roles = self.db.exec(statement).all()

        return [
            {
                "id": role.id,
                "organization_id": role.organization_id,
                "name": role.name,
                "description": role.description,
                "is_default": role.is_default,
                "is_system": role.is_system,
                "level": role.level,
            }
            for role in roles
        ]

    def get_default_role(self, organization_id: str) -> Optional[Dict]:
        """
        Get the default role for an organization

        Args:
            organization_id: The organization identifier

        Returns:
            Dict with default role data or None if not found
        """
        statement = select(Role).where(
            Role.organization_id == organization_id,
            Role.is_default == true(),
        )
        role = self.db.exec(statement).first()
        return (
            {
                "id": role.id,
                "organization_id": role.organization_id,
                "name": role.name,
                "description": role.description,
                "is_default": role.is_default,
                "is_system": role.is_system,
                "level": role.level,
            }
            if role
            else None
        )

    def set_default_role(self, organization_id: str, role_id: str) -> bool:
        """
        Set a role as the default role for an organization
        (This will unset any existing default role)

        Args:
            organization_id: The organization identifier
            role_id: The role ID to set as default

        Returns:
            True if set successfully
        """
        # First, unset any existing default roles
        statement = select(Role).where(
            Role.organization_id == organization_id,
            Role.is_default == true(),
        )
        existing_defaults = self.db.exec(statement).all()
        for role in existing_defaults:
            role.is_default = False
            self.db.add(role)

        # Set the new default role
        statement = select(Role).where(
            Role.id == role_id,
            Role.organization_id == organization_id,
        )
        role = self.db.exec(statement).first()
        if role:
            role.is_default = True
            self.db.add(role)
            self.db.commit()
            return True
        return False
