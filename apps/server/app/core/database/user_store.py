from sqlmodel import Session, select

from app.models.sql_model import OrganizationMember, Role, RolePermission, User


class UserStore:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_user_by_clerk_id(self, clerk_id: str):
        statement = select(User).where(User.clerk_id == clerk_id)
        user = self.db.exec(statement).first()
        return user

    def get_user_roles(self, user_id: str, org_id: str):
        # select organization member by user_id, select roles table by roles_id in organization member
        statement = (
            select(OrganizationMember, Role)
            .join(Role)
            .where(
                OrganizationMember.user_id == user_id,
                OrganizationMember.organization_id == org_id,
            )
        )

        results = self.db.exec(statement).all()
        if results:
            return [role.name for org_member, role in results]
        else:
            return []

    def get_user_role_permissions(self, user_id: str, org_id: str):
        # Get user roles and their permissions in a single query
        statement = (
            select(OrganizationMember, Role, RolePermission)
            .select_from(OrganizationMember)
            .join(Role)
            .join(RolePermission)
            .where(
                OrganizationMember.user_id == user_id,
                OrganizationMember.organization_id == org_id,
            )
        )
        results = self.db.exec(statement).all()
        if results:
            # Extract all actions and remove duplicates using set
            actions = {
                role_permission.action for org_member, role, role_permission in results
            }
            return list(actions)
        else:
            return []
