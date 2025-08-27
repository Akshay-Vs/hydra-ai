from datetime import datetime
from sqlmodel import Session, select
from app.models.sql_model import RevokedToken


class RevokedTokenStore:
    """Class to handle revoked token storage and retrieval"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def revoke_token(
        self, token_jti: str, organization_id: str, expires_at: datetime
    ) -> RevokedToken:
        """
        Add token to revoked tokens list

        Args:
            token_jti: The JWT token identifier
            organization_id: The organization identifier
            expires_at: When the token expires

        Returns:
            Created RevokedToken object
        """
        revoked_token = RevokedToken(
            token_jti=token_jti, organization_id=organization_id, expires_at=expires_at
        )
        self.db.add(revoked_token)
        self.db.commit()
        self.db.refresh(revoked_token)
        return revoked_token

    def is_token_revoked(self, token_jti: str) -> bool:
        """
        Check if token is revoked

        Args:
            token_jti: The JWT token identifier

        Returns:
            True if token is revoked, False otherwise
        """
        statement = select(RevokedToken).where(RevokedToken.token_jti == token_jti)
        return self.db.exec(statement).first() is not None

    def cleanup_expired_revoked_tokens(self) -> int:
        """
        Clean up expired revoked tokens

        Returns:
            Number of tokens cleaned up
        """
        current_time = datetime.now()
        statement = select(RevokedToken).where(RevokedToken.expires_at < current_time)
        expired_tokens = self.db.exec(statement).all()
        count = len(expired_tokens)

        for token in expired_tokens:
            self.db.delete(token)

        self.db.commit()
        return count
