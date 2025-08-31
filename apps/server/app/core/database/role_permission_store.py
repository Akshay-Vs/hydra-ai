from typing import Dict, List
from typing_extensions import Optional
from sqlmodel import Session, select

from app.models.sql_model import Role, RolePermission, Permissions


class RolePermissionStore:
    """Class to handle role permissions using RolePermission model"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_role_permission(self, role_id: str, permission_id: str) -> Optional[Dict]:
        """
        Get a specific role permission

        Args:
            role_id: The role identifier
            permission_id: The permission identifier

        Returns:
            Dict with permission data or None if not found
        """
        statement = select(RolePermission).where(
            RolePermission.id == permission_id,
            RolePermission.role_id == role_id,
        )
        permission = self.db.exec(statement).first()
        return (
            {
                "id": permission.id,
                "role_id": permission.role_id,
                "action": permission.action,
                "created_at": permission.created_at,
            }
            if permission
            else None
        )

    def create_role_permission(
        self, role_id: str, action: Permissions
    ) -> RolePermission:
        """
        Create a new permission for a role

        Args:
            role_id: The role identifier
            action: The permission action

        Returns:
            Created RolePermission object
        """
        permission = RolePermission(
            role_id=role_id,
            action=action,
        )
        self.db.add(permission)
        self.db.commit()
        self.db.refresh(permission)
        return permission

    def delete_role_permission(self, role_id: str, permission_id: str) -> bool:
        """
        Delete a specific role permission

        Args:
            role_id: The role identifier
            permission_id: The permission ID to delete

        Returns:
            Boolean indicating if deletion was successful
        """
        statement = select(RolePermission).where(
            RolePermission.id == permission_id,
            RolePermission.role_id == role_id,
        )
        permission = self.db.exec(statement).first()
        if permission:
            self.db.delete(permission)
            self.db.commit()
            return True
        return False

    def get_role_permissions(self, role_id: str) -> List[Dict]:
        """
        Get all permissions for a role

        Args:
            role_id: The role identifier

        Returns:
            List of permission dictionaries
        """
        statement = select(RolePermission).where(
            RolePermission.role_id == role_id,
        )
        permissions = self.db.exec(statement).all()

        return [
            {
                "id": permission.id,
                "role_id": permission.role_id,
                "action": permission.action,
                "created_at": permission.created_at,
            }
            for permission in permissions
        ]

    def bulk_create_permissions(
        self, role_id: str, actions: List[Permissions]
    ) -> List[RolePermission]:
        """
        Create multiple permissions for a role

        Args:
            role_id: The role identifier
            actions: List of permission actions

        Returns:
            List of created RolePermission objects
        """
        permissions = []
        for action in actions:
            permission = RolePermission(
                role_id=role_id,
                action=action,
            )
            self.db.add(permission)
            permissions.append(permission)

        self.db.commit()
        for permission in permissions:
            self.db.refresh(permission)
        return permissions

    def delete_all_role_permissions(self, role_id: str) -> int:
        """
        Delete all permissions for a role

        Args:
            role_id: The role identifier

        Returns:
            Number of permissions deleted
        """
        statement = select(RolePermission).where(
            RolePermission.role_id == role_id,
        )
        permissions = self.db.exec(statement).all()
        count = 0

        for permission in permissions:
            self.db.delete(permission)
            count += 1

        self.db.commit()
        return count

    def has_permission(self, role_id: str, action: Permissions) -> bool:
        """
        Check if a role has a specific permission

        Args:
            role_id: The role identifier
            action: The permission action to check

        Returns:
            True if role has the permission, False otherwise
        """
        statement = select(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.action == action,
        )
        permission = self.db.exec(statement).first()
        return permission is not None

    def replace_role_permissions(
        self, role_id: str, actions: List[Permissions]
    ) -> List[RolePermission]:
        """
        Replace all permissions for a role with new ones

        Args:
            role_id: The role identifier
            actions: List of new permission actions

        Returns:
            List of created RolePermission objects
        """
        # Delete all existing permissions
        self.delete_all_role_permissions(role_id)

        # Create new permissions
        return self.bulk_create_permissions(role_id, actions)

    def get_roles_with_permission(
        self, organization_id: str, action: Permissions
    ) -> List[Dict]:
        """
        Get all roles in an organization that have a specific permission

        Args:
            organization_id: The organization identifier
            action: The permission action to search for

        Returns:
            List of role dictionaries that have the permission
        """
        statement = (
            select(Role)
            .join(RolePermission)
            .where(
                Role.organization_id == organization_id,
                RolePermission.action == action,
            )
        )
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
