from datetime import datetime
from typing import Optional, List
from sqlmodel import Session as DBSession, select
from app.models.enums import SessionStatus
from app.models.sql_model import Session


class SessionStore:
    """Class to handle session storage and retrieval using SQLModel"""

    def __init__(self, db_session: DBSession):
        self.db = db_session

    def get_session(self, token_jti: str) -> Optional[Session]:
        """
        Retrieve session by token JTI

        Args:
            token_jti: The JWT token identifier

        Returns:
            Session object or None if not found
        """
        statement = select(Session).where(Session.token_jti == token_jti)
        return self.db.exec(statement).first()

    def create_session(
        self,
        token_jti: str,
        organization_id: str,
        expires_at: datetime,
        ip_address: Optional[str] = None,
    ) -> Session:
        """
        Create a new session record

        Args:
            token_jti: The JWT token identifier
            organization_id: The organization identifier
            expires_at: When the session expires
            ip_address: Client IP address (optional)

        Returns:
            Created Session object
        """
        session = Session(
            token_jti=token_jti,
            organization_id=organization_id,
            expires_at=expires_at,
            ip_address=ip_address,
            last_used_at=datetime.now(),
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def update_session_last_used(self, token_jti: str) -> bool:
        """
        Update session's last_used_at timestamp

        Args:
            token_jti: The JWT token identifier

        Returns:
            True if updated successfully, False otherwise
        """
        statement = select(Session).where(Session.token_jti == token_jti)
        session = self.db.exec(statement).first()
        if session:
            session.last_used_at = datetime.now()
            self.db.add(session)
            self.db.commit()
            return True
        return False

    def deactivate_session(self, token_jti: str) -> bool:
        """
        Deactivate a session (set status to inactive)

        Args:
            token_jti: The JWT token identifier

        Returns:
            True if deactivated successfully, False otherwise
        """
        statement = select(Session).where(Session.token_jti == token_jti)
        session = self.db.exec(statement).first()
        if session:
            session.status = (
                SessionStatus.EXPIRED
            )  # You'll need to import SessionStatus
            self.db.add(session)
            self.db.commit()
            return True
        return False

    def delete_session(self, token_jti: str) -> bool:
        """
        Delete session record

        Args:
            token_jti: The JWT token identifier

        Returns:
            True if deleted successfully, False otherwise
        """
        statement = select(Session).where(Session.token_jti == token_jti)
        session = self.db.exec(statement).first()
        if session:
            self.db.delete(session)
            self.db.commit()
            return True
        return False

    def delete_expired_sessions(self) -> int:
        """
        Delete all expired sessions

        Returns:
            Number of sessions deleted
        """
        current_time = datetime.now()
        statement = select(Session).where(Session.expires_at < current_time)
        expired_sessions = self.db.exec(statement).all()
        count = len(expired_sessions)

        for session in expired_sessions:
            self.db.delete(session)

        self.db.commit()
        return count

    def get_organization_settings(
        self, organization_id: str
    ) -> List[Session]:
        """
        Get all active sessions for a specific organization

        Args:
            organization_id: The organization identifier

        Returns:
            List of active Session objects
        """
        current_time = datetime.now()
        statement = select(Session).where(
            Session.organization_id == organization_id,
            Session.status == SessionStatus.ACTIVE,
            Session.expires_at > current_time,
        )
        return list(self.db.exec(statement).all())

    def is_session_valid(self, token_jti: str) -> bool:
        """
        Check if session is valid (exists, active, not expired)

        Args:
            token_jti: The JWT token identifier

        Returns:
            True if session is valid, False otherwise
        """
        current_time = datetime.now()
        statement = select(Session).where(
            Session.token_jti == token_jti,
            Session.status == SessionStatus.ACTIVE,
            Session.expires_at > current_time,
        )
        return self.db.exec(statement).first() is not None
