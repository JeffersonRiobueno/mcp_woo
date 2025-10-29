from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class Product(BaseModel):
    id: int
    name: str
    price: Optional[str]
    regular_price: Optional[str]
    sale_price: Optional[str]
    stock_status: Optional[str]
    categories: List[Dict] = Field(default_factory=list)

class Order(BaseModel):
    id: int
    status: str
    total: str
    customer_id: int
    line_items: List[Dict] = Field(default_factory=list)
