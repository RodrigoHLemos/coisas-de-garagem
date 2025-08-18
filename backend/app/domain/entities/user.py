"""
User entity following Domain-Driven Design.
Encapsulates user business logic and validation.
"""
from typing import Optional
from uuid import UUID
from enum import Enum
from datetime import datetime

from .base import DomainEntity
from ..value_objects.email import Email
from ..value_objects.cpf import CPF
from ..value_objects.phone import Phone
from ...shared.exceptions.domain import DomainValidationError


class UserRole(str, Enum):
    """User role enumeration"""
    BUYER = "buyer"
    SELLER = "seller"
    ADMIN = "admin"


class User(DomainEntity):
    """
    User domain entity.
    Represents a system user with authentication capabilities.
    """
    
    def __init__(
        self,
        email: Email,
        name: str,
        cpf: CPF,
        phone: Phone,
        role: UserRole = UserRole.BUYER,
        password_hash: Optional[str] = None,
        is_active: bool = True,
        is_verified: bool = False,
        id: Optional[UUID] = None
    ):
        super().__init__(id)
        self._email = email
        self._name = name
        self._cpf = cpf
        self._phone = phone
        self._role = role
        self._password_hash = password_hash
        self._is_active = is_active
        self._is_verified = is_verified
        self._last_login: Optional[datetime] = None
        self.validate()

    @property
    def email(self) -> Email:
        return self._email

    @property
    def name(self) -> str:
        return self._name

    @property
    def cpf(self) -> CPF:
        return self._cpf

    @property
    def phone(self) -> Phone:
        return self._phone

    @property
    def role(self) -> UserRole:
        return self._role

    @property
    def password_hash(self) -> Optional[str]:
        return self._password_hash

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def is_verified(self) -> bool:
        return self._is_verified

    @property
    def last_login(self) -> Optional[datetime]:
        return self._last_login

    def update_profile(
        self,
        name: Optional[str] = None,
        phone: Optional[Phone] = None
    ) -> None:
        """Update user profile information"""
        if name:
            self._name = name
        if phone:
            self._phone = phone
        self.update_timestamp()
        self.validate()

    def change_password(self, new_password_hash: str) -> None:
        """Change user password"""
        if not new_password_hash:
            raise DomainValidationError("Password hash cannot be empty")
        self._password_hash = new_password_hash
        self.update_timestamp()
        self.add_domain_event({"type": "PasswordChanged", "user_id": self.id})

    def activate(self) -> None:
        """Activate user account"""
        self._is_active = True
        self.update_timestamp()
        self.add_domain_event({"type": "UserActivated", "user_id": self.id})

    def deactivate(self) -> None:
        """Deactivate user account"""
        self._is_active = False
        self.update_timestamp()
        self.add_domain_event({"type": "UserDeactivated", "user_id": self.id})

    def verify_email(self) -> None:
        """Mark email as verified"""
        self._is_verified = True
        self.update_timestamp()
        self.add_domain_event({"type": "EmailVerified", "user_id": self.id})

    def update_last_login(self) -> None:
        """Update last login timestamp"""
        self._last_login = datetime.utcnow()
        self.update_timestamp()

    def promote_to_seller(self) -> None:
        """Promote user to seller role"""
        if self._role == UserRole.ADMIN:
            raise DomainValidationError("Admin users cannot be promoted to seller")
        self._role = UserRole.SELLER
        self.update_timestamp()
        self.add_domain_event({"type": "UserPromotedToSeller", "user_id": self.id})

    def can_sell(self) -> bool:
        """Check if user can sell products"""
        return self._role in [UserRole.SELLER, UserRole.ADMIN] and self._is_active

    def can_buy(self) -> bool:
        """Check if user can buy products"""
        return self._is_active

    def validate(self) -> None:
        """Validate user entity state"""
        if not self._name or len(self._name.strip()) < 3:
            raise DomainValidationError("Name must be at least 3 characters long")
        
        if len(self._name) > 100:
            raise DomainValidationError("Name cannot exceed 100 characters")
        
        if self._role not in UserRole:
            raise DomainValidationError(f"Invalid role: {self._role}")