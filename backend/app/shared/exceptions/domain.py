"""
Domain exceptions following Single Responsibility Principle.
Each exception class has a specific purpose in the domain layer.
"""


class DomainException(Exception):
    """Base exception for all domain errors"""
    def __init__(self, message: str, code: str = "DOMAIN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class DomainValidationError(DomainException):
    """Raised when domain validation fails"""
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")


class EntityNotFoundError(DomainException):
    """Raised when an entity is not found"""
    def __init__(self, entity_name: str, entity_id: str):
        message = f"{entity_name} with id {entity_id} not found"
        super().__init__(message, "ENTITY_NOT_FOUND")


class BusinessRuleViolationError(DomainException):
    """Raised when a business rule is violated"""
    def __init__(self, message: str):
        super().__init__(message, "BUSINESS_RULE_VIOLATION")


class UnauthorizedError(DomainException):
    """Raised when user is not authorized to perform an action"""
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(message, "UNAUTHORIZED")


class ConflictError(DomainException):
    """Raised when there's a conflict with existing data"""
    def __init__(self, message: str):
        super().__init__(message, "CONFLICT")