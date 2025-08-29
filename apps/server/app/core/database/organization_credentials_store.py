from datetime import datetime
from typing import Dict, List
from typing_extensions import Optional
from sqlmodel import Session, false, null, or_, select, true

from app.models.sql_model import OrganizationCredential
from app.utils.hash_secret import hash_secret


class OrganizationCredentialsStore:
    """Class to handle organization credentials using OrganizationCredential model"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_organization_credential(
        self, organization_id: str, credential_id: str
    ) -> Optional[Dict]:
        """
        Get active organization credentials

        Args:
            organization_id: The organization identifier

        Returns:
            Dict with credentials or None if not found
        """
        current_time = datetime.now()
        statement = select(OrganizationCredential).where(
            OrganizationCredential.id == credential_id,
            OrganizationCredential.organization_id == organization_id,
            OrganizationCredential.is_active == true(),
            # Check if not expired
            or_(
                OrganizationCredential.expires_at == null(),
                OrganizationCredential.expires_at > current_time
                if OrganizationCredential.expires_at is not None
                else true(),
            ),
        )
        credential = self.db.exec(statement).first()
        return (
            {
                "id": credential.id,
                "organization_id": credential.organization_id,
                "client_secret": credential.secret_hash,
                "expires_at": credential.expires_at,
                "is_active": credential.is_active,
                "created_at": credential.created_at,
                "updated_at": credential.updated_at,
            }
            if credential
            else None
        )

    def create_organization_credentials(
        self,
        organization_id: str,
        secret_hash: str,
        expires_at: Optional[datetime] = None,
    ) -> OrganizationCredential:
        """
        Create credentials for an organization

        Args:
            organization_id: The organization identifier
            secret_hash: Hashed secret
            expires_at: Optional expiration date

        Returns:
            Created OrganizationCredential object
        """
        credential = OrganizationCredential(
            organization_id=organization_id,
            secret_hash=secret_hash,
            expires_at=expires_at,
        )
        self.db.add(credential)
        self.db.commit()
        self.db.refresh(credential)
        return credential

    def update_credential_status(self, credential_id: str, is_active: bool) -> bool:
        """
        Update credential active status

        Args:
            credential_id: The credential ID
            is_active: New active status

        Returns:
            True if updated successfully
        """
        statement = select(OrganizationCredential).where(
            OrganizationCredential.id == credential_id
        )
        credential = self.db.exec(statement).first()
        if credential:
            credential.is_active = is_active
            self.db.add(credential)
            self.db.commit()
            return True
        return False

    def deactivate_organization_credential(
        self, organization_id: str, credential_id: str
    ) -> bool:
        """
        Deactivate specified credentials from an organization

        Args:
            organization_id: The organization identifier
            credential_id: The credential ID to deactivate

        Returns:
            Boolean indicating if deactivation was successful
        """
        statement = select(OrganizationCredential).where(
            OrganizationCredential.organization_id == organization_id,
            OrganizationCredential.id == credential_id,
            OrganizationCredential.is_active == true(),
        )
        credential = self.db.exec(statement).first()
        if credential:
            credential.is_active = False
            self.db.add(credential)
            self.db.commit()
            return True
        return False

    def deactivate_all_organization_credentials(self, organization_id: str) -> int:
        """
        Deactivate all credentials for an organization

        Args:
            organization_id: The organization identifier

        Returns:
            Number of credentials deactivated
        """
        statement = select(OrganizationCredential).where(
            OrganizationCredential.organization_id == organization_id,
            OrganizationCredential.is_active is True,
        )
        credentials = self.db.exec(statement).all()
        count = 0

        for credential in credentials:
            credential.is_active = False
            self.db.add(credential)
            count += 1

        self.db.commit()
        return count

    def rotate_organization_secret(
        self,
        organization_id: str,
        new_secret_hash: str,
        expires_at: Optional[datetime] = None,
    ) -> OrganizationCredential:
        """
        Rotate organization secret (deactivate old, create new)

        Args:
            organization_id: The organization identifier
            new_secret_hash: New hashed secret
            expires_at: Optional expiration date for new credential

        Returns:
            New OrganizationCredential object
        """
        # Deactivate existing credentials
        self.deactivate_all_organization_credentials(organization_id)

        # Create new credential
        return self.create_organization_credentials(
            organization_id=organization_id,
            secret_hash=new_secret_hash,
            expires_at=expires_at,
        )

    def get_all_organization_credentials(
        self, organization_id: str, include_inactive: bool = False
    ) -> Optional[List[Dict]]:
        """
        Get all credentials for an organization

        Args:
            organization_id: The organization identifier
            include_inactive: Whether to include inactive credentials

        Returns:
            List of OrganizationCredential objects
        """
        current_time = datetime.now()
        statement = select(OrganizationCredential).where(
            OrganizationCredential.organization_id == organization_id,
            OrganizationCredential.is_active == true()
            if not include_inactive
            else false(),
            # Check if not expired
            or_(
                OrganizationCredential.expires_at == null(),
                OrganizationCredential.expires_at > current_time
                if OrganizationCredential.expires_at is not None
                else true(),
            ),
        )
        credential = self.db.exec(statement).all()

        if not credential:
            return None

        return [
            {
                "id": cred.id,
                "organization_id": cred.organization_id,
                "expires_at": cred.expires_at,
                "is_active": cred.is_active,
                "created_at": cred.created_at,
                "updated_at": cred.updated_at,
            }
            for cred in credential
        ]

    def cleanup_expired_credentials(self) -> int:
        """
        Deactivate expired credentials

        Returns:
            Number of credentials deactivated
        """
        current_time = datetime.now()
        statement = select(OrganizationCredential).where(
            (
                OrganizationCredential.expires_at
                == null() | OrganizationCredential.expires_at
                < current_time
            ),
            OrganizationCredential.is_active is True,
        )
        expired_credentials = self.db.exec(statement).all()
        count = 0

        for credential in expired_credentials:
            credential.is_active = False
            self.db.add(credential)
            count += 1

        self.db.commit()
        return count

    def verify_secret(
        self, organization_id: str, credential_id: str, secret: str
    ) -> bool:
        """
        Verify a secret against stored credentials

        Args:
            organization_id: The organization identifier
            secret: Plain text secret to verify

        Returns:
            True if secret is valid, False otherwise
        """
        credentials = self.get_organization_credential(organization_id, credential_id)
        if not credentials:
            return False

        hashed_input = hash_secret(secret)
        return credentials["client_secret"] == hashed_input
