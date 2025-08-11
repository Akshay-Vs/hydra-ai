from app.core.auth.user_session import UserSession


class PermissionChecker:
    """Utility class for checking user permissions"""

    @staticmethod
    def has_permission(user_session: UserSession, required_permission: str) -> bool:
        """Check if user has a specific permission"""
        return required_permission in user_session.permissions

    @staticmethod
    def has_role(user_session: UserSession, required_role: str) -> bool:
        """Check if user has a specific role"""
        return required_role in user_session.roles

    @staticmethod
    def can_access_org(user_session: UserSession, org_id: str) -> bool:
        """Check if user can access a specific organization"""
        return user_session.org_id == org_id

    @staticmethod
    def is_admin(user_session: UserSession) -> bool:
        """Check if user has admin privileges"""
        return "admin" in user_session.roles or "super_admin" in user_session.roles
