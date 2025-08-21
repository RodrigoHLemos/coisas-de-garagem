"""
Money value object following Domain-Driven Design.
Immutable object that encapsulates monetary values and operations.
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Union


class Money:
    """
    Money value object.
    Handles monetary values with proper precision and currency.
    """
    
    SUPPORTED_CURRENCIES = ["BRL", "USD", "EUR"]
    
    def __init__(self, amount: Union[Decimal, float, str, int], currency: str = "BRL"):
        if currency not in self.SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported currency: {currency}. Supported: {self.SUPPORTED_CURRENCIES}")
        
        try:
            # Convert to Decimal for precision
            decimal_amount = Decimal(str(amount))
            # Round to 2 decimal places
            self._amount = decimal_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid amount: {amount}") from e
        
        if self._amount < 0:
            raise ValueError("Money amount cannot be negative")
        
        self._currency = currency

    @property
    def amount(self) -> Decimal:
        """Get the monetary amount"""
        return self._amount

    @property
    def currency(self) -> str:
        """Get the currency code"""
        return self._currency

    @property
    def formatted(self) -> str:
        """Get formatted money string"""
        if self._currency == "BRL":
            return f"R$ {self._amount:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
        elif self._currency == "USD":
            return f"$ {self._amount:,.2f}"
        elif self._currency == "EUR":
            return f"€ {self._amount:,.2f}"
        return f"{self._currency} {self._amount:,.2f}"

    def add(self, other: 'Money') -> 'Money':
        """Add two money values"""
        if not isinstance(other, Money):
            raise TypeError("Can only add Money to Money")
        
        if self._currency != other._currency:
            raise ValueError(f"Cannot add different currencies: {self._currency} and {other._currency}")
        
        return Money(self._amount + other._amount, self._currency)

    def subtract(self, other: 'Money') -> 'Money':
        """Subtract two money values"""
        if not isinstance(other, Money):
            raise TypeError("Can only subtract Money from Money")
        
        if self._currency != other._currency:
            raise ValueError(f"Cannot subtract different currencies: {self._currency} and {other._currency}")
        
        result = self._amount - other._amount
        if result < 0:
            raise ValueError("Subtraction would result in negative money")
        
        return Money(result, self._currency)

    def multiply(self, factor: Union[Decimal, float, int]) -> 'Money':
        """Multiply money by a factor"""
        try:
            decimal_factor = Decimal(str(factor))
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid multiplication factor: {factor}") from e
        
        if decimal_factor < 0:
            raise ValueError("Cannot multiply money by negative factor")
        
        return Money(self._amount * decimal_factor, self._currency)

    def apply_discount(self, percentage: Union[Decimal, float]) -> 'Money':
        """Apply a percentage discount"""
        if percentage < 0 or percentage > 100:
            raise ValueError("Discount percentage must be between 0 and 100")
        
        discount_factor = Decimal(str(1 - percentage / 100))
        return Money(self._amount * discount_factor, self._currency)

    def is_zero(self) -> bool:
        """Check if money amount is zero"""
        return self._amount == 0

    def __str__(self) -> str:
        return self.formatted

    def __repr__(self) -> str:
        return f"Money({self._amount}, '{self._currency}')"

    def __eq__(self, other: Any) -> bool:
        """Money values are equal if amount and currency match"""
        if not isinstance(other, Money):
            return False
        return self._amount == other._amount and self._currency == other._currency

    def __lt__(self, other: 'Money') -> bool:
        """Less than comparison"""
        if not isinstance(other, Money):
            raise TypeError("Can only compare Money to Money")
        
        if self._currency != other._currency:
            raise ValueError(f"Cannot compare different currencies: {self._currency} and {other._currency}")
        
        return self._amount < other._amount

    def __le__(self, other: 'Money') -> bool:
        """Less than or equal comparison"""
        return self < other or self == other

    def __gt__(self, other: 'Money') -> bool:
        """Greater than comparison"""
        if not isinstance(other, Money):
            raise TypeError("Can only compare Money to Money")
        
        if self._currency != other._currency:
            raise ValueError(f"Cannot compare different currencies: {self._currency} and {other._currency}")
        
        return self._amount > other._amount

    def __ge__(self, other: 'Money') -> bool:
        """Greater than or equal comparison"""
        return self > other or self == other

    def __hash__(self) -> int:
        """Hash based on amount and currency"""
        return hash((self._amount, self._currency))