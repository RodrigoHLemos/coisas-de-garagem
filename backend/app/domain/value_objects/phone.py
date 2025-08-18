"""
Phone number value object.
Immutable object that encapsulates phone validation logic.
"""
import re
from typing import Any, Optional


class Phone:
    """
    Phone value object.
    Validates and formats Brazilian phone numbers.
    """
    
    def __init__(self, value: str):
        if not value:
            raise ValueError("Phone cannot be empty")
        
        # Remove formatting characters
        clean_value = re.sub(r'[^0-9]', '', value)
        
        if not self._is_valid_phone(clean_value):
            raise ValueError(f"Invalid phone number: {value}")
        
        self._value = clean_value

    @staticmethod
    def _is_valid_phone(phone: str) -> bool:
        """Validate Brazilian phone number"""
        # Check if it's a valid Brazilian phone number
        # Format: 11 digits for mobile (with 9) or 10 digits for landline
        if len(phone) not in [10, 11]:
            return False
        
        # Check area code (first 2 digits)
        area_code = int(phone[:2])
        valid_area_codes = [
            11, 12, 13, 14, 15, 16, 17, 18, 19,  # São Paulo
            21, 22, 24,  # Rio de Janeiro
            27, 28,  # Espírito Santo
            31, 32, 33, 34, 35, 37, 38,  # Minas Gerais
            41, 42, 43, 44, 45, 46,  # Paraná
            47, 48, 49,  # Santa Catarina
            51, 53, 54, 55,  # Rio Grande do Sul
            61,  # Distrito Federal
            62, 64,  # Goiás
            63,  # Tocantins
            65, 66,  # Mato Grosso
            67,  # Mato Grosso do Sul
            68,  # Acre
            69,  # Rondônia
            71, 73, 74, 75, 77,  # Bahia
            79,  # Sergipe
            81, 87,  # Pernambuco
            82,  # Alagoas
            83,  # Paraíba
            84,  # Rio Grande do Norte
            85, 88,  # Ceará
            86, 89,  # Piauí
            91, 93, 94,  # Pará
            92, 97,  # Amazonas
            95,  # Roraima
            96,  # Amapá
            98, 99,  # Maranhão
        ]
        
        if area_code not in valid_area_codes:
            return False
        
        # Check if mobile number starts with 9 (for 11 digits)
        if len(phone) == 11 and phone[2] != '9':
            return False
        
        return True

    @property
    def value(self) -> str:
        """Get the unformatted phone value"""
        return self._value

    @property
    def formatted(self) -> str:
        """Get the formatted phone number"""
        if len(self._value) == 11:
            # Mobile: (XX) 9XXXX-XXXX
            return f"({self._value[:2]}) {self._value[2:7]}-{self._value[7:]}"
        else:
            # Landline: (XX) XXXX-XXXX
            return f"({self._value[:2]}) {self._value[2:6]}-{self._value[6:]}"

    @property
    def area_code(self) -> str:
        """Get the area code"""
        return self._value[:2]

    @property
    def is_mobile(self) -> bool:
        """Check if it's a mobile number"""
        return len(self._value) == 11

    @property
    def whatsapp_link(self) -> str:
        """Generate WhatsApp link"""
        return f"https://wa.me/55{self._value}"

    def __str__(self) -> str:
        return self.formatted

    def __repr__(self) -> str:
        return f"Phone('{self.formatted}')"

    def __eq__(self, other: Any) -> bool:
        """Phones are equal if they have the same value"""
        if not isinstance(other, Phone):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        """Hash based on value for use in sets and dicts"""
        return hash(self._value)