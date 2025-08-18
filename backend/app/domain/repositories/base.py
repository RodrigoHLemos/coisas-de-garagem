"""
Base repository interface following Repository pattern.
Defines the contract for all repository implementations.
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Any
from uuid import UUID

from ..entities.base import DomainEntity

T = TypeVar('T', bound=DomainEntity)


class IRepository(ABC, Generic[T]):
    """
    Base repository interface.
    Follows the Repository pattern to abstract data access.
    """
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create a new entity"""
        pass
    
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[T]:
        """Get entity by ID"""
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update an existing entity"""
        pass
    
    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        """Delete an entity by ID"""
        pass
    
    @abstractmethod
    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters: Any
    ) -> List[T]:
        """List entities with pagination and filters"""
        pass
    
    @abstractmethod
    async def count(self, **filters: Any) -> int:
        """Count entities matching filters"""
        pass
    
    @abstractmethod
    async def exists(self, id: UUID) -> bool:
        """Check if entity exists"""
        pass