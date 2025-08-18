"""
CPF (Brazilian tax ID) value object.
Immutable object that encapsulates CPF validation logic.
"""
import re
from typing import Any


class CPF:
    """
    CPF value object.
    Validates and formats Brazilian CPF numbers.
    """
    
    def __init__(self, value: str):
        if not value:
            raise ValueError("CPF cannot be empty")
        
        # Remove formatting characters
        clean_value = re.sub(r'[^0-9]', '', value)
        
        if not self._is_valid_cpf(clean_value):
            raise ValueError(f"Invalid CPF: {value}")
        
        self._value = clean_value

    @staticmethod
    def _is_valid_cpf(cpf: str) -> bool:
        """Validate CPF using the check digits algorithm"""
        if len(cpf) != 11:
            return False
        
        # Check if all digits are the same
        if len(set(cpf)) == 1:
            return False
        
        # Validate first check digit
        sum_digits = sum(int(cpf[i]) * (10 - i) for i in range(9))
        first_digit = (sum_digits * 10) % 11
        if first_digit == 10:
            first_digit = 0
        if first_digit != int(cpf[9]):
            return False
        
        # Validate second check digit
        sum_digits = sum(int(cpf[i]) * (11 - i) for i in range(10))
        second_digit = (sum_digits * 10) % 11
        if second_digit == 10:
            second_digit = 0
        if second_digit != int(cpf[10]):
            return False
        
        return True

    @property
    def value(self) -> str:
        """Get the unformatted CPF value"""
        return self._value

    @property
    def formatted(self) -> str:
        """Get the formatted CPF (XXX.XXX.XXX-XX)"""
        return f"{self._value[:3]}.{self._value[3:6]}.{self._value[6:9]}-{self._value[9:]}"

    def __str__(self) -> str:
        return self.formatted

    def __repr__(self) -> str:
        return f"CPF('{self.formatted}')"

    def __eq__(self, other: Any) -> bool:
        """CPFs are equal if they have the same value"""
        if not isinstance(other, CPF):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        """Hash based on value for use in sets and dicts"""
        return hash(self._value)