"""
Product entity following Domain-Driven Design.
Encapsulates product business logic and validation.
"""
from typing import Optional
from uuid import UUID
from enum import Enum
from decimal import Decimal

from .base import DomainEntity
from ..value_objects.money import Money
from ...shared.exceptions.domain import DomainValidationError


class ProductStatus(str, Enum):
    """Product status enumeration"""
    AVAILABLE = "available"
    SOLD = "sold"
    RESERVED = "reserved"
    INACTIVE = "inactive"


class ProductCategory(str, Enum):
    """Product category enumeration"""
    ELECTRONICS = "electronics"
    FURNITURE = "furniture"
    BOOKS = "books"
    TOYS = "toys"
    CLOTHING = "clothing"
    SPORTS = "sports"
    TOOLS = "tools"
    OTHER = "other"


class Product(DomainEntity):
    """
    Product domain entity.
    Represents a product available for sale in the garage sale system.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        price: Money,
        seller_id: UUID,
        category: ProductCategory = ProductCategory.OTHER,
        quantity: int = 1,
        images: list = None,
        image_url: Optional[str] = None,
        qr_code_data: Optional[str] = None,
        qr_code_image_url: Optional[str] = None,
        status: ProductStatus = ProductStatus.AVAILABLE,
        id: Optional[UUID] = None,
        created_at: Optional[object] = None,
        updated_at: Optional[object] = None
    ):
        super().__init__(id)
        self._name = name
        self._description = description
        self._price = price
        self._seller_id = seller_id
        self._category = category
        self._quantity = quantity
        self._images = images or []
        self._image_url = image_url
        self._qr_code_data = qr_code_data
        self._qr_code_image_url = qr_code_image_url
        self._status = status
        self._view_count = 0
        self._reserved_by: Optional[UUID] = None
        # created_at e updated_at são gerenciados pela classe base
        if created_at:
            self._created_at = created_at
        if updated_at:
            self._updated_at = updated_at
        self.validate()

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def price(self) -> Money:
        return self._price

    @property
    def seller_id(self) -> UUID:
        return self._seller_id

    @property
    def category(self) -> ProductCategory:
        return self._category
    
    @property
    def quantity(self) -> int:
        return self._quantity
    
    @property
    def images(self) -> list:
        return self._images

    @property
    def image_url(self) -> Optional[str]:
        return self._image_url

    @property
    def qr_code_data(self) -> Optional[str]:
        return self._qr_code_data

    @property
    def qr_code_image_url(self) -> Optional[str]:
        return self._qr_code_image_url

    @property
    def status(self) -> ProductStatus:
        return self._status

    @property
    def view_count(self) -> int:
        return self._view_count

    @property
    def reserved_by(self) -> Optional[UUID]:
        return self._reserved_by
    
    @quantity.setter
    def quantity(self, value: int):
        if value < 0:
            raise DomainValidationError("Quantity cannot be negative")
        self._quantity = value
    
    @images.setter
    def images(self, value: list):
        self._images = value or []

    @property
    def is_available(self) -> bool:
        """Check if product is available for purchase"""
        return self._status == ProductStatus.AVAILABLE

    def update_details(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[Money] = None,
        category: Optional[ProductCategory] = None,
        image_url: Optional[str] = None
    ) -> None:
        """Update product details"""
        if self._status == ProductStatus.SOLD:
            raise DomainValidationError("Cannot update a sold product")
        
        if name:
            self._name = name
        if description:
            self._description = description
        if price:
            self._price = price
        if category:
            self._category = category
        if image_url is not None:
            self._image_url = image_url
        
        self.update_timestamp()
        self.validate()
        self.add_domain_event({
            "type": "ProductUpdated",
            "product_id": self.id,
            "seller_id": self._seller_id
        })

    def set_qr_code(self, qr_code_data: str, qr_code_image_url: str) -> None:
        """Set QR code data for the product"""
        if not qr_code_data or not qr_code_image_url:
            raise DomainValidationError("QR code data and image URL are required")
        
        self._qr_code_data = qr_code_data
        self._qr_code_image_url = qr_code_image_url
        self.update_timestamp()
        self.add_domain_event({
            "type": "QRCodeGenerated",
            "product_id": self.id,
            "qr_code_data": qr_code_data
        })

    def mark_as_sold(self, buyer_id: UUID) -> None:
        """Mark product as sold"""
        if self._status == ProductStatus.SOLD:
            raise DomainValidationError("Product is already sold")
        
        if self._status == ProductStatus.INACTIVE:
            raise DomainValidationError("Cannot sell an inactive product")
        
        self._status = ProductStatus.SOLD
        self.update_timestamp()
        self.add_domain_event({
            "type": "ProductSold",
            "product_id": self.id,
            "seller_id": self._seller_id,
            "buyer_id": buyer_id,
            "price": str(self._price.amount)
        })

    def reserve(self, buyer_id: UUID) -> None:
        """Reserve product for a buyer"""
        if not self.is_available:
            raise DomainValidationError(f"Product is not available for reservation. Status: {self._status}")
        
        self._status = ProductStatus.RESERVED
        self._reserved_by = buyer_id
        self.update_timestamp()
        self.add_domain_event({
            "type": "ProductReserved",
            "product_id": self.id,
            "buyer_id": buyer_id
        })

    def release_reservation(self) -> None:
        """Release product reservation"""
        if self._status != ProductStatus.RESERVED:
            raise DomainValidationError("Product is not reserved")
        
        self._status = ProductStatus.AVAILABLE
        self._reserved_by = None
        self.update_timestamp()
        self.add_domain_event({
            "type": "ProductReservationReleased",
            "product_id": self.id
        })

    def deactivate(self) -> None:
        """Deactivate product"""
        if self._status == ProductStatus.SOLD:
            raise DomainValidationError("Cannot deactivate a sold product")
        
        self._status = ProductStatus.INACTIVE
        self.update_timestamp()
        self.add_domain_event({
            "type": "ProductDeactivated",
            "product_id": self.id
        })

    def activate(self) -> None:
        """Activate product"""
        if self._status == ProductStatus.SOLD:
            raise DomainValidationError("Cannot activate a sold product")
        
        self._status = ProductStatus.AVAILABLE
        self.update_timestamp()
        self.add_domain_event({
            "type": "ProductActivated",
            "product_id": self.id
        })

    def increment_view_count(self) -> None:
        """Increment product view count"""
        self._view_count += 1

    def apply_discount(self, percentage: Decimal) -> None:
        """Apply discount to product price"""
        if self._status == ProductStatus.SOLD:
            raise DomainValidationError("Cannot apply discount to a sold product")
        
        if percentage < 0 or percentage > 100:
            raise DomainValidationError("Discount percentage must be between 0 and 100")
        
        discount_amount = self._price.amount * (percentage / 100)
        new_price = self._price.amount - discount_amount
        self._price = Money(new_price, self._price.currency)
        
        self.update_timestamp()
        self.add_domain_event({
            "type": "DiscountApplied",
            "product_id": self.id,
            "discount_percentage": str(percentage),
            "new_price": str(new_price)
        })

    def validate(self) -> None:
        """Validate product entity state"""
        if not self._name or len(self._name.strip()) < 3:
            raise DomainValidationError("Product name must be at least 3 characters long")
        
        if len(self._name) > 200:
            raise DomainValidationError("Product name cannot exceed 200 characters")
        
        if not self._description or len(self._description.strip()) < 10:
            raise DomainValidationError("Product description must be at least 10 characters long")
        
        if len(self._description) > 2000:
            raise DomainValidationError("Product description cannot exceed 2000 characters")
        
        if self._price.amount <= 0:
            raise DomainValidationError("Product price must be greater than zero")
        
        if self._category not in ProductCategory:
            raise DomainValidationError(f"Invalid category: {self._category}")
        
        if self._status not in ProductStatus:
            raise DomainValidationError(f"Invalid status: {self._status}")