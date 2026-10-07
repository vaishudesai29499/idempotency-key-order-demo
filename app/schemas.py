from pydantic import BaseModel, Field
class OrderCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=120)
    product: str = Field(min_length=1, max_length=200)
    quantity: int = Field(gt=0)
    amount: float = Field(gt=0)
class OrderResponse(BaseModel):
    id: int
    customer_name: str
    product: str
    quantity: int
    amount: float
    status: str
    model_config = {"from_attributes": True}
