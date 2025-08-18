"""
Email value object following Domain-Driven Design.
Immutable object that encapsulates email validation logic.
"""
import re
from typing import Any


class Email:
    """
    Email value object.
    Ensures email is always in a valid state.
    """
    
    EMAIL_REGEX = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    def __init__(self, value: str):
        if not value:
            raise ValueError("Email cannot be empty")
        
        value = value.strip().lower()
        
        if not self.EMAIL_REGEX.match(value):
            raise ValueError(f"Invalid email format: {value}")
        
        if len(value) > 255:
            raise ValueError("Email cannot exceed 255 characters")
        
        self._value = value

    @property
    def value(self) -> str:
        """Get the email value"""
        return self._value

    @property
    def domain(self) -> str:
        """Get the email domain"""
        return self._value.split('@')[1]

    @property
    def local_part(self) -> str:
        """Get the local part of the email"""
        return self._value.split('@')[0]

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"Email('{self._value}')"

    def __eq__(self, other: Any) -> bool:
        """Emails are equal if they have the same value"""
        if not isinstance(other, Email):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        """Hash based on value for use in sets and dicts"""
        return hash(self._value)