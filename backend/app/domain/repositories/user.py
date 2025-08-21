"""
User repository interface.
Defines specific operations for user data access.
"""
from typing import Optional
from uuid import UUID

from .base import IRepository
from ..entities.user import User
from ..value_objects.email import Email
from ..value_objects.cpf import CPF


class IUserRepository(IRepository[User]):
    """
    User repository interface.
    Extends base repository with user-specific operations.
    """
    
    async def get_by_email(self, email: Email) -> Optional[User]:
        """Get user by email"""
        pass
    
    async def get_by_cpf(self, cpf: CPF) -> Optional[User]:
        """Get user by CPF"""
        pass
    
    async def email_exists(self, email: Email) -> bool:
        """Check if email already exists"""
        pass
    
    async def cpf_exists(self, cpf: CPF) -> bool:
        """Check if CPF already exists"""
        pass