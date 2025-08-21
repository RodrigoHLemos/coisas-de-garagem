"""
Entidade base seguindo princípios de Domain-Driven Design.
Todas as entidades de domínio herdam desta classe base.
"""
from datetime import datetime
from typing import Optional, Any
from uuid import UUID, uuid4
from abc import ABC, abstractmethod


class DomainEntity(ABC):
    """
    Classe base abstrata para todas as entidades de domínio.
    Segue o padrão Entity do DDD.
    """
    
    def __init__(self, id: Optional[UUID] = None):
        self._id = id or uuid4()
        self._created_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()
        self._events: list = []

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def update_timestamp(self) -> None:
        """Atualizar o timestamp da entidade"""
        self._updated_at = datetime.utcnow()

    def add_domain_event(self, event: Any) -> None:
        """Adicionar um evento de domínio para ser despachado depois"""
        self._events.append(event)

    def clear_events(self) -> None:
        """Limpar todos os eventos de domínio"""
        self._events.clear()

    @property
    def domain_events(self) -> list:
        """Obter todos os eventos de domínio"""
        return self._events.copy()

    def __eq__(self, other: object) -> bool:
        """Entidades são iguais se têm o mesmo ID"""
        if not isinstance(other, DomainEntity):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        """Hash baseado no ID para uso em sets e dicionários"""
        return hash(self._id)

    @abstractmethod
    def validate(self) -> None:
        """
        Validar o estado da entidade.
        Deve lançar ValidationError se inválido.
        """
        pass