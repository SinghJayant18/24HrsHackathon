from datetime import datetime, date
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from .models import OrderStatus


class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    discount_percent: float = 0.0
    image_url: Optional[str] = None
    stock_quantity: int = 0
    is_active: bool = True


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    description: Optional[str] = None
    price: Optional[float] = None
    discount_percent: Optional[float] = None
    image_url: Optional[str] = None
    stock_quantity: Optional[int] = None
    is_active: Optional[bool] = None


class ItemOut(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CustomerBase(BaseModel):
    name: str
    email: EmailStr
    address: Optional[str] = None
    phone: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerOut(CustomerBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class OrderItemCreate(BaseModel):
    item_id: int
    quantity: int


class OrderCreate(BaseModel):
    customer: CustomerCreate
    items: List[OrderItemCreate]


class OrderItemOut(BaseModel):
    id: int
    item_id: int
    quantity: int
    price_at_purchase: float
    item: Optional[ItemOut] = None

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    id: int
    status: OrderStatus
    total_amount: float
    tracking_id: Optional[str] = None
    tracking_url: Optional[str] = None
    expected_delivery_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    customer: CustomerOut
    items: List[OrderItemOut]

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class ReportRequest(BaseModel):
    period: str  # day|month|year
    date_ref: Optional[date] = None


class TaxSummary(BaseModel):
    total_revenue: float
    tax_rate_percent: float
    total_tax_due: float
    period: str


class OwnerRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    pan_card: str
    contact: str
    business_name: Optional[str] = None
    business_address: Optional[str] = None
    gst_number: Optional[str] = None
    aadhar_number: Optional[str] = None
    bank_account: Optional[str] = None
    ifsc_code: Optional[str] = None


class OwnerLogin(BaseModel):
    email: EmailStr
    password: str


class OwnerOut(BaseModel):
    id: int
    name: str
    email: str
    pan_card: str
    contact: str
    business_name: Optional[str] = None
    business_address: Optional[str] = None
    gst_number: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    owner: OwnerOut
